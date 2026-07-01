"""Parse gh auth status for token expiry hints (not relay)."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from typing import Any

_EXPIRE_RE = re.compile(
    r"(?:expires?|expir(?:y|ation)|valid until)\s*[:\s]*(.+)",
    re.IGNORECASE,
)
_INVALID_RE = re.compile(r"(invalid|expired|revoked|not logged in)", re.IGNORECASE)


def _parse_expiry_text(text: str) -> datetime | None:
    raw = (text or "").strip()
    if not raw:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            dt = datetime.strptime(raw.replace(" UTC", "").strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue
    return None


def assess_gh_auth_expiry() -> dict[str, Any]:
    """Return gh auth health including optional expiry datetime."""
    try:
        proc = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc), "needs_reauth": True}

    combined = f"{proc.stdout or ''}\n{proc.stderr or ''}"
    if proc.returncode != 0 or _INVALID_RE.search(combined):
        return {
            "ok": False,
            "needs_reauth": True,
            "detail": combined.strip()[:200],
        }

    expires_at: datetime | None = None
    for line in combined.splitlines():
        match = _EXPIRE_RE.search(line)
        if match:
            expires_at = _parse_expiry_text(match.group(1))
            if expires_at:
                break

    days_left: int | None = None
    warn = False
    if expires_at is not None:
        days_left = int((expires_at - datetime.now(timezone.utc)).total_seconds() // 86400)
        warn = days_left <= 7

    return {
        "ok": True,
        "needs_reauth": False,
        "expires_at": expires_at.isoformat().replace("+00:00", "Z") if expires_at else None,
        "days_left": days_left,
        "warn_expiry": warn,
    }


def format_gh_expiry_line(payload: dict[str, Any]) -> str | None:
    if not payload.get("ok"):
        return "GitHub: re-auth needed (gh auth login)"
    if payload.get("warn_expiry") and payload.get("days_left") is not None:
        return f"GitHub token expires in {payload['days_left']}d — run gh auth login"
    if payload.get("expires_at"):
        return f"GitHub token expires {payload['expires_at'][:10]}"
    return None
