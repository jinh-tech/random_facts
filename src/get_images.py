from dotenv import load_dotenv
import requests
import base64
import os

load_dotenv()  # Load environment variables from .env file


# Use this function to convert an image file from the filesystem to base64
def image_file_to_base64(image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

# Use this function to fetch an image from a URL and convert it to base64
def image_url_to_base64(image_url):
    response = requests.get(image_url)
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

url = "https://api.segmind.com/v1/fast-flux-schnell"

# Request payload
data = {
  "prompt": "Did you know that Indonesia, the world's fourth most populous country, is also home to over 17,000 islands? That's more islands than Starbucks has stores worldwide!",
  "aspect_ratio": "1:1"
}

headers = {'x-api-key': os.environ.get('SEGMIND_API_KEY')}

response = requests.post(url, json=data, headers=headers)
# Save the image response to a file
if response.status_code == 200:
    with open('generated_image.png', 'wb') as f:
        f.write(response.content)
    print("Image saved as 'generated_image.png'")
else:
    print(f"Error: {response.status_code}")
    print(response.text)