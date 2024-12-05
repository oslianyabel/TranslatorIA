import os, sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(base_dir)

import text_to_speech

modelo = text_to_speech.TTS_MMS()
text = "Hola mundo desde Cuba"
audio = modelo.generate_speech(text, "es", "/audios/")
print(audio)