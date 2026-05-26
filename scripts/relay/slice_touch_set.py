"""Active slice touch-set artifact for parallel BUILD discipline (VIZ_LAYER_DISCIPLINE_V1)."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.check_touch_set import check_touch_set
from scripts.relay.apply_control_closeout import load_phase_plan

ACTIVE_SLICE_TOUCH_SET_REL = "artifacts/control_plane/active_slice_touch_set.json"
DEFAULT_FORBIDDEN_TOUCH = ("src/viz/app.py",)
PRODUCT_PLANE = "PRODUCT-PLANE"


def active_touch_set_path(repo_root: Path) -> Path:
    return repo_root.resolve() / ACTIVE_SLICE_TOUCH_SET_REL


def find_slice_in_plan(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and sl.get("sliceId") == slice_id:
            return sl
    return None


def _normalize_prefixes(values: Any) -> tuple[str, ...]:
    if not isinstance(values, list):
        return ()
    out: list[str] = []
    for v in values:
        if isinstance(v, str) and v.strip():
            out.append(PurePosixPath(v.strip().replace("\\", "/")).as_posix())
    return tuple(out)


def write_active_slice_touch_set(
    repo_root: Path,
    *,
    phase_plan_path: Path,
    slice_id: str,
    declared_plane: str | None = None,
) -> Path:
    """Write gitignored artifact; raise ValueError on PRODUCT without touchSet."""
    repo = repo_root.resolve()
    plan = load_phase_plan(phase_plan_path.resolve())
    sl = find_slice_in_plan(plan, slice_id)
    if sl is None:
        raise ValueError(f"slice {slice_id!r} not found in {phase_plan_path}")

    plane = str(declared_plane or sl.get("declaredPlane") or "").strip()
    touch_set = _normalize_prefixes(sl.get("touchSet"))
    forbidden = _normalize_prefixes(sl.get("forbiddenTouch"))
    if not forbidden and plane == PRODUCT_PLANE:
        forbidden = DEFAULT_FORBIDDEN_TOUCH

    if plane == PRODUCT_PLANE and not touch_set:
        raise ValueError(
            f"PRODUCT-PLANE slice {slice_id!r} requires non-empty touchSet in phase plan"
        )

    payload = {
        "sliceId": slice_id,
        "declaredPlane": plane,
        "phasePlanPath": str(phase_plan_path.resolve().relative_to(repo)).replace("\\", "/"),
        "baselineBranch": str(plan.get("baselineBranch") or "main"),
        "touchSet": list(touch_set),
        "forbiddenTouch": list(forbidden),
    }

    out = active_touch_set_path(repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def load_active_slice_touch_set(repo_root: Path) -> dict[str, Any] | None:
    path = active_touch_set_path(repo_root)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def git_diff_paths(repo_root: Path, baseline: str, head: str = "HEAD") -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "diff", "--name-only", baseline, head],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout or "git diff failed")
    return tuple(
        PurePosixPath(ln.strip().replace("\\", "/")).as_posix()
        for ln in result.stdout.splitlines()
        if ln.strip()
    )


def git_worktree_paths_vs_head(repo_root: Path) -> tuple[str, ...]:
    """Paths changed vs HEAD (staged + unstaged on tracked files)."""
    inside = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return ()

    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout or "git diff failed")
    paths = {
        PurePosixPath(ln.strip().replace("\\", "/")).as_posix()
        for ln in result.stdout.splitlines()
        if ln.strip()
    }
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if untracked.returncode == 0:
        for ln in untracked.stdout.splitlines():
            if ln.strip():
                paths.add(PurePosixPath(ln.strip().replace("\\", "/")).as_posix())
    return tuple(sorted(paths))


def verify_active_touch_set(
    repo_root: Path,
    *,
    baseline_branch: str | None = None,
    use_worktree: bool = False,
) -> tuple[bool, list[str]]:
    """Verify current diff against active_slice_touch_set.json."""
    artifact = load_active_slice_touch_set(repo_root)
    if artifact is None:
        return True, []

    touch_set = _normalize_prefixes(artifact.get("touchSet"))
    forbidden = _normalize_prefixes(artifact.get("forbiddenTouch"))
    if not touch_set:
        return False, ["active touch-set artifact has empty touchSet"]

    if use_worktree:
        changed = git_worktree_paths_vs_head(repo_root)
    else:
        baseline = baseline_branch or str(artifact.get("baselineBranch") or "main")
        changed = git_diff_paths(repo_root, baseline)

    return check_touch_set(changed, touch_set, forbidden)


def touch_set_from_env() -> tuple[tuple[str, ...], tuple[str, ...]] | None:
    import os

    raw_allowed = os.environ.get("PPE_SLICE_TOUCH_SET", "").strip()
    if not raw_allowed:
        return None
    allowed = tuple(p.strip() for p in raw_allowed.split(",") if p.strip())
    raw_forbidden = os.environ.get("PPE_SLICE_FORBIDDEN_TOUCH", "").strip()
    forbidden = tuple(p.strip() for p in raw_forbidden.split(",") if p.strip()) if raw_forbidden else ()
    return allowed, forbidden
