"""Find real problems people are asking about right now.

Sources (all free, no API key needed):
  * Reddit  - top posts of the week from advice / help subreddits (public JSON)
  * YouTube - search autocomplete for "how to fix ...", "how to stop ...", etc.

Each problem gets a "viral score" from engagement so the best ones go first.
"""

from __future__ import annotations

import json
import math
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path

USER_AGENT = "problem-channel-finder/0.1"

# Subreddits where people describe real, relatable problems.
DEFAULT_SUBREDDITS = [
    "NoStupidQuestions",
    "LifeProTips",
    "personalfinance",
    "relationship_advice",
    "productivity",
    "sleep",
    "techsupport",
    "CleaningTips",
    "GetMotivated",
    "careerguidance",
]

# Phrases people type when they have a problem.
DEFAULT_SEEDS = [
    "how to fix",
    "how to stop",
    "how to get rid of",
    "why does my",
    "why am i always",
    "what to do when",
    "how to deal with",
]


@dataclass
class Problem:
    text: str
    source: str
    score: float = 0.0
    url: str = ""
    details: str = ""
    tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


def _get_json(url: str, timeout: float = 15.0):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def from_reddit(subreddits=DEFAULT_SUBREDDITS, period: str = "week", limit: int = 15) -> list[Problem]:
    problems: list[Problem] = []
    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/top.json?t={period}&limit={limit}"
        try:
            data = _get_json(url)
        except Exception as exc:  # network errors, rate limits, private subs
            print(f"  [reddit] skipped r/{sub}: {exc}")
            continue
        for child in data.get("data", {}).get("children", []):
            post = child.get("data", {})
            if post.get("over_18") or post.get("stickied"):
                continue
            ups = post.get("ups", 0)
            comments = post.get("num_comments", 0)
            # Comments signal "people relate to this" more than upvotes do.
            score = math.log10(1 + ups) * 10 + math.log10(1 + comments) * 15
            problems.append(
                Problem(
                    text=post.get("title", "").strip(),
                    source=f"reddit/r/{sub}",
                    score=round(score, 1),
                    url="https://www.reddit.com" + post.get("permalink", ""),
                    details=(post.get("selftext") or "")[:600],
                    tags=[sub],
                )
            )
        time.sleep(1.5)  # be polite to Reddit
    return problems


def from_youtube_autocomplete(seeds=DEFAULT_SEEDS, letters: str = "abcdefghijklmnoprstw") -> list[Problem]:
    """Expand each seed with a-z to discover what people actually search."""
    problems: list[Problem] = []
    seen: set[str] = set()
    for seed in seeds:
        for letter in [""] + list(letters):
            q = f"{seed} {letter}".strip()
            url = (
                "https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&q="
                + urllib.parse.quote(q)
            )
            try:
                data = _get_json(url)
            except Exception as exc:
                print(f"  [youtube] skipped '{q}': {exc}")
                break
            suggestions = data[1] if isinstance(data, list) and len(data) > 1 else []
            for rank, s in enumerate(suggestions):
                if s in seen:
                    continue
                seen.add(s)
                # Higher in the autocomplete list = more searched.
                problems.append(
                    Problem(text=s, source="youtube-search", score=round(20 - rank * 1.5, 1), tags=[seed])
                )
            time.sleep(0.3)
    return problems


def load_sample() -> list[Problem]:
    path = Path(__file__).with_name("sample_problems.json")
    return [Problem(**p) for p in json.loads(path.read_text())]


def find_problems(use_reddit=True, use_youtube=True, offline=False, top: int = 30) -> list[Problem]:
    if offline:
        problems = load_sample()
    else:
        problems = []
        if use_reddit:
            print("Searching Reddit...")
            problems += from_reddit()
        if use_youtube:
            print("Searching YouTube autocomplete...")
            problems += from_youtube_autocomplete()
        if not problems:
            print("No live results (network blocked?). Falling back to sample problems.")
            problems = load_sample()

    # De-duplicate by lowercase text, keep the best score.
    best: dict[str, Problem] = {}
    for p in problems:
        key = p.text.lower().strip(" ?!.")
        if len(key) < 12:
            continue
        if key not in best or p.score > best[key].score:
            best[key] = p
    return sorted(best.values(), key=lambda p: p.score, reverse=True)[:top]
