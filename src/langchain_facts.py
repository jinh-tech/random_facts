from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_community.tools import TavilySearchResults
import os

from dotenv import load_dotenv
load_dotenv()

def create_fact_chain():
    """
    Creates a LangChain pipeline for generating facts.
    """
    mistral = ChatMistralAI(
        model="mistral-tiny",
        temperature=0.7,
        max_tokens=200,
    )
    
    search = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
    
    # Create a weird facts discovery chain
    facts_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a curator of fascinating and unusual facts. When given a topic, use the provided search results to find the most interesting, surprising, or weird facts about it. Focus on lesser-known information that would intrigue people."),
        ("user", """Based on these search results, what are 3 of the most interesting or unusual facts about {topic}? 
        Search results: {search_results}
        
        Format your response as a numbered list of weird facts.""")
    ])
    
    # Combine search and LLM into a chain
    facts_chain = (
        {"topic": lambda x: x, "search_results": search} 
        | facts_prompt 
        | mistral
    )
    
    return facts_chain

if __name__ == '__main__':
    chain = create_fact_chain()
    result = chain.invoke("platypus")
    print(result.content)

    