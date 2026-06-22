"""One loop-iteration preflight: heal stale state and auto-run RUN_LOCAL finish passes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_active_run import heal_stale_running_manifest
from scripts.ppe_operator_status import VERDICT_RUN_LOCAL, VERDICT_STALE_STATE, collect_operator_status

# Skip run_ppe_auto for this iteration (handled run-local or waiting on detached worker).
EXIT_PASS_HANDLED = 8


def run_loop_pass(repo: Path) -> int:
    """Return 0 to proceed to run_ppe_auto; 7 guard stop; 8 pass handled."""
    try:
        from scripts.ppe_autobuilder import try_autobuilder_happy_path

        hp = try_autobuilder_happy_path(repo)
        if hp and not hp.get("skipped"):
            action = str(hp.get("action") or "")
            if action == "run-local" and hp.get("started"):
                print("ppe_operator_loop_pass: happy_path run-local started")
                return EXIT_PASS_HANDLED
            if action in ("finish-pending", "retry-build", "handoff", "ensure") and hp.get("started"):
                print(f"ppe_operator_loop_pass: happy_path {action}")
    except ImportError:
        pass

    status = collect_operator_status(repo)
    verdict = str(status.get("verdict") or "")

    if verdict == VERDICT_STALE_STATE:
        if heal_stale_running_manifest(repo):
            print("ppe_operator_loop_pass: healed stale manifest")
            return 0
        print("ppe_operator_loop_pass: STALE_STATE — operator review required", file=sys.stderr)
        return 7

    if verdict == VERDICT_RUN_LOCAL:
        from scripts.ppe_autobuilder import action_run_local

        result = action_run_local(repo)
        if result.get("started"):
            print("ppe_operator_loop_pass: run_ppe_local started (skip run_ppe_auto this pass)")
            return EXIT_PASS_HANDLED
        reason = result.get("reason") or "run-local did not start"
        print(f"ppe_operator_loop_pass: RUN_LOCAL but not started — {reason}", file=sys.stderr)
        return 7

    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Loop pass: heal stale + auto run-local")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    return run_loop_pass(args.repo_root.resolve())


if __name__ == "__main__":
    raise SystemExit(main())
