"""Spawn a detached watch_active_run.py for the current wrapper process."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    if os.environ.get("PPE_WATCH", "").strip().lower() in {"0", "false", "no"}:
        return 0
    if len(sys.argv) < 2:
        print("usage: spawn_active_run_watch.py <repoRoot> [planPath]", file=sys.stderr)
        return 2

    repo = Path(sys.argv[1]).resolve()
    plan = sys.argv[2] if len(sys.argv) > 2 else ""
    script = repo / "scripts" / "watch_active_run.py"
    if not script.is_file():
        return 0

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    # parent PID is read from ACTIVE_RUN.wrapper_pid (cmd.exe running the wrapper).
    cmd = [
        sys.executable,
        str(script),
        "--repo-root",
        str(repo),
        "--parent-pid",
        "0",
        "--plan-path",
        plan,
    ]
    kwargs: dict = {"cwd": repo, "env": env}
    if os.name == "nt":
        # Detached so run_phase.cmd can exit without killing the watcher.
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | getattr(
            subprocess, "DETACHED_PROCESS", 0
        )
        if flags:
            kwargs["creationflags"] = flags
    subprocess.Popen(cmd, **kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
