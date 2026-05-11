"""
Offline text-to-speech for the restaurant voice ordering agent.

macOS engine: the system `say` command (always available, very reliable).
Fallback engine: pyttsx3 (offline, cross-platform, already in requirements.txt).

This module exposes a single public function `speak(text)` that the agent
calls to read its response out loud. It is designed to fail soft: if the
engine is missing or errors out, it logs and returns False instead of
crashing the agent.

Reliability note: pyttsx3 on macOS can occasionally return without audible
speech after many calls in a single process, so we prefer the native `say`
command on macOS and keep pyttsx3 as the fallback.
"""

import logging
import platform
import shutil
import subprocess
import threading

logger = logging.getLogger(__name__)

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    logger.warning(
        "pyttsx3 is not installed. "
        "Install it with `pip install pyttsx3` to enable offline TTS."
    )

try:
    from src.config import CONFIG
except Exception:
    CONFIG = {
        "voice": {
            "tts_enabled": True,
            "tts_rate": 175,
            "tts_volume": 1.0,
            "tts_voice_id": None,
        }
    }


_engine = None
_engine_lock = threading.Lock()


def _build_engine():
    if pyttsx3 is None:
        raise RuntimeError(
            "pyttsx3 is not available. "
            "Run `pip install pyttsx3` to enable offline TTS."
        )

    engine = pyttsx3.init()
    _configure_engine(engine)
    return engine


def _configure_engine(engine):
    voice_cfg = CONFIG.get("voice", {})

    rate = voice_cfg.get("tts_rate", 175)
    volume = voice_cfg.get("tts_volume", 1.0)
    voice_id = voice_cfg.get("tts_voice_id")

    try:
        engine.setProperty("rate", rate)
        engine.setProperty("volume", volume)

        if voice_id:
            engine.setProperty("voice", voice_id)

    except Exception as e:
        logger.warning("Failed to configure TTS engine properties: %s", e)


def _get_engine():
    global _engine

    if _engine is None:
        _engine = _build_engine()

    return _engine


def _speak_with_say_command(text):
    """
    Fallback for macOS: shell out to the native `say` command.
    Returns True on success, False on failure.
    """
    if platform.system() != "Darwin":
        return False

    say_path = shutil.which("say")
    if not say_path:
        return False

    try:
        subprocess.run(
            [say_path, text],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception as e:
        logger.warning("`say` command failed: %s", e)
        return False


def speak(text):
    """
    Speak `text` out loud using the offline TTS engine.

    Returns True on success, False on any failure (so the calling agent
    can fall back to printing without crashing). On macOS, if pyttsx3
    fails or stays silent, automatically falls back to the system `say`
    command.
    """
    if not text or not text.strip():
        return False

    voice_cfg = CONFIG.get("voice", {})

    if not voice_cfg.get("tts_enabled", True):
        logger.info("TTS disabled in config; skipping speech output.")
        return False

    if _speak_with_say_command(text):
        return True

    if pyttsx3 is None:
        return _speak_with_say_command(text)

    try:
        with _engine_lock:
            engine = _get_engine()
            engine.say(text)
            engine.runAndWait()
        return True

    except RuntimeError as e:
        logger.warning("TTS engine runtime error, rebuilding once: %s", e)
        global _engine
        with _engine_lock:
            _engine = None
            try:
                engine = _get_engine()
                engine.say(text)
                engine.runAndWait()
                return True
            except Exception as inner:
                logger.warning("TTS retry failed, falling back to `say`: %s", inner)
                return _speak_with_say_command(text)

    except Exception as e:
        logger.warning("TTS failed, falling back to `say`: %s", e)
        return _speak_with_say_command(text)


def list_voices():
    """
    Return a list of (voice_id, voice_name) tuples for the available
    system voices. Useful when picking a `tts_voice_id` for CONFIG.
    """
    if pyttsx3 is None:
        return []

    try:
        with _engine_lock:
            engine = _get_engine()
            voices = engine.getProperty("voices") or []

        return [
            (getattr(v, "id", ""), getattr(v, "name", ""))
            for v in voices
        ]

    except Exception as e:
        logger.exception("Failed to list voices: %s", e)
        return []


if __name__ == "__main__":
    print("Available voices on this system:")
    for vid, vname in list_voices():
        print(f"  - {vname}\n      id: {vid}")

    print("\nSpeaking a sample greeting...")
    ok = speak(
        "Welcome to Paoli's Pizza Palace. "
        "What can I get started for you today?"
    )
    print("OK" if ok else "Failed")
