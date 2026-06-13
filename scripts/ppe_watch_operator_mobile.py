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

from scripts.ppe_notify_push import (
    is_ntfy_quiet_hours,
    mark_quiet_stuck_sent,
    ntfy_configured,
    notify_enabled,
    quiet_stuck_allowed,
    reset_quiet_stuck_if_awake,
    send_ntfy,
)
from scripts.ppe_operator_hint import append_ppe_go_hint
from scripts.ppe_phone_status import format_phone_alert_body, verdict_headline
from scripts.ppe_operator_status import (
    VERDICT_ERROR,
    VERDICT_FIX_PLAN,
    VERDICT_IDE_BUILD,
    VERDICT_RUN_AUTO,
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

STUCK_VERDICTS = frozenset(
    {
        VERDICT_IDE_BUILD,
        VERDICT_FIX_PLAN,
        VERDICT_STALE_STATE,
        VERDICT_ERROR,
    }
)

HEALTHY_VERDICTS = frozenset(
    {
        VERDICT_RUN_AUTO,
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
    raw = os.environ.get("PPE_NTFY_HEARTBEAT_HOURS", "24").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 24.0


def _stuck_alert_hours() -> float:
    raw = os.environ.get("PPE_NTFY_STUCK_HOURS", "8").strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 8.0


def _auto_build_retry_due(prior: dict[str, Any], verdict: str) -> bool:
    """Retry auto-build when IDE_BUILD stays stuck (prior build failed or never started)."""
    if verdict != VERDICT_IDE_BUILD:
        return False
    if not _stuck_alert_due(prior, verdict):
        return False
    verdict_slice = str(prior.get("last_verdict_slice") or "")
    if not verdict_slice:
        return False
    auto_slice = str(prior.get("last_auto_build_slice") or "")
    last_auto = prior.get("last_auto_build") or {}
    if not auto_slice:
        return True
    if auto_slice != verdict_slice:
        return False
    if not last_auto.get("started"):
        return True
    return True


def _maybe_auto_remote_build(
    repo: Path,
    status: dict[str, Any],
    prior: dict[str, Any],
    *,
    retry: bool = False,
) -> dict[str, Any] | None:
    from scripts.ppe_ide_handoff import ide_handoff_enabled, respond_to_ide_build
    from scripts.ppe_operator_config import auto_remote_build_enabled
    from scripts.ppe_remote_build_agent import read_build_lock, resolve_build_target

    if not auto_remote_build_enabled(repo) and not ide_handoff_enabled(repo):
        return None
    if str(status.get("verdict") or "") != VERDICT_IDE_BUILD:
        return None

    target = resolve_build_target(repo)
    if not target.get("ok") or target.get("mode") != "ide_build":
        return None

    slice_id = str(target.get("slice_id") or "")
    if not slice_id:
        return None

    if read_build_lock(repo):
        return None

    prior_verdict_slice = str(prior.get("last_verdict_slice") or "")
    last_auto = prior.get("last_auto_build") or {}
    if not retry:
        if (
            str(prior.get("last_verdict") or "") == VERDICT_IDE_BUILD
            and prior_verdict_slice == slice_id
            and last_auto.get("started")
            and str(last_auto.get("slice_id") or prior.get("last_auto_build_slice") or "") == slice_id
        ):
            return None
    elif not _auto_build_retry_due(prior, VERDICT_IDE_BUILD):
        return None
    elif prior_verdict_slice and prior_verdict_slice != slice_id:
        return None

    note = "auto-triggered by mobile watch on IDE_BUILD"
    if retry:
        note = "auto-retry by mobile watch (IDE_BUILD still stuck)"
    return respond_to_ide_build(
        repo,
        source="auto-watch",
        note=note,
        force_handoff=retry and bool(prior.get("last_auto_build")),
    )


def _stuck_alert_due(prior: dict[str, Any], verdict: str) -> bool:
    if verdict not in STUCK_VERDICTS:
        return False
    prior_verdict = str(prior.get("last_verdict") or "")
    if verdict != prior_verdict:
        return False
    last = _parse_utc(str(prior.get("last_stuck_alert_at") or ""))
    if last is None:
        return True
    elapsed_h = (datetime.now(timezone.utc) - last).total_seconds() / 3600.0
    return elapsed_h >= _stuck_alert_hours()


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
        priority = "urgent"
        tags = ["ppe", "down"]
    else:
        title = f"PPE OK - {verdict or 'RUNNING'}"
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
    from scripts.ppe_notify_push import bootstrap_operator_notify_env

    repo = repo.resolve()
    bootstrap_operator_notify_env(repo)
    status = collect_operator_status(repo)
    if write_report:
        write_status_report(repo, status)

    verdict = str(status.get("verdict") or "")
    loop_running = is_loop_running()
    prior = load_state(repo)

    reset_quiet_stuck_if_awake(repo)

    alerts: list[tuple[str, str]] = []
    prior_verdict = str(prior.get("last_verdict") or "")
    prior_loop = bool(prior.get("loop_running"))

    auto_build: dict[str, Any] | None = None
    if verdict == VERDICT_IDE_BUILD and verdict != prior_verdict:
        auto_build = _maybe_auto_remote_build(repo, status, prior, retry=False)
    elif verdict == VERDICT_IDE_BUILD:
        auto_build = _maybe_auto_remote_build(repo, status, prior, retry=True)

    if verdict in ATTENTION_VERDICTS and verdict != prior_verdict:
        blocker = str(status.get("blocker") or verdict)
        if auto_build and auto_build.get("started"):
            slice_id = str(auto_build.get("slice_id") or "")
            if str(auto_build.get("mode") or auto_build.get("action")) == "ide_handoff":
                alerts.append(
                    (
                        f"PPE IDE handoff: {slice_id or verdict}",
                        append_ppe_go_hint(blocker, VERDICT_IDE_BUILD),
                    )
                )
            else:
                alerts.append(
                    (
                        f"PPE auto-build started: {slice_id or verdict}",
                        f"{blocker}\nAgent CLI running on desktop — no phone action needed.",
                    )
                )
        else:
            alerts.append((f"PPE operator: {verdict}", append_ppe_go_hint(blocker, verdict)))

    prior_blocker = str(prior.get("last_blocker") or "").strip()
    current_blocker = str(status.get("blocker") or "").strip()
    plan = str(status.get("phase_plan_path") or "").strip()

    if prior_verdict in STUCK_VERDICTS and verdict in HEALTHY_VERDICTS:
        alerts.append(
            (
                f"PPE: cleared - {verdict_headline(verdict)}",
                format_phone_alert_body(status, kind="cleared", prior_verdict=prior_verdict),
            )
        )

    if _stuck_alert_due(prior, verdict) and quiet_stuck_allowed(repo):
        alerts.append(
            (
                f"PPE: still stuck - {verdict_headline(verdict)}",
                format_phone_alert_body(status, kind="stuck"),
            )
        )

    if prior_loop and not loop_running:
        alerts.append(
            (
                "PPE loop stopped",
                format_phone_alert_body(status, kind="loop_down"),
            )
        )

    morning_report: dict[str, Any] | None = None
    try:
        from scripts.ppe_morning_report import maybe_send_morning_report

        morning_report = maybe_send_morning_report(repo, status)
    except Exception as exc:
        morning_report = {"sent": False, "error": str(exc)}

    heartbeat_sent = False
    if loop_running and _heartbeat_hours() > 0 and _heartbeat_due(prior):
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
    stuck_alert_sent = False
    if alerts and notify_enabled() and ntfy_configured():
        for title, body in alerts:
            priority = "urgent" if title == "PPE loop stopped" else "high"
            tags = ["ppe", "watch", "stuck"] if "still stuck" in title.lower() else ["ppe", "watch"]
            if send_ntfy(title, body, tags=tags, priority=priority):
                sent += 1
                if "still stuck" in title.lower():
                    stuck_alert_sent = True
                    if is_ntfy_quiet_hours():
                        mark_quiet_stuck_sent(repo)

    guard = status.get("guard") or {}
    detail = str(guard.get("detail") or status.get("blocker") or "")
    left, right = detail.find("["), detail.find("]")
    verdict_slice = None
    if left >= 0 and right > left:
        ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
        verdict_slice = ids[0] if ids else None

    new_state = {
        "as_of": _utc_now(),
        "last_verdict": verdict,
        "last_blocker": current_blocker or None,
        "last_verdict_slice": verdict_slice,
        "loop_running": loop_running,
        "alerts_sent": sent,
        "last_alert_titles": [title for title, _ in alerts],
        "last_heartbeat_at": _utc_now() if heartbeat_sent else prior.get("last_heartbeat_at"),
        "last_stuck_alert_at": _utc_now()
        if stuck_alert_sent or (verdict in STUCK_VERDICTS and verdict != prior_verdict and sent)
        else prior.get("last_stuck_alert_at"),
    }
    if auto_build:
        new_state["last_auto_build"] = auto_build
        if auto_build.get("started") and auto_build.get("slice_id"):
            new_state["last_auto_build_slice"] = auto_build.get("slice_id")
            new_state["last_auto_build_at"] = _utc_now()

    post_finish: dict[str, Any] | None = None
    try:
        from scripts.ppe_post_build_watcher import try_finish_pending_ide_build

        post_finish = try_finish_pending_ide_build(repo)
        if post_finish and post_finish.get("started"):
            new_state["last_post_build_finish"] = post_finish
    except Exception as exc:
        post_finish = {"action": "post_build_watcher", "error": str(exc)}

    save_state(repo, new_state)

    try:
        from scripts.ppe_operator_daily_metrics import record_watch_sample

        record_watch_sample(repo, loop_running=loop_running, verdict=verdict)
    except Exception:
        pass

    gap_alert: dict[str, Any] | None = None
    try:
        from scripts.ppe_operator_uptime_gap import maybe_send_gap_alert

        gap_alert = maybe_send_gap_alert(
            repo,
            loop_running=loop_running,
            verdict=verdict,
            prior=prior,
        )
    except Exception as exc:
        gap_alert = {"sent": False, "error": str(exc)}

    return {
        "verdict": verdict,
        "loop_running": loop_running,
        "alerts": alerts,
        "alerts_sent": sent,
        "heartbeat_sent": heartbeat_sent,
        "auto_build": auto_build,
        "post_build_finish": post_finish,
        "morning_report": morning_report,
        "gap_alert": gap_alert,
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
