from __future__ import annotations

import math
from typing import Any

from src.engine.implied_distribution import (
    is_anomalous,
    market_implied_density_breeden_litzenberger,
)
from src.engine.strategy_scanner import (
    name_universal_strategy,
    payoff_target_to_strikes_with_work,
    strategy_payoff_at_prices,
)


def _compute_cost_usd(
    forward: float,
    put_by_k: dict[float, float],
    call_by_k: dict[float, float],
    k1: float,
    k2: float,
    k3: float,
    k4: float,
    long_k1: bool,
    long_k2: bool,
    long_k3: bool,
    long_k4: bool,
    use_k1: bool,
    use_k2: bool,
    use_k3: bool,
    use_k4: bool,
) -> float:
    s1 = 0 if not use_k1 else (1 if long_k1 else -1)
    s2 = 0 if not use_k2 else (1 if long_k2 else -1)
    s3 = 0 if not use_k3 else (1 if long_k3 else -1)
    s4 = 0 if not use_k4 else (1 if long_k4 else -1)
    cost_btc = (
        s1 * float(put_by_k.get(k1, 0.0))
        + s2 * float(put_by_k.get(k2, 0.0))
        + s3 * float(call_by_k.get(k3, 0.0))
        + s4 * float(call_by_k.get(k4, 0.0))
    )
    return float(cost_btc * forward)


def _integrate_density_trapezoid(prices: list[float], f: list[float]) -> float:
    """∫ f(x) dx on the price grid (piecewise linear / trapezoid between samples)."""
    if len(prices) < 2 or len(f) != len(prices):
        return 0.0
    total = 0.0
    for i in range(len(prices) - 1):
        dx = float(prices[i + 1]) - float(prices[i])
        if dx <= 0:
            continue
        total += 0.5 * (float(f[i]) + float(f[i + 1])) * dx
    return float(total)


def _area_normalize(prices: list[float], f: list[float]) -> tuple[list[float], float]:
    """Return densities scaled to integrate to 1 (or zeros if degenerate)."""
    area = _integrate_density_trapezoid(prices, f)
    if area <= 0 or math.isnan(area) or math.isinf(area):
        return [0.0] * len(f), 0.0
    return [float(x) / area for x in f], area


def _user_belief_lognormal_pdf_raw(
    prices: list[float],
    mode_usd: float,
    sigma_log: float,
) -> list[float]:
    """
    Log-normal on terminal price with ln S ~ N(μ, σ²).
    Peak (mode) is at exp(μ - σ²) = mode_usd ⇒ μ = ln(mode_usd) + σ².
    """
    if mode_usd <= 0 or sigma_log <= 1e-9:
        return [0.0] * len(prices)
    mu = math.log(mode_usd) + sigma_log * sigma_log
    out: list[float] = []
    for s in prices:
        s = float(s)
        if s <= 0:
            out.append(0.0)
            continue
        z = (math.log(s) - mu) / sigma_log
        density = (1.0 / (s * sigma_log * math.sqrt(2.0 * math.pi))) * math.exp(-0.5 * z * z)
        out.append(float(density))
    return out


def _reference_density_raw_for_belief(
    market_pdf_raw: list[float],
    lognormal_pdf_raw: list[float],
) -> tuple[list[float], str]:
    """
    Prefer Breeden/market-implied if it has usable mass; else lognormal baseline.
    """
    if (
        market_pdf_raw
        and len(market_pdf_raw) == len(lognormal_pdf_raw)
        and max(market_pdf_raw) > 1e-20
    ):
        return [max(0.0, float(x)) for x in market_pdf_raw], "market-implied"
    return [max(0.0, float(x)) for x in lognormal_pdf_raw], "lognormal baseline"


def _argmax_peak_price(prices: list[float], f: list[float]) -> float | None:
    if not prices or not f or len(prices) != len(f):
        return None
    best_i = max(range(len(f)), key=lambda i: float(f[i]))
    return float(prices[best_i])


