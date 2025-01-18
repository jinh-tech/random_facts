from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
import json

FONT = "../quattrocentosans-regular-webfont.ttf"

def join_video_with_audio(video_file_path, audio_file_path, output_file_path):

    video = VideoFileClip(video_file_path)
    audio = AudioFileClip(audio_file_path)

    video_with_audio = video.with_audio(audio)
    video_with_audio.write_videofile(output_file_path, codec="libx264", audio_codec="aac")


def add_subtitle_to_video(video_file_path, subtitle_file_path, output_file_path):

    video = VideoFileClip(video_file_path)
    with open(subtitle_file_path, "r") as file:
        subtitles_dict = json.load(file)["synthesis_durations"]

    video_subtiles = [ 
        TextClip(FONT, 
                text=sub_data['text'], 
                font_size=24, 
                color='white', 
                duration=sub_data['duration'], 
                method='label',
                bg_color='black'
                ).with_start(sub_data['start']).with_position(("center", "bottom"))
        for sub_data in subtitles_dict
    ]

    video_with_subtitles = CompositeVideoClip([video, *video_subtiles])
    video_with_subtitles.write_videofile(output_file_path, codec="libx264", audio_codec="aac")

if __name__ == "__main__":

    video_file_path = '../data/videos/test_videos/test_video_moviepy.mp4'
    audio_file_path = '../data/audio/test_audio/output.wav'
    subtitle_path = '../data/audio/test_audio/result.json'
    
    output_video_audio_path = '../data/videos/test_videos/test_video_moviepy_audio.mp4'
    output_video_audio_subtitle_path = '../data/videos/test_videos/test_video_moviepy_audio_subtitle.mp4'

    join_video_with_audio(video_file_path, audio_file_path, output_video_audio_path)
    add_subtitle_to_video(output_video_audio_path, subtitle_path, output_video_audio_subtitle_path)