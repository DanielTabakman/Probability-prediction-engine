"""
Read-only strategy suggestion boundary for MSOS expression planning.

Wraps existing implied-lab derive outputs — no new payoff math.
"""

from __future__ import annotations

import math
import re
from typing import Any

import pandas as pd

from src.engine.implied_distribution import build_distribution_chart_data
from src.engine.strategy_scanner import build_universal_strategy
from src.viz.app_cache import CACHE_TTL, cached_forward_iv, cached_marks_full, cached_option_expiries
from src.viz.decision_ready_review import build_decision_ready_review_payload
from src.viz.curve_display_labels import build_curve_display_labels
from src.viz.embed_display_boundary import (
    BELIEF_TUNING_BOUNDS,
    build_belief_overlay_from_mults,
    build_distribution_display_payload,
    clamp_belief_mult,
)
from src.viz.embed_only_lab import _load_export_rows
from src.viz.implied_lab_derive import derive_lab_outputs
from src.viz.implied_lab_presets import PresetId, compute_preset_shape, preset_label
from src.viz.implied_lab_state import build_implied_lab_state

STRATEGY_SUGGESTION_KIND = "strategy_suggestion_boundary"
STRATEGY_SUGGESTION_HTTP_PATH = "/ppe-display-api/strategy-suggestion.json"


def _peak_scaled(values: list[float], peak: float = 25.0) -> list[float]:
    if not values:
        return []
    m = max(values)
    if m <= 0:
        return [0.0] * len(values)
    return [float(v) / m * peak for v in values]


