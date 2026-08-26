"""
assembler_service.py

Pure combining/stitching logic -- no LLM calls here, this is the one
fully deterministic agent in the pipeline.

REWRITE NOTE: originally used MoviePy for everything here. Testing found
TWO separate real MoviePy reliability issues in the same session:
1. concatenate_videoclips/concatenate_audioclips silently losing audio
   for later clips during final concatenation (confirmed: individual
   per-shot clips had correct audio, but the MoviePy-concatenated output
   didn't).
2. MoviePy's to_ImageClip()/get_frame() crashing when reading a frame
   near the very end of a video (a known fragile pattern -- duration
   metadata and actual decodable frame count don't always line up
   exactly).
Two separate real bugs in one MoviePy-based file is a strong enough
pattern to stop patching individually and switch to calling ffmpeg
directly for both operations -- more predictable for exactly this kind
of work.
"""

import os
import subprocess


def _get_duration(path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def combine_shot_audio_video(video_path: str, audio_path: str, output_path: str) -> str:
    """
    Attaches audio to video. If durations don't match exactly (expected
    -- Manim's pacing is approximate, not frame-perfect), reconciles by:
    - video shorter than audio -> freeze the last frame to fill the gap
      (ffmpeg's tpad filter -- clones the final frame, no need to read
      back into the file the fragile way MoviePy did)
    - video longer than audio -> trim video down to audio's length
    Final duration always matches the audio, since narration is what
    actually has to be heard in full.
    """
    video_duration = _get_duration(video_path)
    audio_duration = _get_duration(audio_path)

    if video_duration < audio_duration:
        gap = round(audio_duration - video_duration, 2)
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-vf", f"tpad=stop_mode=clone:stop_duration={gap}",
            "-c:v", "libx264", "-c:a", "aac",
            "-t", str(audio_duration),
            output_path,
        ]
    else:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path, "-i", audio_path,
            "-c:v", "libx264", "-c:a", "aac",
            "-t", str(audio_duration),
            output_path,
        ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg combine failed: {result.stderr[-2000:]}")

    return output_path


def concatenate_shots(clip_paths: list, output_path: str) -> str:
    """
    Stitches every shot's combined (video+audio) clip into one final
    video, in order, using ffmpeg's concat feature directly (see
    module-level note for why this replaced MoviePy here).
    """
    list_path = os.path.join(os.path.dirname(output_path), "concat_list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for path in clip_paths:
            safe_path = os.path.abspath(path).replace("\\", "/")
            f.write(f"file '{safe_path}'\n")

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", list_path,
            "-c:v", "libx264", "-c:a", "aac",
            "-r", "24",
            output_path,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg concatenation failed: {result.stderr[-2000:]}")

    return output_path