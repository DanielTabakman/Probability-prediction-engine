"""Poll operator status and push mobile alerts when attention is needed."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy
from scripts.ppe_operator_status import (
    VERDICT_ERROR,
    VERDICT_FIX_PLAN,
    VERDICT_IDE_BUILD,
    VERDICT_RUN_LOCAL,
    VERDICT_STALE_STATE,
    VERDICT_SUPPLY_LOW,
    collect_operator_status,
    write_status_report,
)

STATE_REL = "artifacts/control_plane/MOBILE_WATCH_STATE.json"

ATTENTION_VERDICTS = frozenset(
    {
        VERDICT_IDE_BUILD,
        VERDICT_FIX_PLAN,
        VERDICT_STALE_STATE,
        VERDICT_ERROR,
        VERDICT_RUN_LOCAL,
        VERDICT_SUPPLY_LOW,
    }
)


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


def _heartbeat_hours() -> float:
    raw = os.environ.get("PPE_NTFY_HEARTBEAT_HOURS", "6").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 6.0


def _heartbeat_due(prior: dict[str, Any]) -> bool:
    last = _parse_utc(str(prior.get("last_heartbeat_at") or ""))
    if last is None:
        return True
    elapsed_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600.0
    return elapsed_h >= _heartbeat_hours()


def push_stack_status_notify(
    repo: Path,
    *,
    verdict: str,
    loop_running: bool,
    watch_running: bool,
    reason: str = "status",
    plan: str = "",
) -> bool:
    """Low-friction phone ping: stack health without SSH."""
    if not notify_enabled() or not ntfy_configured():
        return False
    if not loop_running:
        title = "PPE stack down"
        body = "Loop is not running on the desktop. Reboot or run run_ppe_desktop_operator.cmd at the PC."
        priority = "high"
        tags = ["ppe", "down"]
    else:
        title = f"PPE OK — {verdict or 'RUNNING'}"
        parts = ["Loop running."]
        if watch_running:
            parts.append("Watch running.")
        if plan:
            parts.append(f"Plan: {plan}")
        body = " ".join(parts)
        priority = "low"
        tags = ["ppe", "ok", reason]
    return send_ntfy(title, body, tags=tags, priority=priority)


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


def is_loop_running() -> bool:
    from scripts.ppe_desktop_operator_stack import is_loop_running as _stack_loop_running

    return _stack_loop_running()


def watch_once(repo: Path, *, write_report: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    status = collect_operator_status(repo)
    if write_report:
        write_status_report(repo, status)

    verdict = str(status.get("verdict") or "")
    loop_running = is_loop_running()
    prior = load_state(repo)

    alerts: list[tuple[str, str]] = []
    prior_verdict = str(prior.get("last_verdict") or "")
    prior_loop = bool(prior.get("loop_running"))

    if verdict in ATTENTION_VERDICTS and verdict != prior_verdict:
        alerts.append((f"PPE operator: {verdict}", str(status.get("blocker") or verdict)))

    if prior_loop and not loop_running:
        alerts.append(
            (
                "PPE loop stopped",
                "run_ppe_auto_local_loop.cmd is not running on the desktop.",
            )
        )

    heartbeat_sent = False
    if loop_running and _heartbeat_due(prior):
        if push_stack_status_notify(
            repo,
            verdict=verdict,
            loop_running=loop_running,
            watch_running=True,
            reason="heartbeat",
            plan=str(status.get("phase_plan_path") or "").strip(),
        ):
            heartbeat_sent = True

    sent = 0
    if alerts and notify_enabled() and ntfy_configured():
        for title, body in alerts:
            if send_ntfy(title, body, tags=["ppe", "watch"], priority="high"):
                sent += 1

    new_state = {
        "as_of": _utc_now(),
        "last_verdict": verdict,
        "loop_running": loop_running,
        "alerts_sent": sent,
        "last_alert_titles": [title for title, _ in alerts],
        "last_heartbeat_at": _utc_now() if heartbeat_sent else prior.get("last_heartbeat_at"),
    }
    save_state(repo, new_state)

    return {
        "verdict": verdict,
        "loop_running": loop_running,
        "alerts": alerts,
        "alerts_sent": sent,
        "heartbeat_sent": heartbeat_sent,
        "state_path": str(state_path(repo)),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Watch PPE operator status and push mobile alerts")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--once", action="store_true", help="Single poll (default for Task Scheduler)")
    ap.add_argument("--interval", type=int, default=120, help="Seconds between polls in loop mode")
    ap.add_argument("--no-write", action="store_true", help="Do not refresh OPERATOR_STATUS.md")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    write_report = not args.no_write

    if args.once:
        result = watch_once(repo, write_report=write_report)
        print(json.dumps(result, indent=2))
        return 0

    import time

    print(f"ppe_watch_operator_mobile: polling every {args.interval}s — Ctrl+C to stop")
    while True:
        result = watch_once(repo, write_report=write_report)
        brief = f"verdict={result['verdict']} loop={result['loop_running']} alerts={result['alerts_sent']}"
        print(f"[{_utc_now()}] {brief}")
        time.sleep(max(15, args.interval))


if __name__ == "__main__":
    raise SystemExit(main())
