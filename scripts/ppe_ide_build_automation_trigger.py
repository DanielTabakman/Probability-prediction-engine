"""Cursor Automation trigger file + optional webhook for IDE BUILD handoff."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TRIGGER_REL = ".cursor/IDE_BUILD_TRIGGER.json"
TRIGGER_VERSION = 1


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def trigger_path(repo: Path) -> Path:
    return (repo / TRIGGER_REL).resolve()


def load_trigger(repo: Path) -> dict[str, Any]:
    path = trigger_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_trigger(repo: Path, payload: dict[str, Any]) -> Path:
    repo = repo.resolve()
    path = trigger_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    body = {"version": TRIGGER_VERSION, **payload}
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def write_trigger_pending(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    starter_rel: str,
    reason: str,
    source: str,
) -> Path:
    return write_trigger(
        repo,
        {
            "status": "pending",
            "sliceId": slice_id,
            "planPath": plan_path.replace("\\", "/"),
            "starter": starter_rel.replace("\\", "/"),
            "reason": reason,
            "source": source,
            "handoffAt": _utc_now(),
        },
    )


def write_trigger_idle(repo: Path, *, completed_slice: str | None = None) -> Path:
    payload: dict[str, Any] = {"status": "idle", "clearedAt": _utc_now()}
    if completed_slice:
        payload["lastCompletedSlice"] = completed_slice
    return write_trigger(repo, payload)


def write_trigger_dispatched(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    starter_rel: str,
    handoff_at: str,
    source: str = "local-watcher",
    worker_pid: int | None = None,
) -> Path:
    payload: dict[str, Any] = {
        "status": "dispatched",
        "sliceId": slice_id,
        "planPath": plan_path.replace("\\", "/"),
        "starter": starter_rel.replace("\\", "/"),
        "handoffAt": handoff_at,
        "dispatchedAt": _utc_now(),
        "dispatchedBy": source,
    }
    if worker_pid is not None:
        payload["workerPid"] = worker_pid
    return write_trigger(repo, payload)


def post_automation_webhook(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    url = os.environ.get("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", "").strip()
    if not url:
        return {"ok": False, "skipped": True, "reason": "PPE_CURSOR_AUTOMATION_WEBHOOK_URL unset"}
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", "").strip()
    if key:
        headers["Authorization"] = f"Bearer {key}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        detail = exc.reason
        try:
            body = exc.read().decode("utf-8", errors="replace").strip()
            if body:
                detail = body[:500]
        except OSError:
            pass
        return {"ok": False, "error": f"HTTP {exc.code}", "detail": detail}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def notify_automation(repo: Path, *, handoff: dict[str, Any]) -> dict[str, Any]:
    """Write JSON trigger and optionally POST webhook for Cursor Automations."""
    repo = repo.resolve()
    slice_id = str(handoff.get("slice_id") or "").strip()
    plan_path = str(handoff.get("plan_path") or "").strip()
    starter = str(handoff.get("starter") or "").strip()
    reason = str(handoff.get("reason") or "").strip()
    source = str(handoff.get("source") or "").strip()
    if not slice_id or not starter:
        return {"ok": False, "reason": "missing slice_id or starter"}

    trigger_file = write_trigger_pending(
        repo,
        slice_id=slice_id,
        plan_path=plan_path,
        starter_rel=starter,
        reason=reason,
        source=source,
    )
    starter_path = repo / starter.replace("/", os.sep)
    starter_content = ""
    if starter_path.is_file():
        try:
            starter_content = starter_path.read_text(encoding="utf-8")
        except OSError:
            pass

    webhook_payload = {
        "event": "ppe_ide_build_handoff",
        "sliceId": slice_id,
        "planPath": plan_path,
        "starter": starter,
        "starterContent": starter_content,
        "reason": reason,
        "handoffAt": _utc_now(),
        "triggerFile": TRIGGER_REL,
    }
    webhook = post_automation_webhook(repo, webhook_payload)
    result: dict[str, Any] = {
        "ok": True,
        "trigger": str(trigger_file.relative_to(repo)).replace("\\", "/"),
        "webhook": webhook,
    }
    if not webhook.get("ok") and not webhook.get("skipped"):
        try:
            from scripts.ppe_ide_build_automation_health import write_last_error

            err_path = write_last_error(repo, context="handoff_webhook", failure=webhook)
            result["last_error"] = str(err_path.relative_to(repo)).replace("\\", "/")
        except ImportError:
            pass
    return result
