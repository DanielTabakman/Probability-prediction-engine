"""Run the local auto-loop as a headless supervisor child (no visible console)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _hidden_flags() -> int:
    from scripts.ppe_remote_agent_spawn import _win32_hidden_flags

    return _win32_hidden_flags()


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
    env.setdefault("PPE_STACK_HEADLESS", "1")
    env["PPE_HEADLESS_SUPERVISED_LOOP"] = "1"

    entry = repo / "scripts" / "ppe_headless_auto_loop_entry.py"
    if not entry.is_file():
        print(f"ppe_headless_loop_worker: missing {entry}", file=sys.stderr)
        return 1

    proc = subprocess.Popen(
        [sys.executable, str(entry), "--repo-root", str(repo)],
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
