from pathlib import Path
import os
import random
import string
from moviepy.editor import VideoFileClip

BASE_DIR = Path(__file__).resolve().parent.parent.parent
def handle_uploaded_file(f):  
    # Generate a random string with 32 characters.
    random_name = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(16)]) + '.mp4'
    full_path = os.path.join(BASE_DIR, 'static', 'videos', random_name)
    with open(full_path, 'wb+') as destination:  
        for chunk in f.chunks():  
            destination.write(chunk)
    # print(random_name, full_path)
    return random_name, full_path

def check_video_duration(file_path):
    clip = VideoFileClip(file_path)
    return clip.duration