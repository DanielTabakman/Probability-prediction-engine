"""Operator status: verdict + next commands before auto-loop or IDE BUILD."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_auto_select import choose_next_plan
from scripts.ppe_ide_build_starter import format_ide_build_resume, starter_path
from scripts.ppe_operator_hint import PPE_GO_HINT, append_ppe_go_hint
from scripts.ppe_manifest import load_manifest, resolve_summary
from scripts.ppe_operator_guards import (
    GUARD_EXIT,
    GUARD_SKIP_CHAPTER,
    GuardResult,
    evaluate_continuous_guards,
)
from scripts.ppe_preflight import run_preflight
from scripts.ppe_propagate_queue import (
    backlog_path,
    load_backlog,
    promote_first_blocked_with_plan,
)
from scripts.ppe_queue import load_queue
from scripts.ppe_thread_roles import infer_suggest_thread_rotate

STATUS_REPORT_REL = "artifacts/orchestrator/OPERATOR_STATUS.md"
NOTIFY_REL = "artifacts/control_plane/OPERATOR_STATUS_NOTIFY.json"

VERDICT_RUN_AUTO = "RUN_AUTO"
VERDICT_RUN_LOCAL = "RUN_LOCAL"
VERDICT_IDE_BUILD = "IDE_BUILD"
VERDICT_FIX_PLAN = "FIX_PLAN"
VERDICT_SUPPLY_LOW = "SUPPLY_LOW"
VERDICT_STALE_STATE = "STALE_STATE"
VERDICT_ERROR = "ERROR"

STOP_VERDICTS = frozenset({VERDICT_IDE_BUILD, VERDICT_FIX_PLAN, VERDICT_STALE_STATE, VERDICT_ERROR})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _backlog_counts(repo: Path) -> dict[str, int]:
    counts = {"queued": 0, "blocked": 0, "chartered": 0, "done": 0, "other": 0}
    if not backlog_path(repo).is_file():
        return counts
    backlog = load_backlog(repo)
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        st = str(item.get("status") or "").strip().lower()
        if st in counts:
            counts[st] += 1
        else:
            counts["other"] += 1
    return counts


def _queue_ready_count(repo: Path) -> int:
    queue = load_queue(repo)
    return sum(
        1
        for item in (queue.get("items") or [])
        if isinstance(item, dict) and str(item.get("status") or "").upper() == "READY"
    )


def _analyze_supply(repo: Path) -> dict[str, Any]:
    counts = _backlog_counts(repo)
    promote = promote_first_blocked_with_plan(repo, apply=False)
    return {
        "backlog": counts,
        "queue_ready": _queue_ready_count(repo),
        "next_promotable_blocked": promote if promote.get("promoted") else None,
        "promote_reason": promote.get("reason"),
    }


def _stale_running(repo: Path, *, manifest_status: str) -> bool:
    if manifest_status != "RUNNING":
        return False
    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    return not active.is_file()


def _primary_product_slice(plan_path: str, guard: GuardResult) -> str | None:
    if guard.reason != "PRODUCT_BLOCKED" or not guard.detail:
        return None
    left = guard.detail.find("[")
    right = guard.detail.find("]")
    if left < 0 or right <= left:
        return None
    ids = [s.strip() for s in guard.detail[left + 1 : right].split(",") if s.strip()]
    return ids[0] if ids else None


def _commands_for_verdict(
    *,
    verdict: str,
    plan_path: str | None,
    product_slice: str | None,
) -> list[str]:
    if verdict == VERDICT_IDE_BUILD:
        return [PPE_GO_HINT]
    if verdict == VERDICT_RUN_LOCAL:
        return [PPE_GO_HINT]
    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        return [PPE_GO_HINT]
    if verdict == VERDICT_RUN_AUTO:
        return ["run_ppe_auto_local_loop.cmd"]
    if verdict == VERDICT_SUPPLY_LOW:
        return [
            "Add status=queued rows to docs/SOP/PHASE_CHAPTER_BACKLOG.json",
            "run_ppe_auto_local_loop.cmd  (will idle-sleep until work appears)",
        ]
    if verdict == VERDICT_STALE_STATE:
        return [
            "Inspect artifacts/orchestrator/LAST_RUN_REPORT.md",
            "If no slice is running: set manifest status READY or run run_ppe_local.cmd",
        ]
    if verdict == VERDICT_FIX_PLAN:
        return ["Fix phase plan or sprint spec, then run_ppe_operator.cmd again"]
    return []


def _avoid_commands(verdict: str) -> list[str]:
    if verdict == VERDICT_IDE_BUILD:
        return ["run_ppe_auto_local_loop.cmd  (will hit PRODUCT_BLOCKED)"]
    if verdict == VERDICT_RUN_LOCAL:
        return ["run_ppe_auto_local_loop.cmd  (use run_ppe_local.cmd once first)"]
    if verdict == VERDICT_FIX_PLAN:
        return ["run_ppe_auto_local_loop.cmd"]
    return []


def _maybe_heal_idle_queue(repo: Path) -> dict[str, Any]:
    """When manifest is idle, repair roadmap drift and bootstrap the next READY row."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return {}
    out: dict[str, Any] = {}
    try:
        manifest = load_manifest(repo)
    except Exception:
        return out

    status = str(manifest.get("status") or "").strip().upper()
    if status not in ("COMPLETE", ""):
        return out
    if str(manifest.get("phasePlanPath") or "").strip():
        return out
    if _queue_ready_count(repo) > 0:
        return out

    from scripts.ppe_queue_health import repair_roadmap

    roadmap_fixes, _ = repair_roadmap(repo, apply=True)
    if roadmap_fixes:
        out["roadmap_repair"] = roadmap_fixes

    try:
        from scripts.ppe_propagate_queue import maybe_propagate_queue

        prop = maybe_propagate_queue(repo, apply=True)
        if prop.get("propagated") or prop.get("roadmap_repair") or prop.get("chartered_promote"):
            out["propagate"] = prop
    except Exception as exc:
        out["propagate_error"] = str(exc)

    if _queue_ready_count(repo) == 0:
        try:
            from scripts.ppe_roadmap import bootstrap_next_ready

            boot = bootstrap_next_ready(repo, apply=True)
            if boot.get("bootstrapped"):
                out["bootstrap"] = boot
        except Exception as exc:
            out["bootstrap_error"] = str(exc)

    if _queue_ready_count(repo) > 0:
        try:
            manifest = load_manifest(repo)
        except Exception:
            manifest = {}
        if not str(manifest.get("phasePlanPath") or "").strip():
            try:
                from scripts.ppe_auto_select import run_auto_select

                out["auto_select_exit"] = run_auto_select(
                    repo,
                    apply=True,
                    select_only=False,
                    mark_done=False,
                    force=False,
                )
            except Exception as exc:
                out["auto_select_error"] = str(exc)

    return out


