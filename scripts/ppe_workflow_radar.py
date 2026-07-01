"""Weekly workflow radar — friction signals, orphan detection, safe auto-cleanup."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from scripts.ppe_weekly_digest import (
    classify_bullet,
    collect_week_bullets,
    last_completed_week_monday,
    monday_of_week,
    week_dates,
)
from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _parse_iso, _read_jsonl
from scripts.workflow_metrics_cli import context_windows_in_week

RADAR_VERSION = 1
CONTROL_PLANE_DIR = "artifacts/control_plane"
RADAR_LATEST_JSON = f"{CONTROL_PLANE_DIR}/WORKFLOW_RADAR_LATEST.json"
RADAR_LATEST_MD = f"{CONTROL_PLANE_DIR}/WORKFLOW_RADAR_LATEST.md"

GUARD_REPORT_REL = "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
LAST_RUN_JSON_REL = "artifacts/orchestrator/LAST_RUN_REPORT.json"
ACTIVE_RUN_REL = "artifacts/orchestrator/ACTIVE_RUN.json"
BUILD_LOCK_REL = "artifacts/orchestrator/REMOTE_BUILD_LOCK.json"
POST_BUILD_STATE_REL = "artifacts/orchestrator/POST_BUILD_WATCHER_STATE.json"
TRIGGER_REL = ".cursor/IDE_BUILD_TRIGGER.json"

Severity = Literal["escalate", "watch", "info"]

OPS_CHURN_PATTERNS = (
    re.compile(r"fix\(tests\)", re.I),
    re.compile(r"\boperator\b", re.I),
    re.compile(r"\bguard\b", re.I),
    re.compile(r"Workflow-efficiency", re.I),
    re.compile(r"FIX_PLAN", re.I),
)

STALE_TRIGGER_HOURS = 24
STALE_JOB_HOURS = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def radar_json_path(repo: Path, week_monday: date) -> Path:
    return repo / CONTROL_PLANE_DIR / f"WORKFLOW_RADAR_{week_monday.isoformat()}.json"


def _in_week(ts: str | None, week_monday: date) -> bool:
    if not ts:
        return False
    dt = _parse_iso(ts)
    if dt is None:
        return False
    start = datetime.combine(week_monday, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=7)
    return start <= dt.replace(tzinfo=timezone.utc) < end


def _file_mtime_in_week(path: Path, week_monday: date) -> bool:
    if not path.is_file():
        return False
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    start = datetime.combine(week_monday, datetime.min.time(), tzinfo=timezone.utc)
    end = start + timedelta(days=7)
    return start <= mtime < end


def _read_json_file(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


@dataclass
class RadarCandidate:
    id: str
    severity: Severity
    title: str
    evidence: list[str]
    suggested_action: str
    charter_hint: str = "Workflow-Hardening-Slice-00N"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "title": self.title,
            "evidence": list(self.evidence),
            "suggested_action": self.suggested_action,
            "charter_hint": self.charter_hint,
        }


@dataclass
class OrphanFinding:
    id: str
    severity: Severity
    title: str
    detail: str
    path: str = ""
    auto_cleanable: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity,
            "title": self.title,
            "detail": self.detail,
            "path": self.path,
            "auto_cleanable": self.auto_cleanable,
        }


@dataclass
class CleanupAction:
    action: str
    target: str
    result: str

    def to_dict(self) -> dict[str, Any]:
        return {"action": self.action, "target": self.target, "result": self.result}


@dataclass
class RadarReport:
    week_monday: str
    generated_at_utc: str
    signal_counts: dict[str, int] = field(default_factory=dict)
    candidates: list[RadarCandidate] = field(default_factory=list)
    orphans: list[OrphanFinding] = field(default_factory=list)
    cleanup_actions: list[CleanupAction] = field(default_factory=list)
    summary_line: str = ""
    token_economy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": RADAR_VERSION,
            "week_monday": self.week_monday,
            "generated_at_utc": self.generated_at_utc,
            "signal_counts": dict(self.signal_counts),
            "candidates": [c.to_dict() for c in self.candidates],
            "orphans": [o.to_dict() for o in self.orphans],
            "cleanup_actions": [a.to_dict() for a in self.cleanup_actions],
            "summary_line": self.summary_line,
            "token_economy": dict(self.token_economy),
        }


def _slices_in_week(repo: Path, week_monday: date) -> list[dict[str, Any]]:
    rows = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
    out: list[dict[str, Any]] = []
    for row in rows:
        completed = str(row.get("completed_at") or row.get("closed_at") or "").strip()
        if _in_week(completed, week_monday):
            out.append(row)
    return out


def scan_workflow_friction(repo: Path, week_monday: date) -> tuple[list[RadarCandidate], dict[str, int]]:
    signals: dict[str, int] = {}
    candidates: list[RadarCandidate] = []

    slices = _slices_in_week(repo, week_monday)
    high_rt = [
        s
        for s in slices
        if int(s.get("roundtrips") or 0) >= 3 and str(s.get("slice_id") or s.get("sliceId") or "").strip()
    ]
    if len(high_rt) >= 2:
        signals["high_roundtrips"] = len(high_rt)
        evidence = [
            f"{s.get('slice_id') or s.get('sliceId')}: {int(s.get('roundtrips') or 0)} roundtrips"
            for s in high_rt[:5]
        ]
        candidates.append(
            RadarCandidate(
                id="high-roundtrips",
                severity="watch",
                title="Multiple slices needed 3+ roundtrips",
                evidence=evidence,
                suggested_action="Trim BUILD packets or use integrated closeout for low-risk slices.",
            )
        )

    incidents = [s for s in slices if s.get("incident_flag") in (True, "true", 1, "1")]
    if incidents:
        signals["incidents"] = len(incidents)
        candidates.append(
            RadarCandidate(
                id="slice-incidents",
                severity="watch",
                title="Slice incident flags recorded this week",
                evidence=[
                    str(s.get("slice_id") or s.get("sliceId") or "unknown") for s in incidents[:5]
                ],
                suggested_action="Review incident notes in workflow metrics; charter a hardening slice if pattern repeats.",
            )
        )

    rework = [s for s in slices if int(s.get("rework_count") or 0) > 0]
    if rework:
        signals["rework"] = len(rework)
        candidates.append(
            RadarCandidate(
                id="slice-rework",
                severity="info",
                title="Slices with rework logged",
                evidence=[str(s.get("slice_id") or s.get("sliceId") or "unknown") for s in rework[:5]],
                suggested_action="Check whether acceptance criteria or handoff packets need tightening.",
            )
        )

    guard_path = repo / GUARD_REPORT_REL
    if _file_mtime_in_week(guard_path, week_monday):
        signals["guard_stops"] = signals.get("guard_stops", 0) + 1
        text = _read_text(guard_path)
        reason_match = re.search(r"\*\*Reason:\*\* `([^`]+)`", text)
        reason = reason_match.group(1) if reason_match else "unknown"
        severity: Severity = "escalate" if reason in ("CONTEXT_ESCALATE", "TOO_MANY_SLICES") else "watch"
        candidates.append(
            RadarCandidate(
                id="guard-stop",
                severity=severity,
                title=f"Operator guard stop ({reason})",
                evidence=[f"See {GUARD_REPORT_REL}"],
                suggested_action="Split sprint spec, trim handoff packet, or run a Workflow-Hardening slice.",
            )
        )

    last_run = _read_json_file(repo / LAST_RUN_JSON_REL)
    if last_run and last_run.get("awaiting_user"):
        generated = str(last_run.get("generated_at_utc") or last_run.get("as_of") or "").strip()
        if _in_week(generated, week_monday) or _file_mtime_in_week(repo / LAST_RUN_JSON_REL, week_monday):
            signals["stale_last_run"] = 1
            bucket = str(last_run.get("status_bucket") or "review")
            candidates.append(
                RadarCandidate(
                    id="stale-last-run",
                    severity="watch",
                    title="Relay run left awaiting user attention",
                    evidence=[f"status_bucket={bucket}", f"See {LAST_RUN_JSON_REL}"],
                    suggested_action="Read LAST_RUN_REPORT.md and clear blocker before next auto-loop pass.",
                )
            )

    bullets, total = collect_week_bullets(repo, week_monday)
    ops_count = sum(1 for b in bullets if classify_bullet(b) == "ops")
    if total >= 10 and ops_count / total > 0.7:
        signals["ops_heavy_week"] = ops_count
        candidates.append(
            RadarCandidate(
                id="ops-heavy-week",
                severity="info",
                title="Ops-heavy merge week",
                evidence=[f"{ops_count}/{total} merges were control-plane / planning"],
                suggested_action="Confirm product backlog supply; consider queuing the next product chapter.",
            )
        )

    churn = 0
    for b in bullets:
        body = b[2:].strip() if b.startswith("- ") else b
        if any(p.search(body) for p in OPS_CHURN_PATTERNS):
            churn += 1
    if churn >= 3:
        signals["operator_churn"] = churn
        candidates.append(
            RadarCandidate(
                id="operator-churn",
                severity="watch",
                title="Repeated operator / guard / test-fix churn",
                evidence=[f"{churn} changelog bullets matched operator churn patterns"],
                suggested_action="Charter a Workflow-Hardening slice targeting the recurring blocker.",
            )
        )

    ctx_closeouts = context_windows_in_week(repo, week_monday)
    if ctx_closeouts:
        signals["context_closeouts"] = len(ctx_closeouts)
        slices_in_week = _slices_in_week(repo, week_monday)
        slices_closed = len(slices_in_week)
        zero_slice_closeouts = sum(
            1 for c in ctx_closeouts if int(c.get("slices_closed_in_thread") or 0) == 0
        )
        if len(ctx_closeouts) >= 3 and slices_closed == 0:
            signals["context_chat_churn"] = len(ctx_closeouts)
            candidates.append(
                RadarCandidate(
                    id="context-chat-churn",
                    severity="info",
                    title="Many context closeouts, no slices closed this week",
                    evidence=[
                        f"context_closeouts={len(ctx_closeouts)}",
                        f"slices_closed_in_week={slices_closed}",
                        f"zero_slice_closeouts={zero_slice_closeouts}",
                    ],
                    suggested_action=(
                        "Prefer shorter steward threads or run relay between closeouts; "
                        "see artifacts/workflow_metrics/context_windows.jsonl."
                    ),
                )
            )

    return candidates, signals


def scan_structural_health(repo: Path) -> tuple[list[RadarCandidate], dict[str, int]]:
    signals: dict[str, int] = {}
    candidates: list[RadarCandidate] = []

    block: dict[str, Any] | None = None
    health_root = repo / "artifacts" / "health"
    if health_root.is_dir():
        reports = sorted(
            health_root.glob("*/codebase_health_report.json"),
            key=lambda p: p.parent.name,
        )
        if reports:
            try:
                raw = json.loads(reports[-1].read_text(encoding="utf-8-sig"))
                block = raw.get("structural_health") if isinstance(raw, dict) else None
            except (json.JSONDecodeError, OSError):
                block = None

    if not block:
        try:
            from scripts.ppe_structural_health import structural_health_block

            block = structural_health_block(repo)
        except Exception:
            return candidates, signals

    warnings = block.get("warnings") or []
    if warnings:
        signals["structural_health"] = len(warnings)

    for item in warnings:
        if not isinstance(item, dict):
            continue
        severity_raw = str(item.get("severity") or "info")
        severity: Severity = "watch" if severity_raw == "watch" else "info"
        if severity_raw == "escalate":
            severity = "escalate"
        candidates.append(
            RadarCandidate(
                id=str(item.get("id") or "structural"),
                severity=severity,
                title=str(item.get("message") or "Structural health warning"),
                evidence=[
                    f"{item.get('metric')}={item.get('value')} (threshold {item.get('threshold')})"
                ],
                suggested_action=(
                    "Review repo layer map; charter between-chapter housekeeping if overdue."
                ),
            )
        )

    return candidates, signals


def scan_orphans(repo: Path) -> list[OrphanFinding]:
    findings: list[OrphanFinding] = []
    repo = repo.resolve()

    try:
        from scripts.ppe_remote_agent_spawn import process_alive
    except ImportError:
        process_alive = None  # type: ignore[assignment]

    lock_raw = _read_json_file(repo / BUILD_LOCK_REL)
    if lock_raw:
        stale = False
        detail = "build lock present"
        worker_pid = lock_raw.get("worker_pid")
        if worker_pid is not None and process_alive is not None:
            try:
                if not process_alive(int(worker_pid)):
                    stale = True
                    detail = f"REMOTE_BUILD_LOCK worker_pid={worker_pid} is not running"
            except (TypeError, ValueError):
                stale = True
        else:
            try:
                from scripts.ppe_remote_build_agent import is_build_lock_stale

                stale = is_build_lock_stale(repo, lock_raw)
                if stale:
                    detail = "REMOTE_BUILD_LOCK is stale (no live worker / timed out)"
            except ImportError:
                pass
        findings.append(
            OrphanFinding(
                id="stale-build-lock",
                severity="watch" if stale else "info",
                title="Stale IDE build lock" if stale else "IDE build lock active",
                detail=detail,
                path=BUILD_LOCK_REL,
                auto_cleanable=stale,
            )
        )

    active_run = repo / ACTIVE_RUN_REL
    if active_run.is_file():
        findings.append(
            OrphanFinding(
                id="active-run-artifact",
                severity="info",
                title="ACTIVE_RUN.json present on disk",
                detail="May be in-flight or stale relative to manifest",
                path=ACTIVE_RUN_REL,
                auto_cleanable=True,
            )
        )

    trigger = _read_json_file(repo / TRIGGER_REL)
    if trigger:
        status = str(trigger.get("status") or "").lower()
        if status in ("pending", "dispatched"):
            handoff = str(trigger.get("handoffAt") or trigger.get("dispatchedAt") or "").strip()
            dt = _parse_iso(handoff) if handoff else None
            age_hours = (
                (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0 if dt is not None else None
            )
            worker_pid = trigger.get("worker_pid")
            worker_dead = False
            if worker_pid is not None and process_alive is not None:
                try:
                    worker_dead = not process_alive(int(worker_pid))
                except (TypeError, ValueError):
                    worker_dead = True
            stale_trigger = (age_hours is not None and age_hours >= STALE_TRIGGER_HOURS) or worker_dead
            if stale_trigger:
                findings.append(
                    OrphanFinding(
                        id="stale-ide-trigger",
                        severity="watch",
                        title=f"IDE_BUILD_TRIGGER stuck in {status!r}",
                        detail=f"handoff age={age_hours:.1f}h" if age_hours is not None else "no timestamp",
                        path=TRIGGER_REL,
                        auto_cleanable=True,
                    )
                )

    job_dir = repo / "artifacts" / "orchestrator"
    if job_dir.is_dir():
        now = datetime.now(timezone.utc)
        for job in sorted(job_dir.glob("POST_BUILD_FINISH_JOB_*.json")):
            age_h = (now - datetime.fromtimestamp(job.stat().st_mtime, tz=timezone.utc)).total_seconds() / 3600.0
            if age_h < STALE_JOB_HOURS:
                continue
            findings.append(
                OrphanFinding(
                    id="orphan-post-build-job",
                    severity="info",
                    title="Orphan post-build finish job file",
                    detail=f"{job.name} age={age_h:.1f}h",
                    path=job.relative_to(repo).as_posix(),
                    auto_cleanable=True,
                )
            )

    post_state = _read_json_file(repo / POST_BUILD_STATE_REL)
    if post_state:
        pid = post_state.get("worker_pid")
        if pid is not None and process_alive is not None:
            try:
                if not process_alive(int(pid)):
                    findings.append(
                        OrphanFinding(
                            id="stale-post-build-state",
                            severity="info",
                            title="Post-build watcher state references dead worker",
                            detail=f"worker_pid={pid}",
                            path=POST_BUILD_STATE_REL,
                            auto_cleanable=True,
                        )
                    )
            except (TypeError, ValueError):
                pass

    try:
        from scripts.ppe_desktop_operator_stack import is_loop_running

        if is_loop_running():
            import os

            if os.environ.get("PPE_HEADLESS_SUPERVISED_LOOP", "").strip() != "1":
                pass
    except ImportError:
        pass

    return findings


def auto_cleanup_orphans(repo: Path, *, dry_run: bool = False) -> list[CleanupAction]:
    """Safe cleanup of stale locks, triggers, and leftover job files."""
    repo = repo.resolve()
    actions: list[CleanupAction] = []
    orphans = scan_orphans(repo)

    for finding in orphans:
        if not finding.auto_cleanable:
            continue

        if finding.id == "stale-build-lock":
            target = BUILD_LOCK_REL
            if dry_run:
                actions.append(CleanupAction("would_clear", target, "stale REMOTE_BUILD_LOCK"))
            else:
                try:
                    from scripts.ppe_remote_build_agent import clear_build_lock

                    clear_build_lock(repo)
                    actions.append(CleanupAction("cleared", target, "stale REMOTE_BUILD_LOCK"))
                except ImportError:
                    (repo / BUILD_LOCK_REL).unlink(missing_ok=True)
                    actions.append(CleanupAction("cleared", target, "removed lock file"))

        elif finding.id == "active-run-artifact":
            target = ACTIVE_RUN_REL
            try:
                from scripts.ppe_manifest import load_manifest
                from scripts.ppe_preflight import maybe_clear_stale_active_run

                manifest = load_manifest(repo)
                reason = maybe_clear_stale_active_run(repo, manifest)
                if reason:
                    if dry_run:
                        actions.append(CleanupAction("would_clear", target, reason))
                    else:
                        actions.append(CleanupAction("cleared", target, reason))
            except (ImportError, FileNotFoundError, json.JSONDecodeError):
                pass

        elif finding.id == "stale-ide-trigger":
            target = TRIGGER_REL
            if dry_run:
                actions.append(CleanupAction("would_idle", target, "reset stuck IDE_BUILD_TRIGGER"))
            else:
                try:
                    from scripts.ppe_ide_build_automation_trigger import write_trigger_idle

                    write_trigger_idle(repo)
                    actions.append(CleanupAction("cleared", target, "reset IDE_BUILD_TRIGGER to idle"))
                except ImportError:
                    pass

        elif finding.id == "orphan-post-build-job":
            target = finding.path
            job = repo / target
            if dry_run:
                actions.append(CleanupAction("would_delete", target, finding.detail))
            else:
                job.unlink(missing_ok=True)
                actions.append(CleanupAction("deleted", target, finding.detail))

        elif finding.id == "stale-post-build-state":
            target = POST_BUILD_STATE_REL
            if dry_run:
                actions.append(CleanupAction("would_prune", target, "remove dead worker_pid"))
            else:
                try:
                    from scripts.ppe_post_build_watcher import load_state, save_state

                    state = load_state(repo)
                    state.pop("worker_pid", None)
                    save_state(repo, state)
                    actions.append(CleanupAction("pruned", target, "removed dead worker_pid"))
                except ImportError:
                    pass

    return actions


def _rank_severity(severity: Severity) -> int:
    return {"escalate": 0, "watch": 1, "info": 2}[severity]


def _token_friction_candidates(repo: Path) -> tuple[list[RadarCandidate], dict[str, Any]]:
    try:
        from scripts.ppe_token_audit import build_token_audit, scan_token_friction
    except ImportError:
        return [], {}

    report = build_token_audit(repo)
    data = report.to_dict()
    summary = {
        "verdict": report.verdict,
        "always_on_est_tokens_per_turn": data["always_on_est_tokens_per_turn"],
        "starter_count": len(data["starters"]),
        "starter_max_lines": data["starter_line_max"],
    }
    from scripts.ppe_token_audit import scan_token_friction

    candidates: list[RadarCandidate] = []
    for sig in scan_token_friction(repo):
        sid = str(sig.get("id") or "token")
        severity = sig.get("severity")
        if severity not in ("escalate", "watch", "info"):
            continue
        detail = str(sig.get("detail") or "")
        action = "token_audit.cmd --prune-stale; regenerate starters; verify_codex.cmd"
        if sid == "always-on-rules-heavy":
            action = "Keep ppe-operator-core + ppe-desktop-vm-layout always-on only."
        candidates.append(
            RadarCandidate(
                id=sid,
                severity=severity,  # type: ignore[arg-type]
                title=f"Token: {sid.replace('-', ' ')}",
                evidence=[detail],
                suggested_action=action,
            )
        )
    return candidates, summary


def _build_summary(candidates: list[RadarCandidate], orphans: list[OrphanFinding], cleanup: list[CleanupAction]) -> str:
    orphan_stale = [o for o in orphans if o.auto_cleanable]
    parts: list[str] = []
    if candidates:
        charter_worthy = sum(1 for c in candidates if c.severity in ("escalate", "watch"))
        parts.append(f"{len(candidates)} friction signal(s)")
        if charter_worthy:
            parts.append(f"{charter_worthy} worth chartering")
    if orphan_stale:
        parts.append(f"{len(orphan_stale)} orphan artifact(s)")
    if cleanup:
        parts.append(f"{len(cleanup)} auto-cleaned")
    if not parts:
        return "Clean week — no workflow friction or orphans detected."
    return " — ".join(parts) + "."


def build_radar_report(
    repo: Path,
    week_monday: date,
    *,
    run_cleanup: bool = True,
    cleanup_dry_run: bool = False,
) -> RadarReport:
    repo = repo.resolve()
    candidates, signals = scan_workflow_friction(repo, week_monday)
    struct_candidates, struct_signals = scan_structural_health(repo)
    candidates.extend(struct_candidates)
    signals.update(struct_signals)
    orphans = scan_orphans(repo)

    orphan_stale_count = sum(1 for o in orphans if o.auto_cleanable)
    if orphan_stale_count:
        signals["orphan_artifacts"] = orphan_stale_count

    cleanup: list[CleanupAction] = []
    if run_cleanup and any(o.auto_cleanable for o in orphans):
        cleanup = auto_cleanup_orphans(repo, dry_run=cleanup_dry_run)
        if cleanup and not cleanup_dry_run:
            orphans = scan_orphans(repo)

    token_candidates, token_summary = _token_friction_candidates(repo)
    if token_summary.get("verdict"):
        signals["token_verdict"] = 1 if token_summary["verdict"] != "OK" else 0
    candidates.extend(token_candidates)

    try:
        from scripts.ppe_tracking_hub import scan_tracking_friction

        tracking_candidates = scan_tracking_friction(repo, week_monday)
        candidates.extend(tracking_candidates)
        if tracking_candidates:
            signals["tracking_friction"] = len(tracking_candidates)
    except Exception:
        pass

    candidates.sort(key=lambda c: (_rank_severity(c.severity), c.id))
    capped = candidates[:5]

    return RadarReport(
        week_monday=week_monday.isoformat(),
        generated_at_utc=_utc_now(),
        signal_counts=signals,
        candidates=capped,
        orphans=orphans,
        cleanup_actions=cleanup,
        summary_line=_build_summary(capped, orphans, cleanup),
        token_economy=token_summary,
    )


def render_radar_markdown(report: RadarReport, *, repo: Path | None = None) -> str:
    lines = [
        "# Workflow radar (latest)",
        "",
        f"**Week:** {report.week_monday} (Mon–Sun UTC)",
        f"**Generated:** {report.generated_at_utc}",
        "",
        f"**Summary:** {report.summary_line}",
        "",
    ]

    if report.candidates:
        lines.append("## Friction candidates")
        for c in report.candidates:
            lines.append(f"### {c.title} (`{c.severity}`)")
            for ev in c.evidence:
                lines.append(f"- {ev}")
            lines.append(f"- **Action:** {c.suggested_action}")
            lines.append("")
    else:
        lines.append("## Friction candidates")
        lines.append("- None this week.")
        lines.append("")

    if report.orphans:
        lines.append("## Orphan / stale artifacts")
        for o in report.orphans:
            flag = "auto-cleanable" if o.auto_cleanable else "report-only"
            lines.append(f"- **{o.title}** ({flag}): {o.detail}")
            if o.path:
                lines.append(f"  - `{o.path}`")
        lines.append("")

    if report.cleanup_actions:
        lines.append("## Auto-cleanup")
        for a in report.cleanup_actions:
            lines.append(f"- `{a.action}` {a.target}: {a.result}")
        lines.append("")

    if report.token_economy:
        te = report.token_economy
        lines.extend([
            "## Token economy",
            "",
            f"- Verdict: `{te.get('verdict', '?')}` · always-on ~{te.get('always_on_est_tokens_per_turn', '?')} tok/turn",
            f"- Starters: {te.get('starter_count', 0)} on disk · max {te.get('starter_max_lines', 0)} lines",
            "",
        ])

    lines.append("Promotion: steward SELECTION → Workflow-Hardening-Slice-00N (advisory only).")
    if repo is not None:
        try:
            from scripts.ppe_workflow_cost import format_lane_summary_line, summarize_by_lane

            lines.insert(6, f"**{format_lane_summary_line(summarize_by_lane(repo, days=7))}**")
            lines.insert(7, "")
        except Exception:
            pass
    return "\n".join(lines).rstrip() + "\n"


def write_radar_artifacts(repo: Path, report: RadarReport) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / CONTROL_PLANE_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    week_path = radar_json_path(repo, date.fromisoformat(report.week_monday))
    latest_json = repo / RADAR_LATEST_JSON
    latest_md = repo / RADAR_LATEST_MD
    payload = json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
    week_path.write_text(payload, encoding="utf-8")
    latest_json.write_text(payload, encoding="utf-8")
    latest_md.write_text(render_radar_markdown(report, repo=repo), encoding="utf-8")
    return week_path, latest_md


def load_radar_friction_lines(repo: Path, week_monday: date) -> list[str]:
    """Markdown bullets for weekly digest integration."""
    p = radar_json_path(repo, week_monday)
    if not p.is_file():
        latest = repo / RADAR_LATEST_JSON
        if latest.is_file():
            try:
                data = json.loads(latest.read_text(encoding="utf-8"))
                if str(data.get("week_monday") or "") != week_monday.isoformat():
                    return []
                p = latest
            except (OSError, json.JSONDecodeError):
                return []
        else:
            return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []

    lines: list[str] = []
    for c in data.get("candidates") or []:
        if not isinstance(c, dict):
            continue
        title = str(c.get("title") or "").strip()
        action = str(c.get("suggested_action") or "").strip()
        if title:
            lines.append(f"- {title}" + (f" — {action}" if action else ""))

    orphans = [o for o in (data.get("orphans") or []) if isinstance(o, dict) and o.get("auto_cleanable")]
    cleanup = data.get("cleanup_actions") or []
    if orphans and not cleanup:
        lines.append(f"- {len(orphans)} stale operator artifact(s) need cleanup (run workflow radar).")
    elif cleanup:
        lines.append(f"- Auto-cleaned {len(cleanup)} orphan operator artifact(s).")

    try:
        from scripts.ppe_token_reconcile import digest_reconcile_line
        rec = digest_reconcile_line(repo, days=30)
        if rec and len(lines) < 4:
            lines.append(rec)
    except ImportError:
        pass

    return lines[:4]


def cmd_generate(
    repo: Path,
    *,
    week_monday: date | None = None,
    run_cleanup: bool = True,
    cleanup_dry_run: bool = False,
) -> int:
    repo = repo.resolve()
    target = week_monday or last_completed_week_monday()
    report = build_radar_report(repo, target, run_cleanup=run_cleanup, cleanup_dry_run=cleanup_dry_run)
    week_path, md_path = write_radar_artifacts(repo, report)
    print(f"ppe_workflow_radar: {report.summary_line}")
    print(f"ppe_workflow_radar: wrote {week_path.relative_to(repo)}")
    print(f"ppe_workflow_radar: wrote {md_path.relative_to(repo)}")
    return 0


def cmd_cleanup(repo: Path, *, dry_run: bool = False) -> int:
    actions = auto_cleanup_orphans(repo.resolve(), dry_run=dry_run)
    if not actions:
        print("ppe_workflow_radar: no orphan cleanup needed")
        return 0
    for a in actions:
        print(f"ppe_workflow_radar: {a.action} {a.target} — {a.result}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Weekly workflow radar (friction + orphan cleanup)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Scan week + optional orphan cleanup")
    p_gen.add_argument("--week", type=str, default=None, help="Week Monday YYYY-MM-DD")
    p_gen.add_argument("--no-cleanup", action="store_true", help="Skip orphan auto-cleanup")
    p_gen.add_argument("--cleanup-dry-run", action="store_true", help="Report cleanup without applying")

    p_cl = sub.add_parser("cleanup", help="Orphan cleanup only")
    p_cl.add_argument("--dry-run", action="store_true")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "generate":
        week: date | None = None
        if args.week:
            week = monday_of_week(date.fromisoformat(args.week))
        return cmd_generate(
            repo,
            week_monday=week,
            run_cleanup=not args.no_cleanup,
            cleanup_dry_run=args.cleanup_dry_run,
        )
    if args.command == "cleanup":
        return cmd_cleanup(repo, dry_run=args.dry_run)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
