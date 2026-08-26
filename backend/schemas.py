"""
schemas.py

Shared Pydantic schemas across agents -- kept in one file since multiple
agents will read/write this same shape (Planner produces it, Visual and
Narration agents each read one shot from it, Assembler reads the whole
thing). Same "decide the schema before writing the prompt" lesson from
Study Companion Part 2, just applied to a contract BETWEEN agents now,
not just between a prompt and parsing code.
"""

from typing import List
from pydantic import BaseModel, ConfigDict, Field


class Shot(BaseModel):
    model_config = ConfigDict(extra="forbid")  # required for Groq strict mode

    purpose: str  # e.g. "hook", "definition", "example", "recap" -- makes
    # the pedagogical sequence an explicit field, not just an implicit
    # hope buried in the prompt (this is Q1's lesson, made concrete)
    narration: str  # the actual text to be spoken for this shot
    visual_description: str  # plain-English description the Visual Agent
    # will turn into Manim code later -- NOT Manim code itself, the
    # Planner shouldn't need to know Manim syntax


class ShotList(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str

    # NEW: one concrete, specific example (e.g. an actual array of
    # numbers) that the Planner commits to ONCE and every shot must
    # reuse. Root-cause fix for two bugs found in testing: (1) a shot
    # drifting into a totally different algorithm's content because
    # nothing tied it back to a concrete running example, and (2) the
    # Visual Agent inventing an abstract icon/metaphor (a generic
    # "timer" and "loop box") instead of showing real data, because it
    # had nothing concrete to render.
    example_data: str

    shots: List[Shot] = Field(min_length=1, max_length=10)