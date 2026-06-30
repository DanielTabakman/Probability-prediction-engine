"""Build unified research summary from archive health and test report JSON."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SUMMARY_JSON_REL = "artifacts/control_plane/RESEARCH_SUMMARY.json"
SUMMARY_JSON_VERSION = 1


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _cross_venue_block(repo: Path) -> dict[str, Any]:
    scan = _load_json(repo / "artifacts/cross_venue_reports/latest_summary.json")
    backtest = _load_json(repo / "artifacts/cross_venue_backtest/latest_summary.json")
    trade = _load_json(repo / "artifacts/cross_venue_tradeability/latest_summary.json")
    trade_bt = _load_json(repo / "artifacts/cross_venue_tradeability_backtest/latest_summary.json")

    top_gap_pct: float | None = None
    if scan:
        entries = scan.get("entries") or []
        if entries and isinstance(entries[0], dict):
            gap = entries[0].get("abs_gap_pct")
            if gap is not None:
                try:
                    top_gap_pct = float(gap)
                except (TypeError, ValueError):
                    top_gap_pct = None

    return {
        "scan_row_count": int(scan.get("row_count") or 0) if scan else 0,
        "top_gap_pct": top_gap_pct,
        "backtest": {
            "resolved_count": int(backtest.get("resolved_count") or 0) if backtest else 0,
            "pending_count": int(backtest.get("pending_count") or 0) if backtest else 0,
            "strategy_ready": bool(backtest.get("strategy_ready")) if backtest else False,
            "mean_brier_delta_bl_minus_pm": backtest.get("mean_brier_delta_bl_minus_pm") if backtest else None,
        },
        "tradeability": {
            "tradeable_count": int(trade.get("tradeable_count") or 0) if trade else 0,
            "strategy_ready": bool(trade.get("strategy_ready")) if trade else False,
        },
        "tradeability_backtest": {
            "tradeable_resolved_count": int(trade_bt.get("tradeable_resolved_count") or 0) if trade_bt else 0,
            "bl_beat_pm_rate": trade_bt.get("bl_beat_pm_rate") if trade_bt else None,
            "strategy_ready": bool(trade_bt.get("strategy_ready")) if trade_bt else False,
        },
    }


def build_research_summary(repo: Path) -> dict[str, Any]:
    from scripts.research_archive_health import build_archive_health

    health = build_archive_health(repo)
    collectors = health.get("collectors") or []
    stale = [
        {
            "id": item.get("id"),
            "label": item.get("label"),
            "last_snapshot_utc": item.get("last_snapshot_utc"),
            "hours_since_snapshot": item.get("hours_since_snapshot"),
        }
        for item in collectors
        if isinstance(item, dict) and item.get("stale")
    ]
    cv = _cross_venue_block(repo)
    return {
        "version": SUMMARY_JSON_VERSION,
        "as_of_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "archives": collectors,
        "stale_collectors": stale,
        "cross_venue": cv,
    }


def write_research_summary(repo: Path) -> Path:
    payload = build_research_summary(repo)
    out = repo / SUMMARY_JSON_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out
