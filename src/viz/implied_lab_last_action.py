from __future__ import annotations

from typing import Any, Iterable, Literal

LastActionId = Literal[
    "mode_switch",
    "quantity",
    "polarity_reverse",
    "leg_toggle",
    "strike_edit",
    # Sprint 001 — Slice 010 (Phase 2): belief + target-payoff interactions
    "belief_toggle",
    "belief_center",
    "belief_width",
    "net_pnl_mode_toggle",
    "target_payoff_edit",
]


def _fmt_usd(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "—"
    if abs(v) >= 1000:
        return f"${v:,.0f}"
    return f"${v:.2f}"


def _fmt_legs(enabled: Iterable[str]) -> str:
    legs = [str(x).upper() for x in enabled if str(x).strip()]
    return ", ".join(legs) if legs else "—"


def last_action_meaning(
    *,
    action_id: LastActionId,
    mode_label: str | None = None,
    qty: int | None = None,
    reverse: bool | None = None,
    leg: str | None = None,
    leg_enabled: bool | None = None,
    strikes: dict[str, float] | None = None,
    belief_enabled: bool | None = None,
    belief_center_usd: float | None = None,
    belief_width_sigma_ln: float | None = None,
    net_pnl_mode: bool | None = None,
    target_id: str | None = None,
    target_value: float | None = None,
) -> str:
    """
    Sprint 001 — Slice 007 (Phase 2): "Last action" meaning for non-preset interactions.

    Plain-English, contract-safe: descriptive only.
    """
    if action_id == "mode_switch":
        mode = (mode_label or "—").strip() or "—"
        return f"Mode changed to **{mode}**."

    if action_id == "quantity":
        q = int(qty) if isinstance(qty, int) else qty
        return f"Quantity set to **{q}** (scales payoff height)."

    if action_id == "polarity_reverse":
        if reverse is None:
            return "Polarity updated (long/short flipped)."
        return (
            "Polarity reversed (long/short flipped)."
            if bool(reverse)
            else "Polarity set to normal (base long/short)."
        )

    if action_id == "leg_toggle":
        lg = (leg or "").upper().strip() or "—"
        if leg_enabled is None:
            return f"Leg {lg} updated (enabled/disabled)."
        return f"Leg {lg} {'enabled' if bool(leg_enabled) else 'disabled'}."

    if action_id == "strike_edit":
        s = strikes or {}
        k1 = _fmt_usd(s.get("k1"))
        k2 = _fmt_usd(s.get("k2"))
        k3 = _fmt_usd(s.get("k3"))
        k4 = _fmt_usd(s.get("k4"))
        return f"Strikes updated: K1 {k1} · K2 {k2} · K3 {k3} · K4 {k4}."

    if action_id == "belief_toggle":
        if belief_enabled is None:
            return "Belief curve display updated (shown/hidden)."
        return (
            "Belief curve shown (overlay enabled)."
            if bool(belief_enabled)
            else "Belief curve hidden (overlay disabled)."
        )

    if action_id == "belief_center":
        return f"Belief peak updated: **{_fmt_usd(belief_center_usd)}**."

    if action_id == "belief_width":
        try:
            v = float(belief_width_sigma_ln) if belief_width_sigma_ln is not None else None
        except Exception:
            v = None
        if v is None:
            return "Belief uncertainty updated."
        return f"Belief uncertainty updated: σ_ln = **{v:.4f}**."

    if action_id == "net_pnl_mode_toggle":
        if net_pnl_mode is None:
            return "Net P&L mode updated (cost-aware on/off)."
        return (
            "Net P&L mode enabled (cost-aware targets)."
            if bool(net_pnl_mode)
            else "Net P&L mode disabled (intrinsic shape targets)."
        )

    if action_id == "target_payoff_edit":
        tid = (target_id or "").strip() or "target"
        tv = target_value
        if tv is None:
            return f"Target-payoff input updated: **{tid}**."
        # All current targets are in USD terms.
        return f"Target-payoff input updated: **{tid}** = **{_fmt_usd(tv)}**."

    # Defensive fallback (should be unreachable due to Literal typing).
    return "Updated strategy settings."

