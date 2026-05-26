"""Panel parity: compact and verification MVP1 digests use the same materiality caption."""

from __future__ import annotations

from src.viz.app_panels import format_mvp1_materiality_caption


def test_format_mvp1_materiality_caption_matches_decision_surface_keys():
    mvp1 = {
        "materiality": {
            "market_width_1sigma_move_pct": 12.5,
            "benchmark_width_1sigma_move_pct": 10.0,
            "m_ratio": 1.42,
            "materiality_rule_version": "mvp1_v0_provisional",
        }
    }
    cap = format_mvp1_materiality_caption(mvp1)
    assert cap is not None
    assert "12.5" in cap
    assert "10.0" in cap
    assert "1.42" in cap
    assert "mvp1_v0_provisional" in cap


def test_format_mvp1_materiality_caption_missing_returns_none():
    assert format_mvp1_materiality_caption({}) is None
    assert format_mvp1_materiality_caption({"materiality": "bad"}) is None
