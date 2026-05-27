"""Auto-resume incomplete phases and chain to the next READY queue chapter."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from scripts.ppe_manifest import load_manifest, load_phase_plan


def _norm_plan(path: str) -> str:
    return path.replace("\\", "/").strip()


def load_phase_summary(repo_root: Path) -> dict[str, Any] | None:
    p = repo_root / "artifacts" / "orchestrator" / "steward_phase_summary.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8-sig"))


def slice_ids_from_plan(repo_root: Path, plan_path: str) -> list[str]:
    plan = load_phase_plan(repo_root, plan_path)
    out: list[str] = []
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and sl.get("sliceId"):
            out.append(str(sl["sliceId"]))
    return out


def continued_slice_ids(summary: dict[str, Any]) -> set[str]:
    done: set[str] = set()
    for row in summary.get("results") or []:
        if not isinstance(row, dict) or row.get("kind") != "ran":
            continue
        run = row.get("run") or {}
        if str(run.get("status") or "").upper() == "CONTINUE":
            sid = str(row.get("sliceId") or "").strip()
            if sid:
                done.add(sid)
    return done


def remaining_slice_ids(repo_root: Path, plan_path: str, summary: dict[str, Any]) -> list[str]:
    """Slice IDs in plan order that did not end with relay CONTINUE."""
    all_ids = slice_ids_from_plan(repo_root, plan_path)
    done = continued_slice_ids(summary)
    return [sid for sid in all_ids if sid not in done]


def summary_matches_plan(summary: dict[str, Any], plan_path: str) -> bool:
    return _norm_plan(str(summary.get("planPath") or "")) == _norm_plan(plan_path)


def closeout_slice_id(repo_root: Path, plan_path: str) -> str | None:
    plan = load_phase_plan(repo_root, plan_path)
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and sl.get("sliceId") and "closeout" in sl:
            return str(sl["sliceId"])
    return None


def chapter_is_complete(repo_root: Path, plan_path: str) -> bool:
    manifest = load_manifest(repo_root)
    if str(manifest.get("status") or "").upper() == "COMPLETE":
        return True
    summary = load_phase_summary(repo_root)
    if summary is None or not summary_matches_plan(summary, plan_path):
        return False
    closeout = closeout_slice_id(repo_root, plan_path)
    if not closeout:
        return False
    return closeout in continued_slice_ids(summary)


def resume_incomplete_phase(
    repo_root: Path,
    plan_path: str,
    *,
    run_slice: Callable[[str], int],
) -> tuple[bool, int]:
    """Run remaining slices from steward_phase_summary. Returns (recovered, exit_code)."""
    summary = load_phase_summary(repo_root)
    if summary is None:
        return False, 1
    if not summary_matches_plan(summary, plan_path):
        print(f"ppe_auto_chain: summary plan mismatch; skip resume")
        return False, 1

    remaining = remaining_slice_ids(repo_root, plan_path, summary)
    if not remaining:
        if chapter_is_complete(repo_root, plan_path):
            print("ppe_auto_chain: phase already complete (closeout CONTINUE)")
            return True, 0
        return False, 1

    print(f"ppe_auto_chain: auto-resume {len(remaining)} slice(s): {', '.join(remaining)}")
    for slice_id in remaining:
        rc = run_slice(slice_id)
        if rc != 0:
            print(f"ppe_auto_chain: resume stopped at {slice_id} (exit {rc})")
            return False, rc
    return True, 0
