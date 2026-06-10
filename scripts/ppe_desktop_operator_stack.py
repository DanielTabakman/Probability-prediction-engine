"""Desktop operator stack: queue bootstrap, process detection, ensure loop + watch."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

LOOP_CMD_PATTERN = r"run_ppe_auto_local_loop|run_ppe_auto_loop\.cmd"
WATCH_CMD_PATTERN = r"watch_operator_mobile\.ps1|ppe_watch_operator_mobile\.py"
NTFY_CMD_PATTERN = r"ppe_ntfy_listen\.py|watch_ntfy_commands\.cmd"


def _powershell_process_match(pattern: str) -> bool:
    ps = (
        "$hits = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        f"Where-Object {{ $_.CommandLine -match '{pattern}' }}; "
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


def is_ntfy_listen_running() -> bool:
    """True when the remote ntfy command listener is still alive."""
    from scripts.ppe_ntfy_commands import commands_enabled

    if not commands_enabled():
        return False
    return _powershell_process_match(NTFY_CMD_PATTERN)


def stack_status() -> dict[str, bool]:
    loop = is_loop_running()
    watch = is_watch_running()
    ntfy_listen = is_ntfy_listen_running()
    return {
        "loop_running": loop,
        "watch_running": watch,
        "ntfy_listen_running": ntfy_listen,
        "stack_running": loop and watch,
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


def start_full_stack(repo: Path) -> None:
    _start_cmd_window(repo, "start_ppe_desktop_operator.cmd", "PPE desktop operator")


def start_watch_only(repo: Path) -> None:
    _start_cmd_window(repo, "watch_operator_mobile.cmd", "PPE mobile watch")


def start_loop_only(repo: Path) -> None:
    _start_cmd_window(repo, "run_ppe_auto_local_loop.cmd", "PPE auto loop")


def start_ntfy_listen_only(repo: Path) -> None:
    _start_cmd_window(repo, "watch_ntfy_commands.cmd", "PPE ntfy commands")


def restart_stack(repo: Path) -> dict[str, Any]:
    from scripts.ppe_ntfy_commands import stop_stack_processes

    killed = stop_stack_processes()
    import time

    time.sleep(2)
    return {**ensure_stack(repo, start=True), "killed": killed, "restarted": True}


def ensure_stack(repo: Path, *, start: bool = True) -> dict[str, Any]:
    """Ensure auto-loop + mobile watch are running; start missing pieces when allowed."""
    before = stack_status()
    started: list[str] = []
    from scripts.ppe_ntfy_commands import commands_enabled

    if before["stack_running"]:
        after = before
        if commands_enabled() and start and not after.get("ntfy_listen_running"):
            start_ntfy_listen_only(repo)
            started.append("ntfy_listen")
            after = stack_status()
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

    after = stack_status()
    if commands_enabled() and start and not after.get("ntfy_listen_running"):
        start_ntfy_listen_only(repo)
        started.append("ntfy_listen")
        after = stack_status()

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

    if args.ensure and not args.status:
        try:
            from scripts.ppe_watch_operator_mobile import push_stack_status_notify

            stack = result["stack"]
            brief = result.get("operator_brief") or ""
            verdict = "RUNNING"
            for part in brief.split():
                if part.startswith("VERDICT="):
                    verdict = part.split("=", 1)[1]
            if stack.get("stack_running") or stack.get("loop_running"):
                push_stack_status_notify(
                    repo,
                    verdict=verdict.replace("VERDICT=", "") if verdict.startswith("VERDICT=") else verdict,
                    loop_running=bool(stack.get("loop_running")),
                    watch_running=bool(stack.get("watch_running")),
                    reason="startup",
                )
        except Exception:
            pass

    stack = result["stack"]
    if args.ensure and stack.get("action") not in (None, "none", "not_started"):
        return 0 if stack.get("loop_running") or stack.get("started") else 1
    return 0 if result.get("operator_exit") in (0, 7) else int(result.get("operator_exit") or 1)


if __name__ == "__main__":
    raise SystemExit(main())
