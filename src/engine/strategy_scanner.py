"""
Multi-leg options strategy scanner for Phase 3.
Single universal 4-legged strategy: K1,K2 (puts), K3,K4 (calls) with polarity per leg.
"""
from __future__ import annotations

from typing import Any


def _strike_to_marks(marks: list[dict[str, Any]]) -> dict[float, float]:
    """Map strike -> mark_btc (use first if duplicate strikes)."""
    out = {}
    for m in marks:
        k = m.get("strike")
        if k is not None:
            out[float(k)] = float(m.get("mark_btc") or 0)
    return out


def name_universal_strategy(
    k1: float, k2: float, k3: float, k4: float,
    long_k1: bool, long_k2: bool, long_k3: bool, long_k4: bool,
) -> str:
    """
    Name the strategy from shape and polarity.
    Default polarity: short K1, long K2, long K3, short K4 (i.e. long_k1=False, long_k2=True, long_k3=True, long_k4=False).
    """
    # Polarity: (short, long, long, short) = classic straddle/strangle/condor
    if (long_k1, long_k2, long_k3, long_k4) != (False, True, True, False):
        # Non-default: try to label common variants
        if (long_k1, long_k2, long_k3, long_k4) == (True, False, False, True):
            if k1 == k2 and k3 == k4:
                return "Short straddle"
            if k2 < k3:
                return "Short strangle (iron condor style)"
            return "Short straddle/strangle"
        if (long_k1, long_k2, long_k3, long_k4) == (True, False, True, False):
            if k2 < k3:
                return "Put spread + long call"
            return "Risk reversal (long put, short call)"
        if (long_k1, long_k2, long_k3, long_k4) == (False, True, False, True):
            if k2 < k3:
                return "Call spread + long put"
            return "Risk reversal (short put, long call)"
        return "Custom 4-leg"
    # Default polarity
    if k1 == k2 and k3 == k4:
        if k2 == k3:
            return "Straddle"
        return "Strangle"
    if k1 < k2 and k3 < k4:
        if k2 == k3:
            return "Iron butterfly"
        return "Iron condor"
    if k1 == k2 and k3 < k4:
        return "Straddle (capped right)"
    if k1 < k2 and k3 == k4:
        return "Straddle (capped left)"
    return "Strangle (capped)"


