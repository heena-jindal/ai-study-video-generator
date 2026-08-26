"""
visual_service.py

The Visual Agent -- Part 2. Takes one shot's visual_description +
estimated_duration_seconds, generates Manim code, RENDERS it,
and returns the path to the resulting video clip.
"""

import glob
import json
import os
import shutil
import subprocess
import tempfile

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, ConfigDict

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-120b"

SCENE_CLASS_NAME = "GeneratedScene"
MAX_RENDER_ATTEMPTS = 3
RENDER_TIMEOUT_SECONDS = 180

# Groq org TPM ceiling on this account's tier is 8000 tokens PER REQUEST
# (prompt + completion combined) -- confirmed via a 413 rate_limit_exceeded
# error. HARD_TOKEN_CEILING must never be crossed by (prompt + max_tokens).
# Leave a safety margin below the real 8000 limit since our char->token
# estimate is approximate, not exact.
HARD_TOKEN_CEILING = 7600

# Desired completion budgets, used only when the prompt is small enough
# to afford them. Actual budget is clamped by _token_budget_for_prompt().
BASE_MAX_TOKENS = 2500
DENSE_MAX_TOKENS = 4000

# Floor so a request is never sent with an unusably tiny completion budget
# -- if the prompt itself is so large we can't afford this much, fail
# fast with a clear error instead of sending a doomed request.
MIN_VIABLE_MAX_TOKENS = 800


