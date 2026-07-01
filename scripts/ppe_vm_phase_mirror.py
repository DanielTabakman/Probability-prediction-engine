"""Git-tracked VM phase mirror + FINISH_IN_FLIGHT ntfy heartbeat (loop host only)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VM_OPERATOR_PHASE_REL = "docs/SOP/VM_OPERATOR_PHASE.json"
PHASE_NOTIFY_STATE_REL = "artifacts/control_plane/VM_PHASE_NOTIFY_STATE.json"

IN_FLIGHT_PHASES = frozenset({"FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"})
PHASE_NOTIFY_COOLDOWN_SECONDS = 900


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mirror_path(repo: Path) -> Path:
    return (repo / VM_OPERATOR_PHASE_REL).resolve()


def notify_state_path(repo: Path) -> Path:
    return (repo / PHASE_NOTIFY_STATE_REL).resolve()


def load_vm_phase_mirror(repo: Path) -> dict[str, Any] | None:
    path = mirror_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _is_loop_host(repo: Path) -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return False


def write_vm_phase_mirror(repo: Path, status: dict[str, Any]) -> Path | None:
    """Loop host: persist phase/verdict for desktop git pull (no SSH needed)."""
    if not _is_loop_host(repo):
        return None
    phase = str(status.get("phase") or "").strip()
    if not phase:
        return None
    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    payload = {
        "as_of": str(status.get("as_of") or _utc_now()),
        "phase": phase,
        "verdict": str(status.get("verdict") or "").strip(),
        "chapter_name": operator.get("chapter_name"),
        "phase_plan_path": operator.get("phase_plan_path"),
        "recommended_action": status.get("recommended_action"),
    }
    path = mirror_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _load_notify_state(repo: Path) -> dict[str, Any]:
    path = notify_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _save_notify_state(repo: Path, state: dict[str, Any]) -> None:
    path = notify_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def maybe_notify_in_flight_phase(repo: Path, status: dict[str, Any]) -> bool:
    """Loop host: ntfy once per in-flight phase/chapter (deduped). Returns True if sent."""
    if not _is_loop_host(repo):
        return False
    phase = str(status.get("phase") or "").strip()
    if phase not in IN_FLIGHT_PHASES:
        return False

    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    chapter = str(operator.get("chapter_name") or operator.get("phase_plan_path") or "relay").strip()
    fingerprint = f"{phase}|{chapter}|{status.get('verdict')}"
    prior = _load_notify_state(repo)
    if fingerprint == str(prior.get("fingerprint") or ""):
        last_at = _parse_utc(str(prior.get("last_notified_at") or ""))
        if last_at is not None:
            elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
            if elapsed < PHASE_NOTIFY_COOLDOWN_SECONDS:
                return False

    title = f"PPE {phase.replace('_', ' ').title()}"
    body = f"{chapter} — VM loop running; desktop: wait or DESKTOP_CONTINUE when due."
    try:
        from scripts.ppe_notify_push import send_ntfy

        send_ntfy(title=title, body=body, priority="low", tags=["hourglass_flowing_sand"])
    except Exception:
        return False

    _save_notify_state(
        repo,
        {
            "fingerprint": fingerprint,
            "last_notified_at": _utc_now(),
            "phase": phase,
            "chapter": chapter,
        },
    )
    return True


def sync_autobuilder_phase_artifacts(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    """Write git mirror + optional ntfy when autobuilder status changes on loop host."""
    mirror = write_vm_phase_mirror(repo, status)
    notified = maybe_notify_in_flight_phase(repo, status)
    return {"mirror_path": str(mirror) if mirror else None, "notified": notified}
