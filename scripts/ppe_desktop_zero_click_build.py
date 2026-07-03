"""Desktop zero-click IDE BUILD — local trigger watcher + auto handoff (VM loop + desktop BUILD)."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_desktop_operator_stack import (
    is_local_trigger_watcher_running,
    local_trigger_watcher_desired,
)
from scripts.ppe_operator_shortcuts import detect_role, ensure_shortcuts
from scripts.ppe_remote_agent import agent_available, resolve_agent_cli

STATE_REL = "artifacts/orchestrator/DESKTOP_ZERO_CLICK_BUILD.json"
LOG_REL = "artifacts/orchestrator/DESKTOP_ZERO_CLICK_BUILD.log"
OPT_IN_FILE = "ppe_operator_desktop_auto.local.cmd"
OPT_IN_EXAMPLE = "ppe_operator_desktop_auto.local.cmd.example"
NO_LOOP_FILE = "ppe_operator_no_loop.local.cmd"
NO_LOOP_EXAMPLE = "ppe_operator_no_loop.local.cmd.example"


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


def zero_click_desired(repo: Path) -> bool:
    """Zero-click is for daily-driver desktop only (VM runs the relay loop)."""
    repo = repo.resolve()
    if detect_role(repo) != "daily_driver":
        return False
    return (repo / OPT_IN_FILE).is_file()


def ensure_opt_in_token(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    target = repo / OPT_IN_FILE
    if target.is_file():
        patched = _patch_opt_in_auto_dispatch(target)
        return {"ok": True, "action": patched or "already_present", "path": str(target)}
    example = repo / OPT_IN_EXAMPLE
    if not example.is_file():
        return {"ok": False, "action": "missing_example", "path": str(example)}
    target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    _patch_opt_in_auto_dispatch(target)
    return {"ok": True, "action": "created", "path": str(target)}


def _patch_opt_in_auto_dispatch(path: Path) -> str | None:
    """Add PPE_AUTO_DISPATCH=1 to opt-in cmd when missing."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("SET ") and "PPE_AUTO_DISPATCH" in stripped.upper():
            return None
    path.write_text(text.rstrip() + '\nset "PPE_AUTO_DISPATCH=1"\n', encoding="utf-8")
    return "patched_auto_dispatch"


