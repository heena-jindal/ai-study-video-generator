"""
orchestrator.py

The actual multi-agent graph. Different pattern from Study Companion's
agent: there, ONE agent decided WHICH tool to call, dynamically, based
on the user's message. Here, there's no decision to make -- every
request needs Planner, then Narration+Visual+Combine for EVERY shot in
order, then Assembler. This is a "sequential pipeline" multi-agent
pattern -- each node is still a distinct agent with its own job, but the
ROUTING between them is fixed, not chosen by an LLM. Both are legitimate
multi-agent architectures; they just solve different kinds of problems.
"""

import os
import time
from typing import TypedDict, List, Literal
from langgraph.graph import StateGraph, START, END

from planner_service import generate_shot_list
from narration_service import generate_shot_audio
from visual_service import generate_shot_video
from assembler_service import combine_shot_audio_video, concatenate_shots


class PipelineState(TypedDict):
    topic: str
    theme: Literal["light", "dark"]
    instructions: str  # optional, "" means "use your own judgment"
    example_data: str
    work_dir: str
    shots: List[dict]
    current_shot_index: int
    shot_clip_paths: List[str]
    final_video_path: str


def planner_node(state: PipelineState) -> dict:
    shot_list = generate_shot_list(state["topic"], instructions=state.get("instructions", ""))
    return {
        "shots": shot_list["shots"],
        "example_data": shot_list["example_data"],
        "current_shot_index": 0,
        "shot_clip_paths": [],
    }


def narration_node(state: PipelineState) -> dict:
    """
    Runs FIRST for the current shot -- this is the ordering fix from our
    duration-gap finding. Real audio duration gets produced here, before
    the Visual Agent ever runs, so Visual paces against the REAL number,
    not the Planner's rough estimate.
    """
    i = state["current_shot_index"]
    shot = state["shots"][i]
    audio_path = os.path.join(state["work_dir"], f"shot_{i}_audio.wav")

    result = generate_shot_audio(shot["narration"], audio_path)

    # Stash the real duration + audio path onto the shot dict so the next
    # node (visual_node) can read it back out of state.
    shots = state["shots"]
    shots[i]["audio_path"] = result["audio_path"]
    shots[i]["actual_duration_seconds"] = result["actual_duration_seconds"]
    return {"shots": shots}


def visual_node(state: PipelineState) -> dict:
    """
    Runs SECOND -- paces the Manim animation against narration_node's
    REAL measured duration, not the Planner's estimate. Also passes the
    job's chosen theme, the Planner's committed example_data, AND the
    user's optional instructions, so every shot's visuals stay grounded
    AND respect any explicit constraints the user gave (e.g. "avoid
    highlight boxes").
    """
    i = state["current_shot_index"]
    shot = state["shots"][i]
    video_path = os.path.join(state["work_dir"], f"shot_{i}_video.mp4")

    generate_shot_video(
        shot["visual_description"],
        duration_seconds=shot["actual_duration_seconds"],  # real duration, not Planner's guess
        output_path=video_path,
        theme=state.get("theme", "light"),
        example_data=state.get("example_data", ""),
        topic=state["topic"],
        instructions=state.get("instructions", ""),
    )

    shots = state["shots"]
    shots[i]["video_path"] = video_path
    return {"shots": shots}


def combine_node(state: PipelineState) -> dict:
    """
    Runs THIRD -- merges this shot's video + audio into one clip, then
    advances to the next shot.
    """
    i = state["current_shot_index"]
    shot = state["shots"][i]
    combined_path = os.path.join(state["work_dir"], f"shot_{i}_combined.mp4")

    combine_shot_audio_video(shot["video_path"], shot["audio_path"], combined_path)

    clip_paths = state["shot_clip_paths"] + [combined_path]
    return {"shot_clip_paths": clip_paths, "current_shot_index": i + 1}


def has_more_shots(state: PipelineState) -> str:
    """
    The loop condition -- if shots remain, go back to narration_node for
    the next one; otherwise move on to the final assembler step.
    """
    if state["current_shot_index"] < len(state["shots"]):
        return "narration"
    return "assemble"


def assembler_node(state: PipelineState) -> dict:
    final_path = os.path.join(state["work_dir"], "final_video.mp4")
    concatenate_shots(state["shot_clip_paths"], final_path)
    return {"final_video_path": final_path}


graph_builder = StateGraph(PipelineState)
graph_builder.add_node("planner", planner_node)
graph_builder.add_node("narration", narration_node)
graph_builder.add_node("visual", visual_node)
graph_builder.add_node("combine", combine_node)
graph_builder.add_node("assemble", assembler_node)

graph_builder.add_edge(START, "planner")
graph_builder.add_edge("planner", "narration")
graph_builder.add_edge("narration", "visual")
graph_builder.add_edge("visual", "combine")
graph_builder.add_conditional_edges(
    "combine", has_more_shots, {"narration": "narration", "assemble": "assemble"}
)
graph_builder.add_edge("assemble", END)

pipeline = graph_builder.compile()


def run_pipeline(topic: str, theme: str = "light", instructions: str = "") -> str:
    """
    Entry point. Runs the full multi-agent pipeline end to end, returns
    the path to the final assembled video.

    theme: "light" or "dark" -- controls the rendered Manim scenes'
    background/text colors for every shot in this run.
    instructions: OPTIONAL free-text user constraints (e.g. "keep it
    beginner-friendly", "avoid highlight boxes"). Empty string means the
    Planner and Visual Agent use their own judgment, same as before this
    feature existed -- this is purely additive.

    NOTE: uses a persistent LOCAL folder (pipeline_output/<timestamp>/),
    not the OS temp directory. Windows was silently clearing tempfile.
    mkdtemp()'s folder between our debugging steps -- fine for a real
    production run where nothing needs inspecting afterward, but bad for
    development, where we want intermediate per-shot files to actually
    stick around to debug.
    """
    work_dir = os.path.join("pipeline_output", f"run_{int(time.time())}")
    os.makedirs(work_dir, exist_ok=True)

    result = pipeline.invoke({
        "topic": topic,
        "theme": theme,
        "instructions": instructions,
        "example_data": "",
        "work_dir": work_dir,
        "shots": [],
        "current_shot_index": 0,
        "shot_clip_paths": [],
        "final_video_path": "",
    })
    return result["final_video_path"]