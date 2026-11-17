"""Turn a problem into a ready-to-produce viral short with AI characters.

Uses Claude to write: hook, character dialogue, the solution, scene-by-scene
visual prompts (for any AI video/image tool), voiceover lines, title,
description and hashtags.
"""

from __future__ import annotations

from typing import List, Literal

import anthropic
from pydantic import BaseModel

MODEL = "claude-opus-5-5"

SYSTEM = """You write faceless YouTube Shorts / TikTok / Reels scripts for a channel
that solves real people's everyday problems using two recurring AI characters.

Rules for going viral:
- The first line (hook) must stop the scroll in under 2 seconds: name the pain
  directly or state a surprising fact. Never start with "Hey guys" or a greeting.
- 30-50 seconds total, about 90-130 spoken words.
- The "Problem" character voices the frustration the viewer feels.
- The "Fixer" character gives a clear, practical, TRUE solution in 2-4 steps.
  Only give advice that is safe and widely accepted. For health, money or legal
  topics, keep it general and suggest a professional when it really matters.
- Add one small twist or "most people don't know this" moment for retention.
- End with a loop line or a question that makes people comment.
- Visual prompts must describe the SAME two characters consistently every scene
  so the AI video tool keeps them on-model.
"""


class Character(BaseModel):
    name: str
    role: Literal["problem", "fixer"]
    look: str  # detailed, reusable visual description for consistency
    voice: str  # voice style for TTS


class Scene(BaseModel):
    speaker: str
    line: str
    visual_prompt: str
    seconds: float


class VideoPlan(BaseModel):
    problem: str
    hook: str
    characters: List[Character]
    scenes: List[Scene]
    solution_steps: List[str]
    title: str
    description: str
    hashtags: List[str]
    thumbnail_prompt: str
    comment_bait_question: str


def write_video(problem: str, style: str = "cute 3D Pixar-like animation", client: anthropic.Anthropic | None = None) -> VideoPlan:
    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",  # if a request is declined, retry on a fallback model
        output_config={"effort": "medium"},
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Visual style: {style}\n\nProblem people are asking about:\n{problem}",
            }
        ],
        output_format=VideoPlan,
    )
    if response.stop_reason == "refusal":
        raise RuntimeError(f"Claude declined this topic: {problem!r}")
    return response.parsed_output


def to_markdown(plan: VideoPlan) -> str:
    out = [f"# {plan.title}", "", f"**Problem:** {plan.problem}", f"**Hook:** {plan.hook}", "", "## Characters"]
    for c in plan.characters:
        out.append(f"- **{c.name}** ({c.role}) — look: {c.look} | voice: {c.voice}")
    out += ["", "## Script & scenes"]
    for i, s in enumerate(plan.scenes, 1):
        out += [f"### Scene {i} ({s.seconds:.0f}s) — {s.speaker}", f"> {s.line}", "", f"_Visual:_ {s.visual_prompt}", ""]
    out += ["## Solution steps"] + [f"{i}. {step}" for i, step in enumerate(plan.solution_steps, 1)]
    out += [
        "",
        "## Upload info",
        f"**Title:** {plan.title}",
        "",
        f"**Description:** {plan.description}",
        "",
        "**Hashtags:** " + " ".join(h if h.startswith("#") else f"#{h}" for h in plan.hashtags),
        "",
        f"**Pinned comment:** {plan.comment_bait_question}",
        "",
        f"**Thumbnail prompt:** {plan.thumbnail_prompt}",
    ]
    return "\n".join(out) + "\n"
