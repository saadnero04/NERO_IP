"""Command line: find problems, then write viral character videos about them.

    python -m problem_channel find              # list trending problems
    python -m problem_channel make --count 5    # find + write 5 video packages
    python -m problem_channel make --problem "How to stop overthinking"
    python -m problem_channel make --niche money --domain "AI services for small businesses" --count 5
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from .finder import find_problems


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def main() -> None:
    ap = argparse.ArgumentParser(prog="problem_channel")
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("find", help="find trending problems")
    f.add_argument("--top", type=int, default=30)
    f.add_argument("--offline", action="store_true", help="use built-in sample problems")
    f.add_argument("--niche", choices=["general", "money"], default="general")

    m = sub.add_parser("make", help="write video packages")
    m.add_argument("--count", type=int, default=3)
    m.add_argument("--problem", help="write about this exact problem instead of searching")
    m.add_argument("--style", default="cute 3D Pixar-like animation")
    m.add_argument("--offline", action="store_true")
    m.add_argument("--out", default="videos")
    m.add_argument("--niche", choices=["general", "money"], default="general")
    m.add_argument("--domain", default="offering AI services to small businesses", help="money niche: what Cashy recommends")
    m.add_argument("--cta-word", default="AI", help="money niche: word viewers comment")
    m.add_argument("--language", default="English")

    args = ap.parse_args()

    if args.cmd == "find":
        problems = find_problems(offline=args.offline, top=args.top, niche=args.niche)
        for i, p in enumerate(problems, 1):
            print(f"{i:>2}. [{p.score:>5}] {p.text}  ({p.source})")
        Path("problems.json").write_text(json.dumps([p.to_dict() for p in problems], indent=2))
        print("\nSaved to problems.json")
        return

    from .writer import to_markdown, write_money_video, write_video  # needs the anthropic package

    topics = [args.problem] if args.problem else [p.text for p in find_problems(offline=args.offline, top=args.count, niche=args.niche)]
    out_dir = Path(args.out) / date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    for topic in topics:
        print(f"Writing: {topic}")
        try:
            if args.niche == "money":
                plan = write_money_video(topic, args.domain, cta_word=args.cta_word, language=args.language)
            else:
                plan = write_video(topic, style=args.style)
        except Exception as exc:
            print(f"  failed: {exc}")
            continue
        base = out_dir / slug(topic)
        base.with_suffix(".md").write_text(to_markdown(plan))
        base.with_suffix(".json").write_text(plan.model_dump_json(indent=2))
        print(f"  -> {base}.md")


if __name__ == "__main__":
    main()
