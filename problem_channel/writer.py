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


# ---------------------------------------------------------------------------
# Money niche: one recurring main character + a comment-to-ebook funnel
# ---------------------------------------------------------------------------

MAIN_CHARACTER = Character(
    name="Cashy",
    role="fixer",
    look=(
        "a shiny gold coin character with a friendly face, black sunglasses pushed up on his head, "
        "a green hoodie with a small white dollar-sign logo, white sneakers, expressive cartoon eyes, "
        "3D Pixar-like style, standing in a cozy modern room with a laptop glowing behind him"
    ),
    voice="warm, confident, slightly fast, like a big brother giving real advice",
)

MONEY_SYSTEM = f"""You write faceless Shorts / Reels / TikToks for a money channel.
There is ONE main character, always the same: {MAIN_CHARACTER.name} — {MAIN_CHARACTER.look}.
Voice: {MAIN_CHARACTER.voice}. Every visual prompt must describe him this exact way.

Every video follows these 5 beats (35-55 seconds, 100-140 spoken words):
1. HOOK (0-3s): name the money pain the viewer feels right now
   (rent, debt, salary not enough, no savings...). No greetings.
2. PROBLEM: one or two relatable lines about why the usual answer doesn't work.
3. THE DOMAIN: "The best thing you can do in 2026 is ..." then the domain you are
   given, explained in plain words in one or two sentences.
4. PROOF: show that people really make money with it using AI.
   STRICT RULES: only use facts that are real and publicly verifiable (a known
   platform's public numbers, a widely reported trend, a real public case).
   Never invent names, testimonials, screenshots or income figures. Never promise
   the viewer a specific income or say it's guaranteed, easy or fast. Put every
   factual claim you use in claims_to_verify so the creator can check it.
   If you are not sure a fact is true, describe the opportunity instead.
5. CTA: "If you want to start, comment {{cta_word}} and I'll send you the details."
   Then one short loop line.

Also give an on-screen disclaimer in the description: results vary, not financial advice.
"""


class MoneyVideoPlan(VideoPlan):
    domain: str
    cta: str
    claims_to_verify: List[str]


def write_money_video(
    problem: str,
    domain: str,
    cta_word: str = "AI",
    language: str = "English",
    client: anthropic.Anthropic | None = None,
) -> MoneyVideoPlan:
    client = client or anthropic.Anthropic()
    response = client.beta.messages.parse(
        model=MODEL,
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium"},
        system=MONEY_SYSTEM.replace("{cta_word}", cta_word),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Write the video in {language}.\n"
                    f"Money problem people are asking about: {problem}\n"
                    f"Domain to recommend: {domain}\n"
                    f"Comment keyword: {cta_word}\n"
                    f"The characters list must contain only {MAIN_CHARACTER.name}."
                ),
            }
        ],
        output_format=MoneyVideoPlan,
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
    if isinstance(plan, MoneyVideoPlan):
        out += ["", f"**Domain:** {plan.domain}", f"**CTA:** {plan.cta}", "", "## Check these claims before posting"]
        out += [f"- [ ] {c}" for c in plan.claims_to_verify] or ["- (none)"]
    return "\n".join(out) + "\n"
