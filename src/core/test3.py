import os, sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(base_dir)

from src.core.common import preprocess
from src.core import speech_to_text as s2t

vid_aud_list = preprocess.load_videos_from("src/vidub dataset")

transcription_list = []
# audio = Audio('src\core\speech_original.wav')

# transcript = s2t.S2T_Speech_Recognition()
transcript = s2t.S2T_Whisper("medium")
# transcript.get_text(audio,"en-GB")
source_lang = ['en','en','ja','ja','ja','ja','ja','es','es','es','es','es','es']
dest_lang = ['es','es','es','en','en','en','es','en','en','en','en','en','en']
for i, tupl in enumerate(vid_aud_list):
    print(tupl)
    print(tupl[1])
    text = transcript.get_text(source_audio=tupl[1], language=source_lang[i], show_all=False)
    transcription_list.append(text)
    print("\n",tupl[1],"\n\t",text)