"""Dedup guard-stop operator notifications (beep + ntfy) within a cooldown window."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_REL = "artifacts/control_plane/GUARD_NOTIFY_STATE.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


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


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


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


def notify_fingerprint(status: dict[str, Any]) -> str:
    verdict = str(status.get("verdict") or "").strip()
    blocker = str(status.get("blocker") or "").strip()
    plan = str(status.get("phase_plan_path") or "").strip()
    return f"{verdict}|{blocker}|{plan}"


def cooldown_seconds(repo: Path) -> int:
    try:
        from scripts.ppe_operator_config import guard_stop_sleep_seconds

        return max(60, guard_stop_sleep_seconds(repo))
    except Exception:
        return 300


def should_skip_guard_notify(repo: Path, status: dict[str, Any]) -> bool:
    """True when the same guard-stop was already notified inside the cooldown window."""
    prior = load_state(repo)
    fp = notify_fingerprint(status)
    if fp != str(prior.get("fingerprint") or ""):
        return False
    last_at = _parse_utc(str(prior.get("last_notified_at") or ""))
    if last_at is None:
        return False
    elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
    return elapsed < cooldown_seconds(repo)


def record_guard_notify(repo: Path, status: dict[str, Any]) -> None:
    save_state(
        repo,
        {
            "as_of": _utc_now(),
            "fingerprint": notify_fingerprint(status),
            "verdict": status.get("verdict"),
            "last_notified_at": _utc_now(),
        },
    )
