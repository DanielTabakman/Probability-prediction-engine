"""Active IDE slice checkout lock — one in-flight IDE BUILD at a time."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ACTIVE_SLICE_REL = "artifacts/orchestrator/ACTIVE_IDE_SLICE.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def active_slice_path(repo: Path) -> Path:
    return (repo / ACTIVE_SLICE_REL).resolve()


def load_active_slice(repo: Path) -> dict[str, Any] | None:
    p = active_slice_path(repo)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def write_active_slice(
    repo: Path,
    *,
    slice_id: str,
    phase_plan_path: str,
    starter_path: str,
    owner: str = "IDE",
) -> Path:
    p = active_slice_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "sliceId": slice_id.strip(),
        "phasePlanPath": phase_plan_path.replace("\\", "/").strip(),
        "starterPath": starter_path.replace("\\", "/").strip(),
        "owner": owner.strip() or "IDE",
        "checkedOutAt": _utc_now(),
    }
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def clear_active_slice(repo: Path) -> bool:
    p = active_slice_path(repo)
    if p.is_file():
        p.unlink()
        return True
    return False


def active_slice_stale_hours() -> float:
    import os

    raw = os.environ.get("PPE_ACTIVE_SLICE_STALE_HOURS", "24").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 24.0


def is_active_slice_stale(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    hours = active_slice_stale_hours()
    if hours <= 0:
        return False
    checked = str(data.get("checkedOutAt") or "").strip()
    if not checked:
        return False
    try:
        if checked.endswith("Z"):
            checked = checked[:-1] + "+00:00"
        from datetime import datetime, timezone

        then = datetime.fromisoformat(checked)
        if then.tzinfo is None:
            then = then.replace(tzinfo=timezone.utc)
        age_h = (datetime.now(timezone.utc) - then).total_seconds() / 3600.0
        return age_h >= hours
    except ValueError:
        return False
