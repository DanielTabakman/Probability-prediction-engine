"""PHASE_SELECTION_ROADMAP.json — ordered chapter list for auto-SELECTION."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_manifest import load_manifest, load_phase_plan, validate_phase_plan
from scripts.ppe_queue import load_queue, mark_queue_item_done, save_queue, upsert_queue_item

ROADMAP_REL = "docs/SOP/PHASE_SELECTION_ROADMAP.json"
VALID_ROADMAP_STATUSES = frozenset({"done", "pending", "ready", "skipped"})


def roadmap_path(repo_root: Path) -> Path:
    return (repo_root / ROADMAP_REL).resolve()


def roadmap_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_AUTO_ROADMAP", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    return roadmap_path(repo_root).is_file()


def load_roadmap(repo_root: Path) -> dict[str, Any]:
    p = roadmap_path(repo_root)
    if not p.is_file():
        raise FileNotFoundError(f"Missing roadmap: {ROADMAP_REL}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_roadmap(repo_root: Path, roadmap: dict[str, Any]) -> None:
    p = roadmap_path(repo_root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(roadmap, indent=2) + "\n", encoding="utf-8")


def norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _plan_valid(repo_root: Path, plan_path: str) -> tuple[bool, str]:
    rel = norm_plan(plan_path)
    if not rel:
        return False, "empty planPath"
    fs = repo_root / rel
    if not fs.is_file():
        return False, f"plan not found: {rel}"
    try:
        plan = load_phase_plan(repo_root, rel)
    except json.JSONDecodeError as e:
        return False, f"invalid JSON: {e}"
    errors = validate_phase_plan(plan)
    if errors:
        return False, "; ".join(errors)
    return True, ""


def _queue_status_for_roadmap(roadmap_status: str) -> str | None:
    s = roadmap_status.strip().lower()
    if s == "done":
        return "DONE"
    if s == "ready":
        return "READY"
    if s == "pending":
        return "PLANNED"
    return None


def _roadmap_item_fields(item: dict[str, Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    for key in ("reason", "selectionPrep", "workerMode"):
        if item.get(key):
            fields[key] = item[key]
    return fields


def sync_roadmap_to_queue(repo_root: Path, *, apply: bool) -> list[dict[str, Any]]:
    """Align PHASE_QUEUE rows with roadmap statuses (PLANNED / READY / DONE)."""
    repo = repo_root.resolve()
    if not roadmap_enabled(repo) or not roadmap_path(repo).is_file():
        return []
    roadmap = load_roadmap(repo)
    changes: list[dict[str, Any]] = []
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        if not plan:
            continue
        rs = str(item.get("status") or "pending").strip().lower()
        if rs not in VALID_ROADMAP_STATUSES:
            continue
        q_status = _queue_status_for_roadmap(rs)
        if q_status is None:
            continue
        if not apply:
            changes.append({"action": "would_sync", "planPath": plan, "queueStatus": q_status})
            continue
        upsert_queue_item(
            repo,
            plan_path=plan,
            status=q_status,
            **_roadmap_item_fields(item),
        )
        changes.append({"action": "synced", "planPath": plan, "queueStatus": q_status})
    return changes


def _set_roadmap_status(
    roadmap: dict[str, Any],
    plan_path: str,
    status: str,
) -> bool:
    norm = norm_plan(plan_path)
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        if norm_plan(str(item.get("planPath") or "")) != norm:
            continue
        item["status"] = status
        return True
    return False


def _first_pending_with_valid_plan(repo_root: Path, roadmap: dict[str, Any]) -> dict[str, Any] | None:
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        if str(item.get("status") or "").strip().lower() != "pending":
            continue
        plan = norm_plan(str(item.get("planPath") or ""))
        ok, _ = _plan_valid(repo_root, plan)
        if ok:
            return item
    return None


def bootstrap_next_ready(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """If idle (COMPLETE manifest, no READY queue), promote first valid pending roadmap row."""
    repo = repo_root.resolve()
    if not roadmap_enabled(repo):
        return {"bootstrapped": False, "reason": "PPE_AUTO_ROADMAP disabled"}
    if not roadmap_path(repo).is_file():
        return {"bootstrapped": False, "reason": "no roadmap file"}

    try:
        manifest = load_manifest(repo)
    except Exception as e:
        return {"bootstrapped": False, "reason": str(e)}

    status = str(manifest.get("status") or "").strip().upper()
    if status not in ("COMPLETE", ""):
        return {"bootstrapped": False, "reason": f"manifest is {status}"}
    if str(manifest.get("phasePlanPath") or "").strip():
        return {"bootstrapped": False, "reason": "manifest has phasePlanPath"}

    queue = load_queue(repo)
    if any(
        isinstance(it, dict) and str(it.get("status") or "").upper() == "READY"
        for it in (queue.get("items") or [])
    ):
        return {"bootstrapped": False, "reason": "queue already has READY"}

    roadmap = load_roadmap(repo)
    item = _first_pending_with_valid_plan(repo, roadmap)
    if item is None:
        return {"bootstrapped": False, "reason": "no valid pending roadmap item"}

    plan = norm_plan(str(item["planPath"]))
    if not apply:
        return {"bootstrapped": True, "planPath": plan, "reason": "would set READY (dry-run)"}

    _set_roadmap_status(roadmap, plan, "ready")
    save_roadmap(repo, roadmap)
    upsert_queue_item(
        repo,
        plan_path=plan,
        status="READY",
        **_roadmap_item_fields(item),
    )
    return {"bootstrapped": True, "planPath": plan, "reason": "first pending -> READY"}


def advance_after_chapter_closeout(
    repo_root: Path,
    *,
    closed_plan_path: str,
    apply: bool,
) -> dict[str, Any]:
    """Mark closed chapter done; set next pending -> READY in roadmap and queue."""
    repo = repo_root.resolve()
    closed = norm_plan(closed_plan_path)
    if not roadmap_enabled(repo):
        return {"advanced": False, "reason": "PPE_AUTO_ROADMAP disabled"}
    if not roadmap_path(repo).is_file():
        return {"advanced": False, "reason": "no roadmap file"}

    roadmap = load_roadmap(repo)
    if closed:
        _set_roadmap_status(roadmap, closed, "done")
        if apply:
            mark_queue_item_done(
                repo,
                plan_path=closed,
                done_reason="marked DONE by ppe_roadmap (chapter closeout)",
            )

    next_item = _first_pending_with_valid_plan(repo, roadmap)
    if next_item is None:
        if apply:
            save_roadmap(repo, roadmap)
        return {"advanced": False, "closedPlan": closed, "reason": "no pending roadmap item with valid plan"}

    next_plan = norm_plan(str(next_item["planPath"]))
    if not apply:
        return {
            "advanced": True,
            "closedPlan": closed,
            "nextPlan": next_plan,
            "reason": "would set next pending -> READY",
        }

    _set_roadmap_status(roadmap, next_plan, "ready")
    save_roadmap(repo, roadmap)
    upsert_queue_item(
        repo,
        plan_path=next_plan,
        status="READY",
        **_roadmap_item_fields(next_item),
    )
    return {
        "advanced": True,
        "closedPlan": closed,
        "nextPlan": next_plan,
        "reason": "next pending -> READY",
    }


def maybe_advance_roadmap_and_select(
    repo_root: Path,
    *,
    closed_plan_path: str,
    apply: bool,
) -> dict[str, Any]:
    """Hydrate queue, advance roadmap after closeout, bootstrap if needed, run auto-select."""
    repo = repo_root.resolve()
    if not roadmap_enabled(repo):
        return {"skipped": True, "reason": "PPE_AUTO_ROADMAP disabled or no roadmap"}

    out: dict[str, Any] = {"skipped": False}
    if apply:
        sync = sync_roadmap_to_queue(repo, apply=True)
        if sync:
            out["synced"] = len(sync)

    adv = advance_after_chapter_closeout(
        repo,
        closed_plan_path=closed_plan_path,
        apply=apply,
    )
    out["advance"] = adv

    boot = bootstrap_next_ready(repo, apply=apply)
    out["bootstrap"] = boot

    if apply:
        rc = run_auto_select(repo, apply=True, select_only=False, mark_done=False, force=False)
        out["auto_select_exit"] = rc
    return out


def prepare_selection_idle(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Called before auto-select at run_ppe start: sync roadmap + bootstrap if idle."""
    repo = repo_root.resolve()
    if not roadmap_enabled(repo):
        return {"skipped": True}
    out: dict[str, Any] = {"skipped": False}
    if apply:
        sync = sync_roadmap_to_queue(repo, apply=True)
        out["synced"] = len(sync)
    boot = bootstrap_next_ready(repo, apply=apply)
    out["bootstrap"] = boot
    return out
