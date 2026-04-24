from __future__ import annotations

from typing import Any

from src.probability_engine.services.implied_lab_derive import derive_lab_outputs
from src.probability_engine.services.implied_lab_state import build_implied_lab_state


def run_implied_lab(
    *,
    expiry_str: str,
    mode: str,
    qty: int,
    strikes_exact: dict[str, float],
    payoff_targets: dict[str, float],
    legs_enabled: dict[str, bool],
    reverse: bool,
    net_pnl_mode: bool,
    user_belief: dict[str, Any] | None,
    market_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Service runner for implied-lab: compose user-controlled state + market_data into UI-ready outputs.

    Contract:
    - Returns the same `outputs` dict shape previously produced by `derive_lab_outputs(...)`.
    - Streamlit-free (UI owns widget keys and session_state).
    """
    state = build_implied_lab_state(
        expiry_str=expiry_str,
        mode=mode,
        qty=qty,
        strikes_exact=strikes_exact,
        payoff_targets=payoff_targets,
        legs_enabled=legs_enabled,
        reverse=reverse,
        net_pnl_mode=net_pnl_mode,
        user_belief=user_belief,
    )
    return derive_lab_outputs(state, market_data)

