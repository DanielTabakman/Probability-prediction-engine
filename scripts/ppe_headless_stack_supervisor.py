"""Headless desktop operator stack — one supervisor, detached workers, log files only."""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, BinaryIO, TextIO

from scripts.ppe_desktop_operator_stack import (
    LOCAL_TRIGGER_WATCHER_PATTERN,
    LOOP_CMD_PATTERN,
    NTFY_CMD_PATTERN,
    WATCH_CMD_PATTERN,
    _powershell_process_match,
    local_trigger_watcher_desired,
    stack_status,
)
from scripts.ppe_ntfy_commands import commands_enabled
from scripts.ppe_operator_config import headless_stack_mode
from scripts.ppe_remote_agent_spawn import process_alive, spawn_detached_logged

STATE_REL = "artifacts/orchestrator/HEADLESS_STACK_SUPERVISOR.json"
SPAWN_LOCK_REL = "artifacts/orchestrator/HEADLESS_STACK_SPAWN.lock"
SUPERVISOR_LOG_REL = "artifacts/orchestrator/HEADLESS_STACK_SUPERVISOR.log"
DEFAULT_POLL_SECONDS = 30
DEFAULT_WATCH_INTERVAL = 300


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def state_path(repo: Path) -> Path:
    return (repo / STATE_REL).resolve()


def supervisor_log_path(repo: Path) -> Path:
    return (repo / SUPERVISOR_LOG_REL).resolve()


def worker_log_path(repo: Path, name: str) -> Path:
    return (repo / "artifacts" / "orchestrator" / f"HEADLESS_STACK_{name.upper()}.log").resolve()


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


def clear_state(repo: Path) -> None:
    path = state_path(repo)
    if path.is_file():
        path.unlink(missing_ok=True)
    spawn_lock_path(repo).unlink(missing_ok=True)


def spawn_lock_path(repo: Path) -> Path:
    return (repo / SPAWN_LOCK_REL).resolve()


def try_acquire_spawn_lock(repo: Path, *, timeout_sec: float = 30.0) -> bool:
    path = spawn_lock_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode("ascii", errors="replace"))
            os.close(fd)
            return True
        except FileExistsError:
            if not is_supervisor_running(repo):
                path.unlink(missing_ok=True)
            time.sleep(0.5)
    return False


def release_spawn_lock(repo: Path) -> None:
    spawn_lock_path(repo).unlink(missing_ok=True)


def append_supervisor_log(repo: Path, line: str) -> None:
    path = supervisor_log_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{_utc_now()} {line}\n")


def is_supervisor_running(repo: Path) -> bool:
    state = load_state(repo)
    pid = state.get("supervisor_pid")
    if pid is None:
        return False
    try:
        return process_alive(int(pid))
    except (TypeError, ValueError):
        return False


def _operator_env(repo: Path) -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo.resolve())
    env.setdefault("PPE_OPERATOR_PROFILE", "local")
    env.setdefault("PPE_SKIP_ACP", "1")
    env.setdefault("PPE_WORKER_MODE", "deterministic")
    env.setdefault("PPE_STACK_HEADLESS", "1")
    return env


def _worker_env(repo: Path, spec: WorkerSpec) -> dict[str, str]:
    env = _operator_env(repo)
    if spec.name == "loop":
        env["PPE_HEADLESS_SUPERVISED_LOOP"] = "1"
    return env


@dataclass(frozen=True)
class WorkerSpec:
    name: str
    pattern: str
    required: bool

    def build_cmd(self, repo: Path) -> list[str]:
        repo = repo.resolve()
        py = sys.executable
        if self.name == "loop":
            return [
                py,
                str(repo / "scripts" / "ppe_headless_loop_worker.py"),
                "--repo-root",
                str(repo),
            ]
        if self.name == "watch":
            return [
                py,
                str(repo / "scripts" / "ppe_watch_operator_mobile.py"),
                "--repo-root",
                str(repo),
                "--interval",
                str(DEFAULT_WATCH_INTERVAL),
            ]
        if self.name == "ntfy_listen":
            return [py, str(repo / "scripts" / "ppe_ntfy_listen.py"), "--repo-root", str(repo)]
        if self.name == "local_trigger_watcher":
            return [py, str(repo / "scripts" / "ppe_ide_build_local_watcher.py"), "--repo-root", str(repo)]
        raise ValueError(f"unknown worker: {self.name}")


