"""Tests for cross-venue tradeability scoring."""

from __future__ import annotations

from scripts.hedge_backed_event_stage0_1_terminal_witness import classify_market, parse_price_usd
from scripts.run_cross_venue_tradeability import run_cross_venue_tradeability
from src.viz.cross_venue_export import serialize_cross_venue_export_csv
from src.viz.cross_venue_tradeability import build_cross_venue_tradeability_report, score_tradeability_row


def _row(*, gap: str = "15.00", cost: str = "8.00") -> dict[str, str]:
    return {
        "as_of_utc": "2026-06-01T12:00:00+00:00",
        "question": "Will Bitcoin hit $100k?",
        "strike_usd": "100000.00",
        "resolution_date": "2026-06-01",
        "matched_expiry_date": "2026-05-15",
        "horizon_days": "30",
        "expiry_alignment": "before_resolution",
        "polymarket_yes_pct": "40.00",
        "options_ln_p_above_pct": "50.00",
        "options_bl_p_above_pct": "55.00",
        "gap_bl_minus_pm_pct": gap,
        "gap_ln_minus_pm_pct": "10.00",
        "spread_cost_usd": "1000.00",
        "spread_proxy_prob_pct": cost,
        "spot_usd": "105000.00",
        "forward_usd": "100500.00",
        "atm_iv_annual": "0.600000",
        "call_marks_count": "10",
        "match_status": "ok",
    }


def test_score_tradeability_row_net_edge() -> None:
    row = score_tradeability_row(_row(gap="15.00", cost="8.00"))
    assert row is not None
    assert row["tradeable_after_costs"] is True
    assert row["net_edge_pct"] == 7.0


def test_score_tradeability_row_not_tradeable_when_cost_exceeds_gap() -> None:
    row = score_tradeability_row(_row(gap="5.00", cost="8.00"))
    assert row is not None
    assert row["tradeable_after_costs"] is False


def test_run_cross_venue_tradeability_writes_reports(tmp_path) -> None:
    snap_root = tmp_path / "snapshots"
    path = snap_root / "2026-06-01" / "ppe_cross_venue_prob_panel_120000Z.csv"
    path.parent.mkdir(parents=True)
    path.write_text(serialize_cross_venue_export_csv([_row()]), encoding="utf-8")
    report, md_path, json_path = run_cross_venue_tradeability(
        snapshot_root=snap_root,
        report_root=tmp_path / "out",
    )
    assert report["tradeable_count"] == 1
    assert report["strategy_ready"] is True
    assert md_path.name == "latest_report.md"


def test_build_report_strategy_ready_false_when_no_edge() -> None:
    report = build_cross_venue_tradeability_report([_row(gap="2.00", cost="8.00")])
    assert report["strategy_ready"] is False


def test_stage0_1_parse_price_usd_handles_k_and_m_suffixes() -> None:
    assert parse_price_usd("Will BTC be above $120k?") == 120000
    assert parse_price_usd("Will BTC hit $1m?") == 1000000


def test_stage0_1_terminal_above_market_passes_semantic_gate() -> None:
    market = {
        "question": "Will Bitcoin be above $120,000 on December 31, 2026 at 12:00 UTC?",
        "description": "This market resolves Yes if BTC is above $120,000 at 12:00 UTC on December 31, 2026.",
        "outcomes": '["Yes", "No"]',
    }

    classification = classify_market(market)

    assert classification.terminal_candidate is True
    assert classification.decision == "ELIGIBLE_FOR_SCANNER_FEASIBILITY"
    assert classification.comparator == "above"
    assert classification.strike == 120000


def test_stage0_1_touch_market_rejected_before_hedge_compile() -> None:
    market = {
        "question": "Will Bitcoin reach $150,000 by December 31, 2026?",
        "description": "Yes if any Binance BTC/USDT one-minute candle high reaches $150,000 before the deadline.",
        "outcomes": '["Yes", "No"]',
    }

    classification = classify_market(market)

    assert classification.terminal_candidate is False
    assert classification.decision == "REJECT_NOT_SAFELY_HEDGEABLE"
    assert "touch_or_path_dependent" in classification.reasons


def test_stage0_1_above_without_timestamp_is_watch_not_executable() -> None:
    market = {
        "question": "Will Bitcoin be above $120,000?",
        "description": "This market resolves Yes if BTC is above $120,000.",
        "outcomes": '["Yes", "No"]',
    }

    classification = classify_market(market)

    assert classification.terminal_candidate is False
    assert classification.decision == "WATCH_EVIDENCE_INCOMPLETE"
