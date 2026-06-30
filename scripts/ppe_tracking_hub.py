"""Unified tracking hub — events, validation, steering drift, assets, trader outcomes."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from scripts.workflow_metrics_cli import (
    SLICES_FILE,
    _metrics_dir,
    _parse_iso,
    _read_jsonl,
    append_event_row,
    events_in_days,
    read_context_windows,
)

DEMO_SESSIONS_REL = "artifacts/validation/demo_sessions.jsonl"
TRACKING_STATUS_JSON = "artifacts/control_plane/TRACKING_STATUS_LATEST.json"
TRACKING_STATUS_MD = "artifacts/control_plane/TRACKING_STATUS_LATEST.md"

EventType = Literal[
    "validation_session",
    "asset_witness",
    "context_closeout",
    "steering_drift",
    "trader_outcome_snapshot",
    "usage_note",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def record_event(
    repo: Path,
    *,
    event_type: str,
    note: str = "",
    slice_id: str | None = None,
    session_id: str | None = None,
    value_1: str | int | float | None = None,
    value_2: str | int | float | None = None,
) -> dict[str, Any]:
    row = append_event_row(
        repo,
        event_type=event_type,
        note=note,
        slice_id=slice_id,
        session_id=session_id,
        value_1=value_1,
        value_2=value_2,
    )
    return row


def record_validation_session(repo: Path, row: dict[str, Any]) -> dict[str, Any]:
    clarity = str(row.get("clarity") or row.get("pass") or "")
    return_again = str(row.get("return_again") or "")
    return record_event(
        repo,
        event_type="validation_session",
        note=str(row.get("notes") or ""),
        value_1=clarity,
        value_2=return_again,
        session_id=str(row.get("profile") or ""),
    )


def record_asset_witness(repo: Path, report: dict[str, Any]) -> dict[str, Any]:
    results = report.get("results") or []
    tested = sum(1 for r in results if isinstance(r, dict) and not r.get("skipped"))
    failed = sum(1 for r in results if isinstance(r, dict) and not r.get("ok") and not r.get("skipped"))
    return record_event(
        repo,
        event_type="asset_witness",
        note=str(report.get("catalog_detail") or ""),
        value_1=tested,
        value_2=failed,
    )


def record_context_closeout_event(repo: Path, record: dict[str, Any]) -> dict[str, Any]:
    slices_closed = int(record.get("slices_closed_in_thread") or 0)
    triage = record.get("triage_counts") if isinstance(record.get("triage_counts"), dict) else {}
    parked = int(triage.get("park") or triage.get("parked") or 0)
    return record_event(
        repo,
        event_type="context_closeout",
        note=str(record.get("whats_next") or "")[:240],
        slice_id=str(record.get("chapter_id") or "") or None,
        value_1=slices_closed,
        value_2=parked,
    )


def _read_demo_sessions(repo: Path) -> list[dict[str, Any]]:
    path = repo / DEMO_SESSIONS_REL
    return _read_jsonl(path)


def demo_sessions_in_days(repo: Path, days: int) -> list[dict[str, Any]]:
    if days <= 0:
        return _read_demo_sessions(repo)
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    out: list[dict[str, Any]] = []
    for row in _read_demo_sessions(repo):
        raw = str(row.get("date") or row.get("logged_at") or "").strip()
        if not raw:
            continue
        try:
            if len(raw) == 10:
                dt = datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)
            else:
                dt = _parse_iso(raw)
            if dt and dt.timestamp() >= cutoff:
                out.append(row)
        except ValueError:
            continue
    return out


def collect_asset_enablement(repo: Path) -> dict[str, Any]:
    try:
        from src.data.assets_registry import (
            list_asset_ids,
            list_enabled_asset_ids,
            load_tier1_manifest,
        )
    except ImportError:
        return {"available": False, "error": "assets_registry unavailable"}

    enabled = list_enabled_asset_ids()
    total = list_asset_ids()
    manifest = load_tier1_manifest()
    target = manifest.get("target_enabled_count")
    try:
        target_n = int(target) if target is not None else None
    except (TypeError, ValueError):
        target_n = None
    return {
        "available": True,
        "enabled_count": len(enabled),
        "total_registered": len(total),
        "target_enabled_count": target_n,
        "enabled_ids": enabled,
        "gap_to_target": (target_n - len(enabled)) if target_n is not None else None,
    }


def collect_steering_drift(repo: Path) -> dict[str, Any]:
    gaps: list[str] = []
    try:
        from scripts.active_product_direction import Direction, load_direction, markers_need_sync

        direction: Direction = load_direction(repo)
        direction_chapter = direction.active_chapter_id.strip()
        direction_plan = direction.active_plan_path.strip()

        if markers_need_sync(repo):
            gaps.append("product_direction markers need sync (run sync_product_direction.cmd)")

        from scripts.ppe_manifest import load_manifest, resolve_summary

        summary = resolve_summary(repo)
        manifest_plan = str(summary.get("phase_plan_path") or "").strip()
        manifest_chapter = str(summary.get("chapter_name") or "").strip()

        if direction_plan and manifest_plan and direction_plan != manifest_plan:
            gaps.append(f"direction plan {direction_plan!r} != manifest plan {manifest_plan!r}")
        if direction_chapter and manifest_chapter and direction_chapter != manifest_chapter:
            gaps.append(f"direction chapter {direction_chapter!r} != manifest chapter {manifest_chapter!r}")

        return {
            "aligned": len(gaps) == 0,
            "gap_count": len(gaps),
            "gaps": gaps,
            "direction_chapter": direction_chapter or None,
            "direction_plan": direction_plan or None,
            "manifest_chapter": manifest_chapter or None,
            "manifest_plan": manifest_plan or None,
        }
    except Exception as exc:
        return {"aligned": False, "gap_count": 1, "gaps": [str(exc)], "error": str(exc)}


def collect_trader_outcomes(repo: Path) -> dict[str, Any]:
    try:
        from src.viz.frozen_evaluation_store import (
            default_db_path,
            init_schema,
            list_completed_review_snapshots,
            list_snapshots_pending_review,
            _connect,
        )
    except ImportError:
        return {"available": False, "error": "frozen_evaluation_store unavailable"}

    db_path = default_db_path()
    if not db_path.is_file():
        return {
            "available": True,
            "db_path": str(db_path),
            "db_exists": False,
            "frozen_total": 0,
            "pending_review": 0,
            "completed_reviews": 0,
            "completion_rate": None,
            "median_days_to_review": None,
        }

    conn = _connect(db_path)
    try:
        init_schema(conn)
        frozen_total = int(
            conn.execute("SELECT COUNT(*) FROM frozen_evaluations").fetchone()[0]
        )
        pending = len(list_snapshots_pending_review(conn, limit=10_000))
        completed_rows = list_completed_review_snapshots(conn, limit=10_000)
        completed = len(completed_rows)

        completion_rate: float | None = None
        if frozen_total > 0:
            completion_rate = round(completed / frozen_total, 3)

        deltas: list[float] = []
        for row in completed_rows:
            created = _parse_iso(str(row.get("created_at") or ""))
            reviewed = _parse_iso(str(row.get("reviewed_at_utc") or ""))
            if created and reviewed:
                deltas.append((reviewed - created).total_seconds() / 86400.0)
        median_days: float | None = None
        if deltas:
            deltas.sort()
            mid = len(deltas) // 2
            median_days = round(deltas[mid], 1)

        return {
            "available": True,
            "db_path": str(db_path),
            "db_exists": True,
            "frozen_total": frozen_total,
            "pending_review": pending,
            "completed_reviews": completed,
            "completion_rate": completion_rate,
            "median_days_to_review": median_days,
        }
    finally:
        conn.close()


def collect_factory_signals(repo: Path, *, days: int = 7) -> dict[str, Any]:
    slices_path = _metrics_dir(repo) / SLICES_FILE
    slices = [
        row
        for row in _read_jsonl(slices_path)
        if (t := _parse_iso(str(row.get("completed_at") or "")))
        and t.timestamp() >= datetime.now(timezone.utc).timestamp() - days * 86400
    ]
    incidents = sum(1 for s in slices if s.get("incident_flag") in (True, "true", 1, "1"))
    rework = sum(1 for s in slices if int(s.get("rework_count") or 0) > 0)
    high_rt = sum(1 for s in slices if int(s.get("roundtrips") or 0) >= 3)

    ctx_rows = read_context_windows(repo)
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    ctx_recent = [
        row
        for row in ctx_rows
        if (t := _parse_iso(str(row.get("closed_at") or ""))) and t.timestamp() >= cutoff
    ]
    zero_slice_closeouts = sum(
        1 for c in ctx_recent if int(c.get("slices_closed_in_thread") or 0) == 0
    )

    validation = demo_sessions_in_days(repo, days)
    events = events_in_days(repo, days)

    return {
        "days": days,
        "slices_logged": len(slices),
        "incident_slices": incidents,
        "rework_slices": rework,
        "high_roundtrip_slices": high_rt,
        "context_closeouts": len(ctx_recent),
        "zero_slice_closeouts": zero_slice_closeouts,
        "validation_sessions": len(validation),
        "tracking_events": len(events),
    }


def collect_product_usage(repo: Path, *, days: int = 7) -> dict[str, Any]:
    from scripts.ppe_product_usage import summarize_usage
    return summarize_usage(repo, days=days)


def format_usage_line(usage: dict[str, Any]) -> str | None:
    total = int(usage.get("total_events") or 0)
    if total <= 0 and not usage.get("exists"):
        return None
    users = int(usage.get("unique_users") or 0)
    top = usage.get("top_event")
    top_s = f" top={top}" if top else ""
    return f"Product usage: events={total} users={users}{top_s}"


def collect_tracking_snapshot(repo: Path, *, days: int = 7) -> dict[str, Any]:
    return {
        "generated_at_utc": _utc_now(),
        "days": days,
        "steering": collect_steering_drift(repo),
        "assets": collect_asset_enablement(repo),
        "trader_outcomes": collect_trader_outcomes(repo),
        "factory": collect_factory_signals(repo, days=days),
        "product_usage": collect_product_usage(repo, days=days),
    }


def format_operator_tracking_lines(repo: Path, *, days: int = 7) -> list[str]:
    snap = collect_tracking_snapshot(repo, days=days)
    lines: list[str] = []

    factory = snap.get("factory") or {}
    lines.append(
        "Tracking: "
        f"ctx_closeouts={factory.get('context_closeouts', 0)} "
        f"validation_sessions={factory.get('validation_sessions', 0)} "
        f"incidents={factory.get('incident_slices', 0)}"
    )

    steering = snap.get("steering") or {}
    if not steering.get("aligned"):
        lines.append(f"Steering drift: gap_count={steering.get('gap_count', 0)}")

    assets = snap.get("assets") or {}
    if assets.get("available"):
        target = assets.get("target_enabled_count")
        enabled = assets.get("enabled_count", 0)
        if target is not None:
            lines.append(f"Assets: enabled={enabled}/{target}")
        else:
            lines.append(f"Assets: enabled={enabled} registered={assets.get('total_registered', 0)}")

    usage = snap.get("product_usage") or {}
    usage_line = format_usage_line(usage)
    if usage_line:
        lines.append(usage_line)

    trader = snap.get("trader_outcomes") or {}
    if trader.get("db_exists"):
        rate = trader.get("completion_rate")
        rate_s = f"{float(rate):.0%}" if rate is not None else "—"
        lines.append(
            "Trader loop: "
            f"frozen={trader.get('frozen_total', 0)} "
            f"pending={trader.get('pending_review', 0)} "
            f"reviewed={trader.get('completed_reviews', 0)} "
            f"completion={rate_s}"
        )

    return lines


def format_tracking_digest_lines(repo: Path, *, days: int = 7) -> list[str]:
    """Brief markdown bullets for weekly digest / Monday ntfy."""
    snap = collect_tracking_snapshot(repo, days=days)
    lines: list[str] = []

    factory = snap.get("factory") or {}
    closeouts = int(factory.get("context_closeouts") or 0)
    validation = int(factory.get("validation_sessions") or 0)
    if closeouts or validation:
        lines.append(
            f"- Factory window: {closeouts} context closeout(s), {validation} validation session(s)."
        )

    usage = snap.get("product_usage") or {}
    usage_line = format_usage_line(usage)
    if usage_line:
        lines.append(f"- {usage_line}.")
    elif not usage.get("exists"):
        lines.append(
            "- Product usage JSONL not found — run `ppe_pull_product_usage.cmd` on VPS or set "
            "`PPE_PRODUCT_USAGE_JSONL`."
        )

    steering = snap.get("steering") or {}
    if not steering.get("aligned"):
        lines.append(f"- Steering drift: {steering.get('gap_count', 0)} gap(s) vs active manifest.")

    trader = snap.get("trader_outcomes") or {}
    pending = int(trader.get("pending_review") or 0)
    if trader.get("db_exists") and pending > 0:
        lines.append(f"- Trader loop: {pending} snapshot(s) pending review.")

    try:
        from scripts.ppe_export_web_feedback import format_digest_line as feedback_digest_line

        fb = feedback_digest_line(repo, days=days)
        if fb:
            lines.append(fb)
    except Exception:
        pass

    try:
        from scripts.ppe_token_reconcile import digest_reconcile_line

        billing = digest_reconcile_line(repo, days=30)
        if billing:
            lines.append(billing)
    except Exception:
        pass

    return lines[:6]


def render_tracking_markdown(snap: dict[str, Any]) -> str:
    lines = [
        "# Tracking status (latest)",
        "",
        f"**Generated:** {snap.get('generated_at_utc')}",
        f"**Window:** last {snap.get('days', 7)} days",
        "",
        "## Factory signals",
        "",
    ]
    factory = snap.get("factory") or {}
    for key in (
        "slices_logged",
        "incident_slices",
        "rework_slices",
        "high_roundtrip_slices",
        "context_closeouts",
        "zero_slice_closeouts",
        "validation_sessions",
        "tracking_events",
    ):
        lines.append(f"- **{key}:** {factory.get(key, 0)}")
    lines.extend(["", "## Steering", ""])
    steering = snap.get("steering") or {}
    lines.append(f"- **aligned:** {steering.get('aligned')}")
    lines.append(f"- **gap_count:** {steering.get('gap_count', 0)}")
    for gap in steering.get("gaps") or []:
        lines.append(f"  - {gap}")
    lines.extend(["", "## Assets", ""])
    assets = snap.get("assets") or {}
    for key in ("enabled_count", "total_registered", "target_enabled_count", "gap_to_target"):
        if key in assets and assets[key] is not None:
            lines.append(f"- **{key}:** {assets[key]}")
    lines.extend(["", "## Product usage", ""])
    usage = snap.get("product_usage") or {}
    for key in ("exists", "total_events", "unique_users", "top_event", "path"):
        if key in usage:
            lines.append(f"- **{key}:** {usage[key]}")
    by_event = usage.get("by_event") or {}
    if by_event:
        lines.append(f"- **by_event:** {by_event}")
    lines.extend(["", "## Trader outcomes", ""])
    trader = snap.get("trader_outcomes") or {}
    for key in (
        "db_exists",
        "frozen_total",
        "pending_review",
        "completed_reviews",
        "completion_rate",
        "median_days_to_review",
    ):
        if key in trader:
            lines.append(f"- **{key}:** {trader[key]}")
    lines.append("")
    return "\n".join(lines)


def write_tracking_artifacts(repo: Path, snap: dict[str, Any]) -> tuple[Path, Path]:
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / TRACKING_STATUS_JSON
    md_path = repo / TRACKING_STATUS_MD
    json_path.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_tracking_markdown(snap), encoding="utf-8")
    return json_path, md_path


def scan_tracking_friction(repo: Path, week_monday) -> list:
    """Radar hook — friction candidates from tracking snapshot."""
    from scripts.ppe_workflow_radar import RadarCandidate

    snap = collect_tracking_snapshot(repo, days=7)
    candidates: list = []

    steering = snap.get("steering") or {}
    if not steering.get("aligned"):
        candidates.append(
            RadarCandidate(
                id="steering-drift",
                severity="watch",
                title="Product direction drift vs active manifest",
                evidence=list(steering.get("gaps") or [])[:5],
                suggested_action="Run sync_product_direction.cmd; align ACTIVE_PHASE_MANIFEST with direction JSON.",
            )
        )

    assets = snap.get("assets") or {}
    gap = assets.get("gap_to_target")
    if isinstance(gap, int) and gap > 5:
        candidates.append(
            RadarCandidate(
                id="asset-enablement-gap",
                severity="info",
                title="Asset enablement below tier target",
                evidence=[
                    f"enabled={assets.get('enabled_count')}",
                    f"target={assets.get('target_enabled_count')}",
                    f"gap={gap}",
                ],
                suggested_action="Run asset batch wave per POST_PPE_ASSET_BATCH_WAVE1_V1_SELECTION.md.",
                charter_hint="Asset-Batch-Wave-Slice-00N",
            )
        )

    trader = snap.get("trader_outcomes") or {}
    if trader.get("db_exists") and int(trader.get("frozen_total") or 0) >= 3:
        pending = int(trader.get("pending_review") or 0)
        frozen = int(trader.get("frozen_total") or 0)
        if pending / frozen > 0.5:
            candidates.append(
                RadarCandidate(
                    id="trader-review-backlog",
                    severity="info",
                    title="High pending-review ratio on frozen snapshots",
                    evidence=[
                        f"pending={pending}",
                        f"frozen={frozen}",
                        f"completion_rate={trader.get('completion_rate')}",
                    ],
                    suggested_action="Prioritize msos_trader_review_loop_v1 / MSOS post-mortem write path.",
                    charter_hint="Trader-Learning-Spine-Slice-00N",
                )
            )

    factory = snap.get("factory") or {}
    if int(factory.get("validation_sessions") or 0) == 0 and int(factory.get("slices_logged") or 0) >= 3:
        candidates.append(
            RadarCandidate(
                id="no-validation-sessions",
                severity="info",
                title="Factory throughput without validation session logs",
                evidence=[f"slices_logged={factory.get('slices_logged')}"],
                suggested_action="Log demo sessions via log_demo_session.cmd after tester walkthroughs.",
            )
        )

    return candidates
