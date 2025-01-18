from typing import Tuple
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
import random
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, validator

class TopicOutput(BaseModel):
    topic: str
    flag_random: bool
    
    # Add model config for Pydantic v2
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "topic": "elephants",
                    "flag_random": False
                }
            ]
        }
    }

# Fallback random topics if LLM fails
FALLBACK_TOPICS = [
    "cats", "space", "coffee", "penguins", "chocolate", "volcanoes",
    "dinosaurs", "ocean", "rainforest", "ancient egypt"
]



def create_topic_chain():
    """
    Creates a LangChain pipeline for topic handling.
    """
    # Initialize the model
    llm = ChatMistralAI(
        model="mistral-tiny",
        temperature=0.7,
        max_tokens=50,
    )
    
    parser = PydanticOutputParser(pydantic_object=TopicOutput)

    # Create prompt for topic analysis
    topic_prompt = PromptTemplate(
        template="""You are a helpful assistant that determines if a user has a specific topic in mind.
        If they do, extract the main topic. If they don't (e.g. user says 'idk', 'no', 'anything'),
        generate an interesting random topic.
        
        Do not add details to the topic coming from the user!
        While, if you generate a random topic, just stick with something quite general 
        (e.g. 'elephants', 'berghain', 'pizza', ...) 
        
        Answer using a JSON format...
        {{ format_instructions }}

        User input: 'Indonesia'
        {
            "flag_random": false,
            "topic": "Indonesia"
        }

        User input: 'idk'
        {
            "flag_random": True,
            "topic": "sloth"
        }
        
        User input: {{ user_input }}""",
        template_format='jinja2',
        input_variables=["user_input"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    # Create the chain
    topic_chain = topic_prompt | llm | parser
    
    return topic_chain


# Example usage
if __name__ == "__main__":
    # Test cases
    test_inputs = [
        "Tell me about elephants",
        "I don't know, anything is fine",
    ]
    chain = create_topic_chain()
    for input_text in test_inputs:
        result = chain.invoke({'user_input': input_text})
        print(result) 