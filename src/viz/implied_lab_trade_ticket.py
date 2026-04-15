"""
FS-007: copy-paste trade ticket text (pure; safe to import without Streamlit).

Kept separate from `app.py` so unit tests do not execute the full dashboard import graph.
"""

from __future__ import annotations


def implied_lab_trade_ticket_code_text(
    *,
    selected_expiry_str: str,
    qty: int,
    forward: float,
    selected_strategy: dict,
    put_by_k: dict,
    call_by_k: dict,
    summary: dict,
) -> tuple[str, tuple[float, float, float, float], tuple[str, str, str, str]]:
    """
    Deterministic copy-paste ticket body plus per-leg premia (for Show calculations).

    Returns (ticket_text, (prem_k1..4), (side_put1, side_put2, side_call3, side_call4)).
    """
    cost = float(summary.get("cost_usd") or 0.0)
    max_gain = float(summary.get("max_gain") or 0.0)
    max_loss = float(summary.get("max_loss") or 0.0)
    breakevens = summary.get("breakevens") or []

    side_put1 = "Long" if selected_strategy.get("long_k1", False) else "Short"
    side_put2 = "Long" if selected_strategy.get("long_k2", True) else "Short"
    side_call3 = "Long" if selected_strategy.get("long_k3", True) else "Short"
    side_call4 = "Long" if selected_strategy.get("long_k4", False) else "Short"
    k1 = selected_strategy.get("k1")
    k2 = selected_strategy.get("k2")
    k3 = selected_strategy.get("k3")
    k4 = selected_strategy.get("k4")
    prem_k1 = put_by_k.get(k1, 0.0) * forward if k1 is not None else 0.0
    prem_k2 = put_by_k.get(k2, 0.0) * forward if k2 is not None else 0.0
    prem_k3 = call_by_k.get(k3, 0.0) * forward if k3 is not None else 0.0
    prem_k4 = call_by_k.get(k4, 0.0) * forward if k4 is not None else 0.0

    ticket_text = (
        f"Expiry: {selected_expiry_str}\n"
        f"Size: {qty}x\n"
        f"{side_put1} {qty} PUT @ {k1:,.0f}  (≈ {prem_k1:,.0f} USD per 1x)\n"
        f"{side_put2} {qty} PUT @ {k2:,.0f}  (≈ {prem_k2:,.0f} USD per 1x)\n"
        f"{side_call3} {qty} CALL @ {k3:,.0f} (≈ {prem_k3:,.0f} USD per 1x)\n"
        f"{side_call4} {qty} CALL @ {k4:,.0f} (≈ {prem_k4:,.0f} USD per 1x)\n"
        f"Net premium: {cost:,.0f} USD ({'debit' if cost >= 0 else 'credit'})\n"
        f"Max gain (approx): {max_gain:,.0f} USD\n"
        f"Max loss (approx): {max_loss:,.0f} USD\n"
        + (
            f"Breakevens: {', '.join(f'{be:,.0f}' for be in breakevens[:3])} USD\n"
            if breakevens
            else ""
        )
    )
    return ticket_text, (prem_k1, prem_k2, prem_k3, prem_k4), (side_put1, side_put2, side_call3, side_call4)
