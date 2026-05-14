"""
Quick standalone demo for offline TTS.

Usage:
    python tts_demo.py              # speak a default greeting
    python tts_demo.py --list       # list available voices
    python tts_demo.py "any text"   # speak custom text
"""

import sys

from voice.text_to_speech import list_voices, speak


def main():
    args = sys.argv[1:]

    if args and args[0] in {"--list", "-l", "list"}:
        voices = list_voices()
        if not voices:
            print("No voices found (or pyttsx3 not installed).")
            return
        print(f"Found {len(voices)} voice(s):")
        for vid, vname in voices:
            print(f"  - {vname}")
            print(f"      id: {vid}")
        return

    if args:
        text = " ".join(args)
    else:
        text = (
            "Welcome to Paoli's Pizza Palace. "
            "I can help you place an order, "
            "answer questions about the menu, "
            "or check on a current order. "
            "What can I get started for you today?"
        )

    print(f"Speaking: {text!r}")
    ok = speak(text)
    print("Done." if ok else "Failed to speak.")


if __name__ == "__main__":
    main()