def _derive_user_belief_outputs(
    state: dict[str, Any],
    market_data: dict[str, Any],
    market_pdf_raw: list[float],
) -> dict[str, Any]:
    """
    Sprint 2A: user belief curve (peak = center_usd) + textual comparison vs displayed market ref.
    Chart uses peak-scaled series; summary uses area-normalized densities.
    """
    empty_chart = {"user_belief_pct": []}
    ub = state.get("user_belief") or {}
    if not isinstance(ub, dict) or not bool(ub.get("enabled", False)):
        return {"chart_helpers_extra": empty_chart, "belief_summary": {"text": ""}}

    prices: list[float] = market_data["dist"]["prices"]
    vol = float(market_data.get("vol") or 0.6)
    T_years = float(market_data.get("T_years") or 0.02)
    sigma_mkt = max(1e-9, vol * math.sqrt(max(T_years, 1e-9)))

    center = float(ub.get("center_usd") or 0.0)
    width = float(ub.get("width") or 0.0)
    sigma_user = max(0.01, min(2.0, width)) if width > 0 else 0.15

    if center <= 0:
        return {
            "chart_helpers_extra": empty_chart,
            "belief_summary": {"text": "Set a positive belief center (peak price) to compare to the market."},
        }

    lognormal_raw = [float(x) for x in (market_data["dist"].get("pdf_raw") or [])]
    if len(lognormal_raw) != len(prices):
        lognormal_raw = [0.0] * len(prices)

    ref_raw, ref_kind = _reference_density_raw_for_belief(market_pdf_raw, lognormal_raw)
    if len(ref_raw) != len(prices):
        ref_raw = [max(0.0, float(x)) for x in lognormal_raw]
        ref_kind = "lognormal baseline"

    user_raw = _user_belief_lognormal_pdf_raw(prices, center, sigma_user)
    u_norm, _ = _area_normalize(prices, user_raw)
    r_norm, r_area = _area_normalize(prices, ref_raw)

    # Chart overlay: same visual scaling as purple/orange (peak → ~25% tick space)
    max_u = max(user_raw) if user_raw else 0.0
    user_belief_pct = (
        [(d / max_u * 25.0) if max_u > 0 else 0.0 for d in user_raw]
        if max_u > 0
        else []
    )

    if r_area <= 0:
        return {
            "chart_helpers_extra": {"user_belief_pct": user_belief_pct},
            "belief_summary": {"text": "Market reference density is unavailable for comparison on this grid."},
        }

    market_peak = _argmax_peak_price(prices, ref_raw)
    if market_peak is None:
        text = ""
    else:
        delta = center - market_peak
        if abs(delta) < max(1.0, 0.002 * market_peak):
            tilt = "about **aligned** with the market peak"
        elif delta > 0:
            tilt = f"**more bullish** than the {ref_kind} peak (~${delta:,.0f} above the market peak at ${market_peak:,.0f})"
        else:
            tilt = f"**more bearish** than the {ref_kind} peak (~${-delta:,.0f} below the market peak at ${market_peak:,.0f})"

        if sigma_user < sigma_mkt * 0.92:
            spread_txt = "**narrower** uncertainty than ATM-implied log volatility at this horizon"
        elif sigma_user > sigma_mkt * 1.08:
            spread_txt = "**wider** uncertainty than ATM-implied log volatility at this horizon"
        else:
            spread_txt = "**similar** width to ATM-implied log volatility at this horizon"

        disc = [abs(u_norm[i] - r_norm[i]) for i in range(len(prices))]
        if disc:
            i0 = max(range(len(disc)), key=lambda i: disc[i])
            disagree_txt = f"Largest shape gap is near **${prices[i0]:,.0f}** (comparing area-normalized densities)."
        else:
            disagree_txt = ""

        parts = [
            f"**Belief vs {ref_kind}:** your curve peaks at **${center:,.0f}**; the reference peaks near **${market_peak:,.0f}** — you are {tilt}.",
            f"You are {spread_txt}.",
        ]
        if disagree_txt:
            parts.append(disagree_txt)
        text = " ".join(parts)

    return {
        "chart_helpers_extra": {"user_belief_pct": user_belief_pct},
        "belief_summary": {"text": text},
    }