def worker_specs(repo: Path) -> list[WorkerSpec]:
    repo = repo.resolve()
    specs = [
        WorkerSpec("loop", LOOP_CMD_PATTERN, True),
        WorkerSpec("watch", WATCH_CMD_PATTERN, True),
        WorkerSpec("ntfy_listen", NTFY_CMD_PATTERN, commands_enabled()),
        WorkerSpec(
            "local_trigger_watcher",
            LOCAL_TRIGGER_WATCHER_PATTERN,
            local_trigger_watcher_desired(repo),
        ),
    ]
    return [spec for spec in specs if spec.required]


def worker_running(repo: Path, spec: WorkerSpec, state: dict[str, Any] | None = None) -> bool:
    if state is not None:
        workers = state.get("workers")
        if isinstance(workers, dict):
            pid = workers.get(spec.name)
            if pid is not None:
                try:
                    if process_alive(int(pid)):
                        return True
                except (TypeError, ValueError):
                    pass
    return _powershell_process_match(spec.pattern)


def spawn_worker(
    repo: Path,
    spec: WorkerSpec,
    *,
    log_handles: list[TextIO | BinaryIO],
) -> int:
    proc = spawn_detached_logged(
        spec.build_cmd(repo),
        cwd=repo.resolve(),
        env=_worker_env(repo, spec),
        log_path=worker_log_path(repo, spec.name),
        log_handles=log_handles,
    )
    append_supervisor_log(repo, f"spawned {spec.name} pid={proc.pid}")
    return int(proc.pid)


def stop_tracked_workers(repo: Path, state: dict[str, Any]) -> int:
    killed = 0
    workers = state.get("workers")
    if isinstance(workers, dict):
        for pid in workers.values():
            try:
                if process_alive(int(pid)):
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
            except (OSError, TypeError, ValueError):
                pass
    return killed


def ensure_workers(
    repo: Path,
    *,
    log_handles: list[TextIO | BinaryIO],
    state: dict[str, Any],
) -> dict[str, int]:
    workers: dict[str, int] = {}
    if isinstance(state.get("workers"), dict):
        workers = {str(k): int(v) for k, v in state["workers"].items() if v is not None}

    spawned: dict[str, int] = {}
    for spec in worker_specs(repo):
        tracked = workers.get(spec.name)
        if tracked is not None and process_alive(tracked):
            workers[spec.name] = tracked
            continue
        if worker_running(repo, spec, state):
            continue
        pid = spawn_worker(repo, spec, log_handles=log_handles)
        workers[spec.name] = pid
        spawned[spec.name] = pid
    state["workers"] = workers
    save_state(repo, state)
    return spawned


def run_supervisor(repo: Path, *, poll_seconds: int = DEFAULT_POLL_SECONDS) -> int:
    repo = repo.resolve()
    if not headless_stack_mode(repo):
        print(
            "ppe_headless_stack_supervisor: headless mode disabled "
            "(set desktopStack.mode=headless or PPE_STACK_HEADLESS=1)",
            file=sys.stderr,
        )
        return 1

    from scripts.ppe_loop_host_guard import require_loop_host

    require_loop_host()

    if is_supervisor_running(repo):
        existing = load_state(repo)
        print(
            f"ppe_headless_stack_supervisor: already running pid={existing.get('supervisor_pid')}",
            file=sys.stderr,
        )
        return 1

    existing = load_state(repo)
    other_pid = existing.get("supervisor_pid")
    if other_pid is not None:
        try:
            other = int(other_pid)
            if other != os.getpid() and process_alive(other):
                print(
                    f"ppe_headless_stack_supervisor: another supervisor pid={other} is active",
                    file=sys.stderr,
                )
                return 1
        except (TypeError, ValueError):
            pass

    log_handles: list[TextIO | BinaryIO] = []
    state: dict[str, Any] = {
        "supervisor_pid": os.getpid(),
        "mode": "headless",
        "started_at": _utc_now(),
        "workers": {},
    }
    save_state(repo, state)

    def _shutdown(signum: int | None = None, _frame: Any = None) -> None:
        _ = signum
        append_supervisor_log(repo, "shutdown requested")
        stop_tracked_workers(repo, state)
        clear_state(repo)
        for handle in log_handles:
            try:
                handle.close()
            except OSError:
                pass
        raise SystemExit(0)

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    append_supervisor_log(repo, f"supervisor start pid={os.getpid()}")
    print(
        "ppe_headless_stack_supervisor: running — one terminal, detached workers, logs under artifacts/orchestrator/",
        flush=True,
    )
    print("Ctrl+C to stop supervisor and workers.", flush=True)

    spawned = ensure_workers(repo, log_handles=log_handles, state=state)
    if spawned:
        print(f"started workers: {', '.join(spawned)}", flush=True)

    poll_ticks = 0
    while True:
        time.sleep(max(5, poll_seconds))
        poll_ticks += 1
        if poll_ticks % 20 == 0:
            try:
                from scripts.ppe_vm_watchdog import maybe_supervisor_tick

                maybe_supervisor_tick(repo)
            except Exception as exc:
                append_supervisor_log(repo, f"watchdog tick failed: {exc}")
        spawned = ensure_workers(repo, log_handles=log_handles, state=state)
        if spawned:
            print(f"restarted workers: {', '.join(spawned)}", flush=True)


