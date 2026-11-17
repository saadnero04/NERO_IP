"""Command line: find problems, then write viral character videos about them.

    python -m problem_channel find              # list trending problems
    python -m problem_channel make --count 5    # find + write 5 video packages
    python -m problem_channel make --problem "How to stop overthinking"
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

    m = sub.add_parser("make", help="write video packages")
    m.add_argument("--count", type=int, default=3)
    m.add_argument("--problem", help="write about this exact problem instead of searching")
    m.add_argument("--style", default="cute 3D Pixar-like animation")
    m.add_argument("--offline", action="store_true")
    m.add_argument("--out", default="videos")

    args = ap.parse_args()

    if args.cmd == "find":
        problems = find_problems(offline=args.offline, top=args.top)
        for i, p in enumerate(problems, 1):
            print(f"{i:>2}. [{p.score:>5}] {p.text}  ({p.source})")
        Path("problems.json").write_text(json.dumps([p.to_dict() for p in problems], indent=2))
        print("\nSaved to problems.json")
        return

    from .writer import to_markdown, write_video  # needs the anthropic package

    topics = [args.problem] if args.problem else [p.text for p in find_problems(offline=args.offline, top=args.count)]
    out_dir = Path(args.out) / date.today().isoformat()
    out_dir.mkdir(parents=True, exist_ok=True)
    for topic in topics:
        print(f"Writing: {topic}")
        try:
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
