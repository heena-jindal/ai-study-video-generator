"""
test_piper_tts.py

Smoke test -- NOT part of the app. Confirms Piper can actually synthesize
audio locally, no API key/account/billing involved anywhere.

Before running this, download a voice once (only needs to happen once,
model gets cached locally after):

python -m piper.download_voices en_US-lessac-medium

Then run this file with: python tests/test_piper_tts.py
"""

from pathlib import Path
import wave
from piper import PiperVoice

# The download command above saves the voice files into a local folder --
# adjust this path if your download went somewhere else. On most systems
# it defaults to a folder named after the voice in your current directory
# or a piper cache folder.
MODEL_PATH = Path("en_US-lessac-medium.onnx")

if not MODEL_PATH.exists():
    print(f"Voice model not found at {MODEL_PATH}.")
    print("Run this first: python -m piper.download_voices en_US-lessac-medium")
else:
    voice = PiperVoice.load(str(MODEL_PATH))

    output_path = "test_output.wav"
    # with open(output_path, "wb") as wav_file:
    #     voice.synthesize_wav(
    #         "This is a test of local narration for the study video agent.",
    #         wav_file,
    #     )

    with wave.open("output.wav", "wb") as wav_file:
        voice.synthesize_wav("This is a test of local narration for the study video agent.", wav_file)

    print(f"Success! Audio written to {output_path} -- play it to confirm it sounds right.")