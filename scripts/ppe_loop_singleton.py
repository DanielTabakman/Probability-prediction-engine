"""Refuse to start a second run_ppe_auto_loop for the same repo (multi-clone safe)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_lock(lock_path: Path) -> dict:
    if not lock_path.is_file():
        return {}
    try:
        data = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _lock_holder_alive(lock: dict) -> bool:
    pid = lock.get("pid")
    if pid is None:
        return False
    try:
        from scripts.ppe_remote_agent_spawn import process_alive

        return process_alive(int(pid))
    except (TypeError, ValueError):
        return False


def claim_loop_lock(repo: Path) -> tuple[bool, str]:
    """Claim per-repo loop lock. Returns (ok, detail)."""
    from scripts.ppe_operator_instance import loop_lock_path

    repo = repo.resolve()
    lock_path = loop_lock_path(repo)
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _read_lock(lock_path)
    if existing and _lock_holder_alive(existing):
        return False, f"lock held by pid {existing.get('pid')}"
    lock_path.write_text(
        json.dumps(
            {
                "pid": os.getpid(),
                "repo_root": str(repo),
                "started_at": _utc_now(),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return True, "claimed"


def release_loop_lock(repo: Path) -> None:
    from scripts.ppe_operator_instance import loop_lock_path

    lock_path = loop_lock_path(repo.resolve())
    lock = _read_lock(lock_path)
    if lock.get("pid") == os.getpid():
        lock_path.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Single-instance guard for run_ppe_auto_loop (per repo)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--release", action="store_true", help="Release lock for this pid")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.release:
        release_loop_lock(repo)
        return 0

    if os.environ.get("PPE_HEADLESS_SUPERVISED_LOOP", "").strip() == "1":
        return 0

    ok, detail = claim_loop_lock(repo)
    if ok:
        return 0

    from scripts.ppe_desktop_operator_stack import is_loop_running_for_repo

    if is_loop_running_for_repo(repo):
        print(
            f"ppe_loop_singleton: another run_ppe_auto_loop is already running for {repo}",
            file=sys.stderr,
        )
        return 1

    # Stale lock — reclaim
    claim_loop_lock(repo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
