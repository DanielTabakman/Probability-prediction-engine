#!/usr/bin/env python3
"""Generate docs/SOP/CHAPTER_DOC_INDEX.json from PHASE_PLANS/*_relay.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.sop_discovery_core import (  # noqa: E402
    build_chapter_doc_index,
    chapter_doc_index_fresh,
    write_chapter_doc_index,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate CHAPTER_DOC_INDEX.json")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--write", action="store_true", help="Write docs/SOP/CHAPTER_DOC_INDEX.json")
    ap.add_argument(
        "--check",
        action="store_true",
        help="Fail if CHAPTER_DOC_INDEX.json or ARCHIVE_INDEX.md is stale",
    )
    ap.add_argument("--stdout", action="store_true", help="Print JSON to stdout")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.stdout:
        import json

        print(json.dumps(build_chapter_doc_index(repo), indent=2, sort_keys=True))
        return 0

    if args.write:
        out = write_chapter_doc_index(repo)
        index = build_chapter_doc_index(repo)
        print(
            f"generate_chapter_doc_index: wrote {out} "
            f"({index['chapter_count']} chapters, "
            f"{index['active_chapter_count']} active, "
            f"{index['archived_chapter_count']} archived)"
        )
        return 0

    if args.check:
        fresh, reason = chapter_doc_index_fresh(repo)
        if not fresh:
            print(f"generate_chapter_doc_index: {reason}", file=sys.stderr)
            return 1
        print(f"generate_chapter_doc_index: {reason}")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
