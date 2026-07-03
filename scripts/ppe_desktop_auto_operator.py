"""Desktop auto-operator: press BUILD/CONTINUE buttons when status warrants it."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_operator_shortcuts import detect_role, ensure_shortcuts
from scripts.ppe_operator_vm_ssh import (
    fetch_vm_brief,
    ssh_vm,
    vm_advance_command,
)

STATE_REL = "artifacts/orchestrator/DESKTOP_AUTO_OPERATOR.json"
LOG_REL = "artifacts/orchestrator/DESKTOP_AUTO_OPERATOR.log"
DEFAULT_POLL_SECONDS = 120


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def log_path(repo: Path) -> Path:
    return (repo / LOG_REL).resolve()


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, data: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    data["updatedAt"] = _utc_now()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def append_log(repo: Path, line: str) -> None:
    path = log_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_utc_now()} {line}\n")


def desktop_auto_enabled(repo: Path) -> bool:
    """Desktop auto is OPT-IN only — default off (causes confusion/popups on daily PC)."""
    opt_in = repo / "ppe_operator_desktop_auto.local.cmd"
    if not opt_in.is_file():
        return False
    env = os.environ.get("PPE_DESKTOP_AUTO", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    return detect_role(repo) == "daily_driver"


def dispatch_allowed_env() -> bool:
    return os.environ.get("PPE_AUTO_DISPATCH", "").strip().lower() in ("1", "true", "yes")


def _ssh_vm(command: str) -> dict[str, Any]:
    return ssh_vm(command)


def _maybe_git_pull(repo: Path) -> None:
    import subprocess

    subprocess.run(
        ["git", "pull", "origin", "main"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def auto_pass(repo: Path, *, dry_run: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    from scripts.ppe_autobuilder import collect_autobuilder_status

    status = collect_autobuilder_status(repo)
    verdict = str(status.get("verdict") or "")
    phase = str(status.get("phase") or "")
    actions: list[str] = []

    result: dict[str, Any] = {
        "action": "desktop_auto_pass",
        "verdict": verdict,
        "phase": phase,
        "actions": actions,
        "dry_run": dry_run,
    }

    operator_status: dict[str, Any] = {}
    if not dry_run:
        try:
            from scripts.ppe_operator_status import prepare_operator_status

            operator_status = prepare_operator_status(repo)
            from scripts.ppe_operator_dispatch import (
                automation_preflight_blocked,
                dispatch_direct_action,
                recovery_auto_dispatch_allowed,
            )

            blocked, reason, preferred = automation_preflight_blocked(operator_status)
            if blocked:
                result["preflight_blocked"] = {
                    "reason": reason,
                    "preferred_action": preferred,
                }
                actions.append("skip_preflight_blocked")
                if (
                    preferred
                    and dispatch_allowed_env()
                    and recovery_auto_dispatch_allowed(operator_status)
                ):
                    result["auto_dispatch"] = dispatch_direct_action(repo, preferred, force=True)
                    actions.append(f"auto_dispatch_{preferred}")
                result["skipped"] = True
                return result
        except Exception as exc:
            result["preflight_error"] = str(exc)

    if verdict == "IDE_BUILD" and phase in ("AWAITING_BUILD", "DEGRADED", "STACK_DOWN"):
        from scripts.ppe_autobuilder import action_handoff

        if dry_run:
            actions.append("would_handoff_ide_build")
        else:
            handoff = action_handoff(repo)
            actions.append("handoff_ide_build")
            result["handoff"] = handoff
            append_log(repo, f"auto handoff IDE_BUILD phase={phase}")

    from scripts.ppe_post_build_watcher import try_finish_pending_ide_build

    if dry_run:
        target = None
        try:
            from scripts.ppe_post_build_watcher import _resolve_watch_target

            target = _resolve_watch_target(repo)
        except ImportError:
            target = None
        if target:
            actions.append("would_finish_pending_build")
            result["finish_target"] = target
    else:
        finish = try_finish_pending_ide_build(repo)
        if finish.get("started"):
            actions.append("finish_pending_build")
            result["finish"] = finish
            append_log(repo, f"auto finish pending slice={finish.get('slice_id')}")

    if not dry_run and (verdict == "RUN_LOCAL" or phase == "RUN_LOCAL_PENDING"):
        trust = fetch_vm_brief(repo, use_cache=True)
        parsed = trust.get("parsed") if isinstance(trust.get("parsed"), dict) else {}
        vm_phase = str(parsed.get("phase") or "")
        if vm_phase in ("FINISH_IN_FLIGHT", "BUILD_IN_FLIGHT"):
            actions.append("skip_vm_finish_in_flight")
            result["vm_trust"] = {"wait_for_vm": True, "vm_phase": vm_phase}
            if dispatch_allowed_env():
                try:
                    from scripts.ppe_in_flight_monitor import maybe_start_monitor_daemon

                    daemon = maybe_start_monitor_daemon(repo, auto_act=True)
                    actions.append("monitor_daemon")
                    result["monitor_daemon"] = daemon
                except Exception as exc:
                    result["monitor_daemon"] = {"started": False, "error": str(exc)}
        else:
            if dry_run:
                actions.append("would_desktop_continue")
            else:
                continue_cmd = repo / "DESKTOP_CONTINUE.cmd"
                proc = subprocess.run(
                    [str(continue_cmd), "--no-pause"],
                    cwd=repo,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if proc.returncode == 0:
                    actions.append("desktop_continue")
                    append_log(repo, "auto DESKTOP_CONTINUE.cmd --no-pause")
                else:
                    actions.append("desktop_continue_failed")
                result["desktop_continue"] = {
                    "ok": proc.returncode == 0,
                    "exit_code": proc.returncode,
                    "stderr_tail": (proc.stderr or "")[-200:],
                }

    if not actions:
        result["skipped"] = True
    return result


def run_daemon(repo: Path, *, poll_seconds: int = DEFAULT_POLL_SECONDS) -> int:
    repo = repo.resolve()
    append_log(repo, f"daemon start pid={os.getpid()} poll={poll_seconds}s")
    save_state(repo, {"daemon_pid": os.getpid(), "poll_seconds": poll_seconds, "started_at": _utc_now()})

    while True:
        try:
            ensure_shortcuts(repo, quiet=True)
            _maybe_git_pull(repo)
            out = auto_pass(repo)
            if not out.get("skipped"):
                append_log(repo, f"pass actions={out.get('actions')}")
        except Exception as exc:  # noqa: BLE001 — daemon must survive single-pass faults
            append_log(repo, f"pass error: {exc}")
        time.sleep(max(30, poll_seconds))


def start_detached(repo: Path, *, poll_seconds: int = DEFAULT_POLL_SECONDS) -> dict[str, Any]:
    from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

    repo = repo.resolve()
    state = load_state(repo)
    pid = state.get("daemon_pid")
    if pid is not None:
        try:
            if process_alive(int(pid)):
                return {"started": False, "reason": "already running", "pid": int(pid)}
        except (TypeError, ValueError):
            pass

    proc = spawn_python_worker(
        repo,
        "scripts/ppe_desktop_auto_operator.py",
        "--repo-root",
        str(repo),
        "--daemon",
        "--poll-seconds",
        str(poll_seconds),
    )
    save_state(repo, {"daemon_pid": proc.pid, "poll_seconds": poll_seconds, "started_at": _utc_now()})
    append_log(repo, f"detached daemon pid={proc.pid}")
    return {"started": True, "pid": proc.pid}


def stop_daemon(repo: Path) -> dict[str, Any]:
    import subprocess

    from scripts.ppe_remote_agent_spawn import process_alive

    repo = repo.resolve()
    state = load_state(repo)
    pid = state.get("daemon_pid")
    killed: list[int] = []
    if pid is not None:
        try:
            pid_i = int(pid)
            if process_alive(pid_i):
                subprocess.run(["taskkill", "/PID", str(pid_i), "/F"], check=False)
                killed.append(pid_i)
        except (TypeError, ValueError, OSError):
            pass
    save_state(repo, {"daemon_pid": None, "stopped_at": _utc_now()})
    append_log(repo, f"daemon stop killed={killed}")
    return {"stopped": True, "killed": killed}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop auto-operator (BUILD/CONTINUE when appropriate)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--once", action="store_true", help="Single pass (same as pressing buttons when due)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--daemon", action="store_true", help="Foreground poll loop")
    ap.add_argument("--start", action="store_true", help="Start detached background daemon")
    ap.add_argument("--stop", action="store_true", help="Stop background daemon")
    ap.add_argument("--poll-seconds", type=int, default=DEFAULT_POLL_SECONDS)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if not desktop_auto_enabled(repo):
        print("ppe_desktop_auto: disabled (not daily-driver desktop)", file=sys.stderr)
        return 8

    if args.stop:
        result = stop_daemon(repo)
        print(json.dumps(result, indent=2))
        return 0
    if args.start:
        result = start_detached(repo, poll_seconds=args.poll_seconds)
        print(json.dumps(result, indent=2))
        return 0 if result.get("started") or result.get("reason") == "already running" else 1
    if args.daemon:
        return run_daemon(repo, poll_seconds=args.poll_seconds)

    result = auto_pass(repo, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
