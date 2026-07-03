"""Founder pipeline diagnostics — root cause, milestone clock, regression alerts.

Merges coordination check, contradiction detection, and milestone slip tracking
into one founder-readable report. Canon: docs/SOP/PIPELINE_HEALTH_V1.md
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

PIPELINE_HEALTH_REL = "artifacts/control_plane/PIPELINE_HEALTH.json"
PIPELINE_HEALTH_STATE_REL = "artifacts/control_plane/PIPELINE_HEALTH_STATE.json"
PIPELINE_HEALTH_DOC = "docs/SOP/PIPELINE_HEALTH_V1.md"

FIX_PROCEED = "proceed"
FIX_REPAIR = "repair"
FIX_RECOVERY = "recovery"
FIX_PARK = "park"

# Stable contradiction codes (extend CHAPTER_COORDINATION_V1 issue codes).
DEADLOCK_IDE_BUILD_CLOSEOUT = "DEADLOCK_IDE_BUILD_CLOSEOUT"
VM_VERDICT_MISMATCH = "VM_VERDICT_MISMATCH"
BRANCH_BLOCKS_RELAY = "BRANCH_BLOCKS_RELAY"
from scripts.ppe_milestone_gate import (  # noqa: E402
    ACTIVE_CHAPTER_GATE,
    CLOSEOUT_REGISTRY_DEBT,
    MILESTONE_BLOCKED,
    STEERING_CANDIDATE_STALE,
    assess_closeout_debt,
    format_milestone_gate_lines,
    milestone_gate_issues,
)

Issue = dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _days_since(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    delta = datetime.now(timezone.utc) - dt
    return max(0.0, delta.total_seconds() / 86400.0)


def _git_first_commit_date(repo: Path, path: str, pattern: str) -> datetime | None:
    try:
        proc = subprocess.run(
            [
                "git",
                "log",
                "--reverse",
                "--format=%cI",
                "-S",
                pattern,
                "--",
                path,
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        first = (proc.stdout or "").strip().splitlines()
        if first:
            return _parse_utc(first[0])
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _load_direction(repo: Path) -> dict[str, Any]:
    path = repo / "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _next_build_candidate(repo: Path) -> str:
    steering_path = repo / "docs/SOP/AGENT_STEERING_V1.json"
    if steering_path.is_file():
        try:
            steering = json.loads(steering_path.read_text(encoding="utf-8"))
            cid = str(steering.get("nextBuildCandidateId") or "").strip()
            if cid:
                return cid
        except (json.JSONDecodeError, OSError):
            pass
    direction = _load_direction(repo)
    milestone = direction.get("productMilestone") if isinstance(direction.get("productMilestone"), dict) else {}
    return str(milestone.get("id") or "").strip()


def compute_milestone_clock(repo: Path) -> dict[str, Any]:
    """Actionable closeout debt + resolved next BUILD (milestone gate v2)."""
    repo = repo.resolve()
    direction = _load_direction(repo)
    pivot_as_of = str(direction.get("asOf") or "").strip()

    closeout_since = _git_first_commit_date(
        repo,
        "docs/SOP/AGENT_STEERING_V1.json",
        "closeoutOnlyChapterIds",
    )
    closeout_days = _days_since(closeout_since)

    debt: dict[str, Any] = {}
    try:
        debt = assess_closeout_debt(repo)
    except Exception:
        debt = {}

    next_build_steering = debt.get("next_build_steering") or _next_build_candidate(repo) or None
    next_build_resolved = debt.get("next_build_resolved") or next_build_steering

    milestone_blocked_days: float | None = None
    if debt.get("has_active_gate") and debt.get("active_pending_count"):
        milestone_blocked_days = round(closeout_days, 1) if closeout_days is not None else 1.0

    oldest_closeout_debt: dict[str, Any] | None = None
    try:
        from scripts.ppe_chapter_coordination import audit_repo

        issues = audit_repo(repo)
        high = [i for i in issues if str(i.get("severity") or "").lower() == "high"]
        if high:
            oldest_closeout_debt = {
                "code": high[0].get("code"),
                "message": high[0].get("message"),
                "plan_path": high[0].get("planPath"),
                "issue_count": len(issues),
                "high_count": len(high),
            }
    except Exception:
        pass

    return {
        "next_build_candidate": next_build_resolved,
        "next_build_steering": next_build_steering,
        "next_build_resolved": next_build_resolved,
        "steering_stale": bool(debt.get("steering_stale")),
        "direction_pivot_as_of": pivot_as_of or None,
        "closeout_mode_since": closeout_since.isoformat().replace("+00:00", "Z") if closeout_since else None,
        "closeout_mode_days": round(closeout_days, 1) if closeout_days is not None else None,
        "milestone_blocked_days": milestone_blocked_days,
        "active_chapter_id": debt.get("active_chapter_id"),
        "active_pending_count": debt.get("active_pending_count"),
        "registry_total": debt.get("registry_total"),
        "registry_stale": debt.get("registry_stale"),
        "registry_actionable": debt.get("registry_actionable"),
        "has_active_gate": debt.get("has_active_gate"),
        "oldest_closeout_debt": oldest_closeout_debt,
    }


def detect_contradictions(
    repo: Path,
    status: dict[str, Any],
    coordination: dict[str, Any],
) -> list[Issue]:
    """Detect operator-status contradictions with stable codes."""
    issues: list[Issue] = []
    repo = repo.resolve()

    verdict = str(status.get("verdict") or "")
    chapter_mode = status.get("chapter_mode") if isinstance(status.get("chapter_mode"), dict) else {}
    mode = str(chapter_mode.get("mode") or "")
    do_not_rebuild = bool(chapter_mode.get("do_not_rebuild"))

    plan_path = str(status.get("phase_plan_path") or "").strip()
    on_main_slices: list[str] = []
    if plan_path:
        try:
            from scripts.ppe_chapter_mode import product_slices_on_main

            on_main_slices = product_slices_on_main(repo, plan_path)
        except Exception:
            pass

    if verdict == "IDE_BUILD" and (do_not_rebuild or mode == "CLOSEOUT_ONLY") and on_main_slices:
        fix_cmds = []
        for issue in coordination.get("chapter_issues") or []:
            if str(issue.get("code") or "") == "PRODUCT_ON_MAIN_NO_MARKER":
                fix = str(issue.get("fix") or "").strip()
                if fix:
                    fix_cmds.append(fix)
        if not fix_cmds and plan_path:
            fix_cmds.append(
                f"python scripts/ppe_chapter_coordination.py --repair --plan {plan_path}"
            )
        issues.append(
            {
                "code": DEADLOCK_IDE_BUILD_CLOSEOUT,
                "severity": "high",
                "message": (
                    "IDE_BUILD verdict conflicts with CLOSEOUT_ONLY — product already on main; "
                    "missing IDE marker (bookkeeping deadlock, not a BUILD task)."
                ),
                "fix_class": FIX_REPAIR,
                "fix": fix_cmds[0] if fix_cmds else "python scripts/ppe_chapter_coordination.py --repair",
                "commands": fix_cmds[:3],
            }
        )

    branch_pf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else {}
    if branch_pf.get("blocks_relay"):
        cmds = [str(c) for c in branch_pf.get("commands") or [] if str(c).strip()]
        issues.append(
            {
                "code": BRANCH_BLOCKS_RELAY,
                "severity": "high",
                "message": f"Branch `{branch_pf.get('branch')}` blocks relay — recovery before BUILD/relay.",
                "fix_class": FIX_RECOVERY,
                "fix": cmds[0] if cmds else "git checkout main && git pull origin main",
                "commands": cmds[:3],
            }
        )

    vm_trust = status.get("vm_trust") if isinstance(status.get("vm_trust"), dict) else {}
    local_v = verdict
    vm_v = str(vm_trust.get("vm_verdict") or vm_trust.get("effective_verdict") or "").strip()
    if vm_v and local_v and vm_v != local_v and vm_trust.get("trust_vm"):
        issues.append(
            {
                "code": VM_VERDICT_MISMATCH,
                "severity": "medium",
                "message": f"Desktop verdict `{local_v}` disagrees with VM `{vm_v}` — trust VM mirror/live brief.",
                "fix_class": FIX_RECOVERY,
                "fix": "Refresh VM mirror or wait for in-flight phase; do not spawn parallel BUILD.",
                "commands": ["DESKTOP_VM_STATUS.cmd --no-pause"],
            }
        )

    for issue in coordination.get("chapter_issues") or []:
        if str(issue.get("code") or "") == "FRONTIER_AHEAD_OF_EVIDENCE":
            issues.append(
                {
                    "code": "FRONTIER_AHEAD_OF_EVIDENCE",
                    "severity": "high",
                    "message": str(issue.get("message") or "Frontier claims COMPLETE before evidence."),
                    "fix_class": FIX_PARK,
                    "fix": str(issue.get("fix") or "Align MSOS_FRONTIER with evidence doc honestly."),
                    "commands": [str(issue.get("fix") or "")] if issue.get("fix") else [],
                }
            )

    try:
        debt = assess_closeout_debt(repo)
        gate_issues = milestone_gate_issues(repo, debt)
        seen_codes: set[str] = {str(i.get("code") or "") for i in issues}
        for gate_issue in gate_issues:
            code = str(gate_issue.get("code") or "")
            if code and code not in seen_codes:
                if "fix_class" not in gate_issue:
                    gate_issue["fix_class"] = FIX_REPAIR
                issues.append(gate_issue)
                seen_codes.add(code)
    except Exception:
        pass

    return issues


def _pick_root_cause(
    contradictions: list[Issue],
    coordination: dict[str, Any],
    factory: dict[str, Any] | None = None,
) -> Issue | None:
    factory_issues = (factory or {}).get("issues") or []
    for issue in factory_issues:
        code = str(issue.get("code") or "")
        if code in ("STACK_DOWN", "ZERO_THROUGHPUT_24H", "PHASE_STUCK"):
            fix_class = FIX_RECOVERY if code == "STACK_DOWN" else FIX_REPAIR
            return {
                "code": code,
                "severity": issue.get("severity") or "high",
                "message": str(issue.get("message") or ""),
                "fix_class": fix_class,
                "fix": str(issue.get("fix") or ""),
                "commands": [str(issue.get("fix") or "")] if issue.get("fix") else [],
            }

    priority = [
        DEADLOCK_IDE_BUILD_CLOSEOUT,
        BRANCH_BLOCKS_RELAY,
        "FRONTIER_AHEAD_OF_EVIDENCE",
        VM_VERDICT_MISMATCH,
        "ZERO_THROUGHPUT_12H",
        ACTIVE_CHAPTER_GATE,
        STEERING_CANDIDATE_STALE,
        MILESTONE_BLOCKED,
        CLOSEOUT_REGISTRY_DEBT,
    ]
    by_code = {str(i.get("code") or ""): i for i in contradictions}
    factory_moving = str((factory or {}).get("verdict") or "") == "moving"
    defer_informational = factory_moving and ACTIVE_CHAPTER_GATE not in by_code
    for code in priority:
        if defer_informational and code in (
            STEERING_CANDIDATE_STALE,
            MILESTONE_BLOCKED,
            CLOSEOUT_REGISTRY_DEBT,
        ):
            continue
        if code in by_code:
            return by_code[code]

    coord_verdict = str(coordination.get("verdict") or FIX_PROCEED)
    if coord_verdict not in (FIX_PROCEED, FIX_REPAIR):
        return {
            "code": f"COORDINATION_{coord_verdict.upper()}",
            "severity": "high",
            "message": str(coordination.get("summary") or f"Coordination verdict: {coord_verdict}"),
            "fix_class": coord_verdict,
            "fix": (coordination.get("commands") or [None])[0],
            "commands": list(coordination.get("commands") or [])[:3],
        }

    repairable = [
        i
        for i in coordination.get("chapter_issues") or []
        if str(i.get("code") or "") in ("PRODUCT_ON_MAIN_NO_MARKER", "CLOSEOUT_REGISTRY_MISSING", "QUEUE_ACTIVE_PRODUCT_DESYNC")
    ]
    if repairable:
        top = repairable[0]
        return {
            "code": str(top.get("code") or "CHAPTER_COORDINATION"),
            "severity": "high",
            "message": str(top.get("message") or "Chapter coordination desync."),
            "fix_class": FIX_REPAIR,
            "fix": str(top.get("fix") or ""),
            "commands": [str(top.get("fix") or "")] if top.get("fix") else [],
        }

    if contradictions:
        return contradictions[0]
    return None


def assess_pipeline_health(
    repo: Path,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Full pipeline health snapshot for founder surface and operator status."""
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)

    coordination: dict[str, Any] = {}
    try:
        from scripts.ppe_coordination_check import assess_coordination_check, write_coordination_check

        coordination = assess_coordination_check(repo, status)
        write_coordination_check(repo, coordination)
    except Exception as exc:
        coordination = {
            "verdict": FIX_PARK,
            "summary": f"coordination check failed: {exc}",
            "blocks_burst": True,
            "blocks_build": True,
            "commands": ["python scripts/ppe_coordination_check.py --write --json"],
        }

    contradictions = detect_contradictions(repo, status, coordination)
    milestone = compute_milestone_clock(repo)

    factory: dict[str, Any] = {}
    try:
        from scripts.ppe_factory_throughput import (
            assess_factory_throughput,
            write_factory_throughput,
        )

        factory = assess_factory_throughput(repo, status)
        write_factory_throughput(repo, factory)
    except Exception as exc:
        factory = {"ok": False, "verdict": "unknown", "error": str(exc), "issues": []}

    root = _pick_root_cause(contradictions, coordination, factory)

    fix_class = str(root.get("fix_class") if root else coordination.get("verdict") or FIX_PROCEED)
    if fix_class not in (FIX_PROCEED, FIX_REPAIR, FIX_RECOVERY, FIX_PARK):
        fix_class = FIX_PARK

    factory_ok = bool(factory.get("ok", True))
    factory_verdict = str(factory.get("verdict") or "")
    blocks_burst = (
        bool(coordination.get("blocks_burst"))
        or fix_class in (FIX_RECOVERY, FIX_PARK)
        or factory_verdict in ("stuck", "stack_down")
    )
    blocks_build = bool(coordination.get("blocks_build")) or fix_class in (FIX_RECOVERY, FIX_PARK)
    blocks_gate = fix_class in (FIX_RECOVERY, FIX_PARK)

    pipeline_ok = fix_class == FIX_PROCEED and not contradictions
    ok = pipeline_ok and factory_ok

    commands: list[str] = []
    if root:
        commands.extend([str(c) for c in root.get("commands") or [] if str(c).strip()])
        fix_one = str(root.get("fix") or "").strip()
        if fix_one and fix_one not in commands:
            commands.insert(0, fix_one)
    if not commands:
        commands = [str(c) for c in coordination.get("commands") or [] if str(c).strip()]
    if not commands and factory.get("commands"):
        commands = list(factory.get("commands") or [])

    return {
        "as_of": _utc_now(),
        "ok": ok,
        "pipeline_ok": pipeline_ok,
        "factory_ok": factory_ok,
        "fix_class": fix_class,
        "root_cause": root,
        "root_cause_code": str(root.get("code") or "") if root else None,
        "root_cause_message": str(root.get("message") or "") if root else "Pipeline healthy — proceed with relay.",
        "commands": commands[:5],
        "contradictions": contradictions,
        "coordination": {
            "verdict": coordination.get("verdict"),
            "summary": coordination.get("summary"),
            "blocks_burst": coordination.get("blocks_burst"),
            "blocks_build": coordination.get("blocks_build"),
        },
        "milestone": milestone,
        "factory": {
            "verdict": factory.get("verdict"),
            "ok": factory.get("ok"),
            "phase": factory.get("phase"),
            "phase_minutes": factory.get("phase_minutes"),
            "throughput_24h": factory.get("throughput_24h"),
            "throughput_7d": factory.get("throughput_7d"),
            "supply": factory.get("supply"),
            "stack": factory.get("stack"),
            "last_slice": factory.get("last_slice"),
            "top_issue_code": factory.get("top_issue_code"),
            "top_issue_message": factory.get("top_issue_message"),
            "issues": factory.get("issues"),
            "commands": factory.get("commands"),
        },
        "operator_verdict": str(status.get("verdict") or ""),
        "chapter_mode": (status.get("chapter_mode") or {}).get("mode")
        if isinstance(status.get("chapter_mode"), dict)
        else None,
        "blocks_burst": blocks_burst,
        "blocks_build": blocks_build,
        "blocks_gate": blocks_gate,
        "docs": [PIPELINE_HEALTH_DOC, "docs/SOP/CHAPTER_COORDINATION_V1.md", "docs/SOP/FACTORY_THROUGHPUT_V1.md"],
    }


