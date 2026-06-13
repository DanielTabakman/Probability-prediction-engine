"""Wed/Sun steward nudges to PPE_NTFY_STEWARD_TOPIC (human commitments, not loop alerts)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import (
    bootstrap_operator_notify_env,
    send_steward_ntfy,
    steward_ntfy_configured,
)
from scripts.ppe_steward_scoreboard import (
    build_nudge_message,
    build_scoreboard,
    format_scoreboard_text,
    resolve_nudge_slot,
)

STATE_REL = "artifacts/control_plane/STEWARD_NUDGE_STATE.json"


def state_path(repo: Path) -> Path:
    return repo / STATE_REL


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


def week_key(ref: date | None = None) -> str:
    ref = ref or date.today()
    monday = ref.toordinal() - ref.weekday()
    return date.fromordinal(monday).isoformat()


def already_sent_this_week(state: dict[str, Any], slot: str, *, ref: date | None = None) -> bool:
    key = f"last_{slot}_week"
    return str(state.get(key) or "") == week_key(ref)


def mark_sent(repo: Path, state: dict[str, Any], slot: str, *, ref: date | None = None) -> None:
    state = {**state, f"last_{slot}_week": week_key(ref)}
    save_state(repo, state)


def run_nudge(
    repo: Path,
    *,
    slot: str = "auto",
    dry_run: bool = False,
    force: bool = False,
    ref: date | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    bootstrap_operator_notify_env(repo)
    resolved = resolve_nudge_slot(slot, ref=ref)  # type: ignore[arg-type]
    if resolved is None:
        return {"sent": False, "reason": "not_wed_or_sun", "slot_requested": slot}

    scoreboard = build_scoreboard(repo, ref=ref)
    title, body = build_nudge_message(scoreboard, resolved)
    state = load_state(repo)

    if not force and already_sent_this_week(state, resolved, ref=ref):
        return {
            "sent": False,
            "reason": "already_sent_this_week",
            "slot": resolved,
            "week": week_key(ref),
        }

    if dry_run:
        return {
            "sent": False,
            "dry_run": True,
            "slot": resolved,
            "title": title,
            "body": body,
            "scoreboard": scoreboard,
        }

    if not steward_ntfy_configured():
        return {
            "sent": False,
            "reason": "steward_topic_unset",
            "hint": "Set PPE_NTFY_STEWARD_TOPIC in ppe_operator_notify.local.cmd",
            "slot": resolved,
            "title": title,
            "body": body,
        }

    sent = send_steward_ntfy(title, body, tags=["ppe", "steward", resolved[:3]], priority="high")
    if sent:
        mark_sent(repo, state, resolved, ref=ref)
    return {"sent": sent, "slot": resolved, "title": title, "body": body}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Send steward Wed/Sun nudges (separate ntfy topic)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--slot",
        choices=("auto", "wednesday", "sunday"),
        default="auto",
        help="auto = only send on Wed/Sun local day",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print payload without sending")
    ap.add_argument("--force", action="store_true", help="Send even if already sent this week")
    ap.add_argument("--scoreboard", action="store_true", help="Print scoreboard and exit")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.scoreboard:
        print(format_scoreboard_text(build_scoreboard(repo)))
        return 0

    result = run_nudge(repo, slot=args.slot, dry_run=args.dry_run, force=args.force)
    print(json.dumps(result, indent=2))
    if result.get("reason") == "not_wed_or_sun":
        return 0
    if result.get("dry_run") or result.get("reason") == "already_sent_this_week":
        return 0
    if not result.get("sent") and result.get("reason") == "steward_topic_unset":
        print(result.get("hint", ""), file=sys.stderr)
        return 1
    return 0 if result.get("sent") else 1


if __name__ == "__main__":
    raise SystemExit(main())
