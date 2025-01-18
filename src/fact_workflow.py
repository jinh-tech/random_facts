from typing import Annotated, Dict, TypedDict
from langgraph.graph import Graph
from langchain_core.messages import BaseMessage

# Import our existing components
from topic_handler import create_topic_chain, TopicOutput
from langchain_facts import create_fact_chain

class WorkflowState(TypedDict):
    topic: str
    facts: str
    is_random: bool

def create_fact_workflow() -> Graph:
    # Initialize our chains
    topic_chain = create_topic_chain()
    facts_chain = create_fact_chain()
    
    def process_topic(state: Dict) -> WorkflowState:
        """Process the user input to determine the topic"""
        topic_result = topic_chain.invoke({'user_input': state['user_input']})
        return {
            **state,
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
    
    # Create the workflow graph
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("process_topic", process_topic)
    workflow.add_node("generate_facts", generate_facts)
    
    # Define edges
    workflow.add_edge("process_topic", "generate_facts")
    
    # Set entry point
    workflow.set_entry_point("process_topic")
    
    # Set the final node
    workflow.set_finish_point("generate_facts")
    
    return workflow.compile()

if __name__ == "__main__":
    # Create the workflow
    workflow = create_fact_workflow()
    
    # Test cases
    test_inputs = [
        "Tell me about elephants",
        "I don't know, surprise me",
        "platypus"
    ]
    
    for user_input in test_inputs:
        print(f"\nInput: {user_input}")
        result = workflow.invoke({
            "user_input": user_input,
            "topic": "",
            "facts": "",
            "is_random": False
        })
        print(f"Topic: {result['topic']} (Random: {result['is_random']})")
        print("Facts:")
        print(result['facts']) 