"""Uptime gap alerts when loop is off without maintenance (24/7 target)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

GAP_STATE_REL = "artifacts/control_plane/UPTIME_GAP_ALERT_STATE.json"
_DEFAULT_GAP_MINUTES = 45


def gap_alert_minutes() -> int:
    raw = os.environ.get("PPE_NTFY_GAP_ALERT_MIN", str(_DEFAULT_GAP_MINUTES)).strip()
    try:
        return max(15, int(raw))
    except ValueError:
        return _DEFAULT_GAP_MINUTES


def gap_alert_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_GAP_ALERT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def state_path(repo: Path) -> Path:
    return repo / GAP_STATE_REL


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


def maybe_send_gap_alert(
    repo: Path,
    *,
    loop_running: bool,
    verdict: str,
    prior: dict[str, Any],
) -> dict[str, Any]:
    """Alert once when loop has been down (non-maintenance) longer than threshold."""
    repo = repo.resolve()
    if not gap_alert_enabled() or not notify_enabled() or not ntfy_configured():
        return {"sent": False, "reason": "disabled"}

    from scripts.ppe_operator_maintenance import is_maintenance_active

    state = load_state(repo)
    down_since_raw = str(state.get("loopDownSince") or "")
    down_since = _parse_utc(down_since_raw)
    last_alert = _parse_utc(str(state.get("lastGapAlertAt") or ""))

    if loop_running:
        if down_since_raw:
            save_state(repo, {"loopDownSince": None, "lastGapAlertAt": state.get("lastGapAlertAt")})
        return {"sent": False, "reason": "loop_up"}

    if is_maintenance_active(repo):
        save_state(repo, {"loopDownSince": None, "lastGapAlertAt": state.get("lastGapAlertAt")})
        return {"sent": False, "reason": "maintenance"}

    now = _utc_now()
    if down_since is None:
        save_state(repo, {"loopDownSince": now.replace(microsecond=0).isoformat().replace("+00:00", "Z")})
        return {"sent": False, "reason": "gap_started"}

    elapsed_min = (now - down_since).total_seconds() / 60.0
    threshold = gap_alert_minutes()
    if elapsed_min < threshold:
        return {"sent": False, "reason": "below_threshold", "elapsed_min": int(elapsed_min)}

    if last_alert and (now - last_alert).total_seconds() < threshold * 60:
        return {"sent": False, "reason": "cooldown"}

    mins = int(elapsed_min)
    title = f"PPE: loop down {mins}m (24/7 gap)"
    body = (
        f"Auto-loop has been off ~{mins} minutes without maintenance mode.\n"
        f"Verdict: {verdict}. Run restart from phone or run_ppe_auto_local_loop.cmd.\n"
        "If you are working at the desk: maintenance on (counts as intentional downtime)."
    )
    sent = send_ntfy(title, body, tags=["ppe", "watch", "gap"], priority="high", bypass_throttle=True)
    if sent:
        save_state(
            repo,
            {
                "loopDownSince": down_since_raw,
                "lastGapAlertAt": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            },
        )
    return {"sent": sent, "elapsed_min": mins}