def _estimate_tokens(text: str) -> int:
    """
    Cheap, dependency-free token estimate (~4 chars/token for English/code).
    Deliberately rounds UP so we stay on the safe side of the real limit.
    """
    return (len(text) // 4) + 1


def _token_budget_for_prompt(system_content: str, user_content: str, desired: int) -> int:
    """
    Given the actual assembled prompt, work out how much completion budget
    we can request without crossing HARD_TOKEN_CEILING. Returns the LOWER
    of `desired` and whatever headroom is left after the prompt.
    """
    prompt_tokens = _estimate_tokens(system_content) + _estimate_tokens(user_content)
    headroom = HARD_TOKEN_CEILING - prompt_tokens
    budget = min(desired, headroom)

    if budget < MIN_VIABLE_MAX_TOKENS:
        raise RuntimeError(
            f"Prompt too large to fit token budget: ~{prompt_tokens} prompt tokens "
            f"leaves only {headroom} for completion (need >= {MIN_VIABLE_MAX_TOKENS}). "
            f"Shorten visual_description/instructions/previous_error and retry."
        )
    return budget

THEME_COLORS = {
    "light": {"background": "WHITE", "text": "BLACK", "accent": "BLUE_D"},
    "dark": {"background": "#211C17", "text": "#F1E9DC", "accent": "#C9A961"},
}


class ManimCodeResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: str


def _estimate_complexity(visual_description: str, example_data: str) -> str:
    """
    Rough heuristic to decide whether this shot needs the higher token
    budget. Looks at how many discrete items the shot has to lay out
    (array elements, dict entries, result groups) and whether it's a
    summary/closing-style shot, which per ADDITION #4 always has more
    simultaneous zones on screen than a normal shot.
    """
    text = f"{visual_description} {example_data}".lower()

    summary_signals = ("result", "summary", "closing", "final", "recap")
    if any(word in text for word in summary_signals):
        return "dense"

    # Count comma-separated items as a proxy for element count (array
    # elements, dict pairs, etc.) -- six or more items is exactly the
    # shot type that broke last time.
    comma_count = example_data.count(",")
    if comma_count >= 5:
        return "dense"

    return "simple"


def _build_prompt(
    visual_description: str,
    duration_seconds: float,
    theme: str = "light",
    example_data: str = "",
    topic: str = "",
    instructions: str = "",
    previous_error: str = None,
) -> str:
    colors = THEME_COLORS.get(theme, THEME_COLORS["light"])

    base = f"Write a fast-rendering Manim CE scene for: {visual_description}\n"
    if topic:
        base += f"Topic: {topic}\n"
    if example_data:
        base += f"Example Data: {example_data}\n"

    # Consolidated ruleset. Instead of one narrow rule per shot shape
    # (array row, dict panel, result boxes, node graph, ...), this centers
    # on ONE general principle -- measure real bounding boxes and never let
    # two overlap -- plus the handful of Manim-specific mechanics needed to
    # act on it. Fewer, more general rules generalize to shot types we
    # haven't seen yet (node graphs, cycling readouts, etc), instead of
    # needing a new rule every time a new layout shape appears.
    base += (
        f"\nSETUP:\n"
        f"- `class {SCENE_CLASS_NAME}(Scene):` only.\n"
        f"- bg={colors['background']!r} text={colors['text']!r} accent={colors['accent']!r}. Plain `Text`, no MathTex.\n"
        f"- Position via `.move_to()` / `.to_edge()` only. No invented helpers.\n"
        f"- Frame is ~13 units wide, ~7.5 tall, origin at center. Keep 0.5 unit margin on all four edges.\n"
        f"\nTHE ONE RULE THAT MATTERS MOST: NOTHING MAY OVERLAP.\n"
        f"At every point in the video, for every pair of visible Mobjects, their bounding boxes must not "
        f"intersect (allow >=0.3 unit gap between separate elements). This applies to ALL content equally: "
        f"array rows, dict/state panels, captions, per-item labels, diagrams, node graphs, arrows, footers -- "
        f"there is no exception for any element type or shot style. Before placing or moving any Mobject, "
        f"work out its actual bounding box (via `.get_top()`, `.get_bottom()`, `.get_left()`, `.get_right()`, "
        f"or `.get_corner()`) and the bounding boxes of everything already on screen, and choose a position "
        f"with no intersection. NEVER assume a position is safe just because it worked for a shorter/simpler "
        f"version of this shot -- text and diagrams vary in size, so measure fresh every time, including on "
        f"every update (a growing dict, a cycling readout, an added node) -- re-measure, don't reuse an old "
        f"coordinate.\n"
        f"Practical consequences of this one rule:\n"
        f"- Layout zones as a starting scaffold (adjust for content, but keep gaps between them): "
        f"TITLE 3.0-3.5 | PRIMARY CONTENT 0.5-1.5 | LABELS -0.5-0.0 | STATE/RESULT -1.5..-2.5 | FOOTER -3.5. "
        f"Arrays/rows lay out LEFT-TO-RIGHT along X, never stacked vertically within one zone.\n"
        f"- Diagrams with nodes/edges (graphs, trees, flowcharts) need their OWN clear rectangular region "
        f"with no text or other element inside its bounds, including captions -- treat the whole diagram's "
        f"bounding box (via a VGroup wrapping all its parts) as one object nothing else may intersect.\n"
        f"- A repeatedly-updated element (state panel, dict, cycling 'Input/Output' readout, running total) "
        f"is exactly ONE persistent Mobject: update via `Transform(old, new)` or explicit `self.remove(old)` "
        f"before adding the replacement. Old and new content must never both be visible at once.\n"
        f"- An overlay decorating another Mobject (`SurroundingRectangle`, arrow, underline) is bound to that "
        f"target for its lifetime: move together, `FadeOut` together. Never leave one on screen alone.\n"
        f"- Per-item labels in a multi-item row (e.g. one label per result box) each stay within their own "
        f"item's X-range and sit fully above/below that item, never inside it or reaching into a neighbor's "
        f"space. A separate overall caption (e.g. 'Result:') is its own element positioned clear of BOTH the "
        f"items and their per-item labels -- not sharing a Y-range with either.\n"
        f"- Long text (long captions, sentences, dict contents) gets a smaller `font_size` or is split into "
        f"2-3 lines BEFORE positioning, whenever its estimated rendered width would approach the frame's "
        f"safe width -- don't wait to find out it overflows.\n"
        f"- If two `.animate.move_to()` calls in the same `self.play()` would cross paths, split them into "
        f"separate `self.play()` calls instead.\n"
        f"- Process sequential items (array indices, list steps) strictly in order; fully clear item i's "
        f"labels/overlays before item i+1's appear.\n"
        f"- When space is tight, simplify: fewer, correctly-placed elements beat many crowded ones. Drop "
        f"secondary decoration (extra labels, footnotes) before risking any overlap.\n"
        f"\nPACING: run_time 0.3-0.5s/step, `self.wait()` <=0.3s/step, target ~{duration_seconds}s total.\n"
    )

    if instructions:
        base += f"\nInstructions: {instructions}"
    if previous_error:
        base += f"\nPrevious Render Error (Fix this):\n{previous_error}"

    return base


def _generate_code(
    visual_description: str,
    duration_seconds: float,
    theme: str = "light",
    example_data: str = "",
    topic: str = "",
    instructions: str = "",
    previous_error: str = None,
) -> str:
    # Keep previous_error short -- on a retry this gets appended to the
    # prompt, and an untruncated stderr dump can quietly eat hundreds of
    # tokens that were meant for the completion budget.
    if previous_error and len(previous_error) > 500:
        previous_error = previous_error[:500] + " ...[truncated]"

    complexity = _estimate_complexity(visual_description, example_data)
    desired_budget = DENSE_MAX_TOKENS if complexity == "dense" else BASE_MAX_TOKENS

    system_content = (
        "You write concise, high-performance Manim Community Edition code "
        "using standard built-in functions only. Never invent non-existent helpers."
    )
    user_content = _build_prompt(
        visual_description,
        duration_seconds,
        theme,
        example_data,
        topic,
        instructions,
        previous_error,
    )

    token_budget = _token_budget_for_prompt(system_content, user_content, desired_budget)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.2,
        max_tokens=token_budget,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "manim_code_response",
                "strict": True,
                "schema": ManimCodeResponse.model_json_schema(),
            },
        },
    )

    choice = response.choices[0]

    # This is the critical check that was missing before: if the model
    # ran out of tokens mid-generation, the JSON is likely malformed or
    # the code is truncated mid-statement. Treat this as a retryable
    # error with a clear message, instead of silently accepting broken
    # layout code (which is what produced the stacked/overlapping shots).
    if choice.finish_reason == "length":
        raise RuntimeError(
            f"Response truncated (finish_reason=length) at token budget "
            f"{token_budget} for a '{complexity}' shot. The generated code is "
            f"likely incomplete. Retrying will raise the budget or simplify."
        )

    try:
        code = json.loads(choice.message.content)["code"]
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise RuntimeError(f"Malformed response (finish_reason={choice.finish_reason}): {e}")

    if f"class {SCENE_CLASS_NAME}" not in code:
        raise ValueError(f"Generated code doesn't define class {SCENE_CLASS_NAME}")

    return code


