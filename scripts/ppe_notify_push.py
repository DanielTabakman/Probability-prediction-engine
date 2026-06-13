"""Mobile push notifications (ntfy) for PPE operator alerts."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

DEFAULT_NTFY_SERVER = "https://ntfy.sh"
SNOOZE_REL = "artifacts/control_plane/NTFY_SNOOZE.json"
QUIET_ALERT_REL = "artifacts/control_plane/NTFY_QUIET_ALERT_STATE.json"
SEND_STATE_REL = "artifacts/control_plane/NTFY_SEND_STATE.json"
STEWARD_SEND_STATE_REL = "artifacts/control_plane/STEWARD_NTFY_SEND_STATE.json"
QUOTA_STATUS_REL = "artifacts/control_plane/NTFY_QUOTA_STATUS.json"
OUTBOUND_TAG = "from-desktop"
DEFAULT_DAILY_CAP = 40
DEFAULT_STEWARD_DAILY_CAP = 4
DEFAULT_DEDUP_MINUTES = 45.0
DEFAULT_MIN_INTERVAL_SEC = 120.0
DEFAULT_WARN_PCT = 80
SEND_WINDOW = timedelta(hours=24)
PRIORITY_BY_VERDICT = {
    "ERROR": "urgent",
    "IDE_BUILD": "high",
    "FIX_PLAN": "high",
    "STALE_STATE": "high",
    "RUN_LOCAL": "default",
    "SUPPLY_LOW": "low",
}


def notify_enabled() -> bool:
    value = os.environ.get("PPE_NOTIFY", "").strip().lower()
    return value not in ("0", "false")


def ntfy_topic() -> str:
    return os.environ.get("PPE_NTFY_TOPIC", "").strip()


def ntfy_server() -> str:
    raw = os.environ.get("PPE_NTFY_SERVER", DEFAULT_NTFY_SERVER).strip()
    return raw.rstrip("/") if raw else DEFAULT_NTFY_SERVER


def ntfy_configured() -> bool:
    return bool(ntfy_topic())


def steward_ntfy_topic() -> str:
    return os.environ.get("PPE_NTFY_STEWARD_TOPIC", "").strip()


def steward_ntfy_configured() -> bool:
    return bool(steward_ntfy_topic())


def repo_root() -> Path:
    raw = os.environ.get("PPE_REPO_ROOT", "").strip()
    return Path(raw) if raw else Path.cwd()


def bootstrap_operator_notify_env(repo: Path | None = None) -> None:
    """Load PPE_* vars from local cmd wrappers when Python was not started via .cmd."""
    root = (repo or repo_root()).resolve()
    for name in ("ppe_operator_local.cmd", "ppe_operator_notify.local.cmd"):
        path = root / name
        if not path.is_file():
            continue
        try:
            proc = subprocess.run(
                ["cmd", "/c", f'call "{path}" && set PPE'],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        for line in (proc.stdout or "").splitlines():
            if "=" not in line or not line.startswith("PPE"):
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if key and key not in os.environ:
                os.environ[key.strip()] = value


def snooze_path(repo: Path | None = None) -> Path:
    return (repo or repo_root()).resolve() / SNOOZE_REL


def load_ntfy_snooze(repo: Path | None = None) -> dict[str, Any] | None:
    path = snooze_path(repo)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def is_ntfy_snoozed(repo: Path | None = None) -> bool:
    data = load_ntfy_snooze(repo)
    if not data:
        return False
    until_raw = str(data.get("until") or "").strip()
    if not until_raw:
        return False
    try:
        until = datetime.fromisoformat(until_raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) < until


def set_ntfy_snooze(
    *,
    hours: float | None = None,
    until: datetime | None = None,
    reason: str = "manual",
    repo: Path | None = None,
) -> dict[str, Any]:
    now = datetime.now().astimezone()
    if until is None:
        if hours is None:
            hours = 8.0
        until = now + timedelta(hours=max(0.1, hours))
    elif until.tzinfo is None:
        until = until.replace(tzinfo=now.tzinfo)
    payload = {
        "until": until.astimezone(timezone.utc).isoformat(),
        "reason": reason,
        "set_at": now.astimezone(timezone.utc).isoformat(),
    }
    path = snooze_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def clear_ntfy_snooze(repo: Path | None = None) -> bool:
    path = snooze_path(repo)
    if not path.is_file():
        return False
    try:
        path.unlink()
    except OSError:
        return False
    return True


def quiet_hours_enabled() -> bool:
    raw = os.environ.get("PPE_NTFY_QUIET_HOURS", "0").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _parse_quiet_clock(value: str, default: time) -> time:
    parts = (value or "").strip().split(":")
    if len(parts) != 2:
        return default
    try:
        return time(int(parts[0]), int(parts[1]))
    except ValueError:
        return default


def quiet_hours_window() -> tuple[time, time]:
    start = _parse_quiet_clock(os.environ.get("PPE_NTFY_QUIET_START", "01:00"), time(1, 0))
    end = _parse_quiet_clock(os.environ.get("PPE_NTFY_QUIET_END", "08:00"), time(8, 0))
    return start, end


def is_ntfy_quiet_hours(now: datetime | None = None) -> bool:
    if not quiet_hours_enabled():
        return False
    now = now or datetime.now().astimezone()
    start, end = quiet_hours_window()
    current = now.time()
    if start < end:
        return start <= current < end
    return current >= start or current < end


def quiet_hours_until_local(now: datetime | None = None) -> str:
    now = now or datetime.now().astimezone()
    _, end = quiet_hours_window()
    target = datetime.combine(now.date(), end, tzinfo=now.tzinfo)
    if target <= now:
        target += timedelta(days=1)
    return target.strftime("%H:%M")


def quiet_alert_state_path(repo: Path | None = None) -> Path:
    return (repo or repo_root()).resolve() / QUIET_ALERT_REL


def load_quiet_alert_state(repo: Path | None = None) -> dict[str, Any]:
    path = quiet_alert_state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_quiet_alert_state(repo: Path | None, state: dict[str, Any]) -> None:
    path = quiet_alert_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _local_today_iso() -> str:
    return datetime.now().astimezone().date().isoformat()


def reset_quiet_stuck_if_awake(repo: Path | None = None) -> None:
    """Clear one-shot quiet-hours stuck flag after morning."""
    if is_ntfy_quiet_hours():
        return
    state = load_quiet_alert_state(repo)
    if state.get("quiet_stuck_sent_date"):
        state = {k: v for k, v in state.items() if k != "quiet_stuck_sent_date"}
        save_quiet_alert_state(repo, state)


def quiet_stuck_allowed(repo: Path | None = None) -> bool:
    """During quiet hours: at most one stuck reminder per night."""
    reset_quiet_stuck_if_awake(repo)
    if not is_ntfy_quiet_hours():
        return True
    state = load_quiet_alert_state(repo)
    return str(state.get("quiet_stuck_sent_date") or "") != _local_today_iso()


def mark_quiet_stuck_sent(repo: Path | None = None) -> None:
    state = load_quiet_alert_state(repo)
    state["quiet_stuck_sent_date"] = _local_today_iso()
    save_quiet_alert_state(repo, state)


def _is_stuck_reminder(title: str) -> bool:
    return "still stuck" in (title or "").lower()


def _is_phone_command_reply(tags: list[str] | None) -> bool:
    return "cmd" in {str(t) for t in (tags or [])}


def is_routine_notify_muted(
    *,
    title: str = "",
    tags: list[str] | None = None,
    priority: str = "default",
) -> bool:
    """Mute routine auto-alerts during quiet hours (not phone cmds / stuck / urgent)."""
    if _is_phone_command_reply(tags):
        return False
    if _is_stuck_reminder(title):
        return False
    if priority == "urgent":
        return False
    tag_set = {str(t) for t in (tags or [])}
    if "morning" in tag_set or "morning report" in (title or "").lower():
        return False
    return is_ntfy_quiet_hours()


@dataclass(frozen=True)
class SnoozeRequest:
    mode: Literal["clear", "hours", "until"]
    hours: float = 8.0
    until: datetime | None = None


def parse_until_clock(value: str) -> datetime:
    """Next local clock time HH:MM (today or tomorrow)."""
    parts = value.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"expected HH:MM, got {value!r}")
    hour = int(parts[0])
    minute = int(parts[1])
    now = datetime.now().astimezone()
    target = datetime.combine(now.date(), time(hour, minute), tzinfo=now.tzinfo)
    if target <= now:
        target += timedelta(days=1)
    return target


def format_snooze_until(until_iso: str) -> str:
    try:
        until = datetime.fromisoformat(until_iso.replace("Z", "+00:00"))
    except ValueError:
        return until_iso
    return until.astimezone().strftime("%Y-%m-%d %H:%M %Z")


def parse_snooze_args(note: str) -> SnoozeRequest:
    """Parse phone/desktop snooze duration: 6, 6h, 30m, until 08:00, clear."""
    text = (note or "").strip().lower()
    if text in ("clear", "off", "wake", "resume"):
        return SnoozeRequest(mode="clear")
    if not text:
        return SnoozeRequest(mode="hours", hours=8.0)
    if text.startswith("until "):
        return SnoozeRequest(mode="until", until=parse_until_clock(text[6:].strip()))
    if ":" in text and " " not in text:
        return SnoozeRequest(mode="until", until=parse_until_clock(text))
    if text.endswith("m"):
        return SnoozeRequest(mode="hours", hours=max(0.1, float(text[:-1]) / 60.0))
    raw = text[:-1] if text.endswith("h") else text
    return SnoozeRequest(mode="hours", hours=max(0.1, float(raw)))


def apply_snooze_request(request: SnoozeRequest, *, reason: str, repo: Path | None = None) -> dict[str, Any] | None:
    if request.mode == "clear":
        clear_ntfy_snooze(repo)
        return None
    if request.mode == "until" and request.until is not None:
        return set_ntfy_snooze(until=request.until, reason=reason, repo=repo)
    return set_ntfy_snooze(hours=request.hours, reason=reason, repo=repo)


def _header_value(value: str) -> str:
    """ntfy headers must be latin-1; keep phone alerts ASCII-safe."""
    text = (value or "").replace("\u2014", "-").replace("\u2013", "-")
    return text.encode("ascii", "replace").decode("ascii")[:250]


def _priority_for_verdict(verdict: str | None) -> str:
    if not verdict:
        return "default"
    return PRIORITY_BY_VERDICT.get(verdict.strip().upper(), "default")


def ntfy_daily_cap() -> int:
    raw = os.environ.get("PPE_NTFY_DAILY_CAP", str(DEFAULT_DAILY_CAP)).strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_DAILY_CAP


def ntfy_warn_threshold() -> int:
    raw = os.environ.get("PPE_NTFY_WARN_PCT", str(DEFAULT_WARN_PCT)).strip()
    try:
        pct = max(50, min(100, int(raw)))
    except ValueError:
        pct = DEFAULT_WARN_PCT
    return max(1, int(ntfy_daily_cap() * pct / 100))


def ntfy_dedup_minutes() -> float:
    raw = os.environ.get("PPE_NTFY_DEDUP_MINUTES", str(DEFAULT_DEDUP_MINUTES)).strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return DEFAULT_DEDUP_MINUTES


def ntfy_min_interval_seconds() -> float:
    raw = os.environ.get("PPE_NTFY_MIN_INTERVAL_SEC", str(DEFAULT_MIN_INTERVAL_SEC)).strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return DEFAULT_MIN_INTERVAL_SEC


def send_state_path(repo: Path | None = None) -> Path:
    return (repo or repo_root()).resolve() / SEND_STATE_REL


def quota_status_path(repo: Path | None = None) -> Path:
    return (repo or repo_root()).resolve() / QUOTA_STATUS_REL


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_send_state(repo: Path | None = None) -> dict[str, Any]:
    path = send_state_path(repo)
    if not path.is_file():
        return {"sends": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"sends": []}
    return data if isinstance(data, dict) else {"sends": []}


def _save_send_state(state: dict[str, Any], repo: Path | None = None) -> None:
    path = send_state_path(repo)
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


def _message_fingerprint(title: str, tags: list[str] | None, priority: str) -> str:
    norm_title = " ".join((title or "").split()).lower()[:120]
    tag_key = ",".join(sorted(t for t in (tags or []) if t and t != OUTBOUND_TAG))
    return f"{priority}|{tag_key}|{norm_title}"


def _prune_send_state(state: dict[str, Any]) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - SEND_WINDOW
    kept: list[dict[str, Any]] = []
    for item in state.get("sends") or []:
        if not isinstance(item, dict):
            continue
        at = _parse_utc(str(item.get("at") or ""))
        if at is None:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if at >= cutoff:
            kept.append(item)
    return kept


def _heartbeat_dedup_minutes() -> float:
    raw = os.environ.get("PPE_NTFY_HEARTBEAT_DEDUP_MINUTES", "1380").strip()
    try:
        return max(60.0, float(raw))
    except ValueError:
        return 1380.0


def _is_heartbeat_message(title: str, tags: list[str] | None) -> bool:
    tag_set = {str(t) for t in (tags or [])}
    return title.startswith("PPE OK") or {"ok", "heartbeat"}.intersection(tag_set)


def categorize_send_title(title: str) -> str:
    lower = (title or "").lower()
    if "ntfy budget" in lower:
        return "quota"
    if lower.startswith("ppe ok"):
        return "heartbeat"
    if "slice done" in lower:
        return "slice"
    if "chapter done" in lower:
        return "chapter"
    if "ide build" in lower or "ide handoff" in lower or "auto-build" in lower:
        return "ide_build"
    if "loop stopped" in lower or "stack down" in lower:
        return "critical"
    if "still stuck" in lower:
        return "stuck"
    if "fixing" in lower or "fix done" in lower or lower.startswith("ppe fixed"):
        return "fix"
    if "build finished" in lower or "finish failed" in lower:
        return "build"
    if lower.startswith("ppe operator:"):
        return "verdict"
    if lower.startswith("ppe status"):
        return "status"
    if "morning report" in lower:
        return "morning"
    return "other"


def summarize_sends(sends: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for item in sends:
        title = str(item.get("title") or "")
        cat = str(item.get("category") or categorize_send_title(title))
        if cat != "quota":
            counts[cat] += 1
    return dict(counts.most_common())


def suggest_volume_cuts(breakdown: dict[str, int]) -> list[str]:
    cuts: list[str] = []
    if breakdown.get("heartbeat", 0) >= 2:
        cuts.append("PPE_NTFY_HEARTBEAT_HOURS=0 — disable OK heartbeats")
    if breakdown.get("slice", 0) >= 3:
        cuts.append("PPE_NTFY_PROGRESS=chapter — skip per-slice pings")
    if breakdown.get("fix", 0) >= 2:
        cuts.append("Skip notify_fix.cmd unless you need agent fix pings")
    if breakdown.get("stuck", 0) >= 2:
        cuts.append("PPE_NTFY_STUCK_HOURS=12 — fewer stuck reminders")
    if breakdown.get("ide_build", 0) >= 8:
        cuts.append("Fewer IDE_BUILD cycles or raise PPE_NTFY_DAILY_CAP")
    if not cuts:
        cuts.append("PPE_NTFY_PROGRESS=off — mute relay progress")
        cuts.append("PPE_NTFY_HEARTBEAT_HOURS=0 — mute OK pings")
    return cuts[:5]


def build_quota_snapshot(
    *,
    sends: list[dict[str, Any]],
    cap: int | None = None,
    skipped_title: str = "",
    skip_reason: str = "",
) -> dict[str, Any]:
    cap = cap if cap is not None else ntfy_daily_cap()
    count = len(sends)
    breakdown = summarize_sends(sends)
    return {
        "as_of": _utc_now(),
        "count": count,
        "cap": cap,
        "remaining": max(0, cap - count),
        "warn_threshold": ntfy_warn_threshold(),
        "at_cap": count >= cap,
        "skipped_last": skipped_title or None,
        "skip_reason": skip_reason or None,
        "breakdown": breakdown,
        "suggested_cuts": suggest_volume_cuts(breakdown),
    }


def write_quota_status_file(snapshot: dict[str, Any], repo: Path | None = None) -> Path:
    path = quota_status_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    return path


def format_quota_brief(repo: Path | None = None) -> str:
    state = _load_send_state(repo)
    sends = _prune_send_state(state)
    snap = build_quota_snapshot(sends=sends)
    write_quota_status_file(snap, repo)
    lines = [f"ntfy today: {snap['count']}/{snap['cap']} ({snap['remaining']} left)"]
    breakdown = snap.get("breakdown") or {}
    if breakdown:
        parts = [f"{k}={v}" for k, v in list(breakdown.items())[:6]]
        lines.append("breakdown: " + ", ".join(parts))
    if snap.get("at_cap"):
        lines.append("AT CAP — routine pings are being skipped")
    return "\n".join(lines)


def _quota_notice_due(state: dict[str, Any], key: str) -> bool:
    last = _parse_utc(str(state.get(key) or ""))
    if last is None:
        return True
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - last).total_seconds() >= SEND_WINDOW.total_seconds()


def _format_quota_notice_body(snap: dict[str, Any], *, kind: str, skipped_title: str = "") -> str:
    lines = [f"Sent {snap['count']}/{snap['cap']} in the last 24h."]
    if skipped_title:
        lines.append(f"Just skipped: {skipped_title}")
    breakdown = snap.get("breakdown") or {}
    if breakdown:
        lines.append("")
        lines.append("Top senders:")
        for cat, n in list(breakdown.items())[:6]:
            lines.append(f"- {n}x {cat.replace('_', ' ')}")
    cuts = snap.get("suggested_cuts") or []
    if cuts:
        lines.append("")
        lines.append("To cut volume:")
        for cut in cuts:
            lines.append(f"- {cut}")
    lines.append("")
    lines.append(
        "Urgent/loop-down still get through. Phone: status | snooze 8"
        if kind == "exceeded"
        else "Approaching cap. Phone: status for full breakdown."
    )
    return "\n".join(lines)


def _post_ntfy_raw(title: str, body: str, *, tags: list[str] | None = None, priority: str = "default") -> bool:
    if not notify_enabled() or not ntfy_topic():
        return False
    url = f"{ntfy_server()}/{ntfy_topic()}"
    outbound_tags = list(tags or [])
    if OUTBOUND_TAG not in outbound_tags:
        outbound_tags.insert(0, OUTBOUND_TAG)
    headers = {"Title": _header_value(title), "Priority": priority}
    if outbound_tags:
        headers["Tags"] = _header_value(",".join(outbound_tags[:5]))
    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
    except urllib.error.URLError as exc:
        print(f"ppe_notify_push: ntfy failed: {exc}", file=sys.stderr)
        return False


def _maybe_notify_quota_warn(repo: Path | None, state: dict[str, Any], sends: list[dict[str, Any]]) -> None:
    cap = ntfy_daily_cap()
    if len(sends) < ntfy_warn_threshold() or len(sends) >= cap:
        return
    if not _quota_notice_due(state, "quota_warn_sent_at"):
        return
    snap = build_quota_snapshot(sends=sends, cap=cap)
    write_quota_status_file(snap, repo)
    title = f"PPE ntfy budget: {snap['count']}/{cap} today"
    if _post_ntfy_raw(title, _format_quota_notice_body(snap, kind="warn"), tags=["ppe", "quota", "warn"], priority="high"):
        state["quota_warn_sent_at"] = _utc_now()
        _save_send_state(state, repo)


def _maybe_notify_quota_exceeded(
    repo: Path | None, state: dict[str, Any], sends: list[dict[str, Any]], *, skipped_title: str
) -> None:
    if not _quota_notice_due(state, "quota_cap_sent_at"):
        return
    cap = ntfy_daily_cap()
    snap = build_quota_snapshot(sends=sends, cap=cap, skipped_title=skipped_title, skip_reason="daily cap")
    write_quota_status_file(snap, repo)
    title = f"PPE ntfy budget: {snap['count']}/{cap} — cap reached"
    body = _format_quota_notice_body(snap, kind="exceeded", skipped_title=skipped_title)
    if _post_ntfy_raw(title, body, tags=["ppe", "quota", "cap"], priority="urgent"):
        state["quota_cap_sent_at"] = _utc_now()
        _save_send_state(state, repo)


def should_throttle_ntfy(
    title: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    bypass_throttle: bool = False,
    repo: Path | None = None,
) -> tuple[bool, str]:
    """Return (allow_send, skip_reason)."""
    if bypass_throttle or priority == "urgent":
        return True, ""

    state = _load_send_state(repo)
    sends = _prune_send_state(state)
    now = datetime.now(timezone.utc)
    fp = _message_fingerprint(title, tags, priority)
    dedup_minutes = _heartbeat_dedup_minutes() if _is_heartbeat_message(title, tags) else ntfy_dedup_minutes()
    dedup_cutoff = now - timedelta(minutes=dedup_minutes)

    for item in reversed(sends):
        if str(item.get("fp") or "") != fp:
            continue
        at = _parse_utc(str(item.get("at") or ""))
        if at is None:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if at >= dedup_cutoff:
            return False, f"dedup ({dedup_minutes:g}m window)"

    cap = ntfy_daily_cap()
    if len(sends) >= cap:
        snap = build_quota_snapshot(sends=sends, cap=cap, skipped_title=title, skip_reason="daily cap")
        write_quota_status_file(snap, repo)
        _maybe_notify_quota_exceeded(repo, state, sends, skipped_title=title)
        return False, f"daily cap ({cap})"

    min_gap = ntfy_min_interval_seconds()
    if min_gap > 0 and sends:
        last_at = _parse_utc(str(sends[-1].get("at") or ""))
        if last_at is not None:
            if last_at.tzinfo is None:
                last_at = last_at.replace(tzinfo=timezone.utc)
            elapsed = (now - last_at).total_seconds()
            if elapsed < min_gap:
                return False, f"min interval ({min_gap:g}s)"

    return True, ""


def record_ntfy_send(
    title: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    repo: Path | None = None,
) -> None:
    state = _load_send_state(repo)
    sends = _prune_send_state(state)
    sends.append(
        {
            "at": _utc_now(),
            "fp": _message_fingerprint(title, tags, priority),
            "title": title[:160],
            "priority": priority,
            "category": categorize_send_title(title),
        }
    )
    state["sends"] = sends
    write_quota_status_file(build_quota_snapshot(sends=sends), repo)
    _maybe_notify_quota_warn(repo, state, sends)
    _save_send_state(state, repo)


def send_ntfy(
    title: str,
    body: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    click_url: str | None = None,
    bypass_snooze: bool = False,
    bypass_throttle: bool = False,
) -> bool:
    """POST a message to ntfy. Returns True when a message was sent."""
    if not notify_enabled():
        return False
    if not bypass_snooze and is_ntfy_snoozed():
        return False
    if is_routine_notify_muted(title=title, tags=tags, priority=priority):
        print(f"ppe_notify_push: skipped (quiet hours): {title[:80]}", file=sys.stderr)
        return False
    topic = ntfy_topic()
    if not topic:
        return False

    allow, skip_reason = should_throttle_ntfy(
        title,
        tags=tags,
        priority=priority,
        bypass_throttle=bypass_throttle,
        repo=repo_root(),
    )
    if not allow:
        print(f"ppe_notify_push: skipped ({skip_reason}): {title[:80]}", file=sys.stderr)
        return False

    url = f"{ntfy_server()}/{topic}"
    outbound_tags = list(tags or [])
    if OUTBOUND_TAG not in outbound_tags:
        outbound_tags.insert(0, OUTBOUND_TAG)
    headers = {"Title": _header_value(title), "Priority": priority}
    if outbound_tags:
        headers["Tags"] = _header_value(",".join(outbound_tags[:5]))
    if click_url:
        headers["Click"] = _header_value(click_url)

    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = body.encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            ok = 200 <= response.status < 300
            if ok:
                record_ntfy_send(title, tags=outbound_tags, priority=priority, repo=repo_root())
            return ok
    except urllib.error.URLError as exc:
        print(f"ppe_notify_push: ntfy failed: {exc}", file=sys.stderr)
        return False


def steward_daily_cap() -> int:
    raw = os.environ.get("PPE_NTFY_STEWARD_DAILY_CAP", str(DEFAULT_STEWARD_DAILY_CAP)).strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_STEWARD_DAILY_CAP


def _steward_send_state_path(repo: Path | None = None) -> Path:
    return (repo or repo_root()).resolve() / STEWARD_SEND_STATE_REL


def _load_steward_send_state(repo: Path | None = None) -> dict[str, Any]:
    path = _steward_send_state_path(repo)
    if not path.is_file():
        return {"sends": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"sends": []}
    if not isinstance(data, dict):
        return {"sends": []}
    sends = data.get("sends")
    if not isinstance(sends, list):
        data["sends"] = []
    return data


def _save_steward_send_state(state: dict[str, Any], repo: Path | None = None) -> None:
    path = _steward_send_state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _prune_steward_sends(sends: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - SEND_WINDOW
    kept: list[dict[str, Any]] = []
    for item in sends:
        at = _parse_utc(str(item.get("at") or ""))
        if at is None:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if at >= cutoff:
            kept.append(item)
    return kept


def send_steward_ntfy(
    title: str,
    body: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    bypass_throttle: bool = False,
    repo: Path | None = None,
) -> bool:
    """POST to PPE_NTFY_STEWARD_TOPIC — human commitments channel (no loop commands)."""
    if not notify_enabled():
        return False
    topic = steward_ntfy_topic()
    if not topic:
        return False

    repo = repo or repo_root()
    state = _load_steward_send_state(repo)
    sends = _prune_steward_sends(list(state.get("sends") or []))
    cap = steward_daily_cap()
    if not bypass_throttle and len(sends) >= cap:
        print(f"ppe_notify_push: steward skipped (daily cap {cap}): {title[:80]}", file=sys.stderr)
        return False

    url = f"{ntfy_server()}/{topic}"
    outbound_tags = list(tags or ["ppe", "steward"])
    headers = {"Title": _header_value(title), "Priority": priority}
    if outbound_tags:
        headers["Tags"] = _header_value(",".join(outbound_tags[:5]))
    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            ok = 200 <= response.status < 300
            if ok:
                sends.append({"at": _utc_now(), "title": title[:160], "priority": priority})
                state["sends"] = sends
                _save_steward_send_state(state, repo)
            return ok
    except urllib.error.URLError as exc:
        print(f"ppe_notify_push: steward ntfy failed: {exc}", file=sys.stderr)
        return False


def send_weekly_digest_from_payload(payload_path: Path) -> bool:
    if not payload_path.is_file():
        return False
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ppe_notify_push: unreadable weekly digest payload {payload_path}: {exc}", file=sys.stderr)
        return False
    if not isinstance(payload, dict):
        return False

    week = str(payload.get("week_monday") or "").strip()
    in_short = str(payload.get("in_short") or "").strip()
    phone_title = str(payload.get("phone_title") or "").strip()
    phone_body = str(payload.get("phone_body") or "").strip()
    click_url = str(payload.get("click_url") or "").strip() or None
    if not week or (not phone_body and not in_short):
        return False

    title = phone_title or f"PPE weekly digest (week of {week})"
    body = phone_body or in_short
    return send_ntfy(
        title,
        body,
        tags=["ppe", "weekly", "digest"],
        priority="default",
        click_url=click_url,
    )


def send_from_payload(payload_path: Path) -> bool:
    if not payload_path.is_file():
        return False
    try:
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ppe_notify_push: unreadable payload {payload_path}: {exc}", file=sys.stderr)
        return False
    if not isinstance(payload, dict):
        return False

    title = str(payload.get("title") or "PPE operator status")
    body = str(payload.get("body") or "See artifacts/orchestrator/OPERATOR_STATUS.md")
    verdict = str(payload.get("verdict") or "")
    priority = _priority_for_verdict(verdict)
    tags = ["ppe", verdict.lower()] if verdict else ["ppe"]
    return send_ntfy(title, body, tags=tags, priority=priority)


def send_operator_status(status: dict[str, Any]) -> bool:
    from scripts.ppe_operator_hint import append_ppe_go_hint

    verdict = str(status.get("verdict") or "UNKNOWN")
    title = f"PPE operator: {verdict}"
    lines = [f"VERDICT={verdict}"]
    if status.get("blocker"):
        lines.append(str(status["blocker"]))
    commands = status.get("commands") or []
    if commands:
        lines.append("Next: " + str(commands[0]))
    body = append_ppe_go_hint("\n".join(lines), verdict)
    return send_ntfy(
        title,
        body,
        tags=["ppe", verdict.lower()],
        priority=_priority_for_verdict(verdict),
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Send PPE operator alerts to ntfy (mobile push)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--payload", type=Path, help="JSON payload (e.g. OPERATOR_STATUS_NOTIFY.json)")
    ap.add_argument("--weekly-digest", action="store_true", help="Send WEEKLY_DIGEST_NOTIFY.json to ntfy")
    ap.add_argument("--title", help="Direct title (with --body)")
    ap.add_argument("--body", help="Direct body (with --title)")
    ap.add_argument("--verdict", help="Verdict tag for priority when using --title/--body")
    ap.add_argument("--check", action="store_true", help="Print whether ntfy is configured and exit 0/1")
    ap.add_argument("--steward-check", action="store_true", help="Print steward topic config and exit 0/1")
    ap.add_argument("--steward-test", action="store_true", help="Send test message to steward topic")
    ap.add_argument("--quota", action="store_true", help="Print today's ntfy send budget and exit")
    args = ap.parse_args(argv)

    if args.check:
        ok = notify_enabled() and ntfy_configured()
        steward_ok = notify_enabled() and steward_ntfy_configured()
        print(
            f"ppe_notify_push: operator configured={ok} topic={ntfy_topic() or '(unset)'}; "
            f"steward configured={steward_ok} topic={steward_ntfy_topic() or '(unset)'}"
        )
        return 0 if ok else 1

    if args.steward_check:
        ok = notify_enabled() and steward_ntfy_configured()
        print(f"ppe_notify_push: steward configured={ok} topic={steward_ntfy_topic() or '(unset)'}")
        return 0 if ok else 1

    if args.steward_test:
        bootstrap_operator_notify_env(args.repo_root.resolve())
        sent = send_steward_ntfy(
            "PPE steward test",
            "Steward topic works. Wed/Sun nudges land here — not build/fix commands.",
            tags=["ppe", "steward", "test"],
            priority="default",
            bypass_throttle=True,
            repo=args.repo_root.resolve(),
        )
        return 0 if sent or not steward_ntfy_configured() else 1

    if args.quota:
        print(format_quota_brief(args.repo_root.resolve()))
        return 0

    if args.weekly_digest:
        payload = args.payload or (args.repo_root / "artifacts/control_plane/WEEKLY_DIGEST_NOTIFY.json")
        sent = send_weekly_digest_from_payload(payload.resolve())
        return 0 if sent or not ntfy_configured() else 1

    if args.payload:
        sent = send_from_payload(args.payload.resolve())
        return 0 if sent or not ntfy_configured() else 1

    if args.title:
        body = args.body or ""
        sent = send_ntfy(
            args.title,
            body,
            tags=["ppe"],
            priority=_priority_for_verdict(args.verdict),
        )
        return 0 if sent or not ntfy_configured() else 1

    ap.error("provide --payload, --title, or --quota")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
