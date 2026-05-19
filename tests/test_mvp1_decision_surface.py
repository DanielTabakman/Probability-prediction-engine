"""Unit tests for MVP1 decision surface (primary_output_state, data_quality, materiality)."""

from __future__ import annotations

import pytest

from src.viz.mvp1_decision_surface import (
    build_mvp1_decision_surface,
    compute_materiality_witness,
    resolve_data_quality,
    resolve_primary_output_state,
)


def _market_data(**kwargs: object) -> dict:
    base = {"forward": 100_000.0, "vol": 0.55, "T_years": 0.08}
    base.update(kwargs)
    return base


def test_resolve_data_quality_invalid_forward():
    assert (
        resolve_data_quality(
            forward_usd=0,
            vol_annual=0.5,
            breeden_status="computed",
            belief_enabled=False,
            belief_invalid=False,
        )
        == "invalid"
    )


def test_resolve_data_quality_degraded_without_breeden():
    assert (
        resolve_data_quality(
            forward_usd=100_000,
            vol_annual=0.5,
            breeden_status="skipped",
            belief_enabled=False,
            belief_invalid=False,
        )
        == "degraded"
    )


def test_materiality_ratio_below_floor():
    mat = compute_materiality_witness(
        market_width_pct=10.0,
        benchmark_width_pct=10.005,
        data_quality="usable",
    )
    assert mat["m_ratio"] < 1.0


def test_primary_output_no_trade_on_invalid():
    state, _ = resolve_primary_output_state(
        data_quality="invalid",
        classification="insufficient_trust",
        category_id=None,
        m_ratio=2.0,
        shape_gap_strength=None,
    )
    assert state == "no_trade"


def test_primary_output_candidate_width_vol():
    state, reason = resolve_primary_output_state(
        data_quality="usable",
        classification="market_too_wide",
        category_id="width_vol",
        m_ratio=1.5,
        shape_gap_strength="Moderate",
    )
    assert state == "candidate"
    assert "material" in reason.lower() or "wide" in reason.lower()


def test_build_mvp1_decision_surface_width_vol_belief():
    bd = {
        "category_id": "width_vol",
        "width_band": "wider",
        "shape_gap_strength": "Moderate",
        "contract_schema_version": "test",
    }
    bv = {
        "enabled": True,
        "invalid": False,
        "sigma_ln_of_price": 0.25,
        "sigma_mkt_at_horizon": 0.18,
    }
    out = build_mvp1_decision_surface(
        market_data=_market_data(),
        belief_disagreement=bd,
        belief_verification=bv,
        breeden_status="computed",
    )
    assert out["data_quality"] == "usable"
    assert out["primary_output_state"] in ("candidate", "watch_only", "no_trade")
    assert "primary_output_state" in out
    assert out["materiality"]["m_ratio"] > 0


def test_build_mvp1_decision_surface_no_breeden_no_belief():
    out = build_mvp1_decision_surface(
        market_data=_market_data(),
        belief_disagreement=None,
        belief_verification=None,
        breeden_status="skipped",
    )
    assert out["data_quality"] == "degraded"
    assert out["primary_output_state"] in ("watch_only", "no_trade")
