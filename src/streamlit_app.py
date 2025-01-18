import streamlit as st
from fact_workflow import create_fact_workflow
from video_from_images import video_from_images_moviepy
from audio_subtitles import join_video_with_audio, add_subtitle_to_video
import json
from datetime import datetime
from src import DATA_DIR

import logging
from loguru import logger

class StreamlitLogHandler(logging.Handler):
    def __init__(self, widget_update_func):
        super().__init__()
        self.widget_update_func = widget_update_func

    def emit(self, record):
        msg = self.format(record)
        self.widget_update_func(msg)



st.title("Historical Facts Video Generator")
st.write("Enter a historical topic to generate a video about it!")

# Initialize the workflow
@st.cache_resource
def get_workflow():
    return create_fact_workflow()

workflow = get_workflow()

# Create input field
user_input = st.text_input("Enter a historical topic:", "pepsi vs coca cola war")

if st.button("Generate Video"):
    with st.spinner("Generating your video... This may take a few minutes."):

        # Create a Streamlit placeholder for logs
        log_placeholder = st.empty()

        # Configure loguru to use the Streamlit handler
        logger.remove()  # Remove default handler
        logger.add(lambda msg: log_placeholder.code(msg), format="{message}")


        # Generate thread ID

        # thread_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + user_input

        thread_id = '20250118_183003'

        
        # Create the video
        result = workflow.invoke({
            "user_input": user_input,
            "thread_id": thread_id,
        })

        # Set up file paths
        output_folder = f"{DATA_DIR}/output/{thread_id}"
        video_file_path = output_folder + "/video.mp4"
        audio_file_path = output_folder + "/output.wav"
        video_with_audio_path = output_folder + '/video_with_audio.mp4'
        subtitle_file_path = output_folder + '/result.json'
        video_with_audio_subtitle_path = output_folder + '/video_with_audio_subtitle.mp4'

        # Load video duration
        with open(subtitle_file_path) as file:
            video_duration_sec = json.load(file)["audio_duration"]

        logger.info('video_from_images_moviepy...')

        # Generate final video
        video_from_images_moviepy(output_folder, video_file_path, video_duration_sec)

        logger.info('join_video_with_audio...')
        join_video_with_audio(video_file_path, audio_file_path, video_with_audio_path)
        
        logger.info('add_subtitle_to_video...')
        add_subtitle_to_video(video_with_audio_path, subtitle_file_path, video_with_audio_subtitle_path)

        # Display the final video
        st.success("Video generated successfully!")
        st.video(video_with_audio_subtitle_path)
