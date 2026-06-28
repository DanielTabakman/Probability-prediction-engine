"""Lightweight workflow metrics (JSONL + optional CSV export)."""

from __future__ import annotations

import argparse
import csv
import json
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

METRICS_DIR = "artifacts/workflow_metrics"
SESSIONS_FILE = "sessions.jsonl"
SLICES_FILE = "slices.jsonl"
CONTEXT_WINDOWS_FILE = "context_windows.jsonl"

SIZE_WEIGHTS = {"S": 1, "M": 2, "L": 3, "XL": 5}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _metrics_dir(repo: Path) -> Path:
    d = repo / METRICS_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
        except json.JSONDecodeError:
            continue
    return rows


def _parse_iso(ts: str) -> datetime | None:
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def read_context_windows(repo: Path) -> list[dict[str, Any]]:
    return _read_jsonl(_metrics_dir(repo) / CONTEXT_WINDOWS_FILE)


def context_windows_in_week(repo: Path, week_monday: date) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in read_context_windows(repo):
        closed = str(row.get("closed_at") or row.get("generated_at_utc") or "").strip()
        t = _parse_iso(closed)
        if not t:
            continue
        row_monday = t.date() - timedelta(days=t.date().weekday())
        if row_monday == week_monday:
            out.append(row)
    return out


def cmd_session_start(repo: Path, *, notes: str = "") -> int:
    session_id = str(uuid.uuid4())
    row = {
        "session_id": session_id,
        "event": "session_start",
        "started_at": _utc_now(),
        "notes": notes,
    }
    _append_jsonl(_metrics_dir(repo) / SESSIONS_FILE, row)
    print(f"workflow_metrics: session_start id={session_id}")
    return 0


