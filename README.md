# Historical Facts Video Generator

## About

**Project Description:**

Our project aims to change the way we consume educational content by leveraging the power of short-form videos. Through a simple, user-friendly Streamlit frontend, users can input any topic, and our system will automatically generate a 10-second video. Each video showcases an interesting fact about the topic, accompanied by relevant audio, images and subtitles to make learning both engaging and accessible.

In the future, we plan to fully automate this pipeline, utilizing AI agents to gather trending topics from the news or historical knowledge from the web. The AI will generate a short-form video that combines the latest information with dynamic visuals, creating an educational piece that captures attention quickly. These videos will be automatically uploaded to platforms like TikTok, Instagram Reels, and YouTube Shorts, making knowledge shareable and easily accessible to millions of users.

Our goal is to harness the addictive nature of short-form content for positive impact—turning it into a tool for learning, exploration, and curiosity. By automating this process, we aim to keep the content fresh, relevant, and engaging, promoting continuous learning in an increasingly digital world.

## Installation

* Clone the repo
* Run 
``` 
cd PATH_TO_CLONED_REPO
poetry install
```
* Create a `.env` file and enter the keys for the following APIs. We used the free tier for all these APIs.
```
MISTRAL_API_KEY=xxx
TAVILY_API_KEY=xxx
HUGGINGFACE_TOKEN=xxx
LMNT_API_KEY=xxx
SEGMIND_API_KEY=xxx
```
* To launch the streamlit fronted, run

``` 
streamlit run streamlit_app.py 
```
* A web app will open in your browser. Enter a topic and click on generate video.
* A video along with some data will appear in the browser after 30 to 120 sec. Inisde the repo, a new folder with the name `data/output/{DateTime}_{Topic mentioned in prompt}` will be created. Inside this folder, the final video will have the name `video_with_audio_subtitles.mp4` and will be present alongside other intermediate data.


## Technical Details

Here is a step-by-step overview of the technical workflow in our project:

1. User Input via Streamlit  
   The Streamlit frontend accepts input from the user, specifying the topic.

2. Information Retrieval with Tavily  
   Based on the provided topic, we query [Tavily](https://tavily.com/) to retrieve relevant information.

3. Output Generation with Mistral  
   We call Mistral, which generates a JSON output containing two elements:  
   - Fact (text): A textual fact about the topic.  
   - Video Description (text): A description for the video.

4. Text-to-Audio Conversion with LMNT  
   The fact text is converted into an audio voiceover using [LMNT](https://www.lmnt.com/).

5. Dynamic Prompt Creation by Mistral  
   Mistral dynamically generates text-to-image (txt2img) prompts based on the fact text, which will be displayed in the video.

6. Image Generation with Segmind  
   Using the txt2img prompts, we generate two images with [Segmind](https://www.segmind.com/).

7. Video Creation with MoviePy  
   The generated images are stitched into a short video using [MoviePy](https://zulko.github.io/moviepy/), with visual effects such as ZoomIn and FadeIn.

8. Final Video Enhancements  
   The audio voiceover is combined with the video, and subtitles are added using [MoviePy](https://zulko.github.io/moviepy/) once again.

