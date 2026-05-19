"""
MVP1 Phase 3 decision surface: data_quality, materiality witness, primary_output_state.

Pure module (no Streamlit). Precedence matches docs/VISION/PPE_MASTER_MVP1.md §14.
"""

from __future__ import annotations

import math
from typing import Any, Literal

from src.viz.belief_uncertainty import sigma_ln_to_move_pct_1sigma
from src.viz.disagreement_thresholds import WIDTH_NARROWER_RATIO, WIDTH_WIDER_RATIO

DataQuality = Literal["usable", "degraded", "invalid"]
PrimaryOutputState = Literal["candidate", "watch_only", "no_trade"]
ClassificationLabel = Literal[
    "market_too_wide",
    "market_too_narrow",
    "mixed_unclear",
    "insufficient_trust",
    "insufficient_materiality",
    "aligned",
]

MATERIALITY_RULE_VERSION = "mvp1_v0_provisional"
# Provisional floors (labeled in payload; not earned truths per master §6).
N_MEASUREMENT_REL = 0.02
N_BENCHMARK_REL = 0.02
N_EXECUTION_REL = 0.015


def _sigma_ln_at_horizon(vol_annual: float, t_years: float) -> float:
    return max(1e-9, float(vol_annual) * math.sqrt(max(float(t_years), 1e-9)))


def resolve_data_quality(
    *,
    forward_usd: float,
    vol_annual: float,
    breeden_status: str,
    belief_enabled: bool,
    belief_invalid: bool,
) -> DataQuality:
    if forward_usd <= 0 or vol_annual <= 0:
        return "invalid"
    if belief_enabled and belief_invalid:
        return "invalid"
    if breeden_status != "computed":
        return "degraded"
    return "usable"


def compute_materiality_witness(
    *,
    market_width_pct: float,
    benchmark_width_pct: float,
    data_quality: DataQuality,
) -> dict[str, Any]:
    """Width = 1σ intuitive move % at horizon; gaps per master §15."""
    g_abs = abs(market_width_pct - benchmark_width_pct)
    denom = max(abs(benchmark_width_pct), 1e-6)
    g_rel = g_abs / denom
    n_meas = N_MEASUREMENT_REL
    n_bench = N_BENCHMARK_REL
    n_exec = N_EXECUTION_REL
    if data_quality == "degraded":
        n_meas *= 1.5
    if data_quality == "invalid":
        n_meas *= 3.0
    m_floor = max(n_meas, n_bench, n_exec)
    m_ratio = g_abs / max(m_floor, 1e-9)
    return {
        "materiality_rule_version": MATERIALITY_RULE_VERSION,
        "market_width_1sigma_move_pct": round(market_width_pct, 4),
        "benchmark_width_1sigma_move_pct": round(benchmark_width_pct, 4),
        "absolute_gap_pct": round(g_abs, 4),
        "relative_gap": round(g_rel, 4),
        "m_floor_pct": round(m_floor, 4),
        "m_ratio": round(m_ratio, 4),
        "provisional_proxy_note": (
            "M_floor uses fixed v0 proxies (N_measurement, N_benchmark, N_execution); "
            "not calibrated from historical review data."
        ),
    }


def _width_classification(
    *,
    market_sigma_ln: float,
    benchmark_sigma_ln: float,
) -> ClassificationLabel:
    sm = max(benchmark_sigma_ln, 1e-12)
    if market_sigma_ln > sm * WIDTH_WIDER_RATIO:
        return "market_too_wide"
    if market_sigma_ln < sm * WIDTH_NARROWER_RATIO:
        return "market_too_narrow"
    return "aligned"


def resolve_primary_output_state(
    *,
    data_quality: DataQuality,
    classification: ClassificationLabel,
    category_id: str | None,
    m_ratio: float,
    shape_gap_strength: str | None,
) -> tuple[PrimaryOutputState, str]:
    """Returns (state, plain-language reason)."""
    if data_quality == "invalid":
        return (
            "no_trade",
            "Market-implied or benchmark path is not trustworthy enough to evaluate ATM width "
            "disagreement honestly at this horizon.",
        )
    if category_id == "mixed":
        return (
            "watch_only",
            "Disagreement is mixed across peak and width — inspect, but do not promote to a "
            "single ATM-width candidate.",
        )
    if data_quality == "degraded":
        return (
            "watch_only",
            "Data quality is degraded (e.g. market-implied density not fully computed). "
            "Informative only — not promoted to candidate.",
        )
    if classification == "insufficient_trust":
        return ("no_trade", "Insufficient trust in the market-implied width estimate.")
    if classification == "aligned":
        return (
            "watch_only",
            "Market ATM width is similar to the reference benchmark at this horizon — no material "
            "width disagreement to act on.",
        )
    if classification == "insufficient_materiality" or m_ratio < 1.0:
        return (
            "no_trade",
            "Width gap is below the current materiality floor (marginal vs noise and friction proxies).",
        )
    if m_ratio < 1.25:
        return (
            "watch_only",
            "Width disagreement is only marginally above the materiality floor — watch, not candidate.",
        )
    if category_id == "directional":
        return (
            "watch_only",
            "Primary tension is location-shaped (directional), not ATM width alone — width-only "
            "candidate promotion does not apply.",
        )
    if classification in ("market_too_wide", "market_too_narrow") and category_id == "width_vol":
        return (
            "candidate",
            f"Market ATM width is materially {classification.replace('_', ' ')} vs the reference "
            f"(M_ratio={m_ratio:.2f}, usable data).",
        )
    if classification in ("market_too_wide", "market_too_narrow"):
        return (
            "watch_only",
            f"Width pattern suggests {classification.replace('_', ' ')} but category is not "
            f"width_vol — inspect without width-only candidate promotion.",
        )
    _ = shape_gap_strength
    return (
        "watch_only",
        "No clear, material, high-trust ATM width candidate under current rules.",
    )


