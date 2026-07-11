"""Runtime VM phase state + in-flight notifications (loop host only).

Live operator state belongs in the gitignored artifacts plane. This module no
longer stages, commits, pushes, or opens PRs for phase/heartbeat changes.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VM_OPERATOR_PHASE_REL = "artifacts/control_plane/VM_OPERATOR_PHASE.json"
LEGACY_VM_OPERATOR_PHASE_REL = "docs/SOP/VM_OPERATOR_PHASE.json"
PHASE_NOTIFY_STATE_REL = "artifacts/control_plane/VM_PHASE_NOTIFY_STATE.json"
IN_FLIGHT_SINCE_REL = "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json"
STUCK_NOTIFY_STATE_REL = "artifacts/control_plane/VM_IN_FLIGHT_STUCK_NOTIFY.json"
MIRROR_PUBLISH_STATE_REL = "artifacts/control_plane/VM_MIRROR_PUBLISH_STATE.json"

IN_FLIGHT_PHASES = frozenset({"FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"})
PHASE_NOTIFY_COOLDOWN_SECONDS = 900
BUILD_IN_FLIGHT_STUCK_SECONDS = 2700
FINISH_IN_FLIGHT_STUCK_SECONDS = 5400
IN_FLIGHT_STUCK_SECONDS = BUILD_IN_FLIGHT_STUCK_SECONDS
IN_FLIGHT_APPROACHING_SECONDS_BY_PHASE: dict[str, int] = {
    "BUILD_IN_FLIGHT": 1800,
    "FINISH_IN_FLIGHT": 3600,
}
MIRROR_PUBLISH_COOLDOWN_SECONDS = 90
MIRROR_HEARTBEAT_PUBLISH_SECONDS = 600


def stuck_threshold_seconds(phase: str) -> float:
    if phase == "FINISH_IN_FLIGHT":
        return float(FINISH_IN_FLIGHT_STUCK_SECONDS)
    if phase == "BUILD_IN_FLIGHT":
        return float(BUILD_IN_FLIGHT_STUCK_SECONDS)
    return float(IN_FLIGHT_STUCK_SECONDS)


def approaching_threshold_seconds(phase: str) -> float:
    return float(IN_FLIGHT_APPROACHING_SECONDS_BY_PHASE.get(phase, 1800))


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mirror_path(repo: Path) -> Path:
    return (repo / VM_OPERATOR_PHASE_REL).resolve()


def legacy_mirror_path(repo: Path) -> Path:
    return (repo / LEGACY_VM_OPERATOR_PHASE_REL).resolve()


def notify_state_path(repo: Path) -> Path:
    return (repo / PHASE_NOTIFY_STATE_REL).resolve()


def in_flight_since_path(repo: Path) -> Path:
    return (repo / IN_FLIGHT_SINCE_REL).resolve()


def stuck_notify_state_path(repo: Path) -> Path:
    return (repo / STUCK_NOTIFY_STATE_REL).resolve()


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def load_vm_phase_mirror(repo: Path) -> dict[str, Any] | None:
    """Read runtime state first; legacy tracked state is read-only fallback."""
    return _read_json(mirror_path(repo)) or _read_json(legacy_mirror_path(repo))


def _is_loop_host(repo: Path) -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return False


def _mirror_fingerprint(payload: dict[str, Any]) -> str:
    return "|".join(
        [
            str(payload.get("phase") or ""),
            str(payload.get("verdict") or ""),
            str(payload.get("chapter_name") or ""),
            str(payload.get("phase_plan_path") or ""),
            str(payload.get("recommended_action") or ""),
        ]
    )


def write_vm_phase_mirror(repo: Path, status: dict[str, Any]) -> Path | None:
    if not _is_loop_host(repo):
        return None
    phase = str(status.get("phase") or "").strip()
    if not phase:
        return None
    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    payload = {
        "version": 2,
        "description": "Runtime VM autobuilder state. Gitignored; SSH/status is authoritative.",
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


def _heartbeat_publish_due(
    payload: dict[str, Any],
    prior: dict[str, Any],
    *,
    fingerprint: str,
) -> bool:
    """Compatibility helper: runtime heartbeats are never Git publication events."""
    del payload, prior, fingerprint
    return False


def maybe_commit_publish_vm_mirror(repo: Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Compatibility shim. Runtime state must never enter Git history."""
    del repo, payload
    return {"skipped": True, "reason": "runtime_state_not_publishable"}


