"""Explicit operator maintenance mode (intentional loop downtime)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MAINTENANCE_REL = "artifacts/control_plane/OPERATOR_MAINTENANCE.json"


def maintenance_path(repo: Path) -> Path:
    return repo / MAINTENANCE_REL


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


def maintenance_env_active() -> bool:
    raw = os.environ.get("PPE_OPERATOR_MAINTENANCE", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def load_maintenance(repo: Path | None) -> dict[str, Any]:
    if repo is None:
        return {}
    path = maintenance_path(repo.resolve())
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_maintenance(repo: Path, data: dict[str, Any]) -> None:
    path = maintenance_path(repo.resolve())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def clear_maintenance(repo: Path) -> dict[str, Any]:
    path = maintenance_path(repo.resolve())
    if path.is_file():
        path.unlink(missing_ok=True)
    return {"active": False}


def is_maintenance_active(repo: Path | None = None, at: datetime | None = None) -> bool:
    """True when operator marked maintenance (desktop work, other jobs on PC)."""
    if maintenance_env_active():
        return True
    if repo is None:
        return False
    data = load_maintenance(repo)
    if not data.get("active"):
        return False
    since = _parse_utc(str(data.get("since") or ""))
    if since is not None and at is not None and at < since:
        return False
    return True


def _flush_metrics_sample(repo: Path) -> None:
    try:
        from scripts.ppe_desktop_operator_stack import is_loop_running
        from scripts.ppe_operator_daily_metrics import record_watch_sample
        from scripts.ppe_operator_status import collect_operator_status

        status = collect_operator_status(repo)
        record_watch_sample(
            repo,
            loop_running=is_loop_running(),
            verdict=str(status.get("verdict") or ""),
        )
    except Exception:
        pass


def set_maintenance(
    repo: Path,
    active: bool,
    *,
    reason: str = "",
    set_by: str = "operator",
) -> dict[str, Any]:
    repo = repo.resolve()
    _flush_metrics_sample(repo)
    if not active:
        clear_maintenance(repo)
        return {"active": False, "setBy": set_by}

    payload = {
        "active": True,
        "since": _utc_now().replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "reason": str(reason or "manual desktop work").strip()[:200],
        "setBy": set_by,
    }
    save_maintenance(repo, payload)
    return payload


def maintenance_summary(repo: Path | None) -> str | None:
    if maintenance_env_active():
        return "env PPE_OPERATOR_MAINTENANCE=1"
    if repo is None:
        return None
    data = load_maintenance(repo)
    if not data.get("active"):
        return None
    reason = str(data.get("reason") or "manual desktop work").strip()
    return reason
