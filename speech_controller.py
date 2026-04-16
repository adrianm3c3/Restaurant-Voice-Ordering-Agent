from speech_recording import record_audio
from speech_totext import transcribe_file

def run_speech_to_text(duration=5, sample_rate=16000, filename="audio.wav"):
    audio_file = record_audio(
        filename=filename,
        duration=duration,
        sample_rate=sample_rate
    )
    text = transcribe_file(audio_file)
    return text

if __name__ == "__main__":
    print("Recording and transcribing...")
    text = run_speech_to_text()
    print("Transcript:")
    print(text)