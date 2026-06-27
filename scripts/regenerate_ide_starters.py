"""Regenerate all on-disk IDE BUILD starters from phase plans."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def find_plan_for_slice(repo: Path, slice_id: str) -> str | None:
    plans_dir = repo / "docs" / "SOP" / "PHASE_PLANS"
    if not plans_dir.is_dir():
        return None
    for plan_file in sorted(plans_dir.glob("*_relay.json")):
        try:
            data = json.loads(plan_file.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            continue
        for sl in data.get("slices") or []:
            if isinstance(sl, dict) and str(sl.get("sliceId") or "") == slice_id:
                return str(plan_file.relative_to(repo)).replace("\\", "/")
    return None


def regenerate_all(repo: Path, *, prune_stale: bool = True) -> list[tuple[str, int]]:
    from scripts.ppe_ide_build_starter import STARTER_DIR, starter_path, write_starter

    repo = repo.resolve()
    if prune_stale:
        from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters

        prune_starters_for_completed_chapters(repo)

    orch = repo / STARTER_DIR
    results: list[tuple[str, int]] = []
    if not orch.is_dir():
        return results

    for path in sorted(orch.glob("IDE_BUILD_STARTER_*.md")):
        slice_id = path.stem.replace("IDE_BUILD_STARTER_", "", 1)
        plan = find_plan_for_slice(repo, slice_id)
        if not plan:
            path.unlink(missing_ok=True)
            print(f"regenerate_ide_starters: removed orphan {path.name} (no phase plan)")
            continue
        write_starter(repo, slice_id=slice_id, phase_plan=plan)
        lines = len(path.read_text(encoding="utf-8").splitlines())
        results.append((slice_id, lines))
        print(f"regenerate_ide_starters: {slice_id} ({lines} lines)")
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate IDE BUILD starters on disk.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--no-prune", action="store_true")
    args = ap.parse_args(argv)
    rows = regenerate_all(args.repo_root.resolve(), prune_stale=not args.no_prune)
    if not rows:
        print("regenerate_ide_starters: no starters on disk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