def build_universal_strategy(
    forward: float,
    marks_calls: list[dict[str, Any]],
    marks_puts: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Build the single universal 4-leg strategy for the given expiry.
    Returns one dict: k1..k4, polarity (long_k1..long_k4), cost_usd, payoff_type "universal_4leg".
    Default: K1=min, K2=K3=ATM, K4=max; polarity short/long/long/short.
    """
    call = _strike_to_marks(marks_calls)
    put = _strike_to_marks(marks_puts)
    common_strikes = sorted(set(call.keys()) & set(put.keys()))
    if len(common_strikes) < 2:
        return {
            "name": "Universal 4-leg",
            "payoff_type": "universal_4leg",
            "k1": None, "k2": None, "k3": None, "k4": None,
            "long_k1": False, "long_k2": True, "long_k3": True, "long_k4": False,
            "use_k1": True, "use_k2": True, "use_k3": True, "use_k4": True,
            "cost_usd": 0.0, "max_loss": 0.0, "max_gain": 0.0, "rr_ratio": 0.0,
            "legs_desc": "", "description": "", "strike_note": "",
        }
    atm = min(common_strikes, key=lambda k: abs(k - forward))
    k1, k2, k3, k4 = min(common_strikes), atm, atm, max(common_strikes)
    # Default polarity: short K1, long K2, long K3, short K4
    long_k1, long_k2, long_k3, long_k4 = False, True, True, False
    cost_btc = (
        (1 if long_k1 else -1) * put.get(k1, 0)
        + (1 if long_k2 else -1) * put.get(k2, 0)
        + (1 if long_k3 else -1) * call.get(k3, 0)
        + (1 if long_k4 else -1) * call.get(k4, 0)
    )
    cost_usd = cost_btc * forward
    name = name_universal_strategy(k1, k2, k3, k4, long_k1, long_k2, long_k3, long_k4)
    return {
        "name": name,
        "payoff_type": "universal_4leg",
        "k1": k1, "k2": k2, "k3": k3, "k4": k4,
        "long_k1": long_k1, "long_k2": long_k2, "long_k3": long_k3, "long_k4": long_k4,
        "use_k1": True, "use_k2": True, "use_k3": True, "use_k4": True,
        "cost_usd": cost_usd,
        "max_loss": cost_usd if cost_usd > 0 else 0.0,
        "max_gain": float("inf") if cost_usd > 0 else -cost_usd,
        "rr_ratio": 0.0,
        "legs_desc": f"K1 ${k1:,.0f} · K2 ${k2:,.0f} · K3 ${k3:,.0f} · K4 ${k4:,.0f}",
        "description": "Adjust sliders and polarity to shape payoff.",
        "strike_note": "Two bodies (K2, K3), two wings (K1, K4). Toggle polarity per leg.",
    }


def payoff_target_to_strikes(
    body_left: float,
    body_right: float,
    left_wing_payoff_usd: float,
    right_wing_payoff_usd: float,
    avail_strikes: list[float],
) -> tuple[float, float, float, float] | None:
    """
    From desired payoff shape (body range + wing payoff levels), compute K1–K4 for
    standard 4-leg (short K1 put, long K2 put, long K3 call, short K4 call).
    Left flat payoff = K2 - K1, right flat = K4 - K3. So K1 = K2 - L, K4 = K3 + R.
    Returns (k1, k2, k3, k4) snapped to avail_strikes, or None if invalid.
    """
    if not avail_strikes or body_left >= body_right:
        return None
    k2 = body_left
    k3 = body_right
    k1 = k2 - left_wing_payoff_usd
    k4 = k3 + right_wing_payoff_usd
    if k1 >= k2 or k3 >= k4:
        return None
    lo, hi = min(avail_strikes), max(avail_strikes)
    k1 = max(lo, min(hi, k1))
    k4 = max(lo, min(hi, k4))
    k1_snap = min(avail_strikes, key=lambda k: abs(k - k1))
    k2_snap = min(avail_strikes, key=lambda k: abs(k - k2))
    k3_snap = min(avail_strikes, key=lambda k: abs(k - k3))
    k4_snap = min(avail_strikes, key=lambda k: abs(k - k4))
    if not (k1_snap <= k2_snap <= k3_snap <= k4_snap):
        k2_snap = max(k2_snap, k1_snap)
        k3_snap = max(k3_snap, k2_snap)
        k4_snap = max(k4_snap, k3_snap)
    return (k1_snap, k2_snap, k3_snap, k4_snap)


def payoff_target_to_strikes_with_work(
    body_left: float,
    body_right: float,
    left_wing_payoff_usd: float,
    right_wing_payoff_usd: float,
    avail_strikes: list[float],
) -> tuple[tuple[float, float, float, float] | None, dict[str, Any]]:
    """
    Same as payoff_target_to_strikes, but also returns a structured explanation dict
    suitable for rendering a "show your work" breakdown in the UI.
    """
    work: dict[str, Any] = {
        "inputs": {
            "body_left": float(body_left),
            "body_right": float(body_right),
            "left_wing_payoff_usd": float(left_wing_payoff_usd),
            "right_wing_payoff_usd": float(right_wing_payoff_usd),
        },
        "valid": False,
    }
    if not avail_strikes:
        work["error"] = "No available strikes."
        return None, work
    if body_left >= body_right:
        work["error"] = "Invalid: body_left must be < body_right."
        return None, work
    if left_wing_payoff_usd < 0 or right_wing_payoff_usd < 0:
        work["error"] = "Invalid: wing payoff inputs must be ≥ 0."
        return None, work

    k2_raw = float(body_left)
    k3_raw = float(body_right)
    k1_raw = k2_raw - float(left_wing_payoff_usd)
    k4_raw = k3_raw + float(right_wing_payoff_usd)
    work["raw"] = {"k1": k1_raw, "k2": k2_raw, "k3": k3_raw, "k4": k4_raw}

    if k1_raw >= k2_raw or k3_raw >= k4_raw:
        work["error"] = "Invalid: must have K1 < K2 and K3 < K4 after applying wing widths."
        return None, work

    lo, hi = float(min(avail_strikes)), float(max(avail_strikes))
    k1_clamp = max(lo, min(hi, k1_raw))
    k4_clamp = max(lo, min(hi, k4_raw))
    work["clamp"] = {"lo": lo, "hi": hi, "k1": k1_clamp, "k4": k4_clamp}

    k1_snap = float(min(avail_strikes, key=lambda k: abs(k - k1_clamp)))
    k2_snap = float(min(avail_strikes, key=lambda k: abs(k - k2_raw)))
    k3_snap = float(min(avail_strikes, key=lambda k: abs(k - k3_raw)))
    k4_snap = float(min(avail_strikes, key=lambda k: abs(k - k4_clamp)))
    work["snap_nearest"] = {"k1": k1_snap, "k2": k2_snap, "k3": k3_snap, "k4": k4_snap}

    # Enforce ordering if snapping created inversions
    k2_ord = max(k2_snap, k1_snap)
    k3_ord = max(k3_snap, k2_ord)
    k4_ord = max(k4_snap, k3_ord)
    ordered = (k1_snap, k2_ord, k3_ord, k4_ord)
    work["ordered"] = {"k1": ordered[0], "k2": ordered[1], "k3": ordered[2], "k4": ordered[3]}
    work["valid"] = True
    return ordered, work


def strategy_payoff_at_prices(strategy: dict[str, Any], prices: list[float]) -> list[float]:
    """
    Payoff at expiry (USD) for the strategy at each underlying price.
    Payoff = value at expiry - cost (so net P&L). Cost is strategy['cost_usd'] (positive = debit).
    Universal 4-leg: K1,K2 puts, K3,K4 calls; polarity long_kn = True means long that leg.
    """
    cost = float(strategy.get("cost_usd") or 0)
    t = strategy.get("payoff_type")
    out = []
    if t == "universal_4leg":
        k1 = strategy.get("k1")
        k2 = strategy.get("k2")
        k3 = strategy.get("k3")
        k4 = strategy.get("k4")
        u1 = bool(strategy.get("use_k1", True))
        u2 = bool(strategy.get("use_k2", True))
        u3 = bool(strategy.get("use_k3", True))
        u4 = bool(strategy.get("use_k4", True))
        s1 = 0 if not u1 else (1 if strategy.get("long_k1", False) else -1)
        s2 = 0 if not u2 else (1 if strategy.get("long_k2", True) else -1)
        s3 = 0 if not u3 else (1 if strategy.get("long_k3", True) else -1)
        s4 = 0 if not u4 else (1 if strategy.get("long_k4", False) else -1)
        if k1 is not None and k2 is not None and k3 is not None and k4 is not None:
            for s in prices:
                p = (
                    s1 * max(0.0, k1 - s)
                    + s2 * max(0.0, k2 - s)
                    + s3 * max(0.0, s - k3)
                    + s4 * max(0.0, s - k4)
                )
                out.append(p - cost)
            return out
    for s in prices:
        out.append(-cost)
    return out
