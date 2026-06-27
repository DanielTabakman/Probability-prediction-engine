"""Cross-venue backtest — score PM vs options-implied gaps from snapshot history."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.viz.cross_venue_export import CSV_COLUMNS

BACKTEST_JSON_VERSION = 1
DEFAULT_GAP_COLUMN = "gap_bl_minus_pm_pct"
DEFAULT_MIN_SNAPSHOTS = 14

GAP_BUCKETS: tuple[tuple[float, float | None, str], ...] = (
    (0.0, 2.0, "0-2"),
    (2.0, 5.0, "2-5"),
    (5.0, 10.0, "5-10"),
    (10.0, None, "10+"),
)


def _parse_pct(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_usd(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").replace(tzinfo=UTC)
    except ValueError:
        return None


def question_key(row: dict[str, str]) -> str:
    """Stable key for a Polymarket question row across snapshots."""
    return "|".join(
        (
            str(row.get("question") or "").strip(),
            str(row.get("strike_usd") or "").strip(),
            str(row.get("resolution_date") or "").strip(),
        )
    )


def load_cross_venue_snapshot_csv(path: Path) -> list[dict[str, str]]:
    """Load one snapshot CSV written by collect_cross_venue_snapshot."""
    text = path.read_text(encoding="utf-8")
    reader = csv.DictReader(text.splitlines())
    rows: list[dict[str, str]] = []
    for row in reader:
        if not isinstance(row, dict):
            continue
        normalized = {col: str(row.get(col) or "") for col in CSV_COLUMNS}
        if normalized.get("question"):
            rows.append(normalized)
    return rows


def discover_snapshot_csvs(root: Path) -> list[Path]:
    """Return snapshot CSV paths sorted oldest-first by path name."""
    if not root.is_dir():
        return []
    paths = sorted(root.rglob("ppe_cross_venue_prob_panel_*.csv"))
    return paths


def merge_snapshot_history(csv_paths: list[Path]) -> dict[str, list[dict[str, str]]]:
    """Group rows by question key; each series sorted by as_of_utc."""
    series: dict[str, list[dict[str, str]]] = {}
    for path in csv_paths:
        for row in load_cross_venue_snapshot_csv(path):
            key = question_key(row)
            if not key.strip("|"):
                continue
            series.setdefault(key, []).append(row)
    for key in series:
        series[key].sort(key=lambda r: str(r.get("as_of_utc") or ""))
    return series


def gap_bucket_label(abs_gap_pct: float) -> str:
    for low, high, label in GAP_BUCKETS:
        if high is None:
            if abs_gap_pct >= low:
                return label
        elif low <= abs_gap_pct < high:
            return label
    return GAP_BUCKETS[-1][2]


def brier_score_pct(probability_pct: float | None, outcome: int) -> float | None:
    if probability_pct is None:
        return None
    p = max(0.0, min(1.0, float(probability_pct) / 100.0))
    o = float(outcome)
    return (p - o) ** 2


def infer_resolved_outcome(row: dict[str, str]) -> int | None:
    """Return 1/0 when resolution is known from PM convergence or spot vs strike."""
    pm = _parse_pct(row.get("polymarket_yes_pct"))
    if pm is not None:
        if pm >= 99.0:
            return 1
        if pm <= 1.0:
            return 0

    strike = _parse_usd(row.get("strike_usd"))
    spot = _parse_usd(row.get("spot_usd"))
    as_of = _parse_date(row.get("as_of_utc"))
    resolution = _parse_date(row.get("resolution_date"))
    if strike is None or spot is None or as_of is None or resolution is None:
        return None
    if as_of.date() < resolution.date():
        return None
    return 1 if spot > strike else 0


def _first_scoring_row(rows: list[dict[str, str]]) -> dict[str, str] | None:
    for row in rows:
        if row.get("match_status") != "ok":
            continue
        if _parse_pct(row.get("polymarket_yes_pct")) is None:
            continue
        if _parse_pct(row.get("options_bl_p_above_pct")) is None:
            continue
        return row
    return None


def _last_resolved_row(rows: list[dict[str, str]]) -> tuple[dict[str, str], int] | None:
    for row in reversed(rows):
        outcome = infer_resolved_outcome(row)
        if outcome is not None:
            return row, outcome
    return None


def score_question_series(
    rows: list[dict[str, str]],
    *,
    gap_column: str = DEFAULT_GAP_COLUMN,
) -> dict[str, Any] | None:
    """Score one question time series when resolved; None if still open."""
    if not rows:
        return None
    resolved = _last_resolved_row(rows)
    if resolved is None:
        return None
    _, outcome = resolved
    first = _first_scoring_row(rows)
    if first is None:
        return None

    pm = _parse_pct(first.get("polymarket_yes_pct"))
    bl = _parse_pct(first.get("options_bl_p_above_pct"))
    gap = _parse_pct(first.get(gap_column))
    brier_pm = brier_score_pct(pm, outcome)
    brier_bl = brier_score_pct(bl, outcome)
    if brier_pm is None or brier_bl is None:
        return None

    abs_gap = abs(gap) if gap is not None else 0.0
    return {
        "question": first.get("question", ""),
        "strike_usd": first.get("strike_usd", ""),
        "resolution_date": first.get("resolution_date", ""),
        "snapshot_count": len(rows),
        "first_as_of_utc": first.get("as_of_utc", ""),
        "resolved_outcome": outcome,
        "polymarket_yes_pct": first.get("polymarket_yes_pct", ""),
        "options_bl_p_above_pct": first.get("options_bl_p_above_pct", ""),
        gap_column: first.get(gap_column, ""),
        "abs_gap_pct": abs_gap,
        "gap_bucket": gap_bucket_label(abs_gap),
        "brier_pm": round(brier_pm, 6),
        "brier_bl": round(brier_bl, 6),
        "brier_delta_bl_minus_pm": round(brier_bl - brier_pm, 6),
        "bl_beat_pm": brier_bl < brier_pm,
    }


def build_gap_bucket_stats(scored: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, list[dict[str, Any]]] = {}
    for row in scored:
        buckets.setdefault(str(row.get("gap_bucket") or ""), []).append(row)

    order = [label for _, _, label in GAP_BUCKETS]
    stats: list[dict[str, Any]] = []
    for label in order:
        rows = buckets.get(label) or []
        if not rows:
            continue
        n = len(rows)
        stats.append(
            {
                "gap_bucket": label,
                "count": n,
                "mean_abs_gap_pct": round(sum(float(r["abs_gap_pct"]) for r in rows) / n, 4),
                "mean_brier_pm": round(sum(float(r["brier_pm"]) for r in rows) / n, 6),
                "mean_brier_bl": round(sum(float(r["brier_bl"]) for r in rows) / n, 6),
                "mean_brier_delta_bl_minus_pm": round(
                    sum(float(r["brier_delta_bl_minus_pm"]) for r in rows) / n,
                    6,
                ),
                "bl_beat_pm_rate": round(
                    sum(1 for r in rows if r.get("bl_beat_pm")) / n,
                    4,
                ),
            }
        )
    return stats


def build_cross_venue_backtest_report(
    csv_paths: list[Path],
    *,
    gap_column: str = DEFAULT_GAP_COLUMN,
    min_snapshots: int = DEFAULT_MIN_SNAPSHOTS,
    as_of_utc: str | None = None,
) -> dict[str, Any]:
    """Score resolved questions from snapshot CSV history."""
    history = merge_snapshot_history(csv_paths)
    scored: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []

    for key, rows in sorted(history.items()):
        if len(rows) < min_snapshots:
            pending.append(
                {
                    "question_key": key,
                    "snapshot_count": len(rows),
                    "reason": f"needs >= {min_snapshots} snapshots",
                }
            )
            continue
        result = score_question_series(rows, gap_column=gap_column)
        if result is None:
            pending.append(
                {
                    "question_key": key,
                    "snapshot_count": len(rows),
                    "reason": "unresolved or missing probabilities",
                }
            )
            continue
        scored.append(result)

    mean_brier_pm = (
        round(sum(float(r["brier_pm"]) for r in scored) / len(scored), 6) if scored else None
    )
    mean_brier_bl = (
        round(sum(float(r["brier_bl"]) for r in scored) / len(scored), 6) if scored else None
    )

    return {
        "version": BACKTEST_JSON_VERSION,
        "as_of_utc": as_of_utc or datetime.now(tz=UTC).isoformat(),
        "snapshot_files": len(csv_paths),
        "min_snapshots": min_snapshots,
        "gap_column": gap_column,
        "resolved_count": len(scored),
        "pending_count": len(pending),
        "mean_brier_pm": mean_brier_pm,
        "mean_brier_bl": mean_brier_bl,
        "mean_brier_delta_bl_minus_pm": (
            round(mean_brier_bl - mean_brier_pm, 6)
            if mean_brier_pm is not None and mean_brier_bl is not None
            else None
        ),
        "gap_buckets": build_gap_bucket_stats(scored),
        "entries": scored,
        "pending": pending,
    }


def render_cross_venue_backtest_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Cross-venue backtest report",
        "",
        f"**As-of:** {report.get('as_of_utc') or '—'}",
        f"**Snapshot files:** {report.get('snapshot_files', 0)}",
        f"**Resolved questions:** {report.get('resolved_count', 0)}",
        f"**Pending:** {report.get('pending_count', 0)}",
        "",
    ]
    if report.get("mean_brier_pm") is not None:
        lines.extend(
            [
                "## Aggregate Brier scores (first snapshot vs outcome)",
                "",
                f"- Polymarket mean Brier: **{report.get('mean_brier_pm')}**",
                f"- Options BL mean Brier: **{report.get('mean_brier_bl')}**",
                f"- BL − PM: **{report.get('mean_brier_delta_bl_minus_pm')}**",
                "",
            ]
        )

    buckets = report.get("gap_buckets") or []
    if buckets:
        lines.extend(
            [
                "## Gap buckets (|BL−PM| at first snapshot)",
                "",
                "| Bucket | N | Mean |Brier PM| | Mean |Brier BL| | BL beats PM |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for bucket in buckets:
            lines.append(
                "| {label} | {count} | {pm:.4f} | {bl:.4f} | {rate:.0%} |".format(
                    label=bucket.get("gap_bucket", ""),
                    count=bucket.get("count", 0),
                    pm=bucket.get("mean_brier_pm", 0.0),
                    bl=bucket.get("mean_brier_bl", 0.0),
                    rate=bucket.get("bl_beat_pm_rate", 0.0),
                )
            )
        lines.append("")

    entries = report.get("entries") or []
    if entries:
        lines.extend(
            [
                "## Resolved entries",
                "",
                "| Question | Outcome | Gap bucket | Brier PM | Brier BL |",
                "| --- | ---: | --- | ---: | ---: |",
            ]
        )
        for entry in entries:
            question = str(entry.get("question") or "").replace("|", "\\|")[:60]
            lines.append(
                "| {q} | {o} | {b} | {pm:.4f} | {bl:.4f} |".format(
                    q=question,
                    o=entry.get("resolved_outcome", ""),
                    b=entry.get("gap_bucket", ""),
                    pm=entry.get("brier_pm", 0.0),
                    bl=entry.get("brier_bl", 0.0),
                )
            )
        lines.append("")

    return "\n".join(lines)


def serialize_cross_venue_backtest_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"