def ensure_headless_supervisor(
    repo: Path,
    *,
    detach: bool = False,
    start: bool = True,
) -> dict[str, Any]:
    """Start or verify the headless supervisor and worker stack."""
    repo = repo.resolve()
    if start:
        from scripts.ppe_loop_host_guard import loop_host_blocked

        blocked = loop_host_blocked()
        if blocked:
            status = stack_status(repo)
            return {
                **status,
                "headless": True,
                "supervisor_running": is_supervisor_running(repo),
                "started": [],
                "action": "loop_host_blocked",
                **blocked,
            }
    if not start:
        status = stack_status(repo)
        return {
            **status,
            "headless": True,
            "supervisor_running": is_supervisor_running(repo),
            "started": [],
            "action": "not_started",
        }

    if is_supervisor_running(repo):
        status = stack_status(repo)
        return {
            **status,
            "headless": True,
            "supervisor_running": True,
            "started": [],
            "action": "none",
        }

    from scripts.ppe_loop_host_guard import loop_host_blocked

    blocked = loop_host_blocked()
    if blocked:
        status = stack_status(repo)
        return {
            **status,
            "headless": True,
            "supervisor_running": False,
            "started": [],
            "action": "loop_host_blocked",
            **blocked,
        }

    if not try_acquire_spawn_lock(repo):
        status = stack_status(repo)
        return {
            **status,
            "headless": True,
            "supervisor_running": is_supervisor_running(repo),
            "started": [],
            "action": "spawn_locked",
        }

    try:
        if detach:
            env = _operator_env(repo)
            proc = spawn_detached_logged(
                [
                    sys.executable,
                    str(repo / "scripts" / "ppe_headless_stack_supervisor.py"),
                    "--repo-root",
                    str(repo),
                ],
                cwd=repo,
                env=env,
                log_path=supervisor_log_path(repo),
            )
            time.sleep(2)
            running = is_supervisor_running(repo)
            status = stack_status(repo)
            return {
                **status,
                "headless": True,
                "supervisor_running": running,
                "supervisor_pid": proc.pid,
                "started": ["headless_supervisor"] if running else [],
                "action": "headless_supervisor" if running else "headless_supervisor_failed",
            }

        raise RuntimeError("foreground supervisor requires run_ppe_headless_stack.cmd")
    finally:
        release_spawn_lock(repo)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Headless PPE desktop operator stack supervisor")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--poll", type=int, default=DEFAULT_POLL_SECONDS, help="Worker health poll interval")
    ap.add_argument("--ensure", action="store_true", help="Start detached supervisor if not running")
    ap.add_argument("--stop", action="store_true", help="Stop supervisor state and tracked workers")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()

    if args.stop:
        state = load_state(repo)
        killed = stop_tracked_workers(repo, state)
        if state.get("supervisor_pid") is not None:
            try:
                pid = int(state["supervisor_pid"])
                if process_alive(pid):
                    os.kill(pid, signal.SIGTERM)
                    killed += 1
            except (OSError, TypeError, ValueError):
                pass
        clear_state(repo)
        from scripts.ppe_ntfy_commands import stop_stack_processes

        killed += stop_stack_processes()
        print(json.dumps({"stopped": True, "killed": killed}))
        return 0

    if args.ensure:
        result = ensure_headless_supervisor(repo, detach=True, start=True)
        print(json.dumps(result, indent=2))
        return 0 if result.get("supervisor_running") or result.get("stack_running") else 1

    try:
        return run_supervisor(repo, poll_seconds=args.poll)
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
