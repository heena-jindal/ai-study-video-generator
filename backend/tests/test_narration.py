"""
test_narration.py

Run from backend/ with: python tests/test_narration.py

Uses one of the actual shots from your earlier Planner test, so you can
directly compare the ~150wpm ESTIMATE against Piper's REAL measured
duration -- this is the gap the Assembler will eventually need to
reconcile against the Visual Agent's animation length.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from narration_service import generate_shot_audio

# Shot 3 from your earlier Planner test run
narration_text = (
    "Let's find 27 in the list 3, 11, 19, 27, 34, 42, 58. First we "
    "compare 27 to the middle element 27, they match, so we stop. If it "
    "were 34, we'd discard the left half and continue."
)
planner_estimated_duration = 15.6  # from the actual test_planner.py output

output_path = "test_narration_output.wav"

result = generate_shot_audio(narration_text, output_path)

print(f"Audio saved to: {result['audio_path']}")
print(f"Planner's ESTIMATED duration: {planner_estimated_duration}s")
print(f"Piper's ACTUAL measured duration: {result['actual_duration_seconds']}s")
print(f"Difference: {round(abs(planner_estimated_duration - result['actual_duration_seconds']), 2)}s")