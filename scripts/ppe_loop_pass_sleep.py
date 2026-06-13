"""Adaptive sleep between auto-loop passes — minimize unplanned idle time."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_operator_status import (
    VERDICT_IDE_BUILD,
    VERDICT_RUN_AUTO,
    VERDICT_RUN_LOCAL,
    VERDICT_SUPPLY_LOW,
    collect_operator_status,
)


def loop_pass_sleep_seconds(
    repo: Path,
    *,
    reason: str = "idle",
) -> int:
    repo = repo.resolve()
    try:
        from scripts.ppe_operator_maintenance import is_maintenance_active

        if is_maintenance_active(repo):
            from scripts.ppe_operator_config import maintenance_loop_sleep_seconds

            return maintenance_loop_sleep_seconds(repo)
    except ImportError:
        pass

    from scripts.ppe_operator_config import (
        guard_stop_sleep_seconds,
        idle_sleep_seconds,
        min_loop_sleep_seconds,
        supply_low_sleep_seconds,
        worker_poll_sleep_seconds,
    )

    min_sleep = min_loop_sleep_seconds(repo)
    worker_poll = worker_poll_sleep_seconds(repo)

    try:
        from scripts.ppe_auto_run_local import run_local_worker_running

        if run_local_worker_running(repo):
            return worker_poll
    except ImportError:
        pass

    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        if read_build_lock(repo):
            return worker_poll
    except ImportError:
        pass

    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if active.is_file():
        return worker_poll

    if reason in ("guard_stop", "failure"):
        return max(min_sleep, min(guard_stop_sleep_seconds(repo), 30))

    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "")

    if verdict in (VERDICT_RUN_LOCAL, VERDICT_IDE_BUILD, VERDICT_RUN_AUTO):
        return min_sleep

    if verdict == VERDICT_SUPPLY_LOW:
        return max(min_sleep, supply_low_sleep_seconds(repo))

    return max(min_sleep, idle_sleep_seconds(repo))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Seconds to sleep before next auto-loop pass")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--reason",
        choices=("idle", "guard_stop", "failure"),
        default="idle",
        help="Why the loop is sleeping",
    )
    args = ap.parse_args(argv)
    seconds = loop_pass_sleep_seconds(args.repo_root.resolve(), reason=args.reason)
    print(max(3, int(seconds)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
