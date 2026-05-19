"""Verification payload includes MVP1 decision block."""

from __future__ import annotations

from src.viz.implied_lab_provenance import build_verification_payload


def test_build_verification_payload_includes_mvp1_decision() -> None:
    market_data = {
        "forward": 100_000.0,
        "vol": 0.55,
        "T_years": 0.08,
        "dist": {"prices": [80_000.0, 120_000.0], "pdf_raw": [0.5, 0.5]},
        "data_sources": ["test"],
        "as_of_utc": "2026-01-01T00:00:00Z",
    }
    v = build_verification_payload(
        market_data=market_data,
        summary={"name": "—", "cost_usd": 0, "debit_credit": "—", "breakevens": []},
        strategy=None,
        overlay={"prices": market_data["dist"]["prices"], "payoff_usd": []},
        market_pdf_raw=[],
        call_marks=[1, 2, 3],
        belief_verification=None,
        belief_disagreement=None,
    )
    assert "mvp1_decision" in v
    assert v["mvp1_decision"]["primary_output_state"] in ("candidate", "watch_only", "no_trade")
    vs = v["verification_summary"]
    assert vs.get("primary_output_state") == v["mvp1_decision"]["primary_output_state"]
    assert vs.get("data_quality") in ("usable", "degraded", "invalid")
