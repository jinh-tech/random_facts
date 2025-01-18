from typing import Annotated, Dict, TypedDict
import uuid
import json
import os
from langgraph.graph import Graph
from langchain_core.messages import BaseMessage

# Import our existing components
from topic_handler import create_topic_chain, TopicOutput
from langchain_facts import create_fact_chain
from audio import generate_audio_and_update_state
from get_images import create_image_generation_chain

class WorkflowState(TypedDict):
    thread_id: str
    topic: str
    facts: str
    is_random: bool
    audio_filepath: str | None
    image_filepath: str | None

def create_fact_workflow() -> Graph:
    # Initialize our chains
    topic_chain = create_topic_chain()
    facts_chain = create_fact_chain()
    image_chain = create_image_generation_chain()
    
    def process_topic(state: Dict) -> WorkflowState:
        """Process the user input to determine the topic"""
        topic_result = topic_chain.invoke({'user_input': state['user_input']})
        return {
            **state,
            "thread_id": str(uuid.uuid4()),  # Generate unique thread ID
            "topic": topic_result.topic,
            "is_random": topic_result.flag_random
        }
    
    def generate_facts(state: Dict) -> WorkflowState:
        """Generate facts about the determined topic"""
        facts_result = facts_chain.invoke(state["topic"])
        return {
            **state,
            "facts": facts_result.content
        }
    
    def generate_audio(state: Dict) -> WorkflowState:
        """Generate audio from the facts and save results"""
        # Create thread directory
        thread_dir = f"output/{state['thread_id']}"
        os.makedirs(thread_dir, exist_ok=True)
        
        # Generate audio with updated path
        updated_state = generate_audio_and_update_state(
            text=state["facts"], 
            state=state,
            output_filepath=f"{thread_dir}/output.wav"
        )
            
        return updated_state
    
    def generate_image_instructions(state: Dict) -> WorkflowState:
        """Transform facts into specific image generation instructions"""
        # Create a more structured and focused image prompt
        instructions = (
            "Create a single cohesive illustration that represents the following facts:\n"
            f"{state['facts']}\n\n"
            "Art Direction:\n"
            "- Style: Modern digital art with a clean, educational approach\n"
            "- Colors: Rich, vibrant palette with good contrast\n"
            "- Composition: Centered, balanced layout with a clear focal point\n"
            "- Lighting: Soft, natural lighting to enhance readability\n"
            "- Detail Level: High detail for main elements, simplified background\n"
            "- Mood: Engaging and informative\n\n"
            "Technical Requirements:\n"
            "- Maintain professional quality suitable for educational content\n"
            "- Avoid text or labels in the image\n"
            "- Ensure all elements are family-friendly and appropriate\n"
            "- Create a scene that tells a story about the facts"
        )
        
        return {
            **state,
            "image_instructions": instructions
        }
    
    def create_txt2img_prompt(state: Dict) -> WorkflowState:
        """Convert image instructions into a concise, focused text-to-image prompt"""
        # Extract key information and create a more direct prompt
        base_prompt = (
            "A single educational illustration showing "
            f"{state['topic']}, "
            "digital art style, vibrant colors, centered composition, "
            "soft lighting, detailed main subject with simple background. "
            "The scene should depict: "
            f"{state['facts'][:200]}..."  # Truncate facts to avoid overwhelming the model
        )
        
        # Add quality boosters and style modifiers
        enhanced_prompt = (
            f"{base_prompt} "
            "trending on artstation, professional quality, "
            "cohesive composition, educational illustration, "
            "high detail, clean lines, perfect composition"
        )
        
        return {
            **state,
            "txt2img_prompt": enhanced_prompt
        }
    
    def generate_image(state: Dict) -> WorkflowState:
        """Generate an image based on the refined text-to-image prompt"""
        thread_dir = f"output/{state['thread_id']}"
        output_filepath = f"{thread_dir}/image.png"
        
        image_result = image_chain.invoke({
            "prompt": state["txt2img_prompt"],  # Use the refined prompt instead of instructions
            "aspect_ratio": "1:1",
            "output_filepath": output_filepath
        })
        
        return {
            **state,
            "image_filepath": image_result["output_filepath"]
        }
    
    def save_state(state: Dict) -> WorkflowState:
        """Save the final state as JSON"""
        thread_dir = f"output/{state['thread_id']}"
        
        # Save state as JSON
        state_to_save = {
            "thread_id": state["thread_id"],
            "topic": state["topic"],
            "facts": state["facts"],
            "is_random": state["is_random"],
            "audio_filepath": state["audio_filepath"],
            "audio_duration": state["audio_duration"],
            "synthesis_durations": state["synthesis_durations"],
            "image_filepath": state["image_filepath"],
            "image_instructions": state["image_instructions"],
        }
        with open(f"{thread_dir}/result.json", "w") as f:
            json.dump(state_to_save, f, indent=2)
            
        return state
    
    # Create the workflow graph
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("process_topic", process_topic)
    workflow.add_node("generate_facts", generate_facts)
    workflow.add_node("generate_audio", generate_audio)
    workflow.add_node("generate_image_instructions", generate_image_instructions)
    workflow.add_node("create_txt2img_prompt", create_txt2img_prompt)
    workflow.add_node("generate_image", generate_image)
    workflow.add_node("save_state", save_state)
    
    # Define edges
    workflow.add_edge("process_topic", "generate_facts")
    workflow.add_edge("generate_facts", "generate_audio")
    workflow.add_edge("generate_audio", "generate_image_instructions")
    workflow.add_edge("generate_image_instructions", "create_txt2img_prompt")
    workflow.add_edge("create_txt2img_prompt", "generate_image")
    workflow.add_edge("generate_image", "save_state")
    
    # Set entry point
    workflow.set_entry_point("process_topic")
    
    # Set the final node
    workflow.set_finish_point("save_state")
    
    return workflow.compile()

if __name__ == "__main__":
    # Create the workflow
    workflow = create_fact_workflow()
    
    # Test cases
    test_inputs = [
        # "Tell me about elephants",
        # "I don't know, surprise me",
        "indonesia"
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = workflow.invoke({
            "user_input": user_input,
            "thread_id": "",  # Will be generated in process_topic
            "topic": "",
            "facts": "",
            "is_random": False,
            "audio_filepath": None,
        })
        print(f"Thread ID: {result['thread_id']}")
        print(f"Topic: {result['topic']} (Random: {result['is_random']})")
        print("Facts:")
        print(result['facts'])
        print(f"Audio generated at: {result['audio_filepath']}") 