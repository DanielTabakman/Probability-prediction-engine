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
TRACKING_ROLLUP_HTML = "artifacts/control_plane/TRACKING_ROLLUP.html"
LAST_VPS_DEPLOY_REL = Path("data") / "last_vps_deploy.utc"

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
    sessions = int(usage.get("session_starts") or 0)
    page_views = int(usage.get("page_views") or 0)
    streamlit = int(usage.get("streamlit_events") or 0)
    top = usage.get("top_event")
    top_s = f" top={top}" if top else ""
    st_s = f" streamlit={streamlit}" if streamlit else ""
    return (
        f"Product usage: events={total} sessions={sessions} page_views={page_views} "
        f"users={users}{st_s}{top_s}"
    )


def _days_since_vps_deploy(repo: Path) -> float | None:
    path = repo / LAST_VPS_DEPLOY_REL
    if not path.is_file():
        return None
    raw = path.read_text(encoding="utf-8").strip()
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400
    except ValueError:
        return None


def zero_activity_watch_line(repo: Path, usage: dict[str, Any], *, days: int = 7) -> str | None:
    deploy_days = _days_since_vps_deploy(repo)
    if deploy_days is None or deploy_days > 14:
        return None
    total = int(usage.get("total_events") or 0)
    if total > 0:
        return None
    return (
        f"- Product usage ZERO in {days}d but VPS deploy was {deploy_days:.0f}d ago — "
        "check MSOS beacons, docker volume, and `ppe_pull_product_usage.cmd`."
    )


def collect_aggregate_signals(repo: Path, *, days: int = 7) -> dict[str, Any]:
    from scripts.ppe_workflow_aggregate import summarize_aggregate

    return summarize_aggregate(repo, days=days)


