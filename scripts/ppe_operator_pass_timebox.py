"""Operator thread session timebox — recommend rotate after long inaction."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSION_REL = "artifacts/control_plane/OPERATOR_SESSION.json"
TIMEBOX_SECONDS = 600


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


def session_path(repo: Path) -> Path:
    return (repo / SESSION_REL).resolve()


def _session_fingerprint(status: dict[str, Any]) -> str:
    verdict = str(status.get("verdict") or "")
    plan = str(status.get("phase_plan_path") or "")
    mode = ""
    chapter_mode = status.get("chapter_mode")
    if isinstance(chapter_mode, dict):
        mode = str(chapter_mode.get("mode") or "")
    return f"{verdict}|{plan}|{mode}"


def record_operator_session(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    """Track operator session age; recommend thread rotate after TIMEBOX_SECONDS."""
    repo = repo.resolve()
    fp = _session_fingerprint(status)
    path = session_path(repo)
    prior: dict[str, Any] = {}
    if path.is_file():
        try:
            prior = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}

    now = _utc_now()
    if fp != str(prior.get("fingerprint") or ""):
        state = {"fingerprint": fp, "started_at": now, "verdict": status.get("verdict")}
    else:
        state = {**prior, "last_seen_at": now}

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    started = _parse_utc(str(state.get("started_at") or now))
    elapsed = 0.0
    if started is not None:
        elapsed = max(0.0, (datetime.now(timezone.utc) - started).total_seconds())

    rotate = elapsed >= TIMEBOX_SECONDS
    return {
        "elapsed_seconds": int(elapsed),
        "rotate_recommended": rotate,
        "timebox_seconds": TIMEBOX_SECONDS,
        "message": (
            f"Operator session on same verdict/mode for {int(elapsed // 60)}m — rotate thread if stuck."
            if rotate
            else ""
        ),
    }
