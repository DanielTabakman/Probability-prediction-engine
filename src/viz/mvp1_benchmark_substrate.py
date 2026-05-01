"""
MVP1 Phase 1–2 — market + benchmark substrate + ATM width-gap engine v1.

Numerics stay free of Streamlit. Breeden–Litzenberger gate matches implied_lab_derive /
build_verification_payload (len(call_marks) >= 3).

Phase 2 adds G_abs / G_rel, materiality (v0 proxy floors), trust gate usable/degraded/invalid,
and the required deterministic label set (see MVP1_PHASE1_3_SPRINT MVP1-Phase2-Slice001).
"""

from __future__ import annotations

import math
from typing import Any

# Frozen contract identifiers for Phase 1 substrate (bump version when semantics change).
MVP1_BENCHMARK_ID = "ppe_mvp1_lognormal_atm_iv"
MVP1_BENCHMARK_VERSION = "1.0.0"

# Phase 2 width-gap classifier (slice-owned; bump when labeling rules change).
MVP1_WIDTH_GAP_CLASSIFIER_VERSION = "1.0.0"

def _mvp1_materiality_floor_v0(*, trust_gate: str) -> dict[str, Any]:
    """Provisional floors per PPE_MASTER_MVP1 (explicitly labeled, not earned-from-data)."""
    degraded_uplift = 0.006 if trust_gate != "usable" else 0.0
    n_meas = 0.012 + degraded_uplift
    n_bench = 0.008 + 0.5 * degraded_uplift
    n_exec = 0.010 + 0.5 * degraded_uplift
    floor = float(max(n_meas, n_bench, n_exec))
    return {
        "proxy_schema": "mvp1_materiality_floor_v0_proxy",
        "proxy_note": (
            "MVP1 v0 placeholders for N_measurement, N_benchmark, N_execution (σ_ln units); "
            "labeled proxy — not data-calibrated thresholds (see PPE_MASTER_MVP1 materiality)."
        ),
        "N_measurement_sigma_ln": float(n_meas),
        "N_benchmark_sigma_ln": float(n_bench),
        "N_execution_sigma_ln": float(n_exec),
        "M_floor_sigma_ln": floor,
        "effective_trust_gate_for_floor": trust_gate,
    }


