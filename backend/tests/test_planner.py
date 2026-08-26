"""
test_planner.py

Run from backend/ with: python tests/test_planner.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planner_service import generate_shot_list

topic = "binary search"

shot_list = generate_shot_list(topic)

print(f"Topic: {shot_list['topic']}")
print(f"Total shots: {len(shot_list['shots'])}")
print(f"Total estimated duration: {shot_list['total_estimated_duration_seconds']}s\n")

for i, shot in enumerate(shot_list["shots"], 1):
    print(f"--- Shot {i}: {shot['purpose']} ({shot['estimated_duration_seconds']}s) ---")
    print(f"Narration: {shot['narration']}")
    print(f"Visual: {shot['visual_description']}")
    print()