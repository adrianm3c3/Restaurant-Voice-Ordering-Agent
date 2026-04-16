import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

def record_audio(filename="audio.wav", duration=5, sample_rate=16000):
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype=np.int16
    )
    sd.wait()
    write(filename, sample_rate, audio)
    return filename