def _strip_md(text: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", r"\1", text or "").strip()


def _build_trade_review(
    verification: dict[str, Any] | None,
    review: dict[str, Any] | None,
) -> dict[str, Any]:
    """Plain-language strengths/risks + leg summary for MSOS (existing contract fields only)."""
    strengths: list[str] = []
    risks: list[str] = []
    plain_leg = ""

    if isinstance(review, dict):
        payoff = _strip_md(str(review.get("payoff_line") or ""))
        payoff = payoff.replace("Payoff shape (illustrative read):", "").strip()
        if payoff:
            plain_leg = payoff
            strengths.append(payoff)
        structure = _strip_md(str(review.get("structure_line") or ""))
        if structure and not plain_leg:
            plain_leg = structure[:320]

    bd = None
    if isinstance(verification, dict):
        raw_bd = verification.get("belief_disagreement")
        if isinstance(raw_bd, dict):
            bd = raw_bd
    if bd:
        families = bd.get("strategy_families") or []
        if isinstance(families, list):
            for fam in families[:2]:
                if not isinstance(fam, dict):
                    continue
                rationale = _strip_md(str(fam.get("fit_rationale") or ""))
                if rationale and rationale not in strengths:
                    strengths.append(rationale)
                tfm = _strip_md(str(fam.get("tradeoff_failure_mode") or ""))
                if tfm:
                    risks.append(tfm)

    glance = verification.get("belief_vs_market_glance") if isinstance(verification, dict) else None
    if isinstance(glance, dict):
        for line in glance.get("fit_bridge_bullets") or []:
            plain = _strip_md(str(line)).lstrip("- ").strip()
            if plain and plain not in risks:
                risks.append(plain)

    return {
        "strengths": strengths[:4],
        "risks": risks[:4],
        "plain_leg_summary": plain_leg,
    }


def _find_expiry(expiries: list[dict[str, Any]], expiry_date: str) -> dict[str, Any] | None:
    target = str(expiry_date or "").strip()
    if not target:
        return None
    for row in expiries:
        if str(row.get("expiry_date_str") or "") == target:
            return row
    for row in expiries:
        if str(row.get("expiry_date_str") or "").startswith(target[:10]):
            return row
    return None


def _preset_from_tuning(forward_mult: float, vol_mult: float) -> PresetId:
    if vol_mult >= 1.12:
        return "bull_call_spread" if forward_mult >= 1.0 else "bear_put_spread"
    if forward_mult >= 1.03:
        return "bull_call_spread"
    if forward_mult <= 0.97:
        return "bear_put_spread"
    return "short_iron_fly"


def _user_belief_from_tuning(
    *,
    forward: float,
    vol: float,
    t_years: float,
    forward_mult: float,
    vol_mult: float,
) -> dict[str, Any]:
    sigma_mkt_ln = max(1e-9, float(vol) * math.sqrt(max(t_years, 1e-9)))
    sigma_user = max(0.01, min(2.0, sigma_mkt_ln * float(vol_mult)))
    center = max(1.0, float(forward) * float(forward_mult))
    return {"enabled": True, "center_usd": center, "width": sigma_user}


def _legs_from_strategy(strategy: dict[str, Any], expiry_date: str) -> list[dict[str, str]]:
    legs: list[dict[str, str]] = []
    rows = [
        ("k1", "use_k1", "Put", "long_k1"),
        ("k2", "use_k2", "Put", "long_k2"),
        ("k3", "use_k3", "Call", "long_k3"),
        ("k4", "use_k4", "Call", "long_k4"),
    ]
    for key, use_key, instrument, long_key in rows:
        if not strategy.get(use_key):
            continue
        strike = float(strategy.get(key) or 0.0)
        side = "BUY" if strategy.get(long_key) else "SELL"
        legs.append(
            {
                "side": side,
                "instrument": f"BTC {instrument}",
                "strike": f"${strike:,.0f}",
                "tenor": expiry_date,
            }
        )
    return legs


def _build_market_data_for_expiry(expiry: dict[str, Any], spot_usd: float) -> dict[str, Any]:
    expiry_ts = int(expiry["expiry_ts"])
    fwd_iv = cached_forward_iv(expiry_ts, spot_usd) or {}
    forward = float(fwd_iv.get("forward") or spot_usd)
    vol = float(fwd_iv.get("atm_iv") or 0.6)
    if vol <= 0:
        vol = 0.6
    run_ts_utc = pd.Timestamp.now(tz="UTC")
    now_ts = run_ts_utc.timestamp() * 1000
    t_years = max(0.02, max(0.0, (expiry_ts - now_ts) / 1000 / (365.25 * 24 * 3600)))
    price_min = max(1000.0, forward * 0.4)
    price_max = forward * 2.2
    dist = build_distribution_chart_data(
        forward=forward,
        vol_annual=vol,
        T_years=t_years,
        price_min=price_min,
        price_max=price_max,
        num_points=100,
    )
    marks_full = cached_marks_full(expiry_ts) or {}
    call_marks = marks_full.get("calls") or []
    put_marks = marks_full.get("puts") or []
    avail_strikes = sorted({float(m["strike"]) for m in call_marks + put_marks})
    call_by_k = {float(m["strike"]): float(m.get("mark_btc") or 0) for m in call_marks}
    put_by_k = {float(m["strike"]): float(m.get("mark_btc") or 0) for m in put_marks}
    return {
        "forward": forward,
        "vol": vol,
        "T_years": t_years,
        "price_min": price_min,
        "price_max": price_max,
        "dist": dist,
        "marks_full": marks_full,
        "call_marks": call_marks,
        "put_marks": put_marks,
        "avail_strikes": avail_strikes,
        "call_by_k": call_by_k,
        "put_by_k": put_by_k,
        "data_sources": ["Deribit (BTC index, forward, ATM IV, option marks)"],
        "as_of_utc": run_ts_utc.isoformat(),
        "quote_cache_ttl_s": CACHE_TTL,
    }


def build_strategy_suggestion_response(
    *,
    expiry_date: str,
    forward_mult: float = 1.0,
    vol_mult: float = 1.0,
) -> dict[str, Any]:
    fwd_m = clamp_belief_mult("forward_mult", forward_mult)
    vol_m = clamp_belief_mult("vol_mult", vol_mult)

    as_of_utc, spot_usd, export_rows = _load_export_rows()
    expiries, _diag = cached_option_expiries()
    expiry = _find_expiry(expiries, expiry_date)
    if expiry is None:
        return {"kind": "strategy_suggestion_error", "error": f"expiry not found: {expiry_date}"}

    expiry_str = str(expiry["expiry_date_str"])
    market_data = _build_market_data_for_expiry(expiry, spot_usd)
    forward = float(market_data["forward"])
    avail = [float(x) for x in market_data["avail_strikes"]]
    if len(avail) < 2:
        return {
            "kind": "strategy_suggestion_error",
            "error": "insufficient listed strikes for strategy suggestion",
        }

    preset_id = _preset_from_tuning(fwd_m, vol_m)
    shape = compute_preset_shape(preset_id=preset_id, forward=forward, avail_strikes=avail)
    k1, k2, k3, k4 = (
        float(shape["k1"]),
        float(shape["k2"]),
        float(shape["k3"]),
        float(shape["k4"]),
    )
    strikes_exact = {"k1": k1, "k2": k2, "k3": k3, "k4": k4}
    payoff_targets = {
        "body_left": k2,
        "body_right": k3,
        "left_wing": max(0.0, k2 - k1),
        "right_wing": max(0.0, k4 - k3),
    }
    user_belief = _user_belief_from_tuning(
        forward=forward,
        vol=float(market_data["vol"]),
        t_years=float(market_data["T_years"]),
        forward_mult=fwd_m,
        vol_mult=vol_m,
    )
    state = build_implied_lab_state(
        expiry_str=expiry_str,
        mode="exact_strikes",
        qty=int(shape.get("qty", 1) or 1),
        strikes_exact=strikes_exact,
        payoff_targets=payoff_targets,
        legs_enabled={
            "use_k1": bool(shape["use_k1"]),
            "use_k2": bool(shape["use_k2"]),
            "use_k3": bool(shape["use_k3"]),
            "use_k4": bool(shape["use_k4"]),
        },
        reverse=bool(shape.get("reverse", False)),
        net_pnl_mode=True,
        user_belief=user_belief,
    )
    outputs = derive_lab_outputs(state, market_data)
    strategy = outputs.get("strategy")
    summary = outputs.get("summary") or {}
    overlay = outputs.get("overlay") or {}
    verification = outputs.get("verification") or {}
    if not strategy or not overlay.get("payoff_usd"):
        err = summary.get("error") or "strategy suggestion unavailable"
        return {"kind": "strategy_suggestion_error", "error": str(err)}

    prices = [float(p) for p in overlay.get("prices") or []]
    payoff_usd = [float(p) for p in overlay.get("payoff_usd") or []]
    market_pdf = [float(p) for p in market_data["dist"].get("pdf_pct") or []]
    if len(market_pdf) != len(prices):
        market_pdf = _peak_scaled([float(x) for x in market_data["dist"].get("pdf_raw") or []])

    display_payload = build_distribution_display_payload(
        as_of_utc=as_of_utc,
        spot_usd=spot_usd,
        export_rows=export_rows,
    )
    series = next(
        (s for s in display_payload.get("series_by_expiry", []) if s.get("expiry_date") == expiry_str),
        None,
    )
    belief_pdf: list[float] = []
    if series:
        belief_overlay = build_belief_overlay_from_mults(
            series,
            forward_mult=fwd_m,
            vol_mult=vol_m,
        )
        if belief_overlay:
            belief_pdf = [float(x) for x in belief_overlay.get("pdf_pct") or []]

    review = build_decision_ready_review_payload(verification, mvp1_exclude_execution_ui=True)
    ss = verification.get("strategy_summary") or {}
    vals = ss.get("values") if isinstance(ss.get("values"), dict) else {}
    glance = verification.get("belief_vs_market_glance")
    vs = verification.get("verification_summary") or {}

    return {
        "kind": STRATEGY_SUGGESTION_KIND,
        "expiry_date": expiry_str,
        "spot_usd": spot_usd,
        "forward_mult": fwd_m,
        "vol_mult": vol_m,
        "tuning_bounds": BELIEF_TUNING_BOUNDS,
        "market": {
            "prices_usd": prices,
            "pdf_pct": market_pdf[: len(prices)] if len(market_pdf) == len(prices) else market_pdf,
            "belief_pdf_pct": belief_pdf if len(belief_pdf) == len(prices) else [],
            "curve_labels": build_curve_display_labels(),
        },
        "suggested": {
            "preset_id": preset_id,
            "preset_label": preset_label(preset_id),
            "name": str(vals.get("name") or summary.get("name") or preset_label(preset_id)),
            "legs": _legs_from_strategy(strategy, expiry_str),
            "overlay": {
                "prices_usd": prices,
                "payoff_pct": _peak_scaled(payoff_usd),
                "payoff_usd": payoff_usd,
            },
            "summary": {
                "net_cost_usd": vals.get("net_cost_usd", summary.get("cost_usd")),
                "debit_credit": vals.get("debit_credit", summary.get("debit_credit")),
                "max_gain_usd": vals.get("max_gain_usd", summary.get("max_gain")),
                "max_loss_usd": vals.get("max_loss_usd", summary.get("max_loss")),
                "breakevens_usd": vals.get("breakevens_usd", summary.get("breakevens")),
                "qty": vals.get("qty", strategy.get("qty")),
            },
            "review": {
                "structure_line": _strip_md((review or {}).get("structure_line", "")),
                "payoff_line": _strip_md((review or {}).get("payoff_line", "")),
                "linkage_line": _strip_md((review or {}).get("linkage_line", "")),
            }
            if review
            else {},
            "trade_review": _build_trade_review(verification, review),
            "expression_family": vs.get("expression_family"),
            "belief_vs_market_glance": glance if isinstance(glance, dict) else None,
        },
    }