def _width_gap_classification(
    *,
    W_m: float | None,
    W_b: float | None,
    trust_gate: str,
    empirical_status: str,
    breeden_gate: bool,
) -> dict[str, Any]:
    """
    Returns W_m, W_b, gaps, trust gate duplicate, materiality block, width_gap_label.
    """
    eps = 1e-12

    usable = trust_gate == "usable" and W_m is not None and W_b is not None

    if trust_gate == "invalid":
        label = "insufficient_trust"
        mat = _mvp1_materiality_floor_v0(trust_gate="invalid")
        return {
            "classifier_version": MVP1_WIDTH_GAP_CLASSIFIER_VERSION,
            "trust_gate_state": trust_gate,
            "W_m": None,
            "W_b": W_b,
            "W_m_source": None,
            "G_abs": None,
            "G_rel": None,
            "materiality": mat,
            "materiality_ratio": None,
            "materiality_satisfied": False,
            "width_gap_label": label,
            "classification_note": (
                "Invalid inputs for horizon width / benchmark reference — no ATM benchmark gap classified."
            ),
        }

    if not usable:
        label = "insufficient_trust"
        mat = _mvp1_materiality_floor_v0(trust_gate=trust_gate)
        reason = (
            "Empirical market-implied width on the pricing grid is required for MVP1 Phase 2 "
            "benchmark vs Breeden disagreement; degraded Breeden substrate."
        )
        if not breeden_gate:
            reason = "Breeden–Litzenberger gate not satisfied — empirical market width unavailable."
        elif empirical_status != "computed":
            reason = "Empirical σ_ln under Breeden density not computed — width gap withheld."
        return {
            "classifier_version": MVP1_WIDTH_GAP_CLASSIFIER_VERSION,
            "trust_gate_state": trust_gate,
            "W_m": None,
            "W_b": W_b,
            "W_m_source": None,
            "G_abs": None,
            "G_rel": None,
            "materiality": mat,
            "materiality_ratio": None,
            "materiality_satisfied": False,
            "width_gap_label": label,
            "classification_note": reason,
        }

    wm = float(W_m)
    wb = float(W_b)
    g_abs = float(abs(wm - wb))
    g_rel = float(g_abs / max(abs(wb), eps))
    mat = _mvp1_materiality_floor_v0(trust_gate="usable")
    m_floor = float(mat["M_floor_sigma_ln"])
    m_ratio = float(g_abs / max(m_floor, eps))

    if m_ratio < 1.0:
        return {
            "classifier_version": MVP1_WIDTH_GAP_CLASSIFIER_VERSION,
            "trust_gate_state": trust_gate,
            "W_m": wm,
            "W_b": wb,
            "W_m_source": "empirical_market_implied_sigma_ln_grid",
            "G_abs": g_abs,
            "G_rel": g_rel,
            "materiality": mat,
            "materiality_ratio": m_ratio,
            "materiality_satisfied": False,
            "width_gap_label": "insufficient_materiality",
            "classification_note": (
                f"M_ratio={m_ratio:.3f} < 1 versus labeled v0 floor {m_floor:g} σ_ln "
                "(gap has not cleared the floor of indifference)."
            ),
        }

    tie = max(eps, 0.002 * max(abs(wm), abs(wb)))
    if abs(wm - wb) <= tie:
        wg_label = "mixed_unclear"
        note = (
            "Material under v0 floors, but directional tie band treats this ATM gap as ambiguous "
            f"(|Δ| ≤ {tie:g} σ_ln)."
        )
    elif wm > wb:
        wg_label = "market_too_wide"
        note = (
            "Market-implied width (Breeden σ on grid) exceeds lognormal ATM benchmark width "
            "at this horizon under v0 materiality gates."
        )
    else:
        wg_label = "market_too_narrow"
        note = (
            "Market-implied width (Breeden σ on grid) is below the lognormal ATM benchmark width "
            "at this horizon under v0 materiality gates."
        )

    return {
        "classifier_version": MVP1_WIDTH_GAP_CLASSIFIER_VERSION,
        "trust_gate_state": trust_gate,
        "W_m": wm,
        "W_b": wb,
        "W_m_source": "empirical_market_implied_sigma_ln_grid",
        "G_abs": g_abs,
        "G_rel": g_rel,
        "materiality": mat,
        "materiality_ratio": m_ratio,
        "materiality_satisfied": True,
        "width_gap_label": wg_label,
        "classification_note": note,
    }


def _sigma_ln_atm_horizon(vol_annual: float, T_years: float) -> float:
    v = max(0.0, float(vol_annual))
    T = max(0.0, float(T_years))
    return float(v * math.sqrt(max(T, 1e-12)))


def _empirical_sigma_ln_under_pdf(prices: list[float], f_raw: list[float]) -> float | None:
    """
    Trapezoid-normalized density on the price grid; return stdev of ln(price) using segment midpoints.
    """
    if len(prices) < 2 or len(f_raw) != len(prices):
        return None
    if max(abs(float(x)) for x in f_raw) <= 1e-20:
        return None

    area = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        area += 0.5 * (float(f_raw[i]) + float(f_raw[i + 1])) * dx
    if area <= 0 or math.isnan(area) or math.isinf(area):
        return None

    eln = 0.0
    eln2 = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        w = 0.5 * (float(f_raw[i]) / area + float(f_raw[i + 1]) / area) * dx
        mid = 0.5 * (float(prices[i]) + float(prices[i + 1]))
        lm = math.log(max(mid, 1e-12))
        eln += w * lm
        eln2 += w * lm * lm
    var = max(0.0, eln2 - eln * eln)
    out = math.sqrt(var)
    if math.isnan(out) or math.isinf(out):
        return None
    return float(out)


