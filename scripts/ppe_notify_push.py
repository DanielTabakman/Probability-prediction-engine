"""Mobile push notifications (ntfy) for PPE operator alerts."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

DEFAULT_NTFY_SERVER = "https://ntfy.sh"
SNOOZE_REL = "artifacts/control_plane/NTFY_SNOOZE.json"
SEND_STATE_REL = "artifacts/control_plane/NTFY_SEND_STATE.json"
OUTBOUND_TAG = "from-desktop"
DEFAULT_DAILY_CAP = 40
DEFAULT_DEDUP_MINUTES = 45.0
DEFAULT_MIN_INTERVAL_SEC = 120.0
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


def repo_root() -> Path:
    raw = os.environ.get("PPE_REPO_ROOT", "").strip()
    return Path(raw) if raw else Path.cwd()


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


def should_throttle_ntfy(
    title: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    bypass_throttle: bool = False,
    repo: Path | None = None,
) -> tuple[bool, str]:
    """Return (allow_send, skip_reason)."""
    if bypass_throttle:
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

    if priority != "urgent":
        cap = ntfy_daily_cap()
        if len(sends) >= cap:
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
            "at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "fp": _message_fingerprint(title, tags, priority),
            "title": title[:160],
            "priority": priority,
        }
    )
    _save_send_state({"sends": sends}, repo)


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
    topic = ntfy_topic()
    if not topic:
        return False

    allow, skip_reason = should_throttle_ntfy(
        title,
        tags=tags,
        priority=priority,
        bypass_throttle=bypass_throttle,
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
                record_ntfy_send(title, tags=outbound_tags, priority=priority)
            return ok
    except urllib.error.URLError as exc:
        print(f"ppe_notify_push: ntfy failed: {exc}", file=sys.stderr)
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
    verdict = str(status.get("verdict") or "UNKNOWN")
    title = f"PPE operator: {verdict}"
    lines = [f"VERDICT={verdict}"]
    if status.get("blocker"):
        lines.append(str(status["blocker"]))
    commands = status.get("commands") or []
    if commands:
        lines.append("Next: " + str(commands[0]))
    body = "\n".join(lines)
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
    args = ap.parse_args(argv)

    if args.check:
        ok = notify_enabled() and ntfy_configured()
        print(f"ppe_notify_push: configured={ok} topic={ntfy_topic() or '(unset)'}")
        return 0 if ok else 1

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

    ap.error("provide --payload or --title")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
