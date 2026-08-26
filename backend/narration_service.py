"""
narration_service.py

The Narration Agent -- Part 3. Takes one shot's narration text, generates
real audio with Piper (fully local, no API key/account), and returns the
ACTUAL audio duration -- not the Planner's word-count estimate from Part 1.

This distinction matters: the Planner's ~150wpm estimate is a rough guess
made before any real audio exists. Once Piper actually speaks the text,
we know the REAL duration -- which is what the Assembler will need later
to properly sync each shot's video length to its narration.
"""

import os
import wave
from pathlib import Path
from piper import PiperVoice

# Same file location that already worked in your local smoke test --
# keeping this consistent avoids another path-confusion issue like the
# tests/ folder mix-up we just had.
MODEL_PATH = Path(__file__).resolve().parent / "en_US-lessac-medium.onnx"

# Lazy-loaded singleton -- same pattern as Study Companion's embedding
# model fix. Piper is much lighter than PyTorch (ONNX-based), so this
# matters less for memory here, but it's still good practice: nothing
# heavy loads until actually needed, not at import time.
_voice = None


def _get_voice() -> PiperVoice:
    global _voice
    if _voice is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Voice model not found at {MODEL_PATH}. Run: "
                f"python -m piper.download_voices en_US-lessac-medium"
            )
        _voice = PiperVoice.load(str(MODEL_PATH))
    return _voice


def _get_wav_duration_seconds(wav_path: str) -> float:
    """
    Reads the ACTUAL duration back out of the generated wav file --
    frame count divided by frame rate. This is real, measured duration,
    not an estimate.
    """
    with wave.open(wav_path, "rb") as wav_file:
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()
        return round(frames / float(rate), 2)


def generate_shot_audio(narration_text: str, output_path: str) -> dict:
    """
    Synthesizes narration_text to output_path (a .wav file), returns
    both the path and the REAL measured duration.
    """
    voice = _get_voice()

    with wave.open(output_path, "wb") as wav_file:
        voice.synthesize_wav(narration_text, wav_file)

    actual_duration = _get_wav_duration_seconds(output_path)

    return {
        "audio_path": output_path,
        "actual_duration_seconds": actual_duration,
    }


