#!/usr/bin/env python3
"""Generate docs/SOP/CHAPTER_DOC_INDEX.json from PHASE_PLANS/*_relay.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.sop_discovery_core import build_chapter_doc_index, write_chapter_doc_index  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate CHAPTER_DOC_INDEX.json")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--write", action="store_true", help="Write docs/SOP/CHAPTER_DOC_INDEX.json")
    ap.add_argument("--stdout", action="store_true", help="Print JSON to stdout")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.stdout:
        import json

        print(json.dumps(build_chapter_doc_index(repo), indent=2, sort_keys=True))
        return 0

    if args.write:
        out = write_chapter_doc_index(repo)
        data = build_chapter_doc_index(repo)
        print(f"generate_chapter_doc_index: wrote {out} ({data['chapter_count']} chapters)")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