def _breakevens_from_curve(prices: list[float], payoff_usd: list[float]) -> list[float]:
    out: list[float] = []
    if not payoff_usd or len(prices) != len(payoff_usd):
        return out
    for i in range(1, len(payoff_usd)):
        if payoff_usd[i - 1] == 0:
            out.append(prices[i - 1])
        elif payoff_usd[i] == 0:
            out.append(prices[i])
        elif payoff_usd[i - 1] * payoff_usd[i] < 0:
            x0, x1 = prices[i - 1], prices[i]
            y0, y1 = payoff_usd[i - 1], payoff_usd[i]
            if y1 != y0:
                x_be = x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
                out.append(float(x_be))
    return out


def _solve_strikes_from_targets(
    state: dict[str, Any],
    market_data: dict[str, Any],
) -> tuple[tuple[float, float, float, float] | None, dict[str, Any]]:
    """
    Target-payoff mode strike solver.
    - If net_pnl_mode=False: use payoff_target_to_strikes_with_work (intrinsic mapping).
    - If net_pnl_mode=True: cost-aware solver for classic polarity with all legs enabled.
    """
    avail_strikes: list[float] = market_data["avail_strikes"]
    put_by_k: dict[float, float] = market_data["put_by_k"]
    call_by_k: dict[float, float] = market_data["call_by_k"]
    forward: float = market_data["forward"]
    prices: list[float] = market_data["dist"]["prices"]

    targets = state["payoff_targets"]
    BL = float(targets["body_left"])
    BR = float(targets["body_right"])
    L = float(targets["left_wing"])
    R = float(targets["right_wing"])

    if not state.get("net_pnl_mode", False):
        return payoff_target_to_strikes_with_work(BL, BR, max(0.0, L), max(0.0, R), avail_strikes)

    # Net P&L solver (classic polarity, all legs enabled)
    long_k1 = bool(state["polarity"]["long_k1"])
    long_k2 = bool(state["polarity"]["long_k2"])
    long_k3 = bool(state["polarity"]["long_k3"])
    long_k4 = bool(state["polarity"]["long_k4"])
    use_k1 = bool(state["legs_enabled"]["use_k1"])
    use_k2 = bool(state["legs_enabled"]["use_k2"])
    use_k3 = bool(state["legs_enabled"]["use_k3"])
    use_k4 = bool(state["legs_enabled"]["use_k4"])
    classic = (long_k1, long_k2, long_k3, long_k4) == (False, True, True, False)
    if not (classic and use_k1 and use_k2 and use_k3 and use_k4):
        return None, {"valid": False, "error": "Net P&L mode currently assumes classic polarity with all legs enabled."}

    # In net mode: BL/BR are net breakevens, L/R are desired net profit plateaus (after premium).
    # First set K1 and K4 from cancellation identities.
    k1_raw = BL - L
    k4_raw = BR + R
    put_strikes = sorted(put_by_k.keys())
    call_strikes = sorted(call_by_k.keys())
    if not put_strikes or not call_strikes:
        return None, {"valid": False, "error": "Missing option marks for puts/calls at this expiry."}

    k1_snap = float(min(put_strikes, key=lambda k: abs(k - k1_raw)))
    k4_snap = float(min(call_strikes, key=lambda k: abs(k - k4_raw)))
    if k1_snap >= k4_snap:
        return None, {"valid": False, "error": "Invalid net targets: computed K1 is not left of K4."}

    # Search for K2 (put) and derive K3 target from BL+BR-K2.
    best: tuple[float, float, float, float] | None = None
    best_cost: float | None = None
    best_err = float("inf")

    k2_candidates = [float(k) for k in put_strikes if k1_snap <= k <= k4_snap]
    for k2_cand in k2_candidates:
        k3_target = BL + BR - k2_cand
        k3_snap = float(min(call_strikes, key=lambda k: abs(k - k3_target)))
        if not (k1_snap <= k2_cand <= k3_snap <= k4_snap):
            continue

        cost_usd = _compute_cost_usd(
            forward=forward,
            put_by_k=put_by_k,
            call_by_k=call_by_k,
            k1=k1_snap,
            k2=k2_cand,
            k3=k3_snap,
            k4=k4_snap,
            long_k1=long_k1,
            long_k2=long_k2,
            long_k3=long_k3,
            long_k4=long_k4,
            use_k1=True,
            use_k2=True,
            use_k3=True,
            use_k4=True,
        )
        left_be_pred = k2_cand - cost_usd
        right_be_pred = k3_snap + cost_usd
        plateau_left_pred = (k2_cand - k1_snap) - cost_usd
        plateau_right_pred = (k4_snap - k3_snap) - cost_usd

        err = (
            abs(left_be_pred - BL)
            + abs(right_be_pred - BR)
            + abs(plateau_left_pred - L)
            + abs(plateau_right_pred - R)
        )
        if err < best_err:
            best_err = err
            best = (k1_snap, k2_cand, k3_snap, k4_snap)
            best_cost = cost_usd

    if best is None or best_cost is None:
        return None, {"valid": False, "error": "Could not find strikes satisfying ordering for these net targets."}

    k1a, k2a, k3a, k4a = best
    tmp_strategy = {
        "payoff_type": "universal_4leg",
        "k1": k1a,
        "k2": k2a,
        "k3": k3a,
        "k4": k4a,
        "use_k1": True,
        "use_k2": True,
        "use_k3": True,
        "use_k4": True,
        "long_k1": long_k1,
        "long_k2": long_k2,
        "long_k3": long_k3,
        "long_k4": long_k4,
        "cost_usd": best_cost,
    }
    payoff_tmp = strategy_payoff_at_prices(tmp_strategy, prices)
    be_list = _breakevens_from_curve(prices, payoff_tmp)

    work = {
        "valid": True,
        "raw": {"k1": k1_raw, "k2": k2a, "k3": k3a, "k4": k4_raw},
        "snap_nearest": {"k1": k1a, "k2": k2a, "k3": k3a, "k4": k4a},
        "ordered": {"k1": k1a, "k2": k2a, "k3": k3a, "k4": k4a},
        "meta": {
            "targets": {"BL": BL, "BR": BR, "PL": L, "PR": R},
            "cost_usd": best_cost,
            "breakevens_net": be_list,
        },
    }
    return (k1a, k2a, k3a, k4a), work