def collect_operator_status(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    idle_heal = _maybe_heal_idle_queue(repo)
    errors: list[str] = []
    try:
        summary = resolve_summary(repo)
    except Exception as exc:
        return {
            "verdict": VERDICT_ERROR,
            "exit_code": 1,
            "errors": [str(exc)],
            "commands": [],
            "avoid": [],
        }

    errors.extend(str(e) for e in summary.get("errors") or [])
    manifest_status = str(summary.get("status") or "").strip().upper()
    plan_path = str(summary.get("phase_plan_path") or "").strip() or None
    supply = _analyze_supply(repo)
    preflight = run_preflight(repo, allow_complete=True, allow_running=True, check_orchestrator=False)

    guard = GuardResult(exit_code=0, plan_path=plan_path or "")
    if plan_path:
        try:
            guard = evaluate_continuous_guards(repo, plan_path)
        except Exception as exc:
            errors.append(f"guard evaluation failed: {exc}")

    stale = _stale_running(repo, manifest_status=manifest_status)
    if stale:
        from scripts.ppe_active_run import heal_stale_running_manifest

        if heal_stale_running_manifest(repo):
            manifest_status = "READY"
            stale = False
            summary = resolve_summary(repo)
    product_slice: str | None = None
    if plan_path and guard.reason == "PRODUCT_BLOCKED":
        from scripts.ppe_ide_product_ready import next_pending_product_slice

        product_slice = next_pending_product_slice(repo, plan_path=plan_path)
    if not product_slice:
        product_slice = _primary_product_slice(plan_path or "", guard)

    verdict = VERDICT_RUN_AUTO
    exit_code = 0
    blocker: str | None = None

    if errors:
        verdict = VERDICT_ERROR
        exit_code = 1
        blocker = "; ".join(errors)
    elif stale:
        verdict = VERDICT_STALE_STATE
        exit_code = GUARD_EXIT
        blocker = "manifest RUNNING but artifacts/orchestrator/ACTIVE_RUN.json is missing"
    elif guard.exit_code == GUARD_EXIT:
        verdict = VERDICT_FIX_PLAN if guard.reason in ("CONTEXT_ESCALATE", "CONTEXT_WATCH", "TOO_MANY_SLICES") else VERDICT_IDE_BUILD
        if guard.reason == "PRODUCT_BLOCKED":
            verdict = VERDICT_IDE_BUILD
        exit_code = GUARD_EXIT
        blocker = guard.detail or guard.reason
    elif guard.exit_code == GUARD_SKIP_CHAPTER:
        verdict = VERDICT_RUN_AUTO
        blocker = guard.detail
    elif guard.reason == "IDE_MARKER_OK":
        verdict = VERDICT_RUN_LOCAL
        blocker = "IDE product marker present — finish chapter with run_ppe_local"
    elif manifest_status == "READY" and plan_path:
        verdict = VERDICT_RUN_AUTO
    elif manifest_status in ("COMPLETE", "") and not plan_path:
        _, select_reason = choose_next_plan(repo)
        if select_reason == "no READY items in queue" and not supply.get("next_promotable_blocked"):
            if supply["backlog"].get("queued", 0) == 0:
                verdict = VERDICT_SUPPLY_LOW
                blocker = "no READY queue item and no promotable blocked backlog chapter"
        else:
            verdict = VERDICT_SUPPLY_LOW
            blocker = select_reason
    elif manifest_status == "RUNNING":
        verdict = VERDICT_SUPPLY_LOW
        exit_code = 0
        blocker = "phase RUNNING — waiting for in-flight pass to finish"

    commands = _commands_for_verdict(verdict=verdict, plan_path=plan_path, product_slice=product_slice)
    avoid = _avoid_commands(verdict)
    rotate = infer_suggest_thread_rotate(
        verdict=verdict,
        manifest_status=manifest_status,
        plan_path=plan_path or "",
    )

    chapter_mode: dict[str, Any] = {}
    try:
        from scripts.ppe_chapter_mode import (
            is_loop_host_allowed,
            resolve_chapter_mode,
            resolve_operator_commands,
        )

        chapter_mode = resolve_chapter_mode(
            repo,
            verdict=verdict,
            plan_path=plan_path,
            guard_reason=guard.reason if guard.reason else None,
            chapter_name=str(summary.get("chapter_name") or "") or None,
        )
        loop_ok = is_loop_host_allowed()
        commands, avoid = resolve_operator_commands(
            verdict=verdict,
            chapter_mode=chapter_mode,
            loop_host_allowed=loop_ok,
        )
        chapter_mode["loop_host_allowed"] = loop_ok
    except Exception:
        pass

    delegation_hint: str | None = None
    ship_hint: str | None = None
    try:
        from scripts.ppe_delegation_envelope import operator_delegation_hint

        delegation_hint = operator_delegation_hint(repo)
    except ImportError:
        pass
    try:
        from scripts.ppe_worker_lease import operator_ship_hint

        ship_hint = operator_ship_hint(repo)
    except Exception:
        pass

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "chapter_mode": chapter_mode or None,
        "exit_code": exit_code,
        "chapter_name": summary.get("chapter_name"),
        "manifest_status": manifest_status,
        "phase_plan_path": plan_path,
        "blocker": blocker,
        "guard": {
            "exit_code": guard.exit_code,
            "reason": guard.reason,
            "detail": guard.detail,
        },
        "supply": supply,
        "preflight_ok": preflight.get("ok"),
        "preflight_warnings": preflight.get("warnings") or [],
        "delegation_hint": delegation_hint,
        "ship_hint": ship_hint,
        "commands": commands,
        "avoid": avoid,
        "errors": errors,
        "idle_heal": idle_heal or None,
        **rotate,
    }


