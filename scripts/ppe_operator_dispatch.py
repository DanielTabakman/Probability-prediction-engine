"""Execute burst direct_action handlers without a Cursor turn.

Opt-in: PPE_AUTO_DISPATCH=1. Canon: docs/SOP/DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))


def dispatch_allowed() -> bool:
    return os.environ.get("PPE_AUTO_DISPATCH", "").strip().lower() in ("1", "true", "yes")


def run_cmd(cmd: str, repo: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=repo, shell=True, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
    }


def dispatch_direct_action(repo: Path, action: str | None, *, force: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    report: dict[str, Any] = {"action": action, "ok": False, "steps": []}
    if not action:
        report["reason"] = "no direct_action"
        return report
    if not force and not dispatch_allowed():
        report["skipped"] = True
        report["reason"] = "PPE_AUTO_DISPATCH not set"
        return report

    handlers: dict[str, str] = {
        "DESKTOP_CONTINUE.cmd --no-pause": "DESKTOP_CONTINUE.cmd --no-pause",
        "wait_for_vm": "echo wait_for_vm: set PPE_AUTO_DISPATCH and run monitor when ppe_in_flight_monitor ships",
        "resolve_lease": "python scripts/ppe_worker_lease.py --assess",
        "coordination_check": "python scripts/ppe_coordination_check.py --write",
        "branch_recovery": "python scripts/ppe_branch_recovery.py --ship-all",
    }
    cmd = handlers.get(action)
    if action.startswith("DESKTOP_CONTINUE"):
        cmd = action
    if not cmd:
        report["reason"] = f"unknown direct_action: {action}"
        return report

    if action == "branch_recovery":
        try:
            from scripts.ppe_repo_state import load_repo_state

            rs = load_repo_state(repo) or {}
            rec = rs.get("recommended_commands") or []
            if rec:
                cmd = str(rec[0])
        except Exception:
            pass

    step = run_cmd(cmd, repo)
    report["steps"].append(step)
    report["ok"] = bool(step.get("ok"))
    if action == "branch_recovery" and report["ok"]:
        verify = run_cmd("python scripts/ppe_branch_recovery.py --verify --json", repo)
        report["steps"].append(verify)
        report["ok"] = bool(verify.get("ok"))
    return report


def dispatch_from_burst_plan(repo: Path, *, force: bool = False) -> dict[str, Any]:
    from scripts.ppe_burst_plan import refresh_burst_plan
    from scripts.ppe_operator_status import prepare_operator_status

    status = prepare_operator_status(repo)
    plan = refresh_burst_plan(repo, status)
    action = str(plan.get("direct_action") or "").strip() or None
    report = dispatch_direct_action(repo, action, force=force)
    report["burst_plan"] = {"direct_action": action, "burst_allowed": plan.get("burst_allowed")}
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dispatch burst direct_action (opt-in automation).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--action", type=str, default=None, help="direct_action string")
    ap.add_argument("--from-burst-plan", action="store_true")
    ap.add_argument("--force", action="store_true", help="Run even if PPE_AUTO_DISPATCH unset")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.from_burst_plan:
        report = dispatch_from_burst_plan(repo, force=args.force)
    else:
        report = dispatch_direct_action(repo, args.action, force=args.force)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "ok" if report.get("ok") else ("skipped" if report.get("skipped") else "failed")
        print(f"ppe_operator_dispatch: {status} action={report.get('action')}")
    return 0 if report.get("ok") or report.get("skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