def ensure_no_loop_guard(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    target = repo / NO_LOOP_FILE
    if target.is_file():
        return {"ok": True, "action": "already_present", "path": str(target)}
    example = repo / NO_LOOP_EXAMPLE
    if not example.is_file():
        return {"ok": False, "action": "missing_example", "path": str(example)}
    target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    return {"ok": True, "action": "created", "path": str(target)}


def check_agent_cli() -> dict[str, Any]:
    exe = resolve_agent_cli()
    if not exe:
        return {
            "ok": False,
            "code": "AGENT_MISSING",
            "fix": "Run setup_cursor_agent.cmd then agent login",
        }
    proc = subprocess.run(
        [exe, "status"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or "Not logged in" in out:
        return {
            "ok": False,
            "code": "AGENT_NOT_LOGGED_IN",
            "exe": exe,
            "fix": "Run: agent login",
        }
    return {"ok": True, "code": "OK", "exe": exe}


def start_watcher_detached(repo: Path) -> dict[str, Any]:
    from scripts.ppe_remote_agent_spawn import process_alive, spawn_python_worker

    repo = repo.resolve()
    state = load_state(repo)
    pid = state.get("watcher_pid")
    if pid is not None:
        try:
            if process_alive(int(pid)):
                return {"started": False, "reason": "watcher already running", "pid": int(pid)}
        except (TypeError, ValueError):
            pass

    if is_local_trigger_watcher_running():
        return {"started": False, "reason": "watcher process detected"}

    if not local_trigger_watcher_desired(repo):
        return {"started": False, "reason": "local trigger watcher disabled in config"}

    proc = spawn_python_worker(
        repo,
        "scripts/ppe_ide_build_local_watcher.py",
        "--repo-root",
        str(repo),
    )
    save_state(repo, {**state, "watcher_pid": proc.pid, "watcher_started_at": _utc_now()})
    append_log(repo, f"watcher detached pid={proc.pid}")
    return {"started": True, "pid": proc.pid}


def stop_watcher(repo: Path) -> dict[str, Any]:
    from scripts.ppe_remote_agent_spawn import process_alive

    repo = repo.resolve()
    state = load_state(repo)
    killed: list[int] = []
    pid = state.get("watcher_pid")
    if pid is not None:
        try:
            pid_i = int(pid)
            if process_alive(pid_i):
                subprocess.run(["taskkill", "/PID", str(pid_i), "/F"], check=False)
                killed.append(pid_i)
        except (TypeError, ValueError, OSError):
            pass
    save_state(repo, {**state, "watcher_pid": None, "watcher_stopped_at": _utc_now()})
    append_log(repo, f"watcher stop killed={killed}")
    return {"stopped": True, "killed": killed}


def collect_status(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    agent = check_agent_cli()
    return {
        "role": detect_role(repo),
        "zero_click_desired": zero_click_desired(repo),
        "watcher_desired": local_trigger_watcher_desired(repo),
        "watcher_running": is_local_trigger_watcher_running(),
        "watcher_pid": load_state(repo).get("watcher_pid"),
        "agent": agent,
        "agent_available": agent_available(),
    }


def setup(repo: Path, *, install_logon: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    steps: list[dict[str, Any]] = []

    no_loop = ensure_no_loop_guard(repo)
    steps.append({"step": "no_loop_guard", **no_loop})

    opt_in = ensure_opt_in_token(repo)
    steps.append({"step": "desktop_auto_opt_in", **opt_in})

    agent = check_agent_cli()
    steps.append({"step": "agent_cli", **agent})

    shortcuts = ensure_shortcuts(repo, quiet=True)
    steps.append({"step": "shortcuts", **shortcuts})

    logon: dict[str, Any] = {"skipped": True}
    if install_logon:
        proc = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(repo / "scripts" / "install_ppe_desktop_zero_click_task.ps1"),
                "-RepoRoot",
                str(repo),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        logon = {
            "ok": proc.returncode == 0,
            "stdout": (proc.stdout or "").strip(),
            "stderr": (proc.stderr or "").strip(),
        }
    steps.append({"step": "logon_task", **logon})

    ok = all(
        s.get("ok", True)
        for s in steps
        if s["step"] in ("no_loop_guard", "desktop_auto_opt_in", "agent_cli")
    )
    return {"ok": ok, "steps": steps, "status": collect_status(repo)}


def start(repo: Path, *, poll_seconds: int = 120) -> dict[str, Any]:
    repo = repo.resolve()
    if not zero_click_desired(repo):
        return {
            "ok": False,
            "reason": f"missing {OPT_IN_FILE} — run setup_desktop_zero_click_build.cmd first",
        }

    os.environ.setdefault("PPE_DESKTOP_AUTO", "1")
    os.environ.setdefault("PPE_AUTO_DISPATCH", "1")
    from scripts.ppe_desktop_auto_operator import start_detached as start_auto

    watcher = start_watcher_detached(repo)
    auto = start_auto(repo, poll_seconds=poll_seconds)
    monitor: dict[str, Any] = {"skipped": True}
    try:
        from scripts.ppe_in_flight_monitor import maybe_start_monitor_daemon

        monitor = maybe_start_monitor_daemon(repo, auto_act=True)
    except Exception as exc:
        monitor = {"started": False, "error": str(exc)}
    append_log(repo, f"start watcher={watcher} auto={auto} monitor={monitor}")
    status = collect_status(repo)
    return {
        "ok": True,
        "watcher": watcher,
        "auto_operator": auto,
        "monitor_daemon": monitor,
        "status": status,
    }


def stop(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    from scripts.ppe_desktop_auto_operator import stop_daemon as stop_auto

    watcher = stop_watcher(repo)
    auto = stop_auto(repo)
    append_log(repo, f"stop watcher={watcher} auto={auto}")
    return {"ok": True, "watcher": watcher, "auto_operator": auto}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop zero-click IDE BUILD stack")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--setup", action="store_true", help="One-time prerequisites + shortcuts")
    ap.add_argument("--install-logon", action="store_true", help="With --setup: register logon task")
    ap.add_argument("--start", action="store_true", help="Start watcher + auto-operator daemons")
    ap.add_argument("--stop", action="store_true", help="Stop watcher + auto-operator daemons")
    ap.add_argument("--status", action="store_true", help="Print JSON status")
    ap.add_argument("--poll-seconds", type=int, default=120)
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()

    if args.setup:
        result = setup(repo, install_logon=args.install_logon)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    if args.stop:
        result = stop(repo)
        print(json.dumps(result, indent=2))
        return 0

    if args.start:
        result = start(repo, poll_seconds=args.poll_seconds)
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    if args.status or not any((args.setup, args.start, args.stop)):
        result = collect_status(repo)
        print(json.dumps(result, indent=2))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