def derive_lab_outputs(state: dict[str, Any], market_data: dict[str, Any]) -> dict[str, Any]:
    """
    Pure derived-output function for the implied options lab.
    All visible outputs (payoff curve, stats, summary, chart overlays) should derive from this.
    """
    prices: list[float] = market_data["dist"]["prices"]
    forward: float = market_data["forward"]
    put_by_k: dict[float, float] = market_data["put_by_k"]
    call_by_k: dict[float, float] = market_data["call_by_k"]

    call_marks = market_data.get("call_marks") or []
    market_pdf_raw: list[float] = []
    if len(call_marks) >= 3:
        strikes = [m["strike"] for m in call_marks]
        call_usd = [float(m.get("mark_btc") or 0.0) * forward for m in call_marks]
        market_pdf_raw = market_implied_density_breeden_litzenberger(strikes, call_usd, prices)

    # Determine strikes based on mode ownership.
    solve_work: dict[str, Any] | None = None
    if state["mode"] == "target_payoff":
        res, work = _solve_strikes_from_targets(state, market_data)
        solve_work = work
        if res is None:
            # No valid solve: return empty overlay but keep structured error in outputs.
            market_pct: list[float] = []
            anomalous = False
            if market_pdf_raw:
                max_mkt = max(market_pdf_raw) if market_pdf_raw else 1.0
                market_pct = [(d / max_mkt * 25.0) if max_mkt > 0 else 0.0 for d in market_pdf_raw]
                anomalous = is_anomalous(prices, market_data["dist"]["pdf_raw"], market_pdf_raw, threshold=0.015)
            belief_pack = _derive_user_belief_outputs(state, market_data, market_pdf_raw)
            return {
                "strategy": None,
                "overlay": {"prices": prices, "payoff_usd": []},
                "summary": {
                    "name": "—",
                    "cost_usd": 0.0,
                    "debit_credit": "—",
                    "max_gain": 0.0,
                    "max_loss": 0.0,
                    "breakevens": [],
                    "error": work.get("error") if isinstance(work, dict) else "Invalid targets.",
                },
                "chart_helpers": {
                    "market_pdf_raw": market_pdf_raw,
                    "market_pct": market_pct,
                    "anomalous": anomalous,
                    **belief_pack["chart_helpers_extra"],
                },
                "belief_summary": belief_pack["belief_summary"],
                "solve_work": solve_work,
            }
        k1, k2, k3, k4 = res
    else:
        k1, k2, k3, k4 = (
            float(state["strikes_exact"]["k1"]),
            float(state["strikes_exact"]["k2"]),
            float(state["strikes_exact"]["k3"]),
            float(state["strikes_exact"]["k4"]),
        )

    qty = int(state["qty"])
    le = state["legs_enabled"]
    pol = state["polarity"]

    # Compute cost and name.
    cost_usd = _compute_cost_usd(
        forward=forward,
        put_by_k=put_by_k,
        call_by_k=call_by_k,
        k1=k1,
        k2=k2,
        k3=k3,
        k4=k4,
        long_k1=pol["long_k1"],
        long_k2=pol["long_k2"],
        long_k3=pol["long_k3"],
        long_k4=pol["long_k4"],
        use_k1=le["use_k1"],
        use_k2=le["use_k2"],
        use_k3=le["use_k3"],
        use_k4=le["use_k4"],
    )
    k1_for_name = k2 if not le["use_k1"] else k1
    k4_for_name = k3 if not le["use_k4"] else k4
    name = name_universal_strategy(
        k1_for_name,
        k2,
        k3,
        k4_for_name,
        pol["long_k1"],
        pol["long_k2"],
        pol["long_k3"],
        pol["long_k4"],
    )

    strategy = {
        "payoff_type": "universal_4leg",
        "name": name,
        "k1": k1,
        "k2": k2,
        "k3": k3,
        "k4": k4,
        "use_k1": le["use_k1"],
        "use_k2": le["use_k2"],
        "use_k3": le["use_k3"],
        "use_k4": le["use_k4"],
        "long_k1": pol["long_k1"],
        "long_k2": pol["long_k2"],
        "long_k3": pol["long_k3"],
        "long_k4": pol["long_k4"],
        "qty": qty,
        "cost_usd": cost_usd,
        "legs_desc": f"K1 ${k1:,.0f} · K2 ${k2:,.0f} · K3 ${k3:,.0f} · K4 ${k4:,.0f}",
    }

    payoff_1x = strategy_payoff_at_prices(strategy, prices)
    payoff_usd = [qty * float(p) for p in payoff_1x]
    max_gain = max(payoff_usd) if payoff_usd else 0.0
    max_loss = min(payoff_usd) if payoff_usd else 0.0
    breakevens = _breakevens_from_curve(prices, payoff_usd)
    debit_credit = "debit" if cost_usd >= 0 else "credit"

    market_pct: list[float] = []
    anomalous = False
    if market_pdf_raw:
        max_mkt = max(market_pdf_raw) if market_pdf_raw else 1.0
        market_pct = [(d / max_mkt * 25.0) if max_mkt > 0 else 0.0 for d in market_pdf_raw]
        anomalous = is_anomalous(prices, market_data["dist"]["pdf_raw"], market_pdf_raw, threshold=0.015)

    belief_pack = _derive_user_belief_outputs(state, market_data, market_pdf_raw)

    summary = {
        "name": name,
        "cost_usd": float(cost_usd),
        "debit_credit": debit_credit,
        "max_gain": float(max_gain),
        "max_loss": float(max_loss),
        "breakevens": breakevens,
    }

    return {
        "strategy": strategy,
        "overlay": {"prices": prices, "payoff_usd": payoff_usd},
        "summary": summary,
        "chart_helpers": {
            "market_pdf_raw": market_pdf_raw,
            "market_pct": market_pct,
            "anomalous": anomalous,
            **belief_pack["chart_helpers_extra"],
        },
        "belief_summary": belief_pack["belief_summary"],
        "solve_work": solve_work,
    }

