from pydub import AudioSegment
from pydub.silence import split_on_silence

# Cargar archivo de audio (por ejemplo, un archivo WAV o MP3)
audio = AudioSegment.from_mp3("alloy.mp3")

# Dividir el audio en segmentos donde hay silencio (silencio definido por más de 1000 ms y -40 dBFS)
audio_chunks = split_on_silence(
    audio, 
    min_silence_len=1000,  # Longitud mínima del silencio en milisegundos
    silence_thresh=-40  # Umbral de silencio en dBFS (más alto es más silencioso)
)

# Guardar los segmentos divididos en archivos separados
for i, chunk in enumerate(audio_chunks):
    chunk.export(f"chunk_{i}.wav", format="wav")  # Guardar cada segmento como archivo WAV
    print(f"Guardado chunk_{i}.wav")

# Imprimir la cantidad de segmentos
print(f"Se generaron {len(audio_chunks)} segmentos de audio.")
