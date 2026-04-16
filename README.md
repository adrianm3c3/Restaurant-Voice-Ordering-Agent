# Speech-to-Text UI Project
## Overview

The speech to text is split into 4 for modular accesibility:

- `speech_ui.py` handles the graphical user interface
- `speech_controller.py` coordinates the workflow between recording and transcription
- `speech_recording.py` records microphone input and saves it as an audio file
- `speech_totext.py` loads the Whisper model and transcribes the saved audio file

this modular structure makes the project easier to read, debug, and extend

## How It Works

When the user presses the **Start Recording** button in the UI:

1. The UI calls the controller
2. The controller calls the recording script
3. The recording script captures audio from the microphone and saves it as `audio.wav`
4. The controller then calls the transcription script
5. The transcription script uses Whisper to convert the recorded speech into text
6. The UI displays the transcription result in the text box

## File Structure

```text
speech_ui.py
speech_controller.py
speech_recording.py
speech_totext.py