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


def dispatch_allowed(repo: Path | None = None) -> bool:
    if os.environ.get("PPE_AUTO_DISPATCH", "").strip().lower() in ("1", "true", "yes"):
        return True
    if repo is not None:
        return _desktop_auto_dispatch_from_opt_in(repo)
    return False


def _desktop_auto_dispatch_from_opt_in(repo: Path) -> bool:
    """True when desktop opt-in cmd sets PPE_AUTO_DISPATCH=1."""
    path = (repo.resolve() / "ppe_operator_desktop_auto.local.cmd").resolve()
    if not path.is_file():
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("REM"):
            continue
        upper = stripped.upper()
        if upper.startswith("SET ") and "PPE_AUTO_DISPATCH" in upper:
            _, _, value = stripped.partition("=")
            return value.strip().strip('"').lower() in ("1", "true", "yes")
    return False


def ensure_desktop_auto_dispatch_opt_in(repo: Path) -> dict[str, Any]:
    """Ensure ppe_operator_desktop_auto.local.cmd contains PPE_AUTO_DISPATCH=1."""
    repo = repo.resolve()
    path = repo / "ppe_operator_desktop_auto.local.cmd"
    if not path.is_file():
        return {"ok": False, "action": "missing_opt_in", "path": str(path)}
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "action": "read_failed", "error": str(exc), "path": str(path)}
    if _desktop_auto_dispatch_from_opt_in(repo):
        return {"ok": True, "action": "already_present", "path": str(path)}
    patched = text.rstrip() + '\nset "PPE_AUTO_DISPATCH=1"\n'
    path.write_text(patched, encoding="utf-8")
    return {"ok": True, "action": "patched", "path": str(path)}


def scheduled_dispatch_allowed(repo: Path) -> bool:
    """Scheduled dispatch requires the same desktop auto opt-in token as zero-click."""
    return (repo.resolve() / "ppe_operator_desktop_auto.local.cmd").is_file()


def automation_preflight_blocked(
    status: dict[str, Any],
    *,
    action: str | None = None,
) -> tuple[bool, str, str | None]:
    """Return (blocked, reason, preferred_direct_action) for desktop automation."""
    bpf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else {}
    if bpf.get("blocks_relay"):
        return True, "branch_preflight blocks relay", "branch_recovery"

    rs = status.get("repo_state") if isinstance(status.get("repo_state"), dict) else {}
    if rs.get("relay_allowed") is False:
        sev = rs.get("severity_label") or rs.get("severity")
        return True, f"repo_state blocks relay ({sev})", "branch_recovery"

    burst = status.get("burst_plan") if isinstance(status.get("burst_plan"), dict) else {}
    burst_action = str(burst.get("direct_action") or "").strip() or None
    if burst_action in ("branch_recovery", "coordination_check"):
        return True, f"burst direct_action is {burst_action}", burst_action

    if action and action.startswith("DESKTOP_CONTINUE"):
        coord = burst.get("coordination_check") if isinstance(burst.get("coordination_check"), dict) else {}
        if not coord:
            coord = status.get("coordination_check") if isinstance(status.get("coordination_check"), dict) else {}
        if coord.get("blocks_build"):
            verdict = coord.get("verdict") or "recovery"
            preferred = "coordination_check" if verdict in ("recovery", "park") else "branch_recovery"
            return True, f"coordination blocks build ({verdict})", preferred

    return False, "", None


def recovery_auto_dispatch_allowed(status: dict[str, Any]) -> bool:
    rs = status.get("repo_state") if isinstance(status.get("repo_state"), dict) else {}
    tier = str(rs.get("delegation_tier") or rs.get("tier") or "").strip().lower()
    if tier == "human_only":
        return False
    return True


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


def _load_repo_state(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_repo_state import load_repo_state

        data = load_repo_state(repo) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


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

    if not force and not dispatch_allowed(repo):
        report["skipped"] = True
        report["reason"] = "PPE_AUTO_DISPATCH not set"
        return report

    if action.startswith("DESKTOP_CONTINUE"):
        try:
            from scripts.ppe_operator_status import prepare_operator_status

            preflight = prepare_operator_status(repo)
            blocked, reason, preferred = automation_preflight_blocked(preflight, action=action)
            if blocked:
                report["skipped"] = True
                report["preflight_blocked"] = True
                report["reason"] = reason
                report["preferred_action"] = preferred
                return report
        except Exception:
            pass

    if action == "branch_recovery" and not recovery_auto_dispatch_allowed(
        {"repo_state": _load_repo_state(repo)}
    ):
        report["skipped"] = True
        report["reason"] = "human_only delegation — branch recovery requires steward"
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
    if not dispatch_allowed(repo):
        return status
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if bool(loop_host_start_allowed()[0]):
            return status
    except Exception:
        pass

    if status.get("action_ready"):
        completion = str(status.get("completion_action") or "DESKTOP_CONTINUE.cmd --no-pause").strip()
        blocked, reason, preferred = automation_preflight_blocked(status, action=completion)
        if blocked:
            status["auto_dispatch_blocked"] = {
                "reason": reason,
                "preferred_action": preferred,
            }
            if preferred and recovery_auto_dispatch_allowed(status) and dispatch_allowed(repo):
                status["auto_dispatch"] = dispatch_direct_action(repo, preferred, force=True)
            return status
        if completion:
            report = dispatch_direct_action(repo, completion, force=True)
            status["auto_dispatch"] = report
            if report.get("ok"):
                try:
                    from scripts.ppe_notify_push import maybe_notify_action_ready

                    maybe_notify_action_ready(
                        repo,
                        phase=str(
                            (status.get("in_flight_monitor") or {}).get("phase")
                            or (status.get("vm_trust") or {}).get("vm_phase")
                            or ""
                        ),
                        completion_action=completion,
                        auto_dispatched=True,
                    )
                except Exception:
                    pass
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
    blocked, reason, preferred = automation_preflight_blocked(status, action=action)
    if blocked and action and action.startswith("DESKTOP_CONTINUE"):
        action = preferred
    report = dispatch_direct_action(repo, action, force=force, dry_run=dry_run)
    report["source"] = "status"
    report["direct_action"] = action
    if blocked:
        report["preflight"] = {"blocked": True, "reason": reason, "preferred_action": preferred}
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
    ap.add_argument("--auto", action="store_true", help="Scheduled mode: require opt-in token; set PPE_AUTO_DISPATCH=1")
    ap.add_argument("--dry-run", action="store_true", help="Resolve command only; do not execute")
    ap.add_argument("--force", action="store_true", help="Run even if PPE_AUTO_DISPATCH unset")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.auto:
        if not scheduled_dispatch_allowed(repo):
            report = {
                "ok": False,
                "skipped": True,
                "reason": "missing ppe_operator_desktop_auto.local.cmd opt-in token",
            }
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print("ppe_operator_dispatch: skipped — missing desktop auto opt-in token")
            return 1
        os.environ["PPE_AUTO_DISPATCH"] = "1"
        args.from_status = True

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
