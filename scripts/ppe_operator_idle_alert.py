"""Alert when the loop is up but no operator progress for too long (unplanned downtime)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy
from scripts.ppe_operator_status import (
    VERDICT_ERROR,
    VERDICT_FIX_PLAN,
    VERDICT_IDE_BUILD,
    VERDICT_RUN_LOCAL,
    VERDICT_STALE_STATE,
    VERDICT_SUPPLY_LOW,
)

STATE_REL = "artifacts/control_plane/OPERATOR_IDLE_STATE.json"
_DEFAULT_IDLE_MINUTES = 20

IDLE_VERDICTS = frozenset(
    {
        VERDICT_RUN_LOCAL,
        VERDICT_IDE_BUILD,
        VERDICT_SUPPLY_LOW,
        VERDICT_FIX_PLAN,
        VERDICT_STALE_STATE,
        VERDICT_ERROR,
    }
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


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


def idle_alert_minutes(repo: Path | None = None) -> int:
    env = os.environ.get("PPE_NTFY_IDLE_ALERT_MIN", "").strip()
    if env:
        try:
            return max(5, int(env))
        except ValueError:
            pass
    if repo is not None:
        try:
            from scripts.ppe_operator_config import load_operator_config

            cfg = load_operator_config(repo)
            raw = cfg.get("idleAlertMinutes")
            if raw is not None:
                return max(5, int(raw))
        except (ImportError, TypeError, ValueError):
            pass
    return _DEFAULT_IDLE_MINUTES


def idle_alert_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_IDLE_ALERT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def state_path(repo: Path) -> Path:
    return repo / STATE_REL


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def record_progress(repo: Path, *, reason: str = "") -> None:
    """Mark that work is in flight — resets idle timer."""
    repo = repo.resolve()
    state = load_state(repo)
    now = _utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z")
    save_state(
        repo,
        {
            **state,
            "lastProgressAt": now,
            "lastProgressReason": reason or None,
            "idleSince": None,
        },
    )


def _worker_in_flight(repo: Path) -> bool:
    try:
        from scripts.ppe_auto_run_local import run_local_worker_running

        if run_local_worker_running(repo):
            return True
    except ImportError:
        pass
    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        if read_build_lock(repo):
            return True
    except ImportError:
        pass
    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    return active.is_file()


def maybe_send_idle_alert(
    repo: Path,
    *,
    loop_running: bool,
    verdict: str,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Alert when loop is up but no progress beyond idleAlertMinutes."""
    repo = repo.resolve()
    if not idle_alert_enabled() or not notify_enabled() or not ntfy_configured():
        return {"sent": False, "reason": "disabled"}

    try:
        from scripts.ppe_operator_maintenance import is_maintenance_active

        if is_maintenance_active(repo):
            save_state(repo, {**load_state(repo), "idleSince": None})
            return {"sent": False, "reason": "maintenance"}
    except ImportError:
        pass

    if not loop_running:
        save_state(repo, {**load_state(repo), "idleSince": None})
        return {"sent": False, "reason": "loop_down"}

    if _worker_in_flight(repo):
        record_progress(repo, reason="worker_in_flight")
        return {"sent": False, "reason": "worker_active"}

    if verdict not in IDLE_VERDICTS:
        record_progress(repo, reason=f"verdict_{verdict}")
        return {"sent": False, "reason": "not_idle_verdict"}

    state = load_state(repo)
    now = _utc_now()
    idle_since = _parse_utc(str(state.get("idleSince") or ""))
    last_alert = _parse_utc(str(state.get("lastIdleAlertAt") or ""))
    threshold_min = idle_alert_minutes(repo)

    if idle_since is None:
        save_state(
            repo,
            {
                **state,
                "idleSince": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "idleVerdict": verdict,
            },
        )
        return {"sent": False, "reason": "idle_started", "verdict": verdict}

    elapsed_min = (now - idle_since).total_seconds() / 60.0
    if elapsed_min < threshold_min:
        return {"sent": False, "reason": "below_threshold", "elapsed_min": int(elapsed_min)}

    if last_alert and (now - last_alert).total_seconds() < threshold_min * 60:
        return {"sent": False, "reason": "cooldown"}

    blocker = ""
    if status:
        blocker = str(status.get("blocker") or "").strip()
    mins = int(elapsed_min)
    title = f"PPE: idle {mins}m — {verdict}"
    body_lines = [
        f"Loop is running but no progress for ~{mins} minutes.",
        f"Verdict: {verdict}.",
    ]
    if blocker:
        body_lines.append(blocker[:240])
    body_lines.append(
        "Send build/fix from phone or check desktop. Use maintenance mode for intentional downtime."
    )
    sent = send_ntfy(
        title,
        "\n".join(body_lines),
        tags=["ppe", "watch", "idle"],
        priority="high",
        bypass_throttle=True,
    )
    if sent:
        save_state(
            repo,
            {
                **state,
                "idleSince": state.get("idleSince"),
                "idleVerdict": verdict,
                "lastIdleAlertAt": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            },
        )
    return {"sent": sent, "elapsed_min": mins, "verdict": verdict}
