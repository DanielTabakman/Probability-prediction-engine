"""
MVP1 Phase 3 — primary decision surface (candidate / watch_only / no_trade).

Computes structured fields for `verification_payload` only (no Streamlit).
Precedence matches `artifacts/orchestrator/imported_specs/MVP1_PHASE1_3_SPRINT.md`
(MVP1-Phase3-Slice001) and `docs/VISION/PPE_MASTER_MVP1.md` §14 output-state order,
with sprint clause (2) mapping low-trust to **no_trade**.
"""

from __future__ import annotations

from typing import Any

_PHASE3_CONTRACT_VERSION = "mvp1_phase3_decision_surface_v0"


def _trace_fields(belief_disagreement: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not belief_disagreement or not isinstance(belief_disagreement, dict):
        return None, None
    trace = belief_disagreement.get("classification_trace")
    tr = trace if isinstance(trace, dict) else {}
    cat = tr.get("category_id") or belief_disagreement.get("category_id")
    shape = tr.get("shape_gap_strength")
    cat_s = str(cat).strip() if cat is not None else None
    shape_s = str(shape).strip() if shape is not None else None
    return cat_s, shape_s


def _expression_family_mapping(belief_disagreement: dict[str, Any] | None) -> dict[str, Any]:
    labels: list[str] = []
    if belief_disagreement and isinstance(belief_disagreement, dict):
        for fam in (belief_disagreement.get("strategy_families") or [])[:8]:
            if isinstance(fam, dict):
                lab = str(fam.get("label") or "").strip()
                if lab:
                    labels.append(lab)
    return {
        "families": labels,
        "mapping_note": (
            "Family-level illustrative_pattern mapping only — no executable strikes "
            "(MVP1 Phase 3)."
        ),
    }


def _confidence_tier(
    *,
    primary: str,
    shape_gap: str | None,
    materiality_ratio: float | None,
) -> str:
    if primary == "no_trade":
        return "low"
    if primary == "watch_only":
        if isinstance(materiality_ratio, (int, float)) and float(materiality_ratio) >= 1.0:
            return "medium"
        return "low"
    # candidate
    sg = (shape_gap or "").strip().lower()
    if sg == "high":
        return "high"
    if sg == "moderate":
        return "medium"
    return "medium"


def build_mvp1_phase3_decision_surface(
    *,
    mvp1_benchmark_substrate: dict[str, Any] | None,
    belief_disagreement: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Single MVP1 Phase 3 block attached under verification_payload.

    Returns None only when substrate dict is missing (should not happen for BTC lab runs).
    """
    if not mvp1_benchmark_substrate or not isinstance(mvp1_benchmark_substrate, dict):
        return None

    m = mvp1_benchmark_substrate
    tg = str(m.get("trust_gate_state") or "").strip().lower()
    ts = str(m.get("trust_state") or "").strip().lower()
    wgl = str(m.get("width_gap_label") or "").strip().lower()

    Ty = m.get("horizon_years")
    ty_f = float(Ty) if isinstance(Ty, (int, float)) else 0.0

    trace_cat, shape_gap = _trace_fields(
        belief_disagreement if isinstance(belief_disagreement, dict) else None
    )

    m_ratio_raw = m.get("materiality_ratio")
    m_ratio = float(m_ratio_raw) if isinstance(m_ratio_raw, (int, float)) else None

    expr = _expression_family_mapping(
        belief_disagreement if isinstance(belief_disagreement, dict) else None
    )

    # --- Precedence 1–6 (slice sprint ordering) ---
    step: int | None = None
    primary: str = "watch_only"
    explanation: str = "Evaluation could not be classified into a Phase 3 terminal state."
    no_trade_reasoning: str | None = None
    falsification: str = (
        "On a rerun with refreshed marks and unchanged classifier versions, if MVP1 trust becomes usable "
        "and width-gap / materiality labels change accordingly, revisit this evaluation."
    )

    # 1) invalid path → no_trade (benchmark / horizon path — substrate trust_gate only)
    if tg == "invalid":
        step = 1
        primary = "no_trade"
        explanation = (
            "Benchmark / horizon inputs are invalid (trust gate invalid) — MVP1 cannot classify ATM width "
            "disagreement on this path."
        )
        no_trade_reasoning = (
            "Invalid benchmark or market-implied width path under MVP1 Phase 2 gates "
            "(trust_gate_state=invalid)."
        )

    # 2) low-trust → no_trade (slice wording; substrate degraded / insufficient trust)
    elif ts == "degraded" or tg == "degraded" or wgl == "insufficient_trust":
        step = 2
        primary = "no_trade"
        cn = m.get("classification_note")
        cn_txt = str(cn).strip() if isinstance(cn, str) else ""
        explanation = (
            "Market-implied Breeden substrate or trust gate is degraded — MVP1 withholds promotion-style "
            "outputs until empirical width is trustworthy."
        )
        no_trade_reasoning = (
            "Low-trust state: degraded Breeden/market-implied path or insufficient trust for ATM width-gap "
            "classification."
            + (f" Detail: {cn_txt}" if cn_txt else "")
        )

    # 3) mixed / unclear → watch_only or no_trade (prefer watch_only here)
    elif wgl == "mixed_unclear" or trace_cat == "mixed":
        step = 3
        primary = "watch_only"
        explanation = (
            "ATM width-gap direction is materially ambiguous (tie band), or belief-vs-market classification "
            "is mixed — inspect before treating as a clean disagreement signal."
        )
        falsification = (
            "If refreshed marks collapse the tie band so width-gap resolves to market_too_wide / "
            "market_too_narrow with usable trust, or belief classification exits mixed, revisit the watch."
        )

    # 4) insufficient materiality → no_trade
    elif wgl == "insufficient_materiality":
        step = 4
        primary = "no_trade"
        cn = m.get("classification_note")
        cn_txt = str(cn).strip() if isinstance(cn, str) else ""
        explanation = (
            "Width disagreement versus the benchmark has not cleared MVP1 v0 materiality floors "
            "(gap too small versus labeled noise proxies)."
        )
        no_trade_reasoning = (
            "Insufficient materiality: |W_m − W_b| does not exceed the Phase 2 proxy floor "
            "after trust checks."
            + (f" Detail: {cn_txt}" if cn_txt else "")
        )
        falsification = (
            "If a rerun raises G_abs / M_ratio above the v0 floor under the same classifier versions, "
            "materiality may merit watch or candidate reassessment."
        )

    # 5) marginal disagreement → watch_only (shape-gap Low when disagreement direction is settled)
    elif wgl in ("market_too_wide", "market_too_narrow") and (shape_gap or "").strip().lower() == "low":
        step = 5
        primary = "watch_only"
        direction = "market-implied wider than benchmark ATM width" if wgl == "market_too_wide" else (
            "market-implied narrower than benchmark ATM width"
        )
        explanation = (
            f"Directional ATM width disagreement is present ({direction}), but the belief-vs-market "
            "shape-gap label is **Low** — treat as marginal signal pending cleaner separation."
        )
        falsification = (
            "If L₁ shape-gap strengthens to Moderate/High with stable peaks under refreshed marks, "
            "escalate toward candidate review; if peaks/width bands collapse to aligned, downgrade."
        )

    # 6) clear + material + high-trust disagreement → candidate
    elif wgl in ("market_too_wide", "market_too_narrow") and ts == "ok" and tg == "usable":
        step = 6
        primary = "candidate"
        direction = "market-implied wider than benchmark ATM width" if wgl == "market_too_wide" else (
            "market-implied narrower than benchmark ATM width"
        )
        explanation = (
            f"MVP1 surfaces a material ATM width disagreement ({direction}) under usable trust — hypothesis "
            "worth structured inspection (non-advisory)."
        )
        falsification = (
            "Would weaken if empirical σ_ln width or benchmark σ moves such that width_gap_label exits "
            "market_too_wide / market_too_narrow under the same classifier version, or trust degrades."
        )

    # Residual (unexpected label combinations)
    else:
        step = None
        primary = "watch_only"
        explanation = (
            f"Outstanding MVP1 width-gap label `{wgl or '—'}` with trust `{ts}` / gate `{tg}` — inspect "
            "substrate notes before deciding."
        )

    confidence = _confidence_tier(
        primary=primary,
        shape_gap=shape_gap,
        materiality_ratio=m_ratio,
    )

    review_horizon = {
        "horizon_years": ty_f,
        "assignment_note": (
            "Default review horizon tracks the active expiry horizon on this run "
            f"(T ≈ {ty_f:g} years). Snapshot freeze (Phase 4) pins this horizon."
        ),
    }

    return {
        "contract_schema_version": _PHASE3_CONTRACT_VERSION,
        "decision_precedence_step": step,
        "primary_output_state": primary,
        "explanation_plain": explanation,
        "confidence_tier": confidence,
        "expression_family_mapping": expr,
        "falsification_plain": falsification,
        "review_horizon": review_horizon,
        "no_trade_reasoning": no_trade_reasoning,
    }