def _render_scene(code: str, work_dir: str) -> str:
    script_path = os.path.join(work_dir, "scene.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    media_dir = os.path.join(work_dir, "media")

    result = subprocess.run(
        [
            "manim",
            "-ql",
            "--fps",
            "24",
            "--media_dir",
            media_dir,
            script_path,
            SCENE_CLASS_NAME,
        ],
        capture_output=True,
        text=True,
        timeout=RENDER_TIMEOUT_SECONDS,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr[-2000:])

    matches = glob.glob(
        os.path.join(media_dir, "**", f"{SCENE_CLASS_NAME}.mp4"), recursive=True
    )
    if not matches:
        raise RuntimeError("Render reported success but no output file was found")

    return matches[0]


def generate_shot_video(
    visual_description: str,
    duration_seconds: float,
    output_path: str,
    theme: str = "light",
    example_data: str = "",
    topic: str = "",
    instructions: str = "",
) -> str:
    if theme not in THEME_COLORS:
        theme = "light"

    previous_error = None

    for attempt in range(1, MAX_RENDER_ATTEMPTS + 1):
        work_dir = tempfile.mkdtemp(prefix="manim_shot_")
        try:
            code = _generate_code(
                visual_description,
                duration_seconds,
                theme,
                example_data,
                topic,
                instructions,
                previous_error,
            )
            rendered_path = _render_scene(code, work_dir)
            shutil.copy(rendered_path, output_path)
            return output_path
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
            previous_error = str(e)
            if attempt == MAX_RENDER_ATTEMPTS:
                raise RuntimeError(
                    f"Failed to render after {MAX_RENDER_ATTEMPTS} attempts. Last error: {previous_error}"
                )
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)