"""
test_concatenate_only.py

Quick isolated test of JUST the concatenation fix -- reuses the existing
shot_0_combined.mp4 / shot_1_combined.mp4 from your last pipeline run
instead of rerunning the whole slow pipeline again.

Run from backend/ with: python tests/test_concatenate_only.py "<path_to_temp_dir>"

Example:
python tests/test_concatenate_only.py "C:\\Users\\user\\AppData\\Local\\Temp\\video_pipeline_rm8_4jk8"
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from assembler_service import concatenate_shots

temp_dir = sys.argv[1]

clip_paths = [
    os.path.join(temp_dir, "shot_0_combined.mp4"),
    os.path.join(temp_dir, "shot_1_combined.mp4"),
]

for p in clip_paths:
    if not os.path.exists(p):
        print(f"Missing: {p}")
        sys.exit(1)

output_path = "test_concat_output.mp4"
concatenate_shots(clip_paths, output_path)
print(f"Done! Concatenated video saved to: {output_path}")