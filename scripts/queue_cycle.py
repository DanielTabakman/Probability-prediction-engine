"""Chapter-level slice queue for mechanical SELECTION + run_queue_cycle."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import (
    load_manifest,
    save_manifest,
    validate_phase_plan,
)

QUEUE_REL = "docs/SOP/SLICE_QUEUE_V1.json"
QUEUE_ITEM_STATUSES = frozenset({"PENDING", "RUNNING", "DONE", "BLOCKED"})
HARD_STOP_DECISIONS = frozenset({"STOP_FOR_REVIEW", "BLOCKED"})


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def queue_path(repo_root: Path) -> Path:
    return repo_root.resolve() / QUEUE_REL


def load_queue(repo_root: Path, rel_path: str | None = None) -> dict[str, Any]:
    p = repo_root / (rel_path or QUEUE_REL).replace("\\", "/")
    if not p.is_file():
        raise FileNotFoundError(f"Missing queue file: {p.relative_to(repo_root)}")
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_queue(repo_root: Path, data: dict[str, Any], rel_path: str | None = None) -> Path:
    p = repo_root / (rel_path or QUEUE_REL).replace("\\", "/")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return p


def validate_queue_item(item: dict[str, Any], *, repo_root: Path | None = None) -> list[str]:
    errors: list[str] = []
    for key in ("queueId", "chapterId", "chapterTitle", "phasePlanName", "status"):
        if not str(item.get(key) or "").strip():
            errors.append(f"queue item missing {key}")

    status = str(item.get("status") or "").strip()
    if status and status not in QUEUE_ITEM_STATUSES:
        errors.append(f"invalid status {status!r}; expected one of {sorted(QUEUE_ITEM_STATUSES)}")

    slices = item.get("slices")
    if not isinstance(slices, list) or not slices:
        errors.append("queue item: missing non-empty slices array")
        return errors

    if repo_root:
        plan = build_phase_plan_from_item(item, repo_root)
        for key in ("sprintSpecPath", "selectionRecord"):
            rel = str(plan.get(key) or item.get(key) or "").strip()
            if rel:
                p = repo_root / rel.replace("\\", "/")
                if not p.is_file():
                    errors.append(f"queue item path not found: {key}={rel}")
    else:
        plan = _plan_dict_from_item(item, None)
    errors.extend(validate_phase_plan(plan))

    return errors


def _plan_dict_from_item(item: dict[str, Any], repo_root: Path | None) -> dict[str, Any]:
    baseline = str(item.get("baselineBranch") or "main").strip()
    sprint = str(item.get("sprintSpecPath") or "").strip()
    if repo_root and not sprint:
        sprint = str(load_queue(repo_root).get("defaultSprintSpecPath") or "").strip()
    plan: dict[str, Any] = {
        "name": str(item.get("phasePlanName") or item.get("chapterTitle") or "queue_chapter"),
        "baselineBranch": baseline,
        "slices": item.get("slices") or [],
    }
    if sprint:
        plan["sprintSpecPath"] = sprint
    sel = str(item.get("selectionRecord") or "").strip()
    if sel:
        plan["selectionRecord"] = sel
    return plan


def build_phase_plan_from_item(item: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    queue = load_queue(repo_root)
    baseline = str(item.get("baselineBranch") or queue.get("defaultBaselineBranch") or "main").strip()
    sprint = str(item.get("sprintSpecPath") or queue.get("defaultSprintSpecPath") or "").strip()
    plan: dict[str, Any] = {
        "name": str(item.get("phasePlanName") or item.get("chapterTitle") or "queue_chapter"),
        "baselineBranch": baseline,
        "slices": list(item.get("slices") or []),
    }
    if sprint:
        plan["sprintSpecPath"] = sprint
    sel = str(item.get("selectionRecord") or "").strip()
    if sel:
        plan["selectionRecord"] = sel
    return plan


def _safe_plan_filename(queue_id: str, ts: str) -> str:
    safe_id = re.sub(r"[^A-Za-z0-9_-]+", "_", queue_id).strip("_") or "queue"
    safe_ts = re.sub(r"[^0-9]+", "", ts)[:14]
    return f"auto_queue_{safe_id}_{safe_ts}.json"


def write_generated_phase_plan(
    repo_root: Path,
    item: dict[str, Any],
    *,
    ts: str | None = None,
) -> tuple[Path, str]:
    """Write phase plan under docs/SOP/PHASE_PLANS/; return (abs path, repo-relative path)."""
    ts_iso = ts or _utc_now_iso()
    rel_name = f"docs/SOP/PHASE_PLANS/{_safe_plan_filename(str(item['queueId']), ts_iso)}"
    plan = build_phase_plan_from_item(item, repo_root)
    out = repo_root / rel_name.replace("\\", "/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return out, rel_name.replace("\\", "/")


def write_manifest_for_item(
    repo_root: Path,
    item: dict[str, Any],
    plan_rel: str,
) -> None:
    plan = build_phase_plan_from_item(item, repo_root)
    manifest: dict[str, Any] = {
        "phasePlanPath": plan_rel.replace("\\", "/"),
        "sprintSpecPath": str(plan.get("sprintSpecPath") or "").strip(),
        "selectionRecord": str(plan.get("selectionRecord") or item.get("selectionRecord") or "").strip(),
        "status": "READY",
        "notes": (
            f"queueId={item.get('queueId')}; chapterId={item.get('chapterId')}; "
            f"set by run_queue_cycle"
        ),
    }
    save_manifest(repo_root, manifest)


def pick_next_pending(queue: dict[str, Any]) -> dict[str, Any] | None:
    for item in queue.get("items") or []:
        if isinstance(item, dict) and str(item.get("status") or "").strip() == "PENDING":
            return item
    return None


def find_item_by_queue_id(queue: dict[str, Any], queue_id: str) -> dict[str, Any] | None:
    for item in queue.get("items") or []:
        if isinstance(item, dict) and item.get("queueId") == queue_id:
            return item
    return None


def set_item_status(
    repo_root: Path,
    queue_id: str,
    status: str,
    *,
    queue_rel: str | None = None,
) -> None:
    if status not in QUEUE_ITEM_STATUSES:
        raise ValueError(f"invalid queue item status: {status}")
    data = load_queue(repo_root, queue_rel)
    item = find_item_by_queue_id(data, queue_id)
    if item is None:
        raise KeyError(f"queueId not found: {queue_id}")
    item["status"] = status
    item["updatedAt"] = _utc_now_iso()
    save_queue(repo_root, data, queue_rel)


def active_run_exists(repo_root: Path) -> bool:
    return (repo_root / "artifacts/orchestrator/ACTIVE_RUN.json").is_file()


def manifest_is_running(repo_root: Path) -> bool:
    try:
        return str(load_manifest(repo_root).get("status") or "").strip() == "RUNNING"
    except Exception:
        return False


def read_last_run_report(repo_root: Path) -> dict[str, Any] | None:
    p = repo_root / "artifacts/orchestrator/LAST_RUN_REPORT.json"
    if not p.is_file():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return None


def _relay_decision_from_report(report: dict[str, Any] | None) -> str | None:
    if not report:
        return None
    relay = report.get("relay_result")
    if isinstance(relay, dict):
        for key in ("decision", "relay_decision"):
            val = str(relay.get(key) or "").strip()
            if val:
                return val
        stop = relay.get("stop_condition")
        if stop is None and relay.get("safe_to_continue") is True:
            return "CONTINUE"
    bucket = str(report.get("status_bucket") or "").strip()
    if bucket == "continue":
        return "CONTINUE"
    if bucket in ("stop_for_review_or_procedural", "error_or_stopped", "review"):
        return "STOP_FOR_REVIEW"
    return None


def classify_chapter_outcome(
    repo_root: Path,
    *,
    wrapper_exit_code: int,
    plan_rel: str,
) -> tuple[str, str]:
    """
    Return (queue_status, reason).
    queue_status is DONE or BLOCKED.
    """
    report = read_last_run_report(repo_root)
    decision = _relay_decision_from_report(report)

    if wrapper_exit_code != 0:
        return "BLOCKED", f"wrapper_exit_code={wrapper_exit_code}"

    if decision in HARD_STOP_DECISIONS:
        return "BLOCKED", f"relay_decision={decision}"

    try:
        manifest = load_manifest(repo_root)
        manifest_status = str(manifest.get("status") or "").strip()
        manifest_plan = str(manifest.get("phasePlanPath") or "").replace("\\", "/")
    except Exception as e:
        return "BLOCKED", f"manifest_read_error={e}"

    if manifest_plan and manifest_plan != plan_rel.replace("\\", "/"):
        return "BLOCKED", f"manifest_plan_mismatch expected={plan_rel} got={manifest_plan}"

    if manifest_status == "COMPLETE":
        return "DONE", "manifest_complete"

    if decision == "CONTINUE" or (report and report.get("status_bucket") == "continue"):
        # Phase may have stopped early without closeout slice completing manifest.
        if manifest_status == "COMPLETE":
            return "DONE", "manifest_complete"
        return "BLOCKED", f"incomplete_after_continue manifest_status={manifest_status}"

    if report and report.get("awaiting_user") is True:
        return "BLOCKED", f"awaiting_user status_bucket={report.get('status_bucket')}"

    return "BLOCKED", "ambiguous_outcome"


def preflight_cycle(repo_root: Path) -> list[str]:
    errors: list[str] = []
    if active_run_exists(repo_root):
        errors.append("ACTIVE_RUN.json exists; another slice/phase may be in flight")
    if manifest_is_running(repo_root):
        errors.append("ACTIVE_PHASE_MANIFEST.json status is RUNNING")
    return errors
