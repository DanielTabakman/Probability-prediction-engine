"""8am local digest of the last 24h of operator / ntfy activity."""

from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import (
    _load_send_state,
    _parse_utc,
    _prune_send_state,
    categorize_send_title,
    ntfy_configured,
    notify_enabled,
    send_ntfy,
    summarize_sends,
)
from scripts.ppe_phone_status import verdict_headline

MORNING_STATE_REL = "artifacts/control_plane/MORNING_REPORT_STATE.json"
_CATEGORY_LABELS = {
    "ide_build": "IDE BUILD / handoff",
    "verdict": "verdict changes",
    "stuck": "stuck reminders",
    "critical": "loop down",
    "build": "build finish",
    "chapter": "chapter done",
    "slice": "slice done",
    "fix": "fix attempts",
    "status": "status checks",
    "other": "other",
}


def morning_report_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_MORNING_REPORT", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _parse_report_clock(value: str) -> time:
    parts = (value or "08:00").strip().split(":")
    if len(parts) != 2:
        return time(8, 0)
    try:
        return time(int(parts[0]), int(parts[1]))
    except ValueError:
        return time(8, 0)


def morning_report_time() -> time:
    return _parse_report_clock(os.environ.get("PPE_NTFY_MORNING_REPORT_AT", "08:00"))


def morning_report_window_minutes() -> int:
    raw = os.environ.get("PPE_NTFY_MORNING_REPORT_WINDOW_MIN", "45").strip()
    try:
        return max(15, int(raw))
    except ValueError:
        return 45


def state_path(repo: Path) -> Path:
    return repo / MORNING_STATE_REL


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


def _local_today() -> str:
    return datetime.now().astimezone().date().isoformat()


def is_morning_report_window(now: datetime | None = None) -> bool:
    now = now or datetime.now().astimezone()
    target = morning_report_time()
    start = datetime.combine(now.date(), target, tzinfo=now.tzinfo)
    end = start + timedelta(minutes=morning_report_window_minutes())
    return start <= now < end


def _format_local_time(at_raw: str) -> str:
    at = _parse_utc(at_raw)
    if at is None:
        return at_raw
    return at.astimezone().strftime("%m-%d %H:%M")


def build_morning_report(repo: Path, status: dict[str, Any]) -> tuple[str, str]:
    sends = _prune_send_state(_load_send_state(repo))
    activity = [s for s in sends if "morning" not in str(s.get("title") or "").lower()]
    breakdown = summarize_sends(activity)

    lines = ["Good morning. Here's the last 24 hours:", ""]
    verdict = str(status.get("verdict") or "UNKNOWN")
    lines.append(f"Now: {verdict_headline(verdict)}")
    chapter = str(status.get("chapter_name") or "").strip()
    if chapter:
        lines.append(f"Chapter: {chapter}")
    blocker = str(status.get("blocker") or "").strip()
    if blocker and verdict not in ("RUN_AUTO", "RUN_LOCAL"):
        lines.append(blocker[:200])

    lines.append("")
    lines.append("Alerts sent:")
    if not activity:
        lines.append("- None (quiet day).")
    else:
        for cat, count in breakdown.items():
            if cat == "quota":
                continue
            label = _CATEGORY_LABELS.get(cat, cat.replace("_", " "))
            lines.append(f"- {count}x {label}")
        lines.append("")
        lines.append("Highlights:")
        notable = [
            s
            for s in activity
            if str(s.get("category") or categorize_send_title(str(s.get("title") or "")))
            in ("ide_build", "verdict", "critical", "stuck", "chapter", "build", "fix")
        ]
        if not notable:
            notable = activity[-5:]
        for item in notable[-6:]:
            title = str(item.get("title") or "").strip()
            when = _format_local_time(str(item.get("at") or ""))
            if title:
                lines.append(f"- {when}: {title[:100]}")

    lines.append("")
    health_line = str(status.get("operator_health_line") or "").strip()
    if not health_line:
        try:
            from scripts.ppe_operator_blind_spots import HEALTH_REL

            path = repo / HEALTH_REL
            if path.is_file():
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    health_line = str(data.get("line") or "").strip()
        except Exception:
            pass
    if health_line:
        lines.append(f"Infra: {health_line}")

    try:
        from scripts.ppe_gh_auth_expiry import assess_gh_auth_expiry, format_gh_expiry_line

        gh_line = format_gh_expiry_line(assess_gh_auth_expiry())
        if gh_line:
            lines.append(gh_line)
    except Exception:
        pass

    lines.append("")
    lines.append("Send status for the live picture.")
    return "PPE morning report", "\n".join(lines)


def maybe_send_morning_report(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    repo = repo.resolve()
    if not notify_enabled() or not ntfy_configured() or not morning_report_enabled():
        return {"sent": False, "reason": "disabled"}
    if not is_morning_report_window():
        return {"sent": False, "reason": "outside_window"}

    prior = load_state(repo)
    today = _local_today()
    if str(prior.get("last_morning_report_date") or "") == today:
        return {"sent": False, "reason": "already_sent_today"}

    title, body = build_morning_report(repo, status)
    sent = send_ntfy(
        title,
        body,
        tags=["ppe", "morning", "digest"],
        priority="default",
        bypass_throttle=True,
    )
    if sent:
        save_state(repo, {"last_morning_report_date": today, "sent_at": datetime.now(timezone.utc).isoformat()})
    return {"sent": sent, "title": title, "body": body}