def build_mvp1_benchmark_substrate(
    *,
    market_data: dict[str, Any],
    market_pdf_raw: list[float],
    call_marks: list[Any],
) -> dict[str, Any]:
    """
    Single structured block for UI + trust: benchmark identity, widths on shared horizon T,
    and honest degraded handling when Breeden is skipped or empirical width is unusable.
    """
    dist = market_data.get("dist") or {}
    prices: list[float] = dist.get("prices") or []

    vol = float(market_data.get("vol") or 0.0)
    T_years = float(market_data.get("T_years") or 0.0)
    sigma_atm = _sigma_ln_atm_horizon(vol, T_years)

    call_n = len(call_marks)
    breeden_gate = call_n >= 3

    empirical: float | None = None
    empirical_status = "skipped"
    empirical_skip_reason: str | None = None
    if not breeden_gate:
        empirical_skip_reason = (
            "Fewer than 3 call marks at this expiry — no Breeden–Litzenberger density; "
            "empirical market-implied width is not computed."
        )
    elif not market_pdf_raw or len(market_pdf_raw) != len(prices):
        empirical_skip_reason = "Market-implied raw density missing or length mismatch vs grid."
    else:
        empirical = _empirical_sigma_ln_under_pdf(prices, market_pdf_raw)
        if empirical is None:
            empirical_skip_reason = "Empirical σ_ln under market-implied PDF was not usable on this grid."
        else:
            empirical_status = "computed"

    degraded = (not breeden_gate) or (empirical_status != "computed")
    if empirical_status != "computed" and breeden_gate:
        degraded = True

    if not degraded:
        trust_state = "ok"
        trust_note = (
            "Benchmark reference and ATM width are on the same horizon; Breeden–Litzenberger σ estimate "
            "on the pricing grid is available for comparison."
        )
    elif not breeden_gate:
        trust_state = "degraded"
        trust_note = (
            "Degraded: market-implied curve (orange) skipped — only ATM-quoted σ and the lognormal benchmark "
            "on the purple reference are fully anchored."
        )
    else:
        trust_state = "degraded"
        trust_note = (
            "Degraded: Breeden density ran but empirical width on the grid is missing — compare ATM and benchmark σ "
            "only; see Verification for details."
        )

    W_b = float(sigma_atm)
    if (
        vol <= 0.0
        or T_years <= 0.0
        or not math.isfinite(W_b)
        or (empirical is not None and not math.isfinite(float(empirical)))
    ):
        phase2_trust_gate = "invalid"
    elif empirical_status == "computed" and empirical is not None:
        phase2_trust_gate = "usable"
    else:
        phase2_trust_gate = "degraded"

    width_gap_vm = empirical if empirical_status == "computed" else None
    wg_block = _width_gap_classification(
        W_m=width_gap_vm,
        W_b=W_b,
        trust_gate=phase2_trust_gate,
        empirical_status=empirical_status,
        breeden_gate=breeden_gate,
    )

    return {
        "benchmark_id": MVP1_BENCHMARK_ID,
        "benchmark_version": MVP1_BENCHMARK_VERSION,
        "horizon_years": float(T_years),
        "benchmark_definition": (
            "Black–Scholes lognormal terminal density on the chart grid using forward and ATM implied volatility "
            "(purple reference); MVP1 Phase 1 names this the explicit benchmark."
        ),
        "sigma_market_atm_ln": float(sigma_atm),
        "sigma_benchmark_ln": float(sigma_atm),
        "benchmark_sigma_note": (
            "Phase 1: benchmark width equals ATM σ·√T by contract — same inputs as the purple reference curve."
        ),
        "empirical_market_implied_sigma_ln": empirical,
        "empirical_status": empirical_status,
        "empirical_skip_reason": empirical_skip_reason,
        "call_marks_count": int(call_n),
        "trust_state": trust_state,
        "trust_state_note": trust_note,
        **wg_block,
    }
