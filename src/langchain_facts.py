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
        max_tokens=300,
    )
    
    search = TavilySearchResults(api_key=os.getenv("TAVILY_API_KEY"))
    
    # Create a weird facts discovery chain
    facts_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a curator of fascinating and unusual facts. When given a topic, use the provided search results to find the most interesting, surprising, or weird facts about it. Focus on lesser-known information that would intrigue people."),
        ("user", """Based on these search results, what is the most interesting or unusual facts about {topic}? 
        Search results: {search_results}
        
        Format your response so that a person can read it out loud!
        Therefore, do not include bullet points, urls, and so on...
         
        Output should be short, just one sentence because it has to go viral!
        It should be very engaging: use a funny and ironic tone""")
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

    