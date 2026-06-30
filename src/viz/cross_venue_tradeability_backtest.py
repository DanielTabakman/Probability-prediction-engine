"""Historical tradeability backtest — tradeable-at-first gaps vs resolved accuracy."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from src.viz.cross_venue_backtest import (
    DEFAULT_MIN_SNAPSHOTS,
    DEFAULT_SNAPSHOT_ROOT,
    _first_scoring_row,
    discover_snapshot_csvs,
    merge_snapshot_history,
    score_question_series,
)
from src.viz.cross_venue_tradeability import score_tradeability_row

TRADEABILITY_BACKTEST_JSON_VERSION = 1
DEFAULT_REPORT_ROOT = Path("artifacts") / "cross_venue_tradeability_backtest"


def build_cross_venue_tradeability_backtest_report(
    csv_paths: list[Path],
    *,
    min_snapshots: int = DEFAULT_MIN_SNAPSHOTS,
    as_of_utc: str | None = None,
) -> dict[str, Any]:
    history = merge_snapshot_history(csv_paths)
    scored: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []

    for key, rows in sorted(history.items()):
        if len(rows) < min_snapshots:
            pending.append({"question_key": key, "snapshot_count": len(rows), "reason": "thin history"})
            continue
        first = _first_scoring_row(rows)
        if first is None:
            pending.append({"question_key": key, "reason": "missing probabilities"})
            continue
        trade = score_tradeability_row(first)
        if trade is None or not trade.get("tradeable_after_costs"):
            pending.append({"question_key": key, "reason": "not tradeable at first snapshot"})
            continue
        result = score_question_series(rows)
        if result is None:
            pending.append({"question_key": key, "reason": "unresolved"})
            continue
        scored.append({**trade, **result})

    n = len(scored)
    bl_wins = sum(1 for r in scored if r.get("bl_beat_pm"))
    rate = round(bl_wins / n, 4) if n else None
    strategy_ready = n >= 3 and rate is not None

    return {
        "version": TRADEABILITY_BACKTEST_JSON_VERSION,
        "as_of_utc": as_of_utc or datetime.now(tz=UTC).isoformat(),
        "snapshot_files": len(csv_paths),
        "min_snapshots": min_snapshots,
        "tradeable_resolved_count": n,
        "pending_count": len(pending),
        "bl_beat_pm_count": bl_wins,
        "bl_beat_pm_rate": rate,
        "strategy_ready": strategy_ready,
        "strategy_ready_reason": (
            f"{n} tradeable-at-first resolved questions; BL beat PM rate {rate}"
            if strategy_ready
            else "need >=3 tradeable resolved questions"
        ),
        "entries": scored,
        "pending": pending,
    }


def render_tradeability_backtest_markdown(report: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Cross-venue tradeability backtest",
            "",
            f"**Tradeable resolved:** {report.get('tradeable_resolved_count', 0)}",
            f"**BL beat PM rate:** {report.get('bl_beat_pm_rate')}",
            f"**Strategy-ready:** {report.get('strategy_ready')}",
            "",
        ]
    )


def write_tradeability_backtest_reports(
    report: dict[str, Any],
    *,
    report_root: Path = DEFAULT_REPORT_ROOT,
) -> tuple[Path, Path]:
    report_root.mkdir(parents=True, exist_ok=True)
    md_path = report_root / "latest_report.md"
    json_path = report_root / "latest_summary.json"
    md_path.write_text(render_tradeability_backtest_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return md_path, json_path
