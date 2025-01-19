from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.tools import TavilySearchResults
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import os

class FactOutput(BaseModel):
    viral_fact: str = Field(description="A short, engaging sentence about the topic")
    description: str = Field(description="2-3 sentences expanding on the fact with more context")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "viral_fact": "Platypuses glow in the dark under UV light, making them nature's own party animals!",
                    "description": "Scientists discovered that platypus fur fluoresces with a blue-green glow under UV light. This bizarre trait was found in 2020, adding to the already long list of unusual characteristics of these egg-laying mammals."
                }
            ]
        }
    }

def create_fact_chain():
    """
    Creates a LangChain pipeline for generating facts.
    """
    mistral = ChatMistralAI(
        model="mistral-large-latest",
        temperature=0.7,
        max_tokens=2000,
        response_format = {
            "type": "json_object",
        }
    )
    
    search = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
    parser = PydanticOutputParser(pydantic_object=FactOutput)
    
    # Create prompts for both viral fact and video description
    facts_prompts = ChatPromptTemplate.from_messages([
        ("system", "You are a curator of fascinating and unusual facts. When given a topic, use the provided search results to find the most interesting, surprising, or weird facts about it. Focus on lesser-known information that would intrigue people."),
        ("user", """Based on these search results, provide two outputs about {topic}:
        Search results: {search_results}
        
        1. VIRAL FACT:
        Create one short, engaging sentence (80-100 words) with a funny and ironic tone. Make it ready to read out loud (no bullet points or URLs).
        
        2. VIDEO DESCRIPTION:
        Write 2-3 sentences expanding on the fact with more context and details. Include one relevant URL from the search results if available.
        
        The Output is a JSON!
        
        {format_instructions}""")
    ])
    
    # Partially fill the prompt template with format instructions
    facts_prompts_with_format = facts_prompts.partial(format_instructions=parser.get_format_instructions())
    
    # Combine search and LLM into a chain
    facts_chain = (
        {"topic": lambda x: x, 
         "search_results": search} 
        | facts_prompts_with_format 
        | mistral 
        | parser
    )
    
    return facts_chain

if __name__ == '__main__':
    chain = create_fact_chain()
    result = chain.invoke("platypus")
    
    print("Viral Fact:", result.viral_fact)
    print("\nVideo Description:", result.description)

    