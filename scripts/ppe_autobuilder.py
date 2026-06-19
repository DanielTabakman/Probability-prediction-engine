"""PPE autobuilder — unified status, diagnosis, and safe actions for the IDE build pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_JSON_REL = "artifacts/orchestrator/AUTOBUILDER_STATUS.json"
DIAGNOSE_MD_REL = "artifacts/orchestrator/AUTOBUILDER_DIAGNOSE.md"

PHASE_STACK_DOWN = "STACK_DOWN"
PHASE_HEALTHY_IDLE = "HEALTHY_IDLE"
PHASE_AWAITING_BUILD = "AWAITING_BUILD"
PHASE_BUILD_IN_FLIGHT = "BUILD_IN_FLIGHT"
PHASE_CLOSEOUT_PENDING = "CLOSEOUT_PENDING"
PHASE_FINISH_IN_FLIGHT = "FINISH_IN_FLIGHT"
PHASE_RUN_LOCAL_PENDING = "RUN_LOCAL_PENDING"
PHASE_FIX_PLAN = "FIX_PLAN"
PHASE_STALE_STATE = "STALE_STATE"
PHASE_ERROR = "ERROR"
PHASE_DEGRADED = "DEGRADED"

ACTION_STATUS = "status"
ACTION_DIAGNOSE = "diagnose"
ACTION_ENSURE = "ensure"
ACTION_RETRY_BUILD = "retry-build"
ACTION_HANDOFF = "handoff"
ACTION_FINISH_PENDING = "finish-pending"
ACTION_RUN_LOCAL = "run-local"
ACTION_ADVANCE = "advance"

PHASE_ACTIONS: dict[str, list[str]] = {
    PHASE_STACK_DOWN: [ACTION_ENSURE, ACTION_DIAGNOSE],
    PHASE_HEALTHY_IDLE: [ACTION_STATUS],
    PHASE_AWAITING_BUILD: [ACTION_RETRY_BUILD, ACTION_HANDOFF, ACTION_DIAGNOSE],
    PHASE_BUILD_IN_FLIGHT: [ACTION_STATUS, ACTION_DIAGNOSE],
    PHASE_CLOSEOUT_PENDING: [ACTION_FINISH_PENDING, ACTION_DIAGNOSE],
    PHASE_FINISH_IN_FLIGHT: [ACTION_STATUS],
    PHASE_RUN_LOCAL_PENDING: [ACTION_RUN_LOCAL, ACTION_FINISH_PENDING],
    PHASE_FIX_PLAN: [ACTION_DIAGNOSE],
    PHASE_STALE_STATE: [ACTION_DIAGNOSE],
    PHASE_ERROR: [ACTION_DIAGNOSE, ACTION_ENSURE],
    PHASE_DEGRADED: [ACTION_HANDOFF, ACTION_DIAGNOSE, ACTION_ENSURE],
}

PHASE_RECOMMENDED: dict[str, str] = {
    PHASE_STACK_DOWN: ACTION_ENSURE,
    PHASE_HEALTHY_IDLE: ACTION_STATUS,
    PHASE_AWAITING_BUILD: ACTION_RETRY_BUILD,
    PHASE_BUILD_IN_FLIGHT: ACTION_STATUS,
    PHASE_CLOSEOUT_PENDING: ACTION_FINISH_PENDING,
    PHASE_FINISH_IN_FLIGHT: ACTION_STATUS,
    PHASE_RUN_LOCAL_PENDING: ACTION_RUN_LOCAL,
    PHASE_FIX_PLAN: ACTION_DIAGNOSE,
    PHASE_STALE_STATE: ACTION_DIAGNOSE,
    PHASE_ERROR: ACTION_DIAGNOSE,
    PHASE_DEGRADED: ACTION_HANDOFF,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def status_json_path(repo: Path) -> Path:
    return (repo / STATUS_JSON_REL).resolve()


def _tail_log(repo: Path, rel: str, *, max_lines: int = 12) -> str:
    path = repo / rel.replace("/", "\\") if "\\" not in rel else repo / rel
    if not path.is_file():
        return ""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return ""
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    return "\n".join(lines)


def _closeout_pending(repo: Path, *, plan_path: str, slice_id: str | None) -> dict[str, Any]:
    if not plan_path or not slice_id:
        return {"pending": False, "reason": "no slice"}
    try:
        from scripts.ppe_ide_product_ready import (
            _branch_has_commits,
            _resolve_slice_and_branch,
            completed_product_slice_ids,
        )

        if slice_id in completed_product_slice_ids(repo, plan_path=plan_path):
            return {"pending": False, "reason": "slice already marked"}
        _, build_branch, baseline = _resolve_slice_and_branch(
            repo, slice_id=slice_id, plan_path=plan_path, build_branch=None
        )
        has_commits = _branch_has_commits(repo, build_branch=build_branch, baseline=baseline)
        return {
            "pending": has_commits,
            "slice_id": slice_id,
            "build_branch": build_branch,
            "baseline": baseline,
            "branch_has_commits": has_commits,
        }
    except (ValueError, ImportError) as exc:
        return {"pending": False, "reason": str(exc)}


def _finish_worker_running(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_post_build_watcher import load_state, state_path
        from scripts.ppe_remote_agent_spawn import process_alive

        state = load_state(repo)
        pid = state.get("worker_pid")
        if pid is None:
            return {"running": False}
        try:
            alive = process_alive(int(pid))
        except (TypeError, ValueError):
            alive = False
        return {"running": alive, "worker_pid": pid, "state_path": str(state_path(repo))}
    except ImportError:
        return {"running": False}


def _automation_summary(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_ide_build_automation_trigger import load_trigger

        trigger = load_trigger(repo)
        return {
            "trigger_status": str(trigger.get("status") or "unknown"),
            "trigger_slice": trigger.get("sliceId"),
            "last_completed": trigger.get("lastCompletedSlice"),
        }
    except ImportError:
        return {"trigger_status": "unknown"}


def _build_lock_summary(repo: Path) -> dict[str, Any] | None:
    try:
        from scripts.ppe_remote_build_agent import read_build_lock

        lock = read_build_lock(repo)
        if not lock:
            return None
        return {
            "slice_id": lock.get("slice_id"),
            "source": lock.get("source"),
            "started_at": lock.get("started_at"),
            "worker_pid": lock.get("worker_pid"),
        }
    except ImportError:
        return None


def _resolve_pending_slice(repo: Path, operator_status: dict[str, Any]) -> dict[str, Any]:
    plan_path = str(operator_status.get("phase_plan_path") or "").strip()
    slice_id: str | None = None
    starter: str | None = None
    if plan_path:
        try:
            from scripts.ppe_ide_product_ready import next_pending_product_slice
            from scripts.ppe_ide_build_starter import starter_path

            slice_id = next_pending_product_slice(repo, plan_path=plan_path)
            if slice_id:
                starter = starter_path(slice_id)
        except ImportError:
            pass
    guard = operator_status.get("guard") or {}
    detail = str(guard.get("detail") or operator_status.get("blocker") or "")
    verdict = str(operator_status.get("verdict") or "")
    guard_reason = str(guard.get("reason") or "")
    if not slice_id and verdict == "IDE_BUILD" and guard_reason == "PRODUCT_BLOCKED":
        left, right = detail.find("["), detail.find("]")
        if left >= 0 and right > left:
            ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
            slice_id = ids[0] if ids else None
            if slice_id:
                try:
                    from scripts.ppe_ide_build_starter import starter_path

                    starter = starter_path(slice_id)
                except ImportError:
                    pass
    return {
        "slice_id": slice_id,
        "plan_path": plan_path or None,
        "starter": starter,
    }


def derive_phase(
    *,
    operator_status: dict[str, Any],
    stack: dict[str, Any],
    build_lock: dict[str, Any] | None,
    closeout: dict[str, Any],
    finish_worker: dict[str, Any],
    dispatch_degraded: bool,
) -> str:
    verdict = str(operator_status.get("verdict") or "")
    loop_running = bool(stack.get("loop_running"))
    watch_running = bool(stack.get("watch_running"))
    watcher_desired = bool(stack.get("local_trigger_watcher_desired"))
    watcher_running = bool(stack.get("local_trigger_watcher_running"))

    if not loop_running or not watch_running:
        return PHASE_STACK_DOWN
    if watcher_desired and not watcher_running:
        return PHASE_STACK_DOWN
    if finish_worker.get("running"):
        return PHASE_FINISH_IN_FLIGHT
    if build_lock:
        return PHASE_BUILD_IN_FLIGHT
    if closeout.get("pending"):
        return PHASE_CLOSEOUT_PENDING
    if verdict == "ERROR":
        return PHASE_ERROR
    if verdict == "STALE_STATE":
        return PHASE_STALE_STATE
    if verdict == "FIX_PLAN":
        return PHASE_FIX_PLAN
    if verdict == "RUN_LOCAL":
        return PHASE_RUN_LOCAL_PENDING
    if verdict == "IDE_BUILD":
        if dispatch_degraded and not (watcher_desired and watcher_running):
            return PHASE_DEGRADED
        return PHASE_AWAITING_BUILD
    if verdict in ("RUN_AUTO", "SUPPLY_LOW"):
        return PHASE_HEALTHY_IDLE
    return PHASE_HEALTHY_IDLE


def _dispatch_profile(repo: Path) -> dict[str, Any]:
    """CLI/automation constraints for build dispatch (not idle health)."""
    prefer_ide = False
    degraded = False
    reason: str | None = None
    worker_status: dict[str, Any] = {}
    try:
        from scripts.ppe_build_worker import collect_build_worker_status

        worker_status = collect_build_worker_status(repo)
    except ImportError:
        pass
    try:
        from scripts.ppe_ide_handoff import cli_usage_exhausted, prefer_ide_over_cli

        prefer_ide = prefer_ide_over_cli(repo)
        if prefer_ide:
            reason = "near_zero_api_profile"
        if cli_usage_exhausted(repo):
            degraded = True
            reason = reason or "cursor_cli_usage_exhausted"
    except ImportError:
        pass
    if worker_status.get("codex_cli_exhausted"):
        degraded = True
        reason = reason or "codex_cli_usage_exhausted"
    if not degraded:
        try:
            from scripts.ppe_ide_build_automation_health import run_health_checks

            health = run_health_checks(repo, ping_webhook=False)
            if health.get("verdict") == "BROKEN":
                degraded = True
                reason = str(health.get("blocker") or "automation_broken")
        except ImportError:
            pass
    return {
        "prefer_ide": prefer_ide,
        "degraded": degraded,
        "reason": reason,
        **worker_status,
    }


def _recommended_action(phase: str, dispatch: dict[str, Any]) -> str:
    if phase == PHASE_AWAITING_BUILD and (dispatch.get("prefer_ide") or dispatch.get("degraded")):
        return ACTION_HANDOFF
    return PHASE_RECOMMENDED.get(phase, ACTION_STATUS)


def collect_autobuilder_status(repo: Path) -> dict[str, Any]:
    """Compose stack, operator verdict, build pipeline, and recommended actions."""
    repo = repo.resolve()
    from scripts.ppe_desktop_operator_stack import stack_status
    from scripts.ppe_operator_status import collect_operator_status

    operator_status = collect_operator_status(repo)
    stack = stack_status(repo)
    build_lock = _build_lock_summary(repo)
    pending = _resolve_pending_slice(repo, operator_status)
    closeout = _closeout_pending(
        repo,
        plan_path=str(pending.get("plan_path") or ""),
        slice_id=str(pending.get("slice_id") or "") or None,
    )
    finish_worker = _finish_worker_running(repo)
    dispatch = _dispatch_profile(repo)

    phase = derive_phase(
        operator_status=operator_status,
        stack=stack,
        build_lock=build_lock,
        closeout=closeout,
        finish_worker=finish_worker,
        dispatch_degraded=bool(dispatch.get("degraded")),
    )
    recommended = _recommended_action(phase, dispatch)

    try:
        from scripts.ppe_ide_handoff import load_handoff_state

        handoff_state = load_handoff_state(repo)
    except ImportError:
        handoff_state = {}

    marker_present = False
    try:
        from scripts.ppe_ide_product_ready import load_marker

        marker_present = load_marker(repo) is not None
    except ImportError:
        pass

    return {
        "version": 1,
        "as_of": _utc_now(),
        "phase": phase,
        "verdict": operator_status.get("verdict"),
        "exit_code": operator_status.get("exit_code"),
        "blocker": operator_status.get("blocker"),
        "recommended_action": recommended,
        "allowed_actions": list(PHASE_ACTIONS.get(phase, [ACTION_STATUS, ACTION_DIAGNOSE])),
        "stack": {
            **stack,
            "stack_ok": bool(stack.get("loop_running")) and bool(stack.get("watch_running")),
        },
        "operator": {
            "chapter_name": operator_status.get("chapter_name"),
            "manifest_status": operator_status.get("manifest_status"),
            "phase_plan_path": operator_status.get("phase_plan_path"),
            "guard_reason": (operator_status.get("guard") or {}).get("reason"),
        },
        "build": {
            "slice_id": pending.get("slice_id"),
            "plan_path": pending.get("plan_path"),
            "starter": pending.get("starter"),
            "lock": build_lock,
            "worker": dispatch.get("worker"),
            "handoff_worker": dispatch.get("handoff_worker"),
            "worker_pref": dispatch.get("pref"),
            "worker_reason": dispatch.get("reason"),
            "handoff": {
                "last_slice": handoff_state.get("last_handoff_slice"),
                "last_at": handoff_state.get("last_handoff_at"),
                "last_worker": handoff_state.get("last_handoff_worker"),
                "cli_usage_exhausted": handoff_state.get("cli_usage_exhausted"),
                "codex_cli_usage_exhausted": handoff_state.get("codex_cli_usage_exhausted"),
            },
        },
        "closeout": closeout,
        "finish_worker": finish_worker,
        "marker_present": marker_present,
        "automation": _automation_summary(repo),
        "dispatch": dispatch,
        "commands": {
            "status": "ppe_autobuilder.cmd status",
            "diagnose": "ppe_autobuilder.cmd diagnose",
            "ensure": "ppe_autobuilder.cmd ensure",
            "advance": "ppe_autobuilder.cmd advance",
        },
        "agent": "@ppe-autobuilder-operator",
    }


def write_status_artifact(repo: Path, status: dict[str, Any] | None = None) -> Path:
    repo = repo.resolve()
    data = status if status is not None else collect_autobuilder_status(repo)
    path = status_json_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return path


def format_status_brief(status: dict[str, Any]) -> str:
    phase = status.get("phase", "?")
    verdict = status.get("verdict", "?")
    action = status.get("recommended_action", ACTION_STATUS)
    stack = status.get("stack") or {}
    build = status.get("build") or {}
    slice_id = build.get("slice_id") or "-"
    return (
        f"PHASE={phase} VERDICT={verdict} slice={slice_id} "
        f"stack_loop={stack.get('loop_running')} stack_watch={stack.get('watch_running')} "
        f"next={action}"
    )


def run_diagnose(repo: Path, *, ping_webhook: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    status = collect_autobuilder_status(repo)
    checks: list[dict[str, Any]] = []

    try:
        from scripts.ppe_ide_build_automation_health import run_health_checks

        automation = run_health_checks(repo, ping_webhook=ping_webhook)
        checks.extend(automation.get("checks") or [])
        automation_verdict = automation.get("verdict")
    except ImportError:
        automation_verdict = "UNKNOWN"

    stack = status.get("stack") or {}
    if not stack.get("loop_running"):
        checks.append(
            {
                "name": "stack_loop",
                "ok": False,
                "code": "LOOP_NOT_RUNNING",
                "fix": "ppe_autobuilder.cmd ensure",
            }
        )
    if not stack.get("watch_running"):
        checks.append(
            {
                "name": "stack_watch",
                "ok": False,
                "code": "WATCH_NOT_RUNNING",
                "fix": "ppe_autobuilder.cmd ensure",
            }
        )

    phase = str(status.get("phase") or "")
    failed = [c for c in checks if not c.get("ok") and c.get("severity", "error") != "info"]
    lines = [
        "# Autobuilder diagnose",
        "",
        f"**As-of:** {status.get('as_of')}",
        f"**Phase:** `{phase}`",
        f"**Verdict:** `{status.get('verdict')}`",
        f"**Recommended:** `{status.get('recommended_action')}`",
        "",
        "## Summary",
        "",
    ]
    if failed:
        lines.append(f"- **Issues:** {len(failed)} check(s) failed")
        for item in failed[:6]:
            lines.append(f"  - `{item.get('code')}`: {item.get('fix')}")
    else:
        lines.append("- All wiring checks passed (or quota-only).")

    lines.extend(["", "## Phase guidance", ""])
    guidance = {
        PHASE_STACK_DOWN: "Start loop + watch: `ppe_autobuilder.cmd ensure`",
        PHASE_AWAITING_BUILD: "Dispatch build: `ppe_autobuilder.cmd retry-build` or `handoff`",
        PHASE_CLOSEOUT_PENDING: "Finish closeout: `ppe_autobuilder.cmd finish-pending`",
        PHASE_RUN_LOCAL_PENDING: "Run relay: `ppe_autobuilder.cmd run-local`",
        PHASE_BUILD_IN_FLIGHT: "Wait for agent; check `REMOTE_BUILD_AGENT.log`",
        PHASE_DEGRADED: "Use IDE handoff: `ppe_autobuilder.cmd handoff`",
    }
    lines.append(guidance.get(phase, "Run `ppe_autobuilder.cmd status`"))

    for log_rel in (
        "artifacts/orchestrator/REMOTE_BUILD_AGENT.log",
        "artifacts/orchestrator/POST_BUILD_FINISH.log",
    ):
        tail = _tail_log(repo, log_rel)
        if tail:
            lines.extend(["", f"## Log tail: `{log_rel}`", "", "```", tail, "```"])

    md_path = repo / DIAGNOSE_MD_REL
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_body = "\n".join(lines) + "\n"
    md_path.write_text(md_body, encoding="utf-8")

    result = {
        "as_of": status.get("as_of"),
        "phase": phase,
        "verdict": status.get("verdict"),
        "automation_verdict": automation_verdict,
        "checks_failed": len(failed),
        "recommended_action": status.get("recommended_action"),
        "report_md": str(md_path.relative_to(repo)).replace("\\", "/"),
        "status_json": STATUS_JSON_REL,
    }
    write_status_artifact(repo, status)
    return result


def action_ensure(repo: Path) -> dict[str, Any]:
    from scripts.ppe_desktop_operator_stack import ensure_stack

    out = ensure_stack(repo.resolve(), start=True)
    status = collect_autobuilder_status(repo)
    write_status_artifact(repo, status)
    return {"action": ACTION_ENSURE, **out, "phase": status.get("phase")}


def action_retry_build(repo: Path, *, note: str = "", force_handoff: bool = False) -> dict[str, Any]:
    from scripts.ppe_ide_handoff import respond_to_ide_build

    result = respond_to_ide_build(
        repo.resolve(),
        source="autobuilder",
        note=note or "triggered by ppe_autobuilder retry-build",
        force_handoff=force_handoff,
    )
    status = collect_autobuilder_status(repo)
    write_status_artifact(repo, status)
    return {"action": ACTION_RETRY_BUILD, **result, "phase": status.get("phase")}


def action_handoff(repo: Path) -> dict[str, Any]:
    return action_retry_build(repo, force_handoff=True)


def action_finish_pending(repo: Path) -> dict[str, Any]:
    from scripts.ppe_post_build_watcher import try_finish_pending_ide_build

    result = try_finish_pending_ide_build(repo.resolve())
    status = collect_autobuilder_status(repo)
    write_status_artifact(repo, status)
    return {"action": ACTION_FINISH_PENDING, **result, "phase": status.get("phase")}


def action_run_local(repo: Path) -> dict[str, Any]:
    from scripts.ppe_remote_build_agent import launch_build

    result = launch_build(repo.resolve(), source="autobuilder", note="run-local via autobuilder")
    status = collect_autobuilder_status(repo)
    write_status_artifact(repo, status)
    return {"action": ACTION_RUN_LOCAL, **result, "phase": status.get("phase")}


def action_advance(repo: Path) -> dict[str, Any]:
    """Run the recommended safe action for the current phase."""
    status = collect_autobuilder_status(repo)
    phase = str(status.get("phase") or "")
    recommended = str(status.get("recommended_action") or ACTION_STATUS)

    if phase == PHASE_STACK_DOWN:
        return action_ensure(repo)
    if phase == PHASE_AWAITING_BUILD:
        if status.get("dispatch", {}).get("prefer_ide") or status.get("dispatch", {}).get("degraded"):
            return action_handoff(repo)
        return action_retry_build(repo)
    if phase == PHASE_CLOSEOUT_PENDING:
        return action_finish_pending(repo)
    if phase == PHASE_RUN_LOCAL_PENDING:
        return action_run_local(repo)
    if recommended == ACTION_DIAGNOSE:
        return run_diagnose(repo)
    write_status_artifact(repo, status)
    return {
        "action": ACTION_ADVANCE,
        "skipped": True,
        "reason": f"no automatic advance for phase {phase}",
        "phase": phase,
        "recommended_action": recommended,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE autobuilder — status, diagnose, and pipeline actions")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Collect autobuilder status")
    p_status.add_argument("--json", action="store_true")
    p_status.add_argument("--brief", action="store_true")
    p_status.add_argument("--write", action="store_true", help="Write AUTOBUILDER_STATUS.json")

    p_diag = sub.add_parser("diagnose", help="Full diagnose report")
    p_diag.add_argument("--json", action="store_true")
    p_diag.add_argument("--ping-webhook", action="store_true")

    sub.add_parser("ensure", help="Ensure loop + watch stack is running")
    sub.add_parser("retry-build", help="Dispatch build (CLI when allowed, else IDE handoff)")
    sub.add_parser("handoff", help="Force IDE handoff for current product slice")
    sub.add_parser("finish-pending", help="Mark ready + run_ppe_local if commits exist")
    sub.add_parser("run-local", help="Run run_ppe_local when verdict is RUN_LOCAL")
    sub.add_parser("advance", help="Run recommended action for current phase")

    p_reconcile = sub.add_parser(
        "reconcile",
        help="Sync backlog/queue + write CONTROL_PLANE_STATUS.json (canonical operator read)",
    )
    p_reconcile.add_argument("--dry-run", action="store_true", help="Alignment check only")
    p_reconcile.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    try:
        from scripts.ppe_operator_config import apply_operator_env

        apply_operator_env(repo)
    except Exception:
        pass

    if args.command == "status":
        status = collect_autobuilder_status(repo)
        if args.write or not (args.json or args.brief):
            path = write_status_artifact(repo, status)
            if not args.json and not args.brief:
                print(f"ppe_autobuilder: wrote {path}")
        if args.json:
            print(json.dumps(status, indent=2))
        elif args.brief:
            print(format_status_brief(status))
        else:
            print(format_status_brief(status))
        exit_code = int(status.get("exit_code") or 0)
        return 0 if exit_code in (0, 7) else exit_code

    if args.command == "diagnose":
        result = run_diagnose(repo, ping_webhook=args.ping_webhook)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"ppe_autobuilder: diagnose -> {result.get('report_md')}")
        return 0

    if args.command == "reconcile":
        from scripts.ppe_control_plane import collect_alignment_findings, reconcile_control_plane

        if args.dry_run:
            findings = collect_alignment_findings(repo)
            errs = sum(1 for f in findings if f.get("severity") == "error")
            if args.json:
                print(json.dumps({"alignment": {"findings": findings}}, indent=2))
            else:
                print(f"ppe_autobuilder: reconcile dry-run errors={errs}")
            return 1 if errs else 0
        snapshot = reconcile_control_plane(repo, apply=True)
        align = snapshot.get("alignment") or {}
        if args.json:
            print(json.dumps(snapshot, indent=2))
        else:
            print(
                f"ppe_autobuilder: reconcile -> {snapshot.get('artifact')} "
                f"verdict={snapshot.get('verdict')} passed={align.get('passed')}"
            )
        return 0 if align.get("passed", True) else 1

    handlers = {
        "ensure": lambda: action_ensure(repo),
        "retry-build": lambda: action_retry_build(repo),
        "handoff": lambda: action_handoff(repo),
        "finish-pending": lambda: action_finish_pending(repo),
        "run-local": lambda: action_run_local(repo),
        "advance": lambda: action_advance(repo),
    }
    result = handlers[args.command]()
    print(json.dumps(result, indent=2))
    if result.get("started") is False and result.get("skipped"):
        return 0
    if result.get("started") is False and result.get("action") not in (ACTION_ENSURE, ACTION_ADVANCE):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