def _load_notify_state(repo: Path) -> dict[str, Any]:
    return _read_json(notify_state_path(repo)) or {}


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

        sent = send_ntfy(title=title, body=body, priority="low", tags=["hourglass_flowing_sand"])
    except Exception:
        return False
    if sent is False:
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


def _load_in_flight_since(repo: Path) -> dict[str, Any]:
    return _read_json(in_flight_since_path(repo)) or {}


def _save_in_flight_since(repo: Path, state: dict[str, Any]) -> None:
    path = in_flight_since_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def track_in_flight_since(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_loop_host(repo):
        return None
    phase = str(status.get("phase") or "").strip()
    prior = _load_in_flight_since(repo)
    if phase in IN_FLIGHT_PHASES:
        if str(prior.get("phase") or "") != phase:
            state = {
                "phase": phase,
                "since": _utc_now(),
                "verdict": str(status.get("verdict") or ""),
                "chapter_name": (status.get("operator") or {}).get("chapter_name"),
            }
            _save_in_flight_since(repo, state)
            return state
        return prior
    if prior:
        _save_in_flight_since(repo, {})
    return None


def maybe_notify_stuck_in_flight(
    repo: Path,
    status: dict[str, Any],
    *,
    stuck_seconds: int | None = None,
) -> bool:
    if not _is_loop_host(repo):
        return False
    phase = str(status.get("phase") or "").strip()
    if phase not in IN_FLIGHT_PHASES:
        return False
    threshold = int(stuck_seconds) if stuck_seconds is not None else int(stuck_threshold_seconds(phase))
    since_state = _load_in_flight_since(repo)
    since_at = _parse_utc(str(since_state.get("since") or ""))
    if since_at is None:
        return False
    elapsed = (datetime.now(timezone.utc) - since_at).total_seconds()
    if elapsed < max(300, threshold):
        return False

    operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
    chapter = str(operator.get("chapter_name") or operator.get("phase_plan_path") or "relay").strip()
    fingerprint = f"stuck|{phase}|{chapter}"
    stuck_path = stuck_notify_state_path(repo)
    prior = _read_json(stuck_path) or {}
    if fingerprint == str(prior.get("fingerprint") or ""):
        return False

    mins = int(elapsed // 60)
    title = f"PPE stuck: {phase.replace('_', ' ').title()}"
    body = (
        f"{chapter} — in-flight {mins}m. VM: POST_BUILD_FINISH.log / fix_vm_operator.cmd. "
        "Desktop: Remote-SSH ppe-vm or one status SSH."
    )
    try:
        from scripts.ppe_notify_push import ntfy_topic_stuck, send_ntfy_to_topic

        sent = send_ntfy_to_topic(
            ntfy_topic_stuck(),
            title=title,
            body=body,
            priority="high",
            tags=["warning", "rotating_light", "stuck"],
        )
    except Exception:
        return False
    if sent is False:
        return False

    stuck_path.parent.mkdir(parents=True, exist_ok=True)
    stuck_path.write_text(
        json.dumps(
            {
                "fingerprint": fingerprint,
                "last_notified_at": _utc_now(),
                "elapsed_seconds": elapsed,
                "phase": phase,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True


def sync_autobuilder_phase_artifacts(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    mirror = write_vm_phase_mirror(repo, status)
    publish = {"skipped": True, "reason": "runtime_state_not_publishable"}
    notified = maybe_notify_in_flight_phase(repo, status)
    track_in_flight_since(repo, status)
    stuck_notified = maybe_notify_stuck_in_flight(repo, status)
    auto_advance: dict[str, Any] = {"skipped": True}
    try:
        from scripts.ppe_factory_throughput import assess_factory_throughput, maybe_auto_advance_stuck

        operator = status.get("operator") if isinstance(status.get("operator"), dict) else {}
        light_status = {
            "verdict": status.get("verdict") or operator.get("verdict"),
            "phase_plan_path": operator.get("phase_plan_path"),
            "chapter_name": operator.get("chapter_name"),
            "supply": operator.get("supply") or {},
        }
        auto_advance = maybe_auto_advance_stuck(repo, assess_factory_throughput(repo, light_status))
    except Exception:
        pass
    return {
        "mirror_path": str(mirror) if mirror else None,
        "publish": publish,
        "notified": notified,
        "stuck_notified": stuck_notified,
        "auto_advance": auto_advance,
    }
