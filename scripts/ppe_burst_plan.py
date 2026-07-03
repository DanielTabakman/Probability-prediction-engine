"""Adaptive burst plan — preflight sizing + dynamic worker/cycle cap for PPE burst mode."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_context_bands import max_burst_cycles
from scripts.ppe_context_preflight import run_preflight
from scripts.ppe_operator_status import (
    VERDICT_FIX_PLAN,
    VERDICT_IDE_BUILD,
    VERDICT_RUN_LOCAL,
    VERDICT_STALE_STATE,
    VERDICT_ERROR,
    prepare_operator_status,
)
from scripts.ppe_phase_plan_window import non_closeout_slices_pending

BURST_PLAN_REL = "artifacts/control_plane/BURST_PLAN.json"

WORKER_VERDICTS = frozenset({VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL})
TRIAGE_VERDICTS = frozenset({VERDICT_FIX_PLAN, VERDICT_STALE_STATE, VERDICT_ERROR})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_product_slice(repo: Path, status: dict[str, Any]) -> str | None:
    plan_path = str(status.get("phase_plan_path") or "").strip()
    guard = status.get("guard") or {}
    reason = str(guard.get("reason") or "")
    if plan_path and reason == "PRODUCT_BLOCKED":
        try:
            from scripts.ppe_ide_product_ready import next_pending_product_slice

            sid = next_pending_product_slice(repo, plan_path=plan_path)
            if sid:
                return sid
        except ImportError:
            pass
    detail = str(guard.get("detail") or status.get("blocker") or "")
    left = detail.find("[")
    right = detail.find("]")
    if left >= 0 and right > left:
        ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
        if ids:
            return ids[0]
    return None


def compute_burst_plan(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    if status is None:
        status = prepare_operator_status(repo)

    verdict = str(status.get("verdict") or VERDICT_ERROR)
    plan_path = str(status.get("phase_plan_path") or "").strip() or None
    product_slice = _resolve_product_slice(repo, status)

    pending: list[str] = []
    if plan_path:
        pending = non_closeout_slices_pending(repo, plan_path)
    remaining = len(pending)

    preflight_summary: dict[str, Any] | None = None
    overall_band = "NORMAL"
    if plan_path:
        preflight = run_preflight(repo, phase_plan=plan_path, slice_id=product_slice)
        overall_band = str(preflight.get("overall_band") or "NORMAL")
        preflight_summary = {
            "overall_band": overall_band,
            "slice_count": preflight.get("slice_count"),
            "build_packet_band": (preflight.get("build_packet") or {}).get("band")
            if isinstance(preflight.get("build_packet"), dict)
            else None,
            "ide_starter_band": (preflight.get("ide_starter") or {}).get("band")
            if isinstance(preflight.get("ide_starter"), dict)
            else None,
            "advisory_actions": preflight.get("advisory_actions") or [],
        }

    use_director = verdict in WORKER_VERDICTS
    director_recommended = verdict in WORKER_VERDICTS | TRIAGE_VERDICTS

    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    closeout_only = bool(chapter_mode.get("do_not_rebuild")) or str(chapter_mode.get("mode") or "") == "CLOSEOUT_ONLY"
    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    vm_in_flight = bool(vm_trust.get("wait_for_vm"))
    action_ready = bool(status.get("action_ready"))
    completion_action = str(status.get("completion_action") or "").strip()

    direct_action: str | None = None
    if action_ready and completion_action:
        use_director = False
        direct_action = completion_action
        vm_in_flight = False
    elif (
        verdict == VERDICT_RUN_LOCAL
        and closeout_only
        and remaining <= 1
        and not vm_in_flight
    ):
        use_director = False
        direct_action = "DESKTOP_CONTINUE.cmd --no-pause"
    elif vm_in_flight:
        use_director = False
        direct_action = "wait_for_vm"

    band_cap = max_burst_cycles(overall_band, director=use_director or verdict in TRIAGE_VERDICTS)
    max_cycles = band_cap
    if remaining > 0:
        max_cycles = min(max_cycles, remaining)

    if verdict in TRIAGE_VERDICTS:
        max_cycles = min(max_cycles, 1)
        use_director = True

    burst_allowed = max_cycles > 0 and verdict not in ("RUN_AUTO", "SUPPLY_LOW")
    if direct_action == "wait_for_vm":
        burst_allowed = False

    worker_lease: dict[str, Any] | None = None
    try:
        from scripts.ppe_worker_lease import assess_worker_lease

        worker_lease = assess_worker_lease(repo, status)
        if worker_lease.get("blocks_dispatch"):
            burst_allowed = False
            use_director = False
            if direct_action not in ("wait_for_vm",):
                direct_action = "resolve_lease"
    except Exception:
        pass

    coordination_check: dict[str, Any] | None = None
    factory_throughput: dict[str, Any] | None = None
    try:
        from scripts.ppe_coordination_check import assess_coordination_check, write_coordination_check

        coordination_check = assess_coordination_check(repo, status)
        write_coordination_check(repo, coordination_check)
        if coordination_check.get("blocks_burst"):
            burst_allowed = False
            if direct_action not in ("wait_for_vm", "DESKTOP_CONTINUE.cmd --no-pause", "resolve_lease"):
                use_director = True
                if direct_action not in ("wait_for_vm", "resolve_lease"):
                    direct_action = "coordination_check"
    except Exception:
        pass

    repo_state = status.get("repo_state") if isinstance(status.get("repo_state"), dict) else None
    if (
        repo_state
        and int(repo_state.get("severity") or 0) >= 2
        and direct_action not in ("wait_for_vm", completion_action if action_ready else "", "resolve_lease")
    ):
        burst_allowed = False
        use_director = False
        direct_action = "branch_recovery"

    on_loop_host = False
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        on_loop_host = bool(loop_host_start_allowed()[0])
    except Exception:
        pass

    try:
        from scripts.ppe_factory_throughput import assess_factory_throughput, write_factory_throughput

        factory_throughput = assess_factory_throughput(repo, status)
        write_factory_throughput(repo, factory_throughput)
        if (
            on_loop_host
            and not factory_throughput.get("ok")
            and str(factory_throughput.get("verdict") or "") in ("stuck", "stack_down")
            and direct_action not in ("wait_for_vm", "DESKTOP_CONTINUE.cmd --no-pause")
        ):
            burst_allowed = False
            use_director = True
            if direct_action not in ("wait_for_vm", "resolve_lease", "coordination_check"):
                direct_action = "factory_throughput"
    except Exception:
        pass

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "phase_plan_path": plan_path,
        "product_slice": product_slice,
        "pending_slices": pending,
        "remaining_count": remaining,
        "preflight": preflight_summary,
        "overall_band": overall_band,
        "max_cycles": max_cycles,
        "use_director": use_director,
        "director_recommended": director_recommended,
        "burst_allowed": burst_allowed,
        "direct_action": direct_action,
        "closeout_only": closeout_only,
        "worker_verdicts_only": True,
        "worker_lease": worker_lease,
        "coordination_check": coordination_check,
        "repo_state": repo_state,
        "factory_throughput": factory_throughput,
        "suggested_lane": (worker_lease or {}).get("suggested_lane"),
        "prompt": format_burst_director_prompt(
            max_cycles=max_cycles,
            overall_band=overall_band,
            remaining=remaining,
            verdict=verdict,
            burst_allowed=burst_allowed,
            direct_action=direct_action,
            coordination_check=coordination_check,
            factory_throughput=factory_throughput,
            repo_state=repo_state,
        ),
    }


def format_burst_director_prompt(
    *,
    max_cycles: int,
    overall_band: str,
    remaining: int,
    verdict: str,
    burst_allowed: bool,
    direct_action: str | None = None,
    coordination_check: dict[str, Any] | None = None,
    factory_throughput: dict[str, Any] | None = None,
    repo_state: dict[str, Any] | None = None,
) -> str:
    from scripts.ppe_thread_roles import OPERATOR_THREAD_OPENER, prepend_role_opener

    if direct_action == "factory_throughput":
        ft = factory_throughput or {}
        code = str(ft.get("top_issue_code") or ft.get("verdict") or "FACTORY_STUCK")
        summary = str(ft.get("top_issue_message") or "factory throughput blocked")
        body = (
            f"Factory throughput blocked burst ({code}). {summary}. "
            "Read artifacts/control_plane/FACTORY_THROUGHPUT.json. "
            "Run ppe_autobuilder.cmd diagnose/advance before @ppe-director."
        )
    elif direct_action == "pipeline_health":
        body = (
            "Pipeline health blocked burst — read PIPELINE_HEALTH.json and fix ROOT CAUSE first."
        )
    elif direct_action == "coordination_check":
        coord_verdict = str((coordination_check or {}).get("verdict") or "recovery")
        summary = str((coordination_check or {}).get("summary") or "coordination blocked")
        body = (
            f"Coordination blocked burst (verdict={coord_verdict}). "
            f"Spawn @ppe-coordination-check first — {summary}. "
            f"Read artifacts/control_plane/COORDINATION_CHECK.json. "
            "Do NOT spawn ppe-build-worker until coordination returns proceed or repair complete."
        )
    elif direct_action == "branch_recovery":
        rs = repo_state or {}
        cmd = (rs.get("recommended_commands") or ["python scripts/ppe_branch_recovery.py --ship-all"])[0]
        body = (
            f"Repo state {rs.get('severity_label', 'STEWARD')} blocks burst — run recovery first. "
            f"Read artifacts/control_plane/REPO_STATE.json. Command: `{cmd}`"
        )
    elif direct_action == "wait_for_vm":
        body = (
            "VM phase FINISH_IN_FLIGHT or BUILD_IN_FLIGHT — run ppe_in_flight_monitor.cmd "
            "(adaptive cadence until phase clears); do NOT spawn @ppe-director or parallel SSH probes."
        )
    elif direct_action == "resolve_lease":
        body = (
            "Worker lease blocks dispatch — run python scripts/ppe_worker_lease.py --assess; "
            "see docs/SOP/WORKER_LANE_POLICY_V1.md."
        )
    elif direct_action == "DESKTOP_CONTINUE.cmd --no-pause":
        body = (
            "CLOSEOUT_ONLY with ≤1 remaining slice — skip @ppe-director. "
            "Run DESKTOP_CONTINUE.cmd --no-pause once, then rotate operator thread."
        )
    elif not burst_allowed:
        body = (
            "@ppe-director Burst blocked (band=ESCALATE or max_cycles=0). "
            "Read artifacts/control_plane/BURST_PLAN.json. Triage only — do not chain BUILD workers."
        )
    else:
        body = (
            f"@ppe-director Adaptive burst mode. max_workers={max_cycles} "
            f"(band={overall_band}, remaining_slices={remaining}, verdict={verdict}). "
            "Read artifacts/control_plane/BURST_PLAN.json first. "
            "Spawn ppe-build-worker / ppe-finish-worker only for IDE_BUILD and RUN_LOCAL. "
            "Triage verdicts: one ppe-triage-worker max. Terminal loop running."
        )
    return prepend_role_opener(body, OPERATOR_THREAD_OPENER)


def write_burst_plan(repo: Path, plan: dict[str, Any]) -> Path:
    out = repo / BURST_PLAN_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return out


def refresh_burst_plan(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compute adaptive burst plan and write BURST_PLAN.json (operator status parity)."""
    plan = compute_burst_plan(repo, status)
    write_burst_plan(repo, plan)
    return plan


def load_burst_plan(repo: Path) -> dict[str, Any] | None:
    path = repo / BURST_PLAN_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compute adaptive PPE burst plan from operator status + preflight.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"Write {BURST_PLAN_REL}")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    plan = compute_burst_plan(repo)

    if args.write:
        path = write_burst_plan(repo, plan)
        if not args.json:
            print(f"ppe_burst_plan: wrote {path.relative_to(repo)}")

    if args.json:
        sys.stdout.write(json.dumps(plan, indent=2) + "\n")
    elif not args.write:
        print(f"ppe_burst_plan: verdict={plan['verdict']} max_cycles={plan['max_cycles']} band={plan['overall_band']}")
        print(f"  remaining_slices={plan['remaining_count']} use_director={plan['use_director']}")
        if not plan["burst_allowed"]:
            print("  burst_allowed=false — prefer single verdict or split slice")

    return 0 if plan.get("burst_allowed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
