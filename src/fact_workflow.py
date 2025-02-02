from typing import Annotated, Dict, TypedDict
import uuid
import json
import os
from langgraph.graph import Graph
from langchain_core.messages import BaseMessage
from langchain_core.prompts import PromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

# Import our existing components
from src.topic_handler import create_topic_chain, TopicOutput
from src.langchain_facts import create_fact_chain
from src.audio import generate_audio_and_update_state
from src.get_images import create_image_generation_chain
from loguru import logger

from src import OUTPUT_DIR

class WorkflowState(TypedDict):
    thread_id: str
    topic: str
    facts: str
    is_random: bool
    audio_filepath: str | None
    image_filepath: str | None

class ImagePrompts(BaseModel):
    prompts: list[str] = Field(
        description="Two detailed prompts for image generation",
        min_items=2,
        max_items=2
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [{
                "prompts": [
                    "A majestic elephant standing in morning mist, trunk raised, backlit by golden sunlight",
                    "Close-up of an elephant's eye showing intricate wrinkles and long eyelashes"
                ]
            }]
        }
    }

def create_fact_workflow() -> Graph:
    # Initialize our chains
    topic_chain = create_topic_chain()
    facts_chain = create_fact_chain()
    image_chain = create_image_generation_chain()
    
    # Create LLM chain for prompt generation
    llm = ChatMistralAI(
        model="mistral-medium",  # or "mistral-small", "mistral-large" depending on your needs
        temperature=0.7,
        response_format = {
            "type": "json_object",
        }
    )
    
    def process_topic(state: Dict) -> WorkflowState:
        """Process the user input to determine the topic"""

        logger.info('process_topic...')

        topic_result = topic_chain.invoke({'user_input': state['user_input']})
        return {
            **state,
            "topic": topic_result.topic,
            "is_random": topic_result.flag_random
        }
    
    def generate_facts(state: Dict) -> WorkflowState:
        """Generate facts about the determined topic"""

        logger.info('generate_facts...')

        facts_result = facts_chain.invoke(state["topic"])
        return {
            **state,
            "viral_fact": facts_result.viral_fact,
            "description": facts_result.description,
        }
    
    def generate_audio(state: Dict) -> WorkflowState:
        """Generate audio from the facts and save results"""

        logger.info('generate_audio...')

        # Create thread directory
        thread_dir = f"{OUTPUT_DIR}/{state['thread_id']}"
        os.makedirs(thread_dir, exist_ok=True)
        
        # Generate audio with updated path
        updated_state = generate_audio_and_update_state(
            text=state["viral_fact"], 
            state=state,
            output_filepath=f"{thread_dir}/output.wav"
        )
            
        return updated_state
    
    def generate_image_instructions(state: Dict) -> WorkflowState:
        """Transform facts into specific image generation instructions"""
        # Create a more structured and focused image prompt
        instructions = (
            "Create a single cohesive illustration that represents the following facts:\n"
            f"{state['viral_fact']}\n\n"
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
        """Generate two thematically related text-to-image prompts"""

        logger.info('create_txt2img_prompt...')

        parser = PydanticOutputParser(pydantic_object=ImagePrompts)
        
        base_prompt = PromptTemplate(
            template="""Create two different prompts for image generation that illustrate this fact:
                {viral_fact}

                Requirements:
                - Each prompt should be a single detailed sentence
                - Prompts should be thematically related but visually distinct
                - Include specific visual elements and composition details
                - Maintain educational value while being visually engaging
                - Consider lighting, mood, and perspective

                OUTPUT JSON

                {format_instructions}
            """,
            input_variables=["viral_fact"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Generate prompts using the LLM
        chain = base_prompt | llm | parser
        prompt_result = chain.invoke({"viral_fact": state["viral_fact"]})
        
        return {
            **state,
            "txt2img_prompts": prompt_result.prompts
        }

    
    def generate_image(state: Dict) -> WorkflowState:
        """Generate two images based on the refined text-to-image prompts"""

        logger.info('generate_image...')

        thread_dir = f"{OUTPUT_DIR}/{state['thread_id']}"
        
        image_filepaths = []
        for idx, prompt in enumerate(state["txt2img_prompts"]):
            output_filepath = f"{thread_dir}/image_{idx + 1}.png"
            
            image_result = image_chain.invoke({
                "prompt": prompt,
                "aspect_ratio": "9:16",
                "output_filepath": output_filepath
            })
            
            image_filepaths.append(image_result["output_filepath"])
        
        return {
            **state,
            "image_filepaths": image_filepaths
        }
    
    def save_state(state: Dict) -> WorkflowState:
        """Save the final state as JSON"""

        logger.info('save_state...')

        thread_dir = f"{OUTPUT_DIR}/{state['thread_id']}"
        
        # Save state as JSON
        state_to_save = {
            "thread_id": state["thread_id"],
            "topic": state["topic"],
            "viral_fact": state["viral_fact"],
            "description": state["description"],
            "is_random": state["is_random"],
            "audio_filepath": state["audio_filepath"],
            "audio_duration": state["audio_duration"],
            "synthesis_durations": state["synthesis_durations"],
            "txt2img_prompts": state["txt2img_prompts"],
            "image_filepaths": state["image_filepaths"],
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
        "memes"
    ]
    
    from datetime import datetime
    thread_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = workflow.invoke({
            "user_input": user_input,
            "thread_id": thread_id,
        })
        print(f"Thread ID: {result['thread_id']}")
        print(f"Topic: {result['topic']} (Random: {result['is_random']})")