def prepare_operator_status(repo: Path) -> dict[str, Any]:
    """Apply operator config env, then collect status (CLI / handoff / burst parity)."""
    try:
        from scripts.ppe_notify_push import ensure_operator_notify_env

        ensure_operator_notify_env(repo)
    except Exception:
        pass
    try:
        from scripts.ppe_operator_config import apply_operator_env

        apply_operator_env(repo)
    except Exception:
        pass
    status = collect_operator_status(repo)
    status = enrich_operator_status_with_vm_trust(repo, status)
    status = enrich_operator_status_with_monitor(repo, status)
    try:
        from scripts.ppe_repo_state import assess_and_write

        bpf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else None
        status["repo_state"] = assess_and_write(
            repo,
            verdict=str(status.get("verdict") or ""),
            branch_preflight=bpf,
            preflight_warnings=list(status.get("preflight_warnings") or []),
        )
    except Exception:
        pass
    try:
        from scripts.ppe_burst_plan import refresh_burst_plan

        status["burst_plan"] = refresh_burst_plan(repo, status)
    except Exception:
        pass
    try:
        from scripts.ppe_operator_pass_progress import enrich_status_with_pass_progress

        enrich_status_with_pass_progress(repo, status, record=True)
    except Exception:
        pass
    try:
        from scripts.ppe_operator_dispatch import maybe_auto_operate

        status = maybe_auto_operate(repo, status)
    except Exception:
        pass
    return status