def collect_operator_pass_summary(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_pass_progress import collect_operator_pass_stats

        return collect_operator_pass_stats(repo)
    except Exception:
        return {}


def read_operator_passes_for_rollup(repo: Path, *, limit: int = 10) -> list[dict[str, Any]]:
    try:
        from scripts.ppe_operator_pass_progress import read_operator_passes

        return list(reversed(read_operator_passes(repo)[-limit:]))
    except Exception:
        return []


def collect_tracking_snapshot(repo: Path, *, days: int = 7) -> dict[str, Any]:
    return {
        "generated_at_utc": _utc_now(),
        "days": days,
        "steering": collect_steering_drift(repo),
        "assets": collect_asset_enablement(repo),
        "trader_outcomes": collect_trader_outcomes(repo),
        "factory": collect_factory_signals(repo, days=days),
        "aggregate": collect_aggregate_signals(repo, days=days),
        "product_usage": collect_product_usage(repo, days=days),
        "operator_passes": collect_operator_pass_summary(repo),
    }


def format_operator_tracking_lines(repo: Path, *, days: int = 7) -> list[str]:
    snap = collect_tracking_snapshot(repo, days=days)
    lines: list[str] = []

    factory = snap.get("factory") or {}
    agg = snap.get("aggregate") or {}
    lines.append(
        "Tracking: "
        f"slices={agg.get('slices_logged', factory.get('slices_logged', 0))} "
        f"weighted={agg.get('weighted_slices', 0)} "
        f"closeouts={agg.get('context_closeouts', factory.get('context_closeouts', 0))} "
        f"incidents={factory.get('incident_slices', 0)}"
    )
    if agg.get("thread_pulses"):
        lines.append(
            f"Thread pulse: avg_load={agg.get('avg_cognitive_load')} "
            f"pulses={agg.get('thread_pulses', 0)}"
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
    agg = snap.get("aggregate") or {}
    closeouts = int(agg.get("context_closeouts") or factory.get("context_closeouts") or 0)
    validation = int(factory.get("validation_sessions") or 0)
    weighted = int(agg.get("weighted_slices") or 0)
    if closeouts or validation or weighted:
        lines.append(
            f"- Factory window: {weighted} weighted slice(s), {closeouts} closeout(s), "
            f"{validation} validation session(s)."
        )
    if agg.get("thread_pulses"):
        lines.append(
            f"- Thread pulses: {agg.get('thread_pulses')} "
            f"(avg load {agg.get('avg_cognitive_load')}/5)."
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

    zero_line = zero_activity_watch_line(repo, usage, days=days)
    if zero_line:
        lines.append(zero_line)

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

    return lines[:7]


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
    lines.extend(["", "## Aggregate (async/mobile)", ""])
    agg = snap.get("aggregate") or {}
    for key in (
        "slices_logged",
        "weighted_slices",
        "weighted_slices_per_closeout",
        "avg_roundtrips_per_slice",
        "thread_pulses",
        "avg_cognitive_load",
        "context_closeouts",
        "incident_slices",
    ):
        if key in agg:
            lines.append(f"- **{key}:** {agg[key]}")
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
    op_pass = snap.get("operator_passes") or {}
    if op_pass:
        lines.extend(["", "## Operator pass progress", ""])
        for key in (
            "passes_in_window",
            "no_progress_in_window",
            "low_progress_in_window",
            "consecutive_no_progress",
            "wait_health",
        ):
            if key in op_pass:
                lines.append(f"- **{key}:** {op_pass[key]}")
    lines.append("")
    return "\n".join(lines)


def render_tracking_rollup_html(snap: dict[str, Any], repo: Path | None = None) -> str:
    payload = json.dumps(snap, indent=2)
    usage = snap.get("product_usage") or {}
    factory = snap.get("factory") or {}
    agg = snap.get("aggregate") or {}
    rows = [
        ("Generated (UTC)", str(snap.get("generated_at_utc") or "—")),
        ("Window (days)", str(snap.get("days") or "—")),
        ("Slices logged", str(agg.get("slices_logged", factory.get("slices_logged", 0)))),
        ("Weighted slices", str(agg.get("weighted_slices", 0))),
        ("Weighted slices / closeout", str(agg.get("weighted_slices_per_closeout", 0))),
        ("Avg roundtrips / slice", str(agg.get("avg_roundtrips_per_slice", 0))),
        ("Thread pulses", str(agg.get("thread_pulses", 0))),
        ("Avg cognitive load", str(agg.get("avg_cognitive_load", 0))),
        ("Context closeouts", str(agg.get("context_closeouts", factory.get("context_closeouts", 0)))),
        ("Validation sessions", str(factory.get("validation_sessions", 0))),
        ("Product events", str(usage.get("total_events", 0))),
        ("Sessions (session_start)", str(usage.get("session_starts", 0))),
        ("Page views", str(usage.get("page_views", 0))),
        ("Streamlit events", str(usage.get("streamlit_events", 0))),
        ("Unique users", str(usage.get("unique_users", 0))),
    ]
    body_rows = "\n".join(f"<tr><th>{k}</th><td>{v}</td></tr>" for k, v in rows)
    by_event = usage.get("by_event") or {}
    event_rows = "\n".join(
        f"<tr><td>{name}</td><td>{count}</td></tr>" for name, count in sorted(by_event.items())
    )
    pulses = agg.get("recent_pulses") or []
    pulse_rows = "\n".join(
        f"<tr><td>{p.get('recorded_at', '')}</td><td>{p.get('cognitive_load_1_5', '')}</td>"
        f"<td>{p.get('note', '')}</td></tr>"
        for p in pulses
    )
    op_pass = snap.get("operator_passes") or {}
    latest_op = op_pass.get("latest") if isinstance(op_pass.get("latest"), dict) else {}
    op_rows = "\n".join(
        f"<tr><th>{k}</th><td>{v}</td></tr>"
        for k, v in [
            ("Passes in window", op_pass.get("passes_in_window", 0)),
            ("No progress in window", op_pass.get("no_progress_in_window", 0)),
            ("Low progress in window", op_pass.get("low_progress_in_window", 0)),
            ("Stuck/deadlock in window", op_pass.get("stuck_or_deadlock_in_window", 0)),
            ("Consecutive no progress", op_pass.get("consecutive_no_progress", 0)),
            ("Latest wait health", op_pass.get("wait_health") or "—"),
            ("Latest summary", latest_op.get("progress_summary") or "—"),
        ]
    )
    recent_passes = op_pass.get("recent") or []
    pass_history_rows = "\n".join(
        f"<tr><td>{r.get('pass_at', '')}</td><td>{r.get('progress_class', '')}</td>"
        f"<td>{'yes' if r.get('had_progress') else 'no'}</td>"
        f"<td>{r.get('wait_health', '')}</td>"
        f"<td>{(r.get('progress_summary') or '')[:80]}</td></tr>"
        for r in recent_passes
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>PPE tracking rollup</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 960px; }}
    table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #f4f4f4; width: 40%; }}
    pre {{ background: #f8f8f8; padding: 1rem; overflow: auto; font-size: 0.85rem; }}
    h1 {{ font-size: 1.4rem; }}
    h2 {{ font-size: 1.1rem; margin-top: 1.5rem; }}
  </style>
</head>
<body>
  <h1>PPE tracking rollup (in-house)</h1>
  <p>Aggregate-first — no session timers. Slices auto-log; optional thread pulse on closeout.</p>
  <h2>Summary</h2>
  <table>{body_rows}</table>
  <h2>Recent thread pulses</h2>
  <table>
    <tr><th>When</th><th>Load</th><th>Note</th></tr>
    {pulse_rows or '<tr><td colspan="3">None yet</td></tr>'}
  </table>
  <h2>Operator pass progress (last 10)</h2>
  <table>{op_rows}</table>
  <table>
    <tr><th>When</th><th>Class</th><th>Progress</th><th>Wait</th><th>Summary</th></tr>
    {pass_history_rows or '<tr><td colspan="5">No passes recorded — run operator status</td></tr>'}
  </table>
  <h2>Product usage by event</h2>
  <table>
    <tr><th>Event</th><th>Count ({usage.get('days', 7)}d)</th></tr>
    {event_rows or '<tr><td colspan="2">No events</td></tr>'}
  </table>
  <h2>Raw snapshot JSON</h2>
  <pre>{payload}</pre>
</body>
</html>
"""


def write_tracking_artifacts(repo: Path, snap: dict[str, Any]) -> tuple[Path, Path, Path]:
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / TRACKING_STATUS_JSON
    md_path = repo / TRACKING_STATUS_MD
    html_path = repo / TRACKING_ROLLUP_HTML
    json_path.write_text(json.dumps(snap, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_tracking_markdown(snap), encoding="utf-8")
    html_path.write_text(render_tracking_rollup_html(snap, repo), encoding="utf-8")
    try:
        from scripts.workflow_metrics_cli import cmd_export_csv

        cmd_export_csv(repo)
    except OSError:
        pass
    return json_path, md_path, html_path


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

    usage = snap.get("product_usage") or {}
    if int(usage.get("total_events") or 0) == 0:
        deploy_days = _days_since_vps_deploy(repo)
        if deploy_days is not None and deploy_days <= 14:
            candidates.append(
                RadarCandidate(
                    id="product-usage-zero-post-deploy",
                    severity="watch",
                    title="No product usage events after recent VPS deploy",
                    evidence=[f"deploy_days_ago={deploy_days:.1f}", f"path={usage.get('path')}"],
                    suggested_action="Verify MSOS usage API, docker volume, and ppe_pull_product_usage.cmd.",
                )
            )

    return candidates
