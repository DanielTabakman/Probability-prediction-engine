from __future__ import annotations

from typing import Any


def build_implied_lab_state(
    *,
    expiry_str: str,
    mode: str,
    qty: int,
    strikes_exact: dict[str, float],
    payoff_targets: dict[str, float],
    legs_enabled: dict[str, bool],
    reverse: bool,
    net_pnl_mode: bool,
    user_belief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Centralized user-controlled state for the implied options lab screen.
    Market data is intentionally excluded (passed separately as market_data).
    """
    base = (False, True, True, False)  # short K1, long K2, long K3, short K4
    if not reverse:
        long_k1, long_k2, long_k3, long_k4 = base
    else:
        long_k1, long_k2, long_k3, long_k4 = (not b for b in base)
        long_k1, long_k2, long_k3, long_k4 = bool(long_k1), bool(long_k2), bool(long_k3), bool(long_k4)

    ub = user_belief if isinstance(user_belief, dict) else {}

    return {
        "expiry_str": expiry_str,
        "shape_key": f"u4_shape_{expiry_str}",
        "mode": mode,
        "net_pnl_mode": bool(net_pnl_mode),
        "qty": int(qty),
        "strikes_exact": {
            "k1": float(strikes_exact["k1"]),
            "k2": float(strikes_exact["k2"]),
            "k3": float(strikes_exact["k3"]),
            "k4": float(strikes_exact["k4"]),
        },
        "payoff_targets": {
            "body_left": float(payoff_targets["body_left"]),
            "body_right": float(payoff_targets["body_right"]),
            "left_wing": float(payoff_targets["left_wing"]),
            "right_wing": float(payoff_targets["right_wing"]),
        },
        "legs_enabled": {
            "use_k1": bool(legs_enabled["use_k1"]),
            "use_k2": bool(legs_enabled["use_k2"]),
            "use_k3": bool(legs_enabled["use_k3"]),
            "use_k4": bool(legs_enabled["use_k4"]),
        },
        "reverse": bool(reverse),
        "polarity": {
            "long_k1": bool(long_k1),
            "long_k2": bool(long_k2),
            "long_k3": bool(long_k3),
            "long_k4": bool(long_k4),
        },
        "user_belief": {
            "enabled": bool(ub.get("enabled", False)),
            "center_usd": float(ub.get("center_usd") or 0.0),
            "width": float(ub.get("width") or 0.0),
        },
    }