def enrich_operator_status_with_vm_trust(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    """Desktop: attach VM phase mirror/cache so agents act without SSH probes."""
    loop_ok = False
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        loop_ok = bool(loop_host_start_allowed()[0])
        if loop_ok:
            return status
    except Exception:
        pass

    try:
        from scripts.ppe_operator_pass_timebox import record_operator_session

        status["operator_session"] = record_operator_session(repo, status)
    except Exception:
        pass

    try:
        from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight

        branch_pf = assess_operator_branch_preflight(
            repo,
            verdict=str(status.get("verdict") or ""),
            loop_host_allowed=loop_ok,
            chapter_mode=status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else None,
        )
        status["branch_preflight"] = branch_pf
        if branch_pf.get("blocks_relay"):
            status["commands"] = list(branch_pf.get("commands") or [])
            status.setdefault("avoid", []).extend(
                [
                    "DESKTOP_CONTINUE.cmd until branch/tree preflight passes",
                    "Relay / IDE BUILD on wrong branch or dirty product tree",
                ]
            )
    except Exception:
        pass

    try:
        from scripts.ppe_worker_lease import assess_worker_lease, write_worker_events

        worker_lease = assess_worker_lease(repo, status)
        status["worker_lease"] = worker_lease
        write_worker_events(repo, status)
        if worker_lease.get("blocks_dispatch") and not status.get("branch_preflight", {}).get("blocks_relay"):
            status.setdefault("avoid", []).extend(
                ["Second BUILD worker while lease blocks dispatch", "@ppe-director IDE_BUILD until lease resolved"]
            )
    except Exception:
        pass

    vm_mirror = None
    mirror_health: dict[str, Any] | None = None
    try:
        from scripts.ppe_operator_vm_mirror_refresh import (
            assess_mirror_health,
            refresh_vm_mirror_from_git,
        )
        from scripts.ppe_vm_phase_mirror import load_vm_phase_mirror

        refresh_vm_mirror_from_git(repo)
        vm_mirror = load_vm_phase_mirror(repo)
        mirror_health = assess_mirror_health(
            vm_mirror,
            local_verdict=str(status.get("verdict") or ""),
        )
        status["vm_mirror_health"] = mirror_health
        if mirror_health.get("stale"):
            try:
                from scripts.ppe_operator_git_sync import check_and_nudge_merges

                merge_report = check_and_nudge_merges(repo)
                status["vm_mirror_merge"] = merge_report
                refresh_vm_mirror_from_git(repo, force_fetch=True)
                vm_mirror = load_vm_phase_mirror(repo)
                mirror_health = assess_mirror_health(
                    vm_mirror,
                    local_verdict=str(status.get("verdict") or ""),
                )
                status["vm_mirror_health"] = mirror_health
            except Exception:
                pass
    except Exception:
        try:
            from scripts.ppe_vm_phase_mirror import load_vm_phase_mirror

            vm_mirror = load_vm_phase_mirror(repo)
        except Exception:
            pass

    try:
        from scripts.ppe_operator_vm_ssh import fetch_vm_brief, resolve_vm_trust

        vm_brief = None
        mirror_untrusted = bool(mirror_health and mirror_health.get("untrusted"))
        need_live_vm = mirror_untrusted or not vm_mirror or not str(vm_mirror.get("phase") or "").strip()
        if need_live_vm:
            vm_brief = fetch_vm_brief(repo, use_cache=not mirror_untrusted)
        trust = resolve_vm_trust(
            local_verdict=str(status.get("verdict") or ""),
            vm_brief=vm_brief,
            vm_mirror=vm_mirror,
            mirror_stale=mirror_untrusted,
        )
        if mirror_health and mirror_health.get("alert"):
            trust = {
                **trust,
                "mirror_stale": mirror_untrusted,
                "mirror_heartbeat_overdue": bool(mirror_health.get("heartbeat_overdue")),
                "agent_note": mirror_health.get("agent_note") or trust.get("agent_note"),
            }
        status["vm_trust"] = trust

        if status.get("branch_preflight", {}).get("blocks_relay"):
            pass
        elif trust.get("wait_for_vm"):
            status["commands"] = [
                "Adaptive VM monitor: ppe_in_flight_monitor.cmd (repeat per next_poll_s) or --daemon until phase clears.",
                "On action_ready: DESKTOP_CONTINUE.cmd --no-pause or @ppe-finish-worker.",
            ]
            status.setdefault("avoid", []).extend(
                [
                    "SSH findstr/type on queue or manifest JSON",
                    "Multiple parallel ssh to VM",
                    "@ppe-director while VM FINISH_IN_FLIGHT or BUILD_IN_FLIGHT",
                ]
            )
        elif trust.get("recommended_action") == "desktop_continue":
            if str(status.get("verdict") or "") == "RUN_LOCAL":
                status["commands"] = [
                    "DESKTOP_CONTINUE.cmd --no-pause (SSH → VM finish_ide_build)",
                    "Alternative: DO_THE_THING.cmd run",
                ]
    except Exception:
        pass

    try:
        from scripts.check_vm_host_health import collect_host_health, write_host_health
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        loop_host = bool(loop_host_start_allowed()[0])
        host_health = collect_host_health(repo, via_ssh=not loop_host)
        write_host_health(repo, host_health)
        status["vm_host_health"] = host_health
    except Exception:
        pass

    try:
        from scripts.ppe_operator_blind_spots import (
            assess_operator_blind_spots,
            write_blind_spots,
            write_operator_health,
        )

        blind = assess_operator_blind_spots(repo, status, probe_ssh=False)
        write_blind_spots(repo, blind)
        write_operator_health(repo, blind)
        status["operator_blind_spots"] = blind
        status["operator_health_line"] = blind.get("operator_health_line")
    except Exception:
        pass
    return status


def enrich_operator_status_with_monitor(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    """Desktop: promote in-flight monitor transitions (action_ready) into operator status."""
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if bool(loop_host_start_allowed()[0]):
            return status
    except Exception:
        pass

    try:
        from scripts.ppe_in_flight_monitor import collect_monitor_snapshot

        snapshot = collect_monitor_snapshot(
            repo,
            local_verdict=str(status.get("verdict") or ""),
        )
    except Exception:
        return status

    monitor = {
        "phase": snapshot.get("phase"),
        "status": snapshot.get("status"),
        "done": snapshot.get("done"),
        "wait_for_vm": snapshot.get("wait_for_vm"),
        "completion_action": snapshot.get("completion_action"),
        "stuck": snapshot.get("stuck"),
        "stuck_threshold_m": snapshot.get("stuck_threshold_m"),
        "log_tail": snapshot.get("log_tail"),
        "next_poll_s": snapshot.get("next_poll_s"),
        "message": snapshot.get("message"),
    }
    status["in_flight_monitor"] = monitor

    if str(monitor.get("status") or "") != "action_ready":
        return status
    completion = str(monitor.get("completion_action") or "").strip()
    if not completion:
        return status

    status["action_ready"] = True
    status["completion_action"] = completion

    if status.get("branch_preflight", {}).get("blocks_relay"):
        status.setdefault(
            "preflight_warnings",
            [],
        ).append(
            "VM phase cleared (action_ready) but branch preflight blocks relay — fix branch/tree before continue.",
        )
        return status

    status["commands"] = [
        f"{completion} (monitor: phase cleared — execute now)",
        "Then: prepare_operator_status refresh or ask what's next? in operator thread",
    ]
    vm_trust = status.get("vm_trust")
    if isinstance(vm_trust, dict):
        status["vm_trust"] = {**vm_trust, "wait_for_vm": False, "agent_note": monitor.get("message")}
    return status


def _format_burst_summary(burst_plan: dict[str, Any] | None) -> list[str]:
    if not burst_plan:
        return []
    allowed = bool(burst_plan.get("burst_allowed"))
    lines = [
        "Burst: "
        f"max_workers={burst_plan.get('max_cycles')} "
        f"band={burst_plan.get('overall_band')} "
        f"remaining={burst_plan.get('remaining_count')} "
        f"allowed={'true' if allowed else 'false'}"
    ]
    if allowed and burst_plan.get("use_director"):
        lines.append(
            "Burst path: read artifacts/control_plane/BURST_PLAN.json → @ppe-director "
            "(adaptive burst default; ppe_go.cmd --single to opt out)"
        )
    elif burst_plan.get("direct_action") == "DESKTOP_CONTINUE.cmd --no-pause":
        lines.append(
            "Burst path: CLOSEOUT_ONLY — run DESKTOP_CONTINUE.cmd --no-pause directly (no @ppe-director)"
        )
    elif burst_plan.get("direct_action") == "wait_for_vm":
        lines.append(
            "Burst path: monitor — ppe_in_flight_monitor.cmd until VM phase clears; no burst workers"
        )
    elif burst_plan.get("direct_action") == "resolve_lease":
        lines.append("Burst path: worker lease conflict — ppe_worker_lease.py --assess")
    elif burst_plan.get("direct_action") == "coordination_check":
        lines.append("Burst path: coordination blocked — read COORDINATION_CHECK.json; repair/recovery first")
    elif burst_plan.get("direct_action") == "factory_throughput":
        ft = burst_plan.get("factory_throughput") if isinstance(burst_plan.get("factory_throughput"), dict) else {}
        code = ft.get("top_issue_code") or ft.get("verdict") or "FACTORY_STUCK"
        lines.append(f"Burst path: factory throughput blocked ({code}) — read FACTORY_THROUGHPUT.json")
    elif burst_plan.get("direct_action") == "pipeline_health":
        lines.append("Burst path: pipeline health blocked — read PIPELINE_HEALTH.json")
    elif burst_plan.get("suggested_lane"):
        lines.append(f"Worker lane: `{burst_plan.get('suggested_lane')}`")
    elif not allowed:
        lines.append("Burst path: single verdict only — split slice or trim spec before chaining workers")
    return lines


def assess_founder_posture(status: dict[str, Any]) -> str:
    """Founder posture: wait | kick | alert | nothing."""
    monitor = status.get("in_flight_monitor") if isinstance(status.get("in_flight_monitor"), dict) else {}
    if monitor.get("stuck"):
        return "alert"
    if status.get("action_ready"):
        return "kick"
    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    if monitor.get("status") == "watching" or vm_trust.get("wait_for_vm"):
        return "wait"
    return "nothing"


def build_founder_truth_card(status: dict[str, Any]) -> dict[str, Any]:
    """Compact founder-facing snapshot for status header."""
    monitor = status.get("in_flight_monitor") if isinstance(status.get("in_flight_monitor"), dict) else {}
    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    mirror_age_s = monitor.get("mirror_age_s")
    mirror_age_m: int | None = None
    if isinstance(mirror_age_s, (int, float)):
        mirror_age_m = int(mirror_age_s // 60)
    return {
        "posture": assess_founder_posture(status),
        "verdict": str(status.get("verdict") or ""),
        "vm_phase": vm_trust.get("vm_phase") or monitor.get("phase"),
        "mirror_age_m": mirror_age_m,
        "monitor_status": monitor.get("status"),
        "action_ready": bool(status.get("action_ready")),
        "next_poll_m": monitor.get("next_poll_m"),
    }


def format_founder_truth_card_lines(status: dict[str, Any]) -> list[str]:
    card = build_founder_truth_card(status)
    parts = [
        f"posture={card['posture']}",
        f"verdict={card['verdict']}" if card.get("verdict") else None,
        f"vm={card['vm_phase']}" if card.get("vm_phase") else None,
        f"mirror={card['mirror_age_m']}m" if card.get("mirror_age_m") is not None else None,
        f"monitor={card['monitor_status']}" if card.get("monitor_status") else None,
        "action_ready" if card.get("action_ready") else None,
    ]
    detail = " · ".join(p for p in parts if p)
    return [f"Truth card: {detail}"]


def _format_human(
    status: dict[str, Any],
    repo: Path | None = None,
    *,
    burst_plan: dict[str, Any] | None = None,
) -> str:
    lines = [
        f"VERDICT: {status.get('verdict')}",
        "",
    ]
    truth_lines = format_founder_truth_card_lines(status)
    if truth_lines:
        lines.extend(truth_lines)
        lines.append("")
    pass_lines = status.get("operator_pass_lines")
    if isinstance(pass_lines, list) and pass_lines:
        lines.extend(str(x) for x in pass_lines)
        lines.append("")
    chapter_mode = status.get("chapter_mode")
    if isinstance(chapter_mode, dict) and chapter_mode.get("mode"):
        try:
            from scripts.ppe_chapter_mode import format_chapter_mode_block

            mode_lines = format_chapter_mode_block(chapter_mode)
            if mode_lines:
                lines.extend(mode_lines)
                lines.append("")
        except Exception:
            pass
    if repo is not None:
        try:
            from scripts.sop_discovery_core import format_operator_resolve_lines

            chapter_mode_dict = chapter_mode if isinstance(chapter_mode, dict) else {}
            resolve_lines = format_operator_resolve_lines(
                repo,
                plan_path=str(status.get("phase_plan_path") or "") or None,
                next_build_candidate=str(chapter_mode_dict.get("next_build_candidate") or "")
                or None,
            )
            if resolve_lines:
                lines.extend(resolve_lines)
                lines.append("")
        except Exception:
            pass
    if repo is not None:
        try:
            from scripts.sop_discovery_core import format_operator_sop_health_lines

            sop_lines = format_operator_sop_health_lines(repo)
            if sop_lines:
                lines.extend(sop_lines)
                lines.append("")
        except Exception:
            pass
    if repo is not None:
        try:
            from scripts.ppe_chapter_coordination import format_operator_coordination_lines

            coord_lines = format_operator_coordination_lines(repo)
            if coord_lines:
                lines.extend(coord_lines)
                lines.append("")
        except Exception:
            pass
    if status.get("chapter_name"):
        lines.append(f"Chapter: {status['chapter_name']}")
    if status.get("manifest_status"):
        lines.append(f"Manifest: {status['manifest_status']}")
    if status.get("phase_plan_path"):
        lines.append(f"Plan: {status['phase_plan_path']}")
    if status.get("blocker"):
        lines.append(f"Blocker: {status['blocker']}")
    supply = status.get("supply") or {}
    backlog = supply.get("backlog") or {}
    lines.append(
        "Supply: "
        f"queued={backlog.get('queued', 0)} "
        f"blocked={backlog.get('blocked', 0)} "
        f"queue_READY={supply.get('queue_ready', 0)}"
    )
    try:
        from scripts.ppe_workflow_cost import operator_lane_line

        if repo is not None:
            lines.append(operator_lane_line(repo))
    except Exception:
        pass
    if repo is not None:
        try:
            from scripts.ppe_tracking_hub import format_operator_tracking_lines

            lines.extend(format_operator_tracking_lines(repo))
        except Exception:
            pass
    next_promo = supply.get("next_promotable_blocked")
    if isinstance(next_promo, dict) and next_promo.get("chapterId"):
        lines.append(f"Next after closeout: {next_promo.get('chapterId')} ({next_promo.get('planPath')})")
    elif supply.get("promote_reason") and status.get("verdict") == VERDICT_SUPPLY_LOW:
        lines.append(f"Promote: {supply.get('promote_reason')}")

    if repo is not None:
        skip_archives = False
        if isinstance(chapter_mode, dict) and chapter_mode.get("do_not_rebuild"):
            skip_archives = True
        if not skip_archives:
            try:
                from scripts.research_archive_health import build_archive_health, format_health_line

                collectors_health = build_archive_health(repo).get("collectors") or []
                if collectors_health:
                    lines.append("")
                    lines.append("Research archives:")
                    for item in collectors_health:
                        if isinstance(item, dict):
                            lines.append(f"  {format_health_line(item)}")
            except Exception:
                pass

    burst = burst_plan if burst_plan is not None else status.get("burst_plan")
    if isinstance(burst, dict):
        lines.extend(_format_burst_summary(burst))

    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else None
    if vm_trust and (vm_trust.get("vm_phase") or vm_trust.get("agent_note")):
        lines.append("")
        phase = vm_trust.get("vm_phase") or "?"
        source = vm_trust.get("source") or "?"
        lines.append(f"VM phase: `{phase}` (source={source})")
        note = vm_trust.get("agent_note")
        if note:
            lines.append(f"  → {note}")

    if status.get("action_ready"):
        completion = str(status.get("completion_action") or "DESKTOP_CONTINUE.cmd --no-pause")
        lines.append("")
        lines.append(f"**Action ready:** VM phase cleared — run `{completion}` (not wait).")

    monitor = status.get("in_flight_monitor") if isinstance(status.get("in_flight_monitor"), dict) else None
    monitor_status = str(monitor.get("status") or "") if monitor else ""
    if monitor and monitor_status in ("watching", "stuck") and not status.get("action_ready"):
        elapsed = monitor.get("message")
        if elapsed:
            lines.append("")
            label = "VM monitor (stuck)" if monitor.get("stuck") else "VM monitor"
            lines.append(f"**{label}:** {elapsed}")
        if monitor.get("stuck"):
            log_tail = monitor.get("log_tail") if isinstance(monitor.get("log_tail"), dict) else None
            if log_tail and log_tail.get("lines"):
                rel = log_tail.get("path") or "log"
                lines.append(f"**Log tail** (`{rel}`):")
                for row in log_tail.get("lines") or []:
                    lines.append(f"  {row}")

    branch_pf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else None
    if branch_pf and branch_pf.get("blocks_relay"):
        lines.extend(
            [
                "",
                "**Branch preflight: BLOCKS relay**",
                f"  Branch: `{branch_pf.get('branch')}` (on_main={branch_pf.get('on_main')})",
            ]
        )
        for reason in branch_pf.get("reasons") or []:
            lines.append(f"  - {reason}")

    worker_lease = status.get("worker_lease") if isinstance(status.get("worker_lease"), dict) else None
    if worker_lease:
        try:
            from scripts.ppe_worker_lease import format_lease_lines

            lines.extend(format_lease_lines(worker_lease))
        except Exception:
            pass

    mirror_health = status.get("vm_mirror_health") if isinstance(status.get("vm_mirror_health"), dict) else None
    if mirror_health and mirror_health.get("alert"):
        lines.append("")
        lines.append(f"**VM mirror alert:** {mirror_health.get('agent_note')}")

    op_session = status.get("operator_session") if isinstance(status.get("operator_session"), dict) else None
    if op_session and op_session.get("rotate_recommended"):
        lines.append("")
        lines.append(f"**Thread timebox:** {op_session.get('message')}")

    blind = status.get("operator_blind_spots") if isinstance(status.get("operator_blind_spots"), dict) else None
    if blind:
        try:
            from scripts.ppe_operator_blind_spots import format_blind_spot_lines

            lines.extend(format_blind_spot_lines(blind))
        except Exception:
            pass

    lines.extend(
        [
            "",
            "Operator: nothing required — agents auto-execute below.",
        ]
    )
    cmds = status.get("commands") or []
    if cmds:
        lines.extend(["", "Agent action (auto-execute — not operator):"])
        for i, cmd in enumerate(cmds, 1):
            lines.append(f"  {i}. {cmd}")
    avoid = status.get("avoid") or []
    if avoid:
        lines.extend(["", "Do NOT run:"])
        for item in avoid:
            lines.append(f"  - {item}")
    warnings = status.get("preflight_warnings") or []
    repo_state = status.get("repo_state") if isinstance(status.get("repo_state"), dict) else None
    if repo_state:
        try:
            from scripts.ppe_repo_state import format_repo_state_lines, split_preflight_warnings

            lines.extend(format_repo_state_lines(repo_state))
            actionable, _info = split_preflight_warnings(warnings)
            if actionable and not repo_state.get("blockers"):
                lines.extend(["", "Preflight (actionable):"])
                for w in actionable:
                    lines.append(f"  - {w}")
        except Exception:
            pass
    elif warnings:
        lines.extend(["", "Preflight warnings (action required before relay):"])
        for w in warnings:
            lines.append(f"  - {w}")
        lines.append(
            "  → Resolve branch/dirty-tree issues or enter RECOVERY per docs/SOP/RECOVERY_PROTOCOL.md"
        )
    delegation_hint = status.get("delegation_hint")
    if delegation_hint:
        lines.extend(["", "Delegation:", f"  - {delegation_hint}"])
    ship_hint = status.get("ship_hint")
    if ship_hint:
        try:
            from scripts.ppe_worker_lease import format_ship_hint_lines

            lines.extend(format_ship_hint_lines(str(ship_hint)))
        except Exception:
            lines.extend(["", "Ship (agent):", f"  → {ship_hint}"])
    errors = status.get("errors") or []
    if errors:
        lines.extend(["", "Errors:"])
        for e in errors:
            lines.append(f"  - {e}")
    if status.get("suggest_thread_rotate"):
        from scripts.ppe_thread_roles import THREAD_ROTATE_FOOTER

        lines.extend(
            [
                "",
                "Thread rotate (recommended)",
                f"Reason: {status.get('thread_rotate_reason')}",
                str(status.get("thread_rotate_message") or ""),
                THREAD_ROTATE_FOOTER,
            ]
        )
    return "\n".join(lines) + "\n"


def _format_brief(status: dict[str, Any]) -> str:
    verdict = status.get("verdict", VERDICT_ERROR)
    exit_code = status.get("exit_code", 1)
    plan = status.get("phase_plan_path") or ""
    return f"VERDICT={verdict} exit={exit_code} plan={plan}"


def write_status_report(repo: Path, status: dict[str, Any], *, sync_burst: bool = True) -> Path:
    out = repo / STATUS_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    burst_plan: dict[str, Any] | None = None
    if sync_burst:
        try:
            from scripts.ppe_burst_plan import refresh_burst_plan

            burst_plan = refresh_burst_plan(repo, status)
            status["burst_plan"] = burst_plan
        except Exception:
            pass
    whats_next_block = ""
    try:
        from scripts.ppe_context_window_closeout import load_whats_next_markdown

        wn = load_whats_next_markdown(repo)
        if wn:
            # Inject body only (skip duplicate H1 if present).
            body_lines = wn.splitlines()
            if body_lines and body_lines[0].startswith("# "):
                body_lines = body_lines[2:] if len(body_lines) > 2 and not body_lines[1].strip() else body_lines[1:]
            whats_next_block = "\n## What's next (last context closeout)\n\n" + "\n".join(body_lines).strip() + "\n"
    except ImportError:
        pass
    pipeline_block = ""
    try:
        from scripts.ppe_pipeline_health import (
            assess_pipeline_health,
            format_root_cause_block,
            maybe_notify_pipeline_regression,
            write_pipeline_health,
        )

        pipeline_health = assess_pipeline_health(repo, status)
        write_pipeline_health(repo, pipeline_health)
        status["pipeline_health"] = pipeline_health
        maybe_notify_pipeline_regression(repo, pipeline_health)
        pipeline_block = format_root_cause_block(pipeline_health) + "\n"
    except Exception:
        pass
    try:
        if not status.get("operator_pass_lines"):
            from scripts.ppe_operator_pass_progress import enrich_status_with_pass_progress

            enrich_status_with_pass_progress(repo, status, record=True)
    except Exception:
        pass
    body = f"""# Operator status

**As-of:** {status.get("as_of")}
**Verdict:** `{status.get("verdict")}`

{pipeline_block}{_format_human(status, repo, burst_plan=burst_plan)}
{whats_next_block}"""
    out.write_text(body, encoding="utf-8")
    try:
        from scripts.research_archive_health import write_archive_health

        write_archive_health(repo)
    except Exception:
        pass
    try:
        from src.viz.research_summary import write_research_summary

        write_research_summary(repo)
    except Exception:
        pass
    try:
        from scripts.ppe_operator_compass import sync_compass

        sync_compass(repo, status=status, patch_map=True)
    except Exception:
        pass
    return out


def _write_notify_payload(repo: Path, status: dict[str, Any]) -> Path:
    out = repo / NOTIFY_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    verdict = str(status.get("verdict") or "")
    body = append_ppe_go_hint(str(status.get("blocker") or _format_brief(status)), verdict, repo=repo)
    resolve_hint: str | None = None
    if verdict == VERDICT_IDE_BUILD:
        try:
            from scripts.sop_discovery_core import format_notify_resolve_hint

            chapter_mode = status.get("chapter_mode") or {}
            resolve_hint = format_notify_resolve_hint(
                repo,
                plan_path=str(status.get("phase_plan_path") or "") or None,
                next_build_candidate=str(chapter_mode.get("next_build_candidate") or "") or None,
            )
            if resolve_hint:
                body = f"{body}\n{resolve_hint}"
        except Exception:
            pass
    payload = {
        "as_of": status.get("as_of"),
        "verdict": status.get("verdict"),
        "exit_code": status.get("exit_code"),
        "title": f"PPE operator: {status.get('verdict')}",
        "body": body,
        "resolve_hint": resolve_hint,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def _maybe_auto_remote_build(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    """CLI build or IDE handoff when loop hits IDE_BUILD guard stop."""
    if str(status.get("verdict") or "") != VERDICT_IDE_BUILD:
        return None
    try:
        from scripts.ppe_ide_handoff import ide_handoff_enabled, respond_to_ide_build
        from scripts.ppe_operator_config import auto_remote_build_enabled
        from scripts.ppe_remote_build_agent import read_build_lock
    except ImportError:
        return None
    if not auto_remote_build_enabled(repo) and not ide_handoff_enabled(repo):
        return None
    if read_build_lock(repo):
        return None
    return respond_to_ide_build(
        repo,
        source="loop-guard",
        note="auto-triggered by operator loop on IDE_BUILD guard stop",
    )


def _notify_mobile(repo: Path, *, status: dict[str, Any] | None = None) -> None:
    auto_build = _maybe_auto_remote_build(repo, status or {}) if status else None
    push = repo / "scripts" / "ppe_notify_push.py"
    if not push.is_file():
        return
    if auto_build and auto_build.get("started"):
        if auto_build.get("notified"):
            return
        mode = str(auto_build.get("mode") or auto_build.get("action") or "build")
        if mode == "ide_handoff":
            title = f"PPE IDE handoff: {auto_build.get('slice_id') or 'IDE_BUILD'}"
            body = append_ppe_go_hint(
                str(auto_build.get("message") or "IDE BUILD ready."),
                VERDICT_IDE_BUILD,
                repo=repo,
            )
        else:
            title = f"PPE auto-build started: {auto_build.get('slice_id') or 'IDE_BUILD'}"
            body = str(auto_build.get("message") or "Agent CLI running on desktop.")
        subprocess.run(
            [
                sys.executable,
                str(push),
                "--title",
                title,
                "--body",
                body,
                "--verdict",
                VERDICT_IDE_BUILD,
            ],
            cwd=repo,
            check=False,
        )
        return
    payload = repo / NOTIFY_REL
    if not payload.is_file():
        return
    subprocess.run(
        [sys.executable, str(push), "--payload", str(payload)],
        cwd=repo,
        check=False,
    )


def _notify_windows(repo: Path, *, status: dict[str, Any]) -> None:
    ps = repo / "scripts" / "notify_operator_status.ps1"
    if ps.is_file():
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps),
                "-RepoRoot",
                str(repo),
            ],
            cwd=repo,
            check=False,
        )
    _notify_mobile(repo, status=status)


def _configure_stdio_utf8() -> None:
    """Avoid UnicodeEncodeError on Windows cp1252 consoles (e.g. arrows in PPE_GO_HINT)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main(argv: list[str] | None = None) -> int:
    _configure_stdio_utf8()
    ap = argparse.ArgumentParser(description="PPE operator status and next-command verdict")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Print JSON only")
    ap.add_argument("--brief", action="store_true", help="One-line verdict for loop wrappers")
    ap.add_argument("--notify", action="store_true", help="Windows toast when verdict needs attention")
    ap.add_argument("--no-write", action="store_true", help="Do not write OPERATOR_STATUS.md")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    status = prepare_operator_status(repo)

    if not args.no_write:
        report = write_status_report(repo, status)
        if not args.brief and not args.json:
            print(f"ppe_operator_status: report={report}")

    if args.json:
        print(json.dumps(status, indent=2))
    elif args.brief:
        print(_format_brief(status))
    else:
        print(_format_human(status, repo), end="")

    if args.notify and status.get("verdict") in STOP_VERDICTS:
        from scripts.ppe_guard_notify_dedup import record_guard_notify, should_skip_guard_notify

        if should_skip_guard_notify(repo, status):
            if not args.brief and not args.json:
                print("ppe_operator_status: guard notify skipped (dedup cooldown)")
        else:
            _write_notify_payload(repo, status)
            _notify_windows(repo, status=status)
            record_guard_notify(repo, status)

    return int(status.get("exit_code") or 0)


if __name__ == "__main__":
    raise SystemExit(main())
