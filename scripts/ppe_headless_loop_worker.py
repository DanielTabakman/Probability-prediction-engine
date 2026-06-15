"""Run the local auto-loop as a headless supervisor child (no visible console)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _hidden_flags() -> int:
    if sys.platform != "win32":
        return 0
    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS  # type: ignore[attr-defined]
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        flags |= subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    return flags


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Headless auto-loop worker")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    env.setdefault("PPE_OPERATOR_PROFILE", "local")
    env.setdefault("PPE_SKIP_ACP", "1")
    env.setdefault("PPE_WORKER_MODE", "deterministic")
    env["PPE_HEADLESS_SUPERVISED_LOOP"] = "1"

    script = repo / "run_ppe_auto_local_loop.cmd"
    if not script.is_file():
        print(f"ppe_headless_loop_worker: missing {script}", file=sys.stderr)
        return 1

    proc = subprocess.Popen(
        ["cmd", "/c", str(script)],
        cwd=repo,
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=_hidden_flags(),
    )
    return int(proc.wait())


if __name__ == "__main__":
    raise SystemExit(main())
