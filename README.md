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

Below we mention the technical details about our project.
1. The streamlit frontend takes input from the user.
2. Using the topic and existing prompt, we query [Tavily](https://tavily.com/) to receive a fact(text) about the topic and a video description(text).
3. We convert the fact(text) into audio using [LMNT](https://www.lmnt.com/).
4. We use [Segmind](https://www.segmind.com/) to generate 2 images based on the fact that was generated earlier.
5. Using [Moviepy](https://zulko.github.io/moviepy/), we stich the images into a short video with effects like ZoomIn and FadeIn.
6. We combine the audio and add subtiles to the video created in the previous step by using [Moviepy](https://zulko.github.io/moviepy/) again.

