from fact_workflow import create_fact_workflow
from video_from_images import video_from_images_moviepy
from audio_subtitles import join_video_with_audio, add_subtitle_to_video
import json

workflow = create_fact_workflow()
    
test_input = "pepsi vs coca cola war"

from datetime import datetime
thread_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + test_input

result = workflow.invoke({
    "user_input": test_input,
    "thread_id": thread_id,
})

output_folder = f"../data/output/{thread_id}"
video_file_path = output_folder + "/video.mp4"
audio_file_path = output_folder + "/output.wav"
video_with_audio_path = output_folder + '/video_with_audio.mp4'
subtitle_file_path = output_folder + '/result.json'
video_with_audio_subtitle_path = output_folder + '/video_with_audio_subtitle.mp4'

with open(output_folder + '/result.json') as file:
    video_duration_sec = json.load(file)["audio_duration"]

video_from_images_moviepy(output_folder, video_file_path, video_duration_sec)
join_video_with_audio(video_file_path, audio_file_path, video_with_audio_path)
add_subtitle_to_video(video_with_audio_path, subtitle_file_path, video_with_audio_subtitle_path)
