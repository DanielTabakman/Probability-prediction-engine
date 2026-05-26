"""Resolve and summarize ACTIVE_PHASE_MANIFEST.json + phase plan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_manifest import resolve_summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Resolve active phase manifest")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Print JSON only")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    try:
        summary = resolve_summary(repo)
    except Exception as e:
        if args.json:
            print(json.dumps({"errors": [str(e)]}))
        else:
            print(f"resolve_active_phase: error: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0 if not summary.get("errors") else 1

    print(f"manifest: {summary.get('manifest_path')}")
    print(f"status: {summary.get('status')}")
    if summary.get("chapter_name"):
        print(f"chapter: {summary.get('chapter_name')}")
    if summary.get("phase_plan_path"):
        print(f"phase_plan: {summary.get('phase_plan_path')}")
        print(f"slices: {summary.get('slice_count')}")
        print(f"first_slice: {summary.get('first_slice_id')}")
    if summary.get("notes"):
        print(f"notes: {summary.get('notes')}")
    if summary.get("errors"):
        print("errors:")
        for err in summary["errors"]:
            print(f"  - {err}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
