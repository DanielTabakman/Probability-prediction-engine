"""Desktop operator stack: queue bootstrap, process detection, ensure loop + watch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_operator_config import headless_stack_mode

LOOP_CMD_PATTERN = r"run_ppe_auto_local_loop|run_ppe_auto_loop\.cmd|ppe_headless_loop_worker\.py"
HEADLESS_SUPERVISOR_PATTERN = r"ppe_headless_stack_supervisor\.py"
WATCH_CMD_PATTERN = r"watch_operator_mobile\.ps1|ppe_watch_operator_mobile\.py"
LOCAL_TRIGGER_WATCHER_PATTERN = r"ppe_ide_build_local_watcher\.py|watch_ide_build_local\.cmd"
NTFY_CMD_PATTERN = r"ppe_ntfy_listen\.py|watch_ntfy_commands\.cmd"


def _powershell_process_match(pattern: str) -> bool:
    # Only match worker hosts (python/cmd). Excluding powershell.exe avoids false positives
    # when this probe's own -Command string contains the same regex literal.
    allowed = "@('python.exe','cmd.exe','pwsh.exe')"
    ps = (
        "$hits = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        f"Where-Object {{ $_.Name -in {allowed} -and $_.CommandLine -match '{pattern}' }}; "
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


def is_loop_running() -> bool:
    """True when the Windows auto-loop cmd wrapper is still alive."""
    return _powershell_process_match(LOOP_CMD_PATTERN)


def is_watch_running() -> bool:
    """True when the mobile watch process is still alive."""
    return _powershell_process_match(WATCH_CMD_PATTERN)


def is_local_trigger_watcher_running() -> bool:
    """True when the local IDE_BUILD trigger watcher is still alive."""
    return _powershell_process_match(LOCAL_TRIGGER_WATCHER_PATTERN)


def local_trigger_watcher_desired(repo: Path) -> bool:
    try:
        from scripts.ppe_ide_build_local_watcher import local_trigger_watcher_enabled

        return local_trigger_watcher_enabled(repo.resolve())
    except ImportError:
        return False


def is_ntfy_listen_running() -> bool:
    """True when the remote ntfy command listener is still alive."""
    from scripts.ppe_ntfy_commands import commands_enabled

    if not commands_enabled():
        return False
    return _powershell_process_match(NTFY_CMD_PATTERN)


def is_headless_supervisor_running() -> bool:
    return _powershell_process_match(HEADLESS_SUPERVISOR_PATTERN)


def stack_status(repo: Path | None = None) -> dict[str, bool]:
    loop = is_loop_running()
    watch = is_watch_running()
    ntfy_listen = is_ntfy_listen_running()
    local_watcher = is_local_trigger_watcher_running()
    watcher_desired = local_trigger_watcher_desired(repo) if repo is not None else False
    headless = is_headless_supervisor_running()
    stack_ok = loop and watch and (local_watcher or not watcher_desired)
    return {
        "loop_running": loop,
        "watch_running": watch,
        "ntfy_listen_running": ntfy_listen,
        "local_trigger_watcher_running": local_watcher,
        "local_trigger_watcher_desired": watcher_desired,
        "headless_supervisor_running": headless,
        "headless_mode": headless_stack_mode(repo) if repo is not None else False,
        "stack_running": stack_ok,
    }


def bootstrap_queue(repo: Path, *, apply: bool = True) -> dict[str, Any]:
    """Git pull (optional caller) + backlog propagate hook."""
    repo = repo.resolve()
    from scripts.ppe_propagate_queue import maybe_propagate_queue

    prop = maybe_propagate_queue(repo, apply=apply)
    return {"propagate": prop}


def _start_cmd_window(repo: Path, script_name: str, title: str) -> None:
    repo = repo.resolve()
    script = repo / script_name
    if not script.is_file():
        raise FileNotFoundError(f"Missing {script_name}")
    subprocess.Popen(
        ["cmd", "/c", "start", title, "cmd", "/k", "call", str(script)],
        cwd=repo,
        close_fds=True,
    )


def _ensure_headless(repo: Path) -> dict[str, Any]:
    from scripts.ppe_headless_stack_supervisor import ensure_headless_supervisor

    return ensure_headless_supervisor(repo, detach=True, start=True)


def start_full_stack(repo: Path) -> None:
    if headless_stack_mode(repo):
        _ensure_headless(repo)
        return
    _start_cmd_window(repo, "start_ppe_desktop_operator.cmd", "PPE desktop operator")


def start_watch_only(repo: Path) -> None:
    if headless_stack_mode(repo):
        _ensure_headless(repo)
        return
    _start_cmd_window(repo, "watch_operator_mobile.cmd", "PPE mobile watch")


def start_loop_only(repo: Path) -> None:
    if headless_stack_mode(repo):
        _ensure_headless(repo)
        return
    _start_cmd_window(repo, "run_ppe_auto_local_loop.cmd", "PPE auto loop")


def start_ntfy_listen_only(repo: Path) -> None:
    if headless_stack_mode(repo):
        _ensure_headless(repo)
        return
    _start_cmd_window(repo, "watch_ntfy_commands.cmd", "PPE ntfy commands")


def start_local_trigger_watcher_only(repo: Path) -> None:
    if headless_stack_mode(repo):
        _ensure_headless(repo)
        return
    _start_cmd_window(repo, "watch_ide_build_local.cmd", "PPE IDE BUILD watcher")


def restart_stack(repo: Path) -> dict[str, Any]:
    from scripts.ppe_ntfy_commands import stop_stack_processes

    killed = stop_stack_processes()
    if headless_stack_mode(repo):
        from scripts.ppe_headless_stack_supervisor import clear_state

        clear_state(repo)
    import time

    time.sleep(2)
    return {**ensure_stack(repo, start=True), "killed": killed, "restarted": True}


def ensure_stack(repo: Path, *, start: bool = True) -> dict[str, Any]:
    """Ensure auto-loop + mobile watch are running; start missing pieces when allowed."""
    repo = repo.resolve()
    if start:
        from scripts.ppe_loop_host_guard import loop_host_blocked

        blocked = loop_host_blocked()
        if blocked:
            before = stack_status(repo)
            return {**before, "started": [], "action": "loop_host_blocked", **blocked}
    if headless_stack_mode(repo):
        if not start:
            before = stack_status(repo)
            return {**before, "started": [], "action": "not_started"}
        from scripts.ppe_headless_stack_supervisor import ensure_headless_supervisor

        return ensure_headless_supervisor(repo, detach=True, start=True)

    before = stack_status(repo)
    started: list[str] = []
    from scripts.ppe_ntfy_commands import commands_enabled

    def _ensure_extras(after: dict[str, bool]) -> dict[str, bool]:
        nonlocal started
        if commands_enabled() and start and not after.get("ntfy_listen_running"):
            start_ntfy_listen_only(repo)
            started.append("ntfy_listen")
            after = stack_status(repo)
        if after.get("local_trigger_watcher_desired") and start and not after.get("local_trigger_watcher_running"):
            start_local_trigger_watcher_only(repo)
            started.append("local_trigger_watcher")
            after = stack_status(repo)
        return after

    if before["stack_running"]:
        after = _ensure_extras(before)
        return {**after, "started": started, "action": ",".join(started) or "none"}

    if not start:
        return {**before, "started": started, "action": "not_started"}

    if before["loop_running"] and not before["watch_running"]:
        start_watch_only(repo)
        started.append("watch")
    elif not before["loop_running"]:
        if before["watch_running"]:
            start_loop_only(repo)
            started.append("loop")
        else:
            start_full_stack(repo)
            started.append("stack")

    after = _ensure_extras(stack_status(repo))
    return {**after, "started": started, "action": ",".join(started) or "none"}


def collect_status(repo: Path, *, apply_propagate: bool = True, ensure: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    out: dict[str, Any] = {"repo_root": str(repo)}
    if apply_propagate:
        out["queue"] = bootstrap_queue(repo, apply=True)
    out["stack"] = ensure_stack(repo, start=ensure)
    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    proc = subprocess.run(
        [sys.executable, str(repo / "scripts" / "ppe_operator_status.py"), "--repo-root", str(repo), "--brief"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    out["operator_brief"] = (proc.stdout or "").strip()
    out["operator_exit"] = proc.returncode
    try:
        from scripts.ppe_autobuilder import collect_autobuilder_status, write_status_artifact

        write_status_artifact(repo, collect_autobuilder_status(repo))
    except Exception:
        pass
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE desktop operator stack (queue + loop + watch)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--ensure", action="store_true", help="Start loop/watch if not running")
    ap.add_argument("--status", action="store_true", help="Status only (no stack start unless --ensure too)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--no-propagate", action="store_true", help="Skip backlog propagate")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    result = collect_status(repo, apply_propagate=not args.no_propagate, ensure=args.ensure)

    if args.json or args.status:
        print(json.dumps(result, indent=2))
    else:
        stack = result["stack"]
        print(f"stack: loop={stack['loop_running']} watch={stack['watch_running']} action={stack.get('action')}")
        if result.get("queue"):
            prop = result["queue"].get("propagate") or {}
            reason = prop.get("reason") or prop.get("chapterId") or "ok"
            print(f"queue: propagated={prop.get('propagated')} reason={reason}")
        if result.get("operator_brief"):
            print(result["operator_brief"])

    stack = result["stack"]
    if args.ensure and stack.get("action") not in (None, "none", "not_started"):
        return 0 if stack.get("loop_running") or stack.get("started") else 1
    return 0 if result.get("operator_exit") in (0, 7) else int(result.get("operator_exit") or 1)


if __name__ == "__main__":
    raise SystemExit(main())
