"""
test_orchestrator.py

Run from backend/ with: python tests/test_orchestrator.py

WARNING: this runs the ENTIRE pipeline for real -- Planner LLM call, then
for each shot: narration synthesis + Manim code generation + actual
render + combine. Even with just 2 shots this could take several
minutes. Not a quick test -- expect to wait.
"""

import sys
import shutil
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner_service import generate_shot_list
import orchestrator

# Monkey-patch a smaller shot range for this first test run -- 2 shots
# instead of 3-6, so we get a full end-to-end result faster before
# committing to a longer run.
_original_generate_shot_list = generate_shot_list
def _small_shot_list(topic, min_shots=2, max_shots=2):
    return _original_generate_shot_list(topic, min_shots=min_shots, max_shots=max_shots)
orchestrator.generate_shot_list = _small_shot_list

topic = "binary search"

print(f"Running full pipeline for topic: '{topic}' (2 shots, this will take a few minutes)...")
final_path = orchestrator.run_pipeline(topic)

# Copy the result somewhere easy to find, since it's currently sitting in
# a temp directory that gets harder to locate later.
output_path = "final_video_test.mp4"
shutil.copy(final_path, output_path)

print(f"Done! Final video copied to: {output_path}")