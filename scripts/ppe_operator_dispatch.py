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

# Static handlers — dynamic actions (DESKTOP_CONTINUE*) resolved separately.
DIRECT_ACTION_COMMANDS: dict[str, str] = {
    "wait_for_vm": "python scripts/ppe_in_flight_monitor.py --daemon --auto-act",
    "resolve_lease": "python scripts/ppe_worker_lease.py --assess",
    "coordination_check": "python scripts/ppe_coordination_check.py --write",
    "factory_throughput": "python scripts/ppe_factory_throughput.py --write",
    "pipeline_health": "python scripts/ppe_pipeline_health.py --write",
    "branch_recovery": "python scripts/ppe_branch_recovery.py --plane control --ship",
}


def dispatch_allowed() -> bool:
    return os.environ.get("PPE_AUTO_DISPATCH", "").strip().lower() in ("1", "true", "yes")


def _resolve_branch_recovery_cmd(repo: Path) -> str:
    try:
        from scripts.ppe_repo_state import load_repo_state

        rs = load_repo_state(repo) or {}
        rec = rs.get("recommended_commands") or []
        if rec:
            return str(rec[0])
    except Exception:
        pass
    return DIRECT_ACTION_COMMANDS["branch_recovery"]


def resolve_dispatch_command(repo: Path, action: str | None) -> str | None:
    """Map direct_action string to shell command (no execution)."""
    if not action:
        return None
    if action.startswith("DESKTOP_CONTINUE"):
        return action
    if action == "branch_recovery":
        return _resolve_branch_recovery_cmd(repo)
    return DIRECT_ACTION_COMMANDS.get(action)


def run_cmd(cmd: str, repo: Path) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=repo, shell=True, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": (proc.stdout or "")[-2000:],
        "stderr": (proc.stderr or "")[-2000:],
    }


def dispatch_direct_action(
    repo: Path,
    action: str | None,
    *,
    force: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    report: dict[str, Any] = {"action": action, "ok": False, "steps": []}
    if not action:
        report["reason"] = "no direct_action"
        return report

    cmd = resolve_dispatch_command(repo, action)
    if not cmd:
        report["reason"] = f"unknown direct_action: {action}"
        return report

    report["cmd"] = cmd
    if dry_run:
        report["dry_run"] = True
        report["ok"] = True
        report["reason"] = "dry_run"
        return report

    if not force and not dispatch_allowed():
        report["skipped"] = True
        report["reason"] = "PPE_AUTO_DISPATCH not set"
        return report

    step = run_cmd(cmd, repo)
    report["steps"].append(step)
    report["ok"] = bool(step.get("ok"))
    if action == "branch_recovery" and report["ok"]:
        verify = run_cmd("python scripts/ppe_branch_recovery.py --verify --json", repo)
        report["steps"].append(verify)
        report["ok"] = bool(verify.get("ok"))
    return report


def maybe_auto_operate(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    """Opt-in automation: start monitor daemon on wait_for_vm; run completion when action_ready."""
    if not dispatch_allowed():
        return status
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if bool(loop_host_start_allowed()[0]):
            return status
    except Exception:
        pass

    if status.get("action_ready") and not status.get("branch_preflight", {}).get("blocks_relay"):
        completion = str(status.get("completion_action") or "DESKTOP_CONTINUE.cmd --no-pause").strip()
        if completion:
            report = dispatch_direct_action(repo, completion, force=True)
            status["auto_dispatch"] = report
            return status

    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    if vm_trust.get("wait_for_vm"):
        try:
            from scripts.ppe_in_flight_monitor import maybe_start_monitor_daemon

            daemon = maybe_start_monitor_daemon(repo, auto_act=True)
            status["monitor_daemon"] = daemon
            if daemon.get("started") or daemon.get("reason") == "already running":
                pid = daemon.get("pid")
                status["commands"] = [
                    f"Monitor daemon active (pid={pid}) — adaptive poll until VM phase clears.",
                    "On action_ready: DESKTOP_CONTINUE runs automatically when PPE_AUTO_DISPATCH=1.",
                ]
        except Exception as exc:
            status["monitor_daemon"] = {"started": False, "error": str(exc)}
    return status


def _action_from_status(status: dict[str, Any]) -> str | None:
    burst = status.get("burst_plan") if isinstance(status.get("burst_plan"), dict) else {}
    action = str(burst.get("direct_action") or "").strip()
    if action:
        return action
    if status.get("action_ready"):
        return str(status.get("completion_action") or "DESKTOP_CONTINUE.cmd --no-pause").strip() or None
    return None


def dispatch_from_status(repo: Path, *, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
    from scripts.ppe_operator_status import prepare_operator_status

    status = prepare_operator_status(repo)
    action = _action_from_status(status)
    report = dispatch_direct_action(repo, action, force=force, dry_run=dry_run)
    report["source"] = "status"
    report["direct_action"] = action
    return report


def dispatch_from_burst_plan(repo: Path, *, force: bool = False, dry_run: bool = False) -> dict[str, Any]:
    from scripts.ppe_burst_plan import refresh_burst_plan
    from scripts.ppe_operator_status import prepare_operator_status

    status = prepare_operator_status(repo)
    plan = refresh_burst_plan(repo, status)
    action = str(plan.get("direct_action") or "").strip() or None
    report = dispatch_direct_action(repo, action, force=force, dry_run=dry_run)
    report["source"] = "burst_plan"
    report["burst_plan"] = {"direct_action": action, "burst_allowed": plan.get("burst_allowed")}
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Dispatch burst direct_action (opt-in automation).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--action", type=str, default=None, help="direct_action string")
    ap.add_argument("--from-burst-plan", action="store_true")
    ap.add_argument("--from-status", action="store_true", help="Read direct_action from operator status / burst plan")
    ap.add_argument("--dry-run", action="store_true", help="Resolve command only; do not execute")
    ap.add_argument("--force", action="store_true", help="Run even if PPE_AUTO_DISPATCH unset")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.from_status:
        report = dispatch_from_status(repo, force=args.force, dry_run=args.dry_run)
    elif args.from_burst_plan:
        report = dispatch_from_burst_plan(repo, force=args.force, dry_run=args.dry_run)
    else:
        report = dispatch_direct_action(repo, args.action, force=args.force, dry_run=args.dry_run)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if report.get("dry_run"):
            status = "dry_run"
        elif report.get("ok"):
            status = "ok"
        elif report.get("skipped"):
            status = "skipped"
        else:
            status = "failed"
        print(f"ppe_operator_dispatch: {status} action={report.get('action')}")
        if report.get("cmd"):
            print(f"  cmd: {report['cmd']}")
    return 0 if report.get("ok") or report.get("skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