def write_pipeline_health(repo: Path, payload: dict[str, Any]) -> Path:
    out = repo / PIPELINE_HEALTH_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def format_root_cause_block(health: dict[str, Any]) -> str:
    """Markdown block for top of OPERATOR_STATUS.md."""
    factory = health.get("factory") if isinstance(health.get("factory"), dict) else {}
    factory_lines: list[str] = []
    try:
        from scripts.ppe_factory_throughput import format_throughput_lines

        if factory.get("verdict"):
            ft_payload = {
                "verdict": factory.get("verdict"),
                "phase": factory.get("phase"),
                "phase_minutes": factory.get("phase_minutes"),
                "throughput_24h": factory.get("throughput_24h") or {},
                "top_issue_message": factory.get("top_issue_message"),
                "supply": factory.get("supply") or {},
            }
            factory_lines = format_throughput_lines(ft_payload)
    except ImportError:
        pass

    if health.get("ok"):
        milestone = health.get("milestone") if isinstance(health.get("milestone"), dict) else {}
        next_build = milestone.get("next_build_candidate") or "—"
        lines = [
            "## Pipeline health\n",
            "**ROOT CAUSE:** none — pipeline + factory OK",
            f"**FIX CLASS:** `{FIX_PROCEED}`",
            f"**NEXT BUILD:** `{next_build}` (not blocked)",
        ]
        lines.extend(factory_lines)
        return "\n".join(lines) + "\n"

    code = health.get("root_cause_code") or "UNKNOWN"
    msg = health.get("root_cause_message") or "Pipeline unhealthy"
    fix_class = health.get("fix_class") or FIX_PARK
    milestone = health.get("milestone") if isinstance(health.get("milestone"), dict) else {}
    blocked = milestone.get("milestone_blocked_days")
    next_build = milestone.get("next_build_resolved") or milestone.get("next_build_candidate") or "—"
    steering_build = milestone.get("next_build_steering")
    active_id = milestone.get("active_chapter_id")
    pending = milestone.get("active_pending_count")
    if active_id and pending:
        blocked_line = f"**ACTIVE GATE:** `{active_id}` — {pending} pending slice(s)"
    elif blocked is not None:
        blocked_line = f"**MILESTONE BLOCKED:** `{next_build}` — ~{blocked} day(s)"
    else:
        blocked_line = f"**NEXT BUILD (resolved):** `{next_build}`"
    gate_detail_lines = format_milestone_gate_lines(milestone)
    if steering_build and milestone.get("steering_stale") and steering_build != next_build:
        gate_detail_lines = [
            f"**Steering drift:** `{steering_build}` (COMPLETE) → resolved `{next_build}`",
            *gate_detail_lines,
        ]
    cmds = health.get("commands") or []
    cmd_line = f"**FIX:** `{cmds[0]}`" if cmds else ""
    parts = [
        "## Pipeline health\n",
        f"**ROOT CAUSE:** `{code}` — {msg}",
        f"**FIX CLASS:** `{fix_class}`",
        blocked_line,
    ]
    for detail in gate_detail_lines:
        if detail not in parts:
            parts.append(detail)
    if cmd_line:
        parts.append(cmd_line)
    parts.extend(factory_lines)
    parts.append(
        "Detail: `artifacts/control_plane/PIPELINE_HEALTH.json` + "
        "`artifacts/control_plane/FACTORY_THROUGHPUT.json`"
    )
    return "\n".join(parts) + "\n"


