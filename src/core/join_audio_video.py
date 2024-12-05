from src.core.common import Video, Audio
import moviepy.editor as mp
import os
import shutil
from pyffmpeg import FFmpeg

class Video_Audio_joiner:
    """Class for changing the audio of the video for the audio in the other language """

    def __init__(self, video: Video, audio: Audio):
        """
        Initialize a Video_Audio_joiner object with the video and audio file to merge.

        Args:
            video (Video): a valid Video object.
            audio (Audio): a valid Audio object.
        """
        self.video_file = video.get_filename()
        self.audio_file = audio.get_filename()
    
    def join(self, output_file: str) -> str:
        """
        Replace the audio in the video, for the provided one.
        
        Args:
            output_file (str): The file path to save the new video.
        """
        try:
            audio = mp.AudioFileClip(self.audio_file)
            video = mp.VideoFileClip(self.video_file)

            generated_video:mp.VideoFileClip = video.set_audio(audio)
            generated_video.write_videofile(output_file)
            generated_video.close()
        except Exception as e:
            print(f"Error during video generation: {e}")


def watermark_by_text(video: Video, output_file: str, text: str='YML-Multilanguage', fontsize=24, color='black', position=("bottom","right")):
    
    clip = mp.VideoFileClip(video.get_filename()) 
        
    # Generate a text clip 
    txt_clip = mp.TextClip(text, fontsize=fontsize, color=color, method='caption') 
    txt_clip = txt_clip.set_position(position)
        
    # Overlay the text clip on the first video clip 
    waterm_video = mp.CompositeVideoClip([clip, txt_clip]) 

    waterm_video.write_videofile(output_file)
    waterm_video.close()

def watermark_by_image(video: Video, image_file: str):
    video_file = video.get_filename()
    video_clip = mp.VideoFileClip(video_file)

    file_path, file_name = os.path.split(video_file)
    file_name_without_ext, file_ext = os.path.splitext(file_name)
    temp_file = f"{file_name_without_ext}_watermarked{file_ext}"
    temp_file = os.path.join(file_path, temp_file)
    open(temp_file,'w+').close()

    # wm = mp.ImageClip(image_file).set_duration(video_clip.duration).set_pos(("left", "bottom"))
    # video_wm = mp.CompositeVideoClip([video_clip, wm])
    # video_wm.write_videofile(temp_file)

    # print(video.get_filename(), image_file, temp_file)
    ff = FFmpeg()
    ff.options(f"-i {video.get_filename()} -i {image_file} -filter_complex overlay=W-w-30:H-h-30 {temp_file}")
    
    # # new_output_file = os.path.join(file_path, file_name)
    shutil.move(temp_file, video.get_filename())
    # # os.remove(temp_file)
