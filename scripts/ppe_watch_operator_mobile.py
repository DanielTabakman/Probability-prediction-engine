"""Poll operator status and push mobile alerts when attention is needed."""

from __future__ import annotations

import argparse
import json
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
    """True when the Windows auto-loop cmd wrapper is still alive."""
    ps = (
        "$hits = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.CommandLine -match 'run_ppe_auto_local_loop|run_ppe_auto_loop\\.cmd' }; "
        "if ($hits) { 'yes' } else { 'no' }"
    )
    try:
        proc = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.stdout.strip().lower() == "yes"


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
    }
    save_state(repo, new_state)

    return {
        "verdict": verdict,
        "loop_running": loop_running,
        "alerts": alerts,
        "alerts_sent": sent,
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
