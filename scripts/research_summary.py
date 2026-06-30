"""Write unified RESEARCH_SUMMARY.json rollup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.research_summary import build_research_summary, write_research_summary  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build research pipeline summary JSON")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    payload = build_research_summary(repo)
    if args.write:
        write_research_summary(repo)
    if args.json or not args.write:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
