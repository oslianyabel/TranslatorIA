import os
from src.core.common import AudioExtractor, Audio, Video

def file_to_Video(video_file: str, language: str = "Unknown"):
    """
    Given the path of the video file and the language of it, returns an instance of Video.

    Args:
        video_file (str): The file path of the video.
        language (str): The language of the video.

    Returns:
        Video: instance of Video.
    """
    name = os.path.splitext(os.path.basename(video_file))[0]+'.mp4'
    # print(video_file)
    return Video(video_file,name,language)

def video_file_to_Video_Audio(video_file: str, path_to_save_audio: str, language: str = "Unknown"):
    """
    Given the path of the video file, the path to save the audio and the language of it, returns a tuple of (Video, Audio).

    Args:
        video_file (str): The file path of the video.
        path_to_save_audio (str): path to save the video audio. It must include the audio name and extension (.wav).
        split (bool): whether to split the audio by silences.
        language (str): The language of the video.

    Returns:
        tuple[Video, Audio]: instances of Video and Audio.
    """
    video = file_to_Video(video_file)
    extr = AudioExtractor(video)
    extr.extract(path_to_save_audio)
    audio = Audio(path_to_save_audio, language)

    return video, audio

def load_videos_from(videos_directory: str):
    """ 
    Given a directory(folder), recursively search all .mp4 files and from each extract Video and Audio.
    
    Returns:
        List[tuple[Video, Audio]]: all the videos in the directory tree.
    """
    ext = ['.mp4']
    audio_path = os.path.join("src","app","static","audio")
    vid_aud_list = []
    for p in os.listdir(videos_directory):
        full_p = os.path.join(videos_directory, p)
        if os.path.isfile(full_p):
            # if p is a file, check if it is a .mp4 and process it
            for e in ext:
                if e in full_p:
                    save_audio = os.path.join(audio_path,p[:-4]+'.wav')
                    tupl = video_file_to_Video_Audio(video_file=full_p, path_to_save_audio=save_audio)
                    vid_aud_list.append(tupl)
                    break
        
        else:
            # if p is a folder, recursively call this method
            sub_list = load_videos_from(full_p)
            for t in sub_list:
                vid_aud_list.append(t)

    return vid_aud_list
