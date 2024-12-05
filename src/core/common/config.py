from pathlib import Path
import os

class Config():

    BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent  # Path(os.getcwd())
    
    # user inputs
    INPUT_LANGUAGE = "en-US"
    TARGET_LANGUAGE = "hi-IN"

    # common settings
    # DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    # FACE_DETECTION_ASYNC_ENABLED = True

    ORIGINAL_SAMPLING_RATE = 44100
    AUDIO_DEFAULT_FORMAT = "wav"
    VIDEO_DEFAULT_FORMAT = "mp4"
    
    # declare a private constructor to prevent instantiation of this class
    def __init__(self):
        raise NotImplementedError("Config is a static class and cannot be instantiated.")