def format_founder_report(health: dict[str, Any]) -> str:
    """~15-line human report for founder / phone."""
    lines = ["PPE pipeline health", ""]
    if health.get("ok"):
        lines.append("Status: OK — proceed with relay")
    else:
        lines.append(f"Status: ACTION NEEDED ({health.get('fix_class')})")
        lines.append(f"Root: {health.get('root_cause_code')} — {health.get('root_cause_message')}")
    milestone = health.get("milestone") if isinstance(health.get("milestone"), dict) else {}
    if milestone.get("next_build_candidate"):
        blocked = milestone.get("milestone_blocked_days")
        if blocked is not None:
            lines.append(
                f"Milestone: {milestone['next_build_candidate']} blocked ~{blocked}d"
            )
        else:
            lines.append(f"Next BUILD: {milestone['next_build_candidate']}")
    coord = health.get("coordination") if isinstance(health.get("coordination"), dict) else {}
    if coord.get("verdict"):
        lines.append(f"Coordination: {coord.get('verdict')} — {coord.get('summary')}")
    lines.append(f"Operator verdict: {health.get('operator_verdict')}  mode={health.get('chapter_mode')}")
    if health.get("blocks_burst"):
        lines.append("Burst: BLOCKED")
    if health.get("blocks_gate"):
        lines.append("Gate: BLOCKED on recovery/park paths")
    factory = health.get("factory") if isinstance(health.get("factory"), dict) else {}
    if factory.get("verdict"):
        t24 = factory.get("throughput_24h") or {}
        lines.append(
            f"Factory: {factory.get('verdict')} phase={factory.get('phase')} "
            f"24h slices={t24.get('slices', 0)} closeouts={t24.get('closeouts', 0)}"
        )
        if factory.get("top_issue_message"):
            lines.append(f"  {factory['top_issue_message']}")
    cmds = health.get("commands") or []
    if cmds:
        lines.append("")
        lines.append("Fix (first):")
        lines.append(f"  → {cmds[0]}")
    debt = milestone.get("oldest_closeout_debt") if isinstance(milestone.get("oldest_closeout_debt"), dict) else None
    if debt and debt.get("high_count"):
        lines.append("")
        lines.append(f"Closeout debt: {debt.get('high_count')} high-severity issue(s)")
    lines.append("")
    lines.append("OK" if health.get("ok") else "ACTION NEEDED")
    return "\n".join(lines)


