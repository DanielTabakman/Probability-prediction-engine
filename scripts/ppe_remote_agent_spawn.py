"""Spawn detached PPE worker processes (Windows-safe)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def _detached_popen(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.Popen[Any]:
    kwargs: dict[str, Any] = {
        "cwd": cwd,
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
    else:
        kwargs["start_new_session"] = True
    return subprocess.Popen(cmd, **kwargs)


def spawn_python_worker(repo: Path, script_rel: str, *args: str) -> subprocess.Popen[Any]:
    repo = repo.resolve()
    script = repo / script_rel
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    cmd = [sys.executable, str(script), *args]
    return _detached_popen(cmd, cwd=repo, env=env)


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if sys.platform == "win32":
        try:
            import ctypes

            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259
            handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
            if not handle:
                return False
            try:
                exit_code = ctypes.c_ulong()
                if not ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                    return False
                return int(exit_code.value) == STILL_ACTIVE
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except (OSError, AttributeError):
            return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True
