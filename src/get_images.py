from typing import TypedDict
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
import requests
import os

load_dotenv()

class ImageGenerationInput(TypedDict):
    prompt: str
    aspect_ratio: str
    output_filepath: str

class ImageGenerationOutput(TypedDict):
    output_filepath: str

def generate_image(input: ImageGenerationInput) -> ImageGenerationOutput:

    print('generating image...')
    
    url = "https://api.segmind.com/v1/fast-flux-schnell"
    
    data = {
        "prompt": input["prompt"],
        "aspect_ratio": input["aspect_ratio"]
    }

    headers = {'x-api-key': os.environ.get('SEGMIND_API_KEY')}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 200:
        with open(input["output_filepath"], 'wb') as f:
            f.write(response.content)
        return {"output_filepath": input["output_filepath"]}
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

def create_image_generation_chain():
    return RunnableLambda(generate_image)