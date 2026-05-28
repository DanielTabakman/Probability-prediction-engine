"""Heuristics to recover common STOP_FOR_REVIEW exits and continue automatically.

Goal: keep `run_ppe.cmd` moving when a relay slice STOPs for review due to
promotion locks or closeout not being applied, *when it is safe*.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from scripts.ppe_manifest import load_phase_plan


def _find_latest_relay_result(repo: Path) -> Path | None:
    candidates: list[Path] = []
    # Prefer worktree relay results (most recent orchestrator run).
    wt = repo / "_worktrees" / "acp_orchestrator"
    if wt.is_dir():
        candidates.extend(wt.glob("*/artifacts/relay/runs/*/relay_result.json"))
    # Fallback: repo-local relay results (rare).
    candidates.extend((repo / "artifacts" / "relay" / "runs").glob("*/relay_result.json"))
    existing = [p for p in candidates if p.is_file()]
    if not existing:
        return None
    return max(existing, key=lambda p: p.stat().st_mtime)


def _next_slice_after(plan: dict, *, current_slice_id: str) -> str | None:
    slices = plan.get("slices") if isinstance(plan.get("slices"), list) else []
    ids = [s.get("sliceId") for s in slices if isinstance(s, dict)]
    if current_slice_id not in ids:
        return None
    i = ids.index(current_slice_id)
    if i + 1 >= len(ids):
        return None
    nxt = ids[i + 1]
    return str(nxt) if isinstance(nxt, str) and nxt else None


def maybe_recover_stop_for_review(
    *,
    repo: Path,
    plan_path: str,
    run_slice: Callable[[str], int],
) -> bool:
    """
    Attempt to recover when the wrapper exits 20 (STOP_FOR_REVIEW).

    Recovery strategy (safe-only):
    - If the latest relay_result.json says the last slice was safe_to_continue and
      STOP_FOR_REVIEW was due to promotion not performed, run the *next* slice
      (often smoke/closeout) which may be able to promote or close out in its own
      worktree context.
    - If we can't parse / don't have enough evidence, do nothing.
    """
    latest = _find_latest_relay_result(repo)
    if latest is None:
        return False

    data = json.loads(latest.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        return False

    # We only auto-act when the relay itself indicates it's safe to continue.
    if not bool(data.get("safe_to_continue", False)):
        return False

    last_slice_id = str(data.get("slice_id") or "").strip()
    if not last_slice_id:
        return False

    promotion = data.get("promotion") if isinstance(data.get("promotion"), dict) else {}
    promotion_performed = bool(promotion.get("performed", False))

    # If promotion didn't happen, it's a common benign STOP_FOR_REVIEW; attempt next slice.
    if not promotion_performed:
        plan = load_phase_plan(repo, plan_path)
        next_slice = _next_slice_after(plan, current_slice_id=last_slice_id)
        if not next_slice:
            return False
        rc = run_slice(next_slice)
        return rc == 0

    return False

