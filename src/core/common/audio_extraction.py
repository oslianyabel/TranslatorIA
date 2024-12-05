from src.core.common import Video
from pydub import AudioSegment

class AudioExtractor:
    """Class for extracting audio from a video file"""

    def __init__(self, video: Video):
        """
        Initialize an AudioExtractor object with a video file

        Args:
            video (Video): a valid Video object.
        """
        self.video_file = video.get_filename()

    def extract(self, output_file: str):
        """
        Extract audio from the video file and save it to the specified file.
        
        Args:
            output_file (str): The file path to save the audio.
        """
        try:
            print(self.video_file)
            print(output_file)
            video = AudioSegment.from_file(self.video_file, self.video_file.split(".")[-1])
            video.export(output_file, format="wav")
        except Exception as e:
            print(f"Error during audio extraction: {e}")

    