def build_mvp1_decision_surface(
    *,
    market_data: dict[str, Any],
    belief_disagreement: dict[str, Any] | None,
    belief_verification: dict[str, Any] | None,
    breeden_status: str,
) -> dict[str, Any]:
    """
    Build MVP1 decision block for verification payload and frozen-record witness.
    """
    forward = float(market_data.get("forward") or 0.0)
    vol = float(market_data.get("vol") or 0.0)
    t_years = float(market_data.get("T_years") or 0.0)
    sigma_bench_ln = _sigma_ln_at_horizon(vol, t_years)
    bench_width_pct = sigma_ln_to_move_pct_1sigma(sigma_bench_ln)

    bd = belief_disagreement if isinstance(belief_disagreement, dict) else {}
    bv = belief_verification if isinstance(belief_verification, dict) else {}
    belief_enabled = bool(bv.get("enabled")) if bv else bool(bd)
    belief_invalid = bool(bv.get("invalid")) if bv else False

    trace = bd.get("classification_trace") if isinstance(bd.get("classification_trace"), dict) else {}
    category_id = str(bd.get("category_id") or trace.get("category_id") or "").strip() or None
    width_band = str(bd.get("width_band") or trace.get("width_band") or "").strip() or None
    shape_gap = str(bd.get("shape_gap_strength") or trace.get("shape_gap_strength") or "").strip() or None

    data_quality = resolve_data_quality(
        forward_usd=forward,
        vol_annual=vol,
        breeden_status=breeden_status,
        belief_enabled=belief_enabled,
        belief_invalid=belief_invalid,
    )

    sigma_mkt_ln = sigma_bench_ln
    if belief_enabled and not belief_invalid:
        sm = bv.get("sigma_mkt_at_horizon")
        if sm is not None:
            sigma_mkt_ln = max(1e-9, float(sm))

    market_width_pct = sigma_ln_to_move_pct_1sigma(sigma_mkt_ln)
    if width_band == "wider":
        market_width_pct = sigma_ln_to_move_pct_1sigma(sigma_mkt_ln * WIDTH_WIDER_RATIO)
    elif width_band == "narrower":
        market_width_pct = sigma_ln_to_move_pct_1sigma(sigma_mkt_ln * WIDTH_NARROWER_RATIO)

    if data_quality == "invalid":
        classification: ClassificationLabel = "insufficient_trust"
    elif breeden_status != "computed" and not belief_enabled:
        classification = "insufficient_trust"
    elif category_id == "mixed":
        classification = "mixed_unclear"
    elif category_id == "directional":
        classification = "mixed_unclear"
    elif category_id == "aligned" or width_band == "similar":
        classification = "aligned"
    elif width_band == "wider":
        classification = "market_too_wide"
    elif width_band == "narrower":
        classification = "market_too_narrow"
    elif category_id == "width_vol":
        classification = "market_too_wide"
    else:
        classification = _width_classification(
            market_sigma_ln=sigma_mkt_ln, benchmark_sigma_ln=sigma_bench_ln
        )

    mat = compute_materiality_witness(
        market_width_pct=market_width_pct,
        benchmark_width_pct=bench_width_pct,
        data_quality=data_quality,
    )
    primary, reason = resolve_primary_output_state(
        data_quality=data_quality,
        classification=classification,
        category_id=category_id,
        m_ratio=float(mat["m_ratio"]),
        shape_gap_strength=shape_gap,
    )

    expression_family = "no_expression"
    if primary == "candidate":
        expression_family = "short_vol_family" if classification == "market_too_wide" else "long_vol_family"
    elif primary == "watch_only":
        expression_family = "watch_only"

    return {
        "mvp1_decision_schema_version": "mvp1_decision_v0",
        "data_quality": data_quality,
        "classification_label": classification,
        "primary_output_state": primary,
        "primary_output_reason": reason,
        "materiality": mat,
        "expression_family": expression_family,
        "review_horizon": str(market_data.get("expiry") or market_data.get("expiry_str") or ""),
        "falsification_note": (
            "Width disagreement compresses toward benchmark within the frozen expiry horizon, "
            "or data quality degrades below usable."
        ),
    }
