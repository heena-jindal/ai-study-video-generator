"""
test_visual.py

Run from backend/ with: python tests/test_visual.py
This will take a while -- an LLM call plus an actual Manim render.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from visual_service import generate_shot_video

visual_description = (
    "Bullet points appear one by one summarizing three rules about binary "
    "search: it works on sorted data, it repeatedly halves the search "
    "space, and it gives logarithmic speed. A checkmark animation appears "
    "next to each bullet as it's added."
)

output_path = "test_shot_output_recap.mp4"

print("Generating and rendering... this may take a minute or two.")
result = generate_shot_video(visual_description, duration_seconds=12.0, output_path=output_path)
print(f"Success! Video saved to: {result}")