def _load_health_state(repo: Path) -> dict[str, Any]:
    path = repo / PIPELINE_HEALTH_STATE_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _write_health_state(repo: Path, state: dict[str, Any]) -> Path:
    path = repo / PIPELINE_HEALTH_STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def maybe_notify_pipeline_regression(repo: Path, health: dict[str, Any]) -> bool:
    """Push ntfy when pipeline regresses OK→NOT OK or milestone blocked ≥24h."""
    try:
        from scripts.ppe_notify_push import ensure_operator_notify_env

        ensure_operator_notify_env(repo)
    except Exception:
        pass
    prev = _load_health_state(repo)
    now = _utc_now()
    was_ok = bool(prev.get("ok"))
    now_ok = bool(health.get("ok"))
    prev_code = str(prev.get("root_cause_code") or "")
    now_code = str(health.get("root_cause_code") or "")

    milestone = health.get("milestone") if isinstance(health.get("milestone"), dict) else {}
    blocked_days = milestone.get("milestone_blocked_days")
    last_blocked_alert = _parse_utc(str(prev.get("last_milestone_alert_at") or ""))

    should_notify = False
    title = "PPE pipeline health"
    body_lines: list[str] = []

    if was_ok and not now_ok:
        should_notify = True
        title = "PPE pipeline: regression"
        body_lines = [
            f"Was OK → now {health.get('fix_class')}",
            f"{now_code}: {health.get('root_cause_message')}",
        ]
    elif not now_ok and now_code and now_code != prev_code:
        should_notify = True
        title = f"PPE pipeline: {now_code}"
        body_lines = [str(health.get("root_cause_message") or "")]
    elif (
        not now_ok
        and isinstance(blocked_days, (int, float))
        and blocked_days >= 1.0
        and (last_blocked_alert is None or _days_since(last_blocked_alert) or 0 >= 1.0)
    ):
        should_notify = True
        title = "PPE pipeline: milestone blocked"
        body_lines = [
            f"{milestone.get('next_build_candidate')}: ~{blocked_days:.1f} day(s)",
            str(health.get("root_cause_message") or ""),
        ]

    state = {
        "as_of": now,
        "ok": now_ok,
        "root_cause_code": now_code or None,
        "fix_class": health.get("fix_class"),
        "milestone_blocked_days": blocked_days,
    }
    if should_notify:
        state["last_milestone_alert_at"] = now
        state["last_alert_at"] = now
    else:
        state["last_milestone_alert_at"] = prev.get("last_milestone_alert_at")
        state["last_alert_at"] = prev.get("last_alert_at")

    _write_health_state(repo, state)

    throughput_sent = False
    factory_blob = health.get("factory") if isinstance(health.get("factory"), dict) else {}
    if factory_blob.get("verdict"):
        try:
            from scripts.ppe_factory_throughput import maybe_notify_throughput_regression

            ft_payload = {
                "ok": factory_blob.get("ok", True),
                "verdict": factory_blob.get("verdict"),
                "top_issue_code": factory_blob.get("top_issue_code"),
                "top_issue_message": factory_blob.get("top_issue_message"),
                "commands": factory_blob.get("commands") or [],
                "issues": factory_blob.get("issues") or [],
            }
            throughput_sent = maybe_notify_throughput_regression(repo, ft_payload)
        except Exception:
            pass

    if not should_notify:
        return throughput_sent

    cmds = health.get("commands") or []
    if cmds:
        body_lines.append(f"Fix: {cmds[0]}")
    body = "\n".join(body_lines)

    try:
        from scripts.ppe_notify_push import notify_enabled, ntfy_configured, send_ntfy

        if not notify_enabled() or not ntfy_configured():
            return False
        return send_ntfy(
            title,
            body,
            tags=["ppe", "pipeline", str(health.get("fix_class") or "alert")],
            priority="high" if health.get("fix_class") in (FIX_RECOVERY, FIX_PARK) else "default",
        )
    except Exception:
        return False


