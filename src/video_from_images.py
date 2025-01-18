import cv2
import os
import random
import numpy as np
from moviepy import ImageClip, concatenate_videoclips, CompositeVideoClip, vfx
from moviepy.video.fx import SlideIn, SlideOut, FadeIn, FadeOut


MAX_IMAGES_IN_VIDEO = 10
MIN_SEC_PER_IMAGE = 1
MAX_SEC_PER_IMAGE = 5
MP4V_CODEC = cv2.VideoWriter_fourcc(*'mp4v')
VIDEO_FPS = 30

FADE_DURATION = 0.3
SLIDE_DURATION = 0.5
ZOOM_SPEED = 0.06

RANDOM_EFFECT_LIST = [
    [FadeIn(FADE_DURATION)],
    [FadeOut(FADE_DURATION)],
    [SlideIn(SLIDE_DURATION, 'left')],
    [SlideOut(SLIDE_DURATION, 'left')],
    [SlideIn(SLIDE_DURATION, 'right')],
    [SlideOut(SLIDE_DURATION, 'right')],
    [vfx.Resize(lambda t : 1+ZOOM_SPEED*t)],
    [vfx.Resize(lambda t : 1-ZOOM_SPEED*t)],
]

RANDOM_EFFECT_DICT = {i: effect for i, effect in enumerate(RANDOM_EFFECT_LIST)}

def random_moviepy_effect():
    rand_index = random.randint(0, len(RANDOM_EFFECT_DICT)-1)
    return RANDOM_EFFECT_DICT[rand_index]

def ensure_video_length(images_path, duration_per_image_list, video_duration_sec):

    if sum(duration_per_image_list) < video_duration_sec:
        mult_factor = np.ceil(video_duration_sec/sum(duration_per_image_list))
        duration_per_image_list = [int(duration * mult_factor) for duration in duration_per_image_list]
    
    video_length_till_now = 0
    for index, duration in enumerate(duration_per_image_list):
        video_length_till_now += duration
        if video_length_till_now >= video_duration_sec:
            break
    
    duration_per_image_list[index] -= (video_length_till_now - video_duration_sec)

    return images_path[:index+1], duration_per_image_list[:index+1]
    
# def video_from_images(image_folder, video_folder, video_name):

#     images_path = [img for img in os.listdir(image_folder) if img.endswith(".jpg")]
#     images_path = images_path[:MAX_IMAGES_IN_VIDEO]

#     frame = cv2.imread(os.path.join(image_folder, images_path[0]))
#     height, width, layers = frame.shape

#     video_save_path = os.path.join(video_folder, video_name)
#     video = cv2.VideoWriter(video_save_path, MP4V_CODEC, VIDEO_FPS, (width,height))

#     for image_path in images_path:
#         random_num_frames = int(random.uniform(MIN_SEC_PER_IMAGE, MAX_SEC_PER_IMAGE) * VIDEO_FPS)
#         image_path = os.path.join(image_folder, image_path)
#         image = cv2.imread(image_path)
        
#         for _ in range(random_num_frames):
#             video.write(image)

#     cv2.destroyAllWindows()
#     video.release()

def video_from_images_moviepy(image_folder, video_file_path, video_duration_sec):

    images_path = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images_path = images_path[:MAX_IMAGES_IN_VIDEO]

    clips = []
    duration_per_image_list = [int(random.uniform(MIN_SEC_PER_IMAGE, MAX_SEC_PER_IMAGE)) for _ in images_path]
    images_path, duration_per_image_list = ensure_video_length(images_path, duration_per_image_list, video_duration_sec)

    for image, duration_per_image in zip(images_path, duration_per_image_list):
        image_path = os.path.join(image_folder, image)
        random_effect = random_moviepy_effect()
        image_clip = ImageClip(image_path, duration=duration_per_image).with_effects(random_effect)
        clip = CompositeVideoClip([image_clip])
        clips.append(clip)

    video = concatenate_videoclips(clips)
    video.write_videofile(video_file_path, fps=30)

if __name__ == "__main__":

    image_folder = '../data/images/test_images/'
    video_file_path = '../data/videos/test_videos/test_video_moviepy.mp4'
    video_duration_sec = 16

    video_from_images_moviepy(image_folder, video_file_path, video_duration_sec)