def _open_session(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    open_id: str | None = None
    for row in rows:
        if row.get("event") == "session_start":
            open_id = str(row.get("session_id") or "")
        if row.get("event") == "session_stop" and open_id and row.get("session_id") == open_id:
            open_id = None
    if not open_id:
        return None
    for row in reversed(rows):
        if row.get("event") == "session_start" and row.get("session_id") == open_id:
            return row
    return None


def cmd_session_stop(
    repo: Path,
    *,
    cognitive_load: int,
    roundtrips: int | None = None,
    notes: str = "",
) -> int:
    path = _metrics_dir(repo) / SESSIONS_FILE
    rows = _read_jsonl(path)
    start = _open_session(rows)
    if start is None:
        print("workflow_metrics: no open session (run session start first)")
        return 1

    started_at = str(start.get("started_at") or "")
    ended_at = _utc_now()
    active_minutes: float | None = None
    t0 = _parse_iso(started_at)
    t1 = _parse_iso(ended_at)
    if t0 and t1:
        active_minutes = round((t1 - t0).total_seconds() / 60.0, 1)

    slice_rows = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
    session_id = str(start.get("session_id") or "")
    closed_in_session = [s for s in slice_rows if s.get("primary_session_id") == session_id]
    weighted = sum(int(s.get("size_weight_actual") or 0) for s in closed_in_session)

    row = {
        "session_id": session_id,
        "event": "session_stop",
        "started_at": started_at,
        "ended_at": ended_at,
        "active_minutes": active_minutes,
        "cognitive_load_1_5": cognitive_load,
        "total_roundtrips": roundtrips,
        "slices_completed_count": len(closed_in_session),
        "weighted_slices_completed": weighted,
        "session_notes": notes,
    }
    _append_jsonl(path, row)
    print(
        f"workflow_metrics: session_stop id={session_id} "
        f"active_min={active_minutes} weighted_slices={weighted}"
    )
    return 0


def append_slice_close_row(
    repo: Path,
    *,
    slice_id: str,
    size: str,
    roundtrips: int,
    rework: int = 0,
    session_id: str | None = None,
    notes: str = "",
    worker_lane: str | None = None,
    api_calls: int | None = None,
    source: str | None = None,
) -> None:
    size_u = size.upper()
    if size_u not in SIZE_WEIGHTS:
        raise ValueError(f"invalid size {size!r} (use S|M|L|XL)")

    if not session_id:
        start = _open_session(_read_jsonl(_metrics_dir(repo) / SESSIONS_FILE))
        session_id = str(start.get("session_id") or "") if start else ""

    row: dict[str, Any] = {
        "slice_id": slice_id,
        "status": "closed",
        "planned_size": size_u,
        "actual_size": size_u,
        "size_weight_actual": SIZE_WEIGHTS[size_u],
        "completed_at": _utc_now(),
        "roundtrips": roundtrips,
        "rework_count": rework,
        "primary_session_id": session_id or None,
        "notes": notes,
    }
    lane = (worker_lane or "").strip()
    if lane:
        row["worker_lane"] = lane
    if api_calls is not None:
        row["api_calls"] = api_calls
    src = (source or "").strip()
    if src:
        row["source"] = src
    _append_jsonl(_metrics_dir(repo) / SLICES_FILE, row)


def cmd_slice_close(
    repo: Path,
    *,
    slice_id: str,
    size: str,
    roundtrips: int,
    rework: int = 0,
    session_id: str | None = None,
    notes: str = "",
    worker_lane: str | None = None,
    api_calls: int | None = None,
    source: str | None = None,
) -> int:
    try:
        append_slice_close_row(
            repo,
            slice_id=slice_id,
            size=size,
            roundtrips=roundtrips,
            rework=rework,
            session_id=session_id,
            notes=notes,
            worker_lane=worker_lane,
            api_calls=api_calls,
            source=source or "manual",
        )
    except ValueError as exc:
        print(f"workflow_metrics: {exc}")
        return 1
    size_u = size.upper()
    lane_msg = f" lane={worker_lane}" if worker_lane else ""
    print(f"workflow_metrics: slice_close {slice_id} size={size_u} roundtrips={roundtrips}{lane_msg}")
    return 0


def _slices_in_days(repo: Path, days: int) -> list[dict[str, Any]]:
    slices = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
    if days <= 0:
        return slices
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    return [
        row
        for row in slices
        if (t := _parse_iso(str(row.get("completed_at") or ""))) and t.timestamp() >= cutoff
    ]


def cmd_summary(repo: Path, *, days: int = 7, by_lane: bool = False) -> int:
    sessions = _read_jsonl(_metrics_dir(repo) / SESSIONS_FILE)
    slices_window = _slices_in_days(repo, days)

    stops = [s for s in sessions if s.get("event") == "session_stop"]
    if days > 0:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        stops = [
            s
            for s in stops
            if (t := _parse_iso(str(s.get("ended_at") or ""))) and t.timestamp() >= cutoff
        ]

    total_active = sum(float(s.get("active_minutes") or 0) for s in stops)
    total_weighted = sum(int(s.get("weighted_slices_completed") or 0) for s in stops)
    total_roundtrips = sum(int(s.get("total_roundtrips") or 0) for s in stops if s.get("total_roundtrips"))
    avg_load_vals = [int(s.get("cognitive_load_1_5") or 0) for s in stops if s.get("cognitive_load_1_5")]
    avg_load = sum(avg_load_vals) / len(avg_load_vals) if avg_load_vals else 0.0

    slice_roundtrips = [int(s.get("roundtrips") or 0) for s in slices_window if s.get("roundtrips") is not None]
    avg_slice_roundtrips = sum(slice_roundtrips) / len(slice_roundtrips) if slice_roundtrips else 0.0
    wsph = (total_weighted / (total_active / 60.0)) if total_active > 0 else 0.0

    print(f"workflow_metrics summary (last {days} days)")
    print(f"  sessions_closed: {len(stops)}")
    print(f"  active_minutes: {total_active:.1f}")
    print(f"  weighted_slices_per_active_hour: {wsph:.2f}")
    print(f"  avg_cognitive_load: {avg_load:.2f}")
    print(f"  session_roundtrips_total: {total_roundtrips}")
    print(f"  slices_logged: {len(slices_window)}")
    print(f"  avg_slice_roundtrips: {avg_slice_roundtrips:.2f}")

    if by_lane:
        from scripts.ppe_workflow_cost import format_lane_summary_line, summarize_by_lane

        lane_summary = summarize_by_lane(repo, days=days)
        print(f"  {format_lane_summary_line(lane_summary)}")
        print("  by_lane:")
        for lane, count in (lane_summary.get("by_lane") or {}).items():
            print(f"    {lane}: {count}")
        if lane_summary.get("api_calls_total"):
            print(f"  api_calls_total: {lane_summary['api_calls_total']}")
        if lane_summary.get("est_usd_total"):
            print(f"  est_usd_total (advisory): {lane_summary['est_usd_total']}")
    return 0


def cmd_export_csv(repo: Path) -> int:
    out_dir = _metrics_dir(repo)
    sessions = _read_jsonl(out_dir / SESSIONS_FILE)
    slices = _read_jsonl(out_dir / SLICES_FILE)

    sessions_csv = out_dir / "sessions_export.csv"
    slices_csv = out_dir / "weekly_summary.csv"

    session_fields = [
        "session_id",
        "started_at",
        "ended_at",
        "active_minutes",
        "cognitive_load_1_5",
        "total_roundtrips",
        "slices_completed_count",
        "weighted_slices_completed",
        "session_notes",
    ]
    with sessions_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=session_fields, extrasaction="ignore")
        w.writeheader()
        for row in sessions:
            if row.get("event") != "session_stop":
                continue
            w.writerow({k: row.get(k, "") for k in session_fields})

    slice_fields = [
        "slice_id",
        "completed_at",
        "actual_size",
        "size_weight_actual",
        "roundtrips",
        "rework_count",
        "worker_lane",
        "api_calls",
        "source",
        "primary_session_id",
        "notes",
    ]
    with slices_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=slice_fields, extrasaction="ignore")
        w.writeheader()
        for row in slices:
            w.writerow({k: row.get(k, "") for k in slice_fields})

    print(f"workflow_metrics: wrote {sessions_csv}")
    print(f"workflow_metrics: wrote {slices_csv}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Workflow metrics CLI (JSONL under artifacts/workflow_metrics).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_start = sub.add_parser("session", help="Session subcommands")
    sess_sub = p_start.add_subparsers(dest="session_cmd", required=True)
    s_start = sess_sub.add_parser("start")
    s_start.add_argument("--notes", default="")
    s_stop = sess_sub.add_parser("stop")
    s_stop.add_argument("--cognitive-load", type=int, required=True)
    s_stop.add_argument("--roundtrips", type=int, default=None)
    s_stop.add_argument("--notes", default="")

    p_slice = sub.add_parser("slice", help="Slice subcommands")
    slice_sub = p_slice.add_subparsers(dest="slice_cmd", required=True)
    s_close = slice_sub.add_parser("close")
    s_close.add_argument("--slice-id", required=True)
    s_close.add_argument("--size", required=True, choices=["S", "M", "L", "XL", "s", "m", "l", "xl"])
    s_close.add_argument("--roundtrips", type=int, required=True)
    s_close.add_argument("--rework", type=int, default=0)
    s_close.add_argument("--session-id", default=None)
    s_close.add_argument("--notes", default="")
    s_close.add_argument(
        "--worker-lane",
        default=None,
        help="Cost lane: deterministic-local | cursor-cli | codex-cli | manual | acp | local-agent",
    )
    s_close.add_argument("--api-calls", type=int, default=None)
    s_close.add_argument("--source", default="manual")

    p_sum = sub.add_parser("summary")
    p_sum.add_argument("--days", type=int, default=7)
    p_sum.add_argument("--by-lane", action="store_true", help="Include worker-lane rollup")

    p_backfill = sub.add_parser("backfill", help="Backfill recent slice closes from progress + git log")
    p_backfill.add_argument("--limit", type=int, default=10)
    p_backfill.add_argument("--dry-run", action="store_true")

    sub.add_parser("export-csv")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "session" and args.session_cmd == "start":
        return cmd_session_start(repo, notes=args.notes)
    if args.command == "session" and args.session_cmd == "stop":
        return cmd_session_stop(
            repo,
            cognitive_load=args.cognitive_load,
            roundtrips=args.roundtrips,
            notes=args.notes,
        )
    if args.command == "slice" and args.slice_cmd == "close":
        return cmd_slice_close(
            repo,
            slice_id=args.slice_id,
            size=args.size,
            roundtrips=args.roundtrips,
            rework=args.rework,
            session_id=args.session_id,
            notes=args.notes,
            worker_lane=args.worker_lane,
            api_calls=args.api_calls,
            source=args.source,
        )
    if args.command == "summary":
        return cmd_summary(repo, days=args.days, by_lane=args.by_lane)
    if args.command == "backfill":
        from scripts.ppe_workflow_cost import backfill_recent_slices

        result = backfill_recent_slices(repo, limit=args.limit, dry_run=args.dry_run)
        mode = "dry-run" if result.get("dry_run") else "applied"
        print(f"workflow_metrics backfill ({mode}): recorded={len(result.get('recorded') or [])} skipped={len(result.get('skipped') or [])}")
        for sid in result.get("recorded") or []:
            print(f"  + {sid}")
        return 0
    if args.command == "export-csv":
        return cmd_export_csv(repo)

    ap.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
