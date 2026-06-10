"""Mobile push notifications (ntfy) for PPE operator alerts."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_NTFY_SERVER = "https://ntfy.sh"
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


def _header_value(value: str) -> str:
    """ntfy headers must be latin-1; keep phone alerts ASCII-safe."""
    text = (value or "").replace("\u2014", "-").replace("\u2013", "-")
    return text.encode("ascii", "replace").decode("ascii")[:250]


def _priority_for_verdict(verdict: str | None) -> str:
    if not verdict:
        return "default"
    return PRIORITY_BY_VERDICT.get(verdict.strip().upper(), "default")


def send_ntfy(
    title: str,
    body: str,
    *,
    tags: list[str] | None = None,
    priority: str = "default",
    click_url: str | None = None,
) -> bool:
    """POST a message to ntfy. Returns True when a message was sent."""
    if not notify_enabled():
        return False
    topic = ntfy_topic()
    if not topic:
        return False

    url = f"{ntfy_server()}/{topic}"
    headers = {"Title": _header_value(title), "Priority": priority}
    if tags:
        headers["Tags"] = _header_value(",".join(tags[:5]))
    if click_url:
        headers["Click"] = _header_value(click_url)

    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    data = body.encode("utf-8")
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return 200 <= response.status < 300
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