def gate_check_pipeline_health(repo: Path, *, pre_push: bool = False) -> int:
    """Hard-block gate on recovery/park when on main or pre-push from main."""
    health = assess_pipeline_health(repo)
    if not health.get("blocks_gate"):
        return 0

    try:
        from scripts.ppe_delegation_envelope import current_branch

        branch = current_branch(repo)
    except Exception:
        branch = ""

    if branch not in ("main", "master"):
        return 0

    label = "pre-push" if pre_push else "commit"
    print(
        f"run_pushable_gate: pipeline health blocks {label} on main "
        f"({health.get('root_cause_code')}: {health.get('fix_class')})",
        file=sys.stderr,
    )
    print(f"  → {PIPELINE_HEALTH_REL}", file=sys.stderr)
    for cmd in health.get("commands") or []:
        print(f"  → {cmd}", file=sys.stderr)
    return 1


def gate_check_pipeline_on_sensitive_changes(repo: Path, files: list[str]) -> int:
    """Block commits on main touching coordination-sensitive paths when pipeline is recovery/park."""
    try:
        from scripts.ppe_chapter_coordination import COORDINATION_SENSITIVE_PREFIXES
    except ImportError:
        return 0

    try:
        from scripts.ppe_delegation_envelope import current_branch

        branch = current_branch(repo)
        if branch not in ("main", "master"):
            return 0
    except Exception:
        return 0

    norm = [f.replace("\\", "/") for f in files]
    sensitive = any(
        any(n == prefix or n.startswith(prefix) for prefix in COORDINATION_SENSITIVE_PREFIXES)
        for n in norm
    )
    if not sensitive:
        return 0
    return gate_check_pipeline_health(repo, pre_push=False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Founder pipeline diagnostics (root cause + milestone clock)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"Write {PIPELINE_HEALTH_REL}")
    ap.add_argument("--notify", action="store_true", help="Send ntfy on regression")
    ap.add_argument("--no-status", action="store_true", help="Skip prepare_operator_status (use cached inputs)")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    status: dict[str, Any] | None = None
    if not args.no_status:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)

    health = assess_pipeline_health(repo, status)
    if args.write:
        path = write_pipeline_health(repo, health)
        if not args.json:
            print(f"ppe_pipeline_health: wrote {path.relative_to(repo)}")

    if args.notify:
        maybe_notify_pipeline_regression(repo, health)

    if args.json:
        print(json.dumps(health, indent=2))
    else:
        print(format_founder_report(health))

    return 0 if health.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
