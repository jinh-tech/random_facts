import streamlit as st
from src.fact_workflow import create_fact_workflow
from src.video_from_images import video_from_images_moviepy
from src.audio_subtitles import join_video_with_audio, add_subtitle_to_video
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


# Text input field
user_input = st.text_input(
    "Enter a historical or trending topic (e.g. try 'Pepsi fleet', 'Pinerolo', ...):",
    key="user_input"
)



# Button to generate the video
if st.button("Generate Video") and user_input:
    st.write(f"Generating video for: {user_input}")
    
    with st.spinner(f"Generating your video about '{user_input}'... This may take 30 seconds."):

        # Create a Streamlit placeholder for logs
        log_placeholder = st.empty()

        # Configure loguru to use the Streamlit handler
        logger.remove()  # Remove default handler
        logger.add(lambda msg: log_placeholder.code(msg), format="{message}")


        # Generate thread ID
        thread_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + user_input

        # Create the video
        result = workflow.invoke({
            "user_input": user_input,
            "thread_id": thread_id,
        })

        # # Set up file paths
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

        # Display the subtitle JSON content
        with open(subtitle_file_path) as file:
            subtitle_data = json.load(file)

        st.video(video_with_audio_subtitle_path)

        st.markdown(subtitle_data['description'])

        st.subheader("Intermediate data and prompts")
        st.json(subtitle_data)
        