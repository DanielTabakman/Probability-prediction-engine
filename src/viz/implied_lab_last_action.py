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
    # Sprint002-Slice003: chart underlying-price window (shape language)
    "shape_window",
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
    shape_window_label: str | None = None,
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

    if action_id == "shape_window":
        label = (shape_window_label or "—").strip() or "—"
        return (
            f"Chart **shape window** set to **{label}** on the **underlying price (USD)** axis "
            "(how much of the distribution you see; **same priced inputs**)."
        )

    # Defensive fallback (should be unreachable due to Literal typing).
    return "Updated strategy settings."


def shape_window_local_region_story(
    *,
    zoom_choice: str,
    xr0: float,
    xr1: float,
    forward: float,
    belief_overlay_enabled: bool,
    verification: dict[str, Any] | None,
) -> tuple[str, str]:
    """
    Sprint002-Slice004: one compact descriptive read for the active chart **shape window**.

    Reuses verification glance fields only (no new engine metrics). Returns
    ``(markdown_for_chart_column, plain_text_for_shape_strip)``. Strip text is
    empty when there is no narrowed-window story to echo in the strip.
    """
    z = (zoom_choice or "").strip()
    if z == "Full range":
        chart = (
            "**Shape window:** full **underlying-price** span on this chart (no narrowed band). "
            "Pick a non–**Full range** **shape window** above to see a short **local band** readout here — **same priced inputs**."
        )
        return chart, ""

    lo = float(xr0)
    hi = float(xr1)
    if hi <= lo:
        return (
            "**Shape window:** chart range is invalid or empty — reset to **Full range** if this persists.",
        ), ""

    band = f"{_fmt_usd(lo)}–{_fmt_usd(hi)}"
    v = verification if isinstance(verification, dict) else {}
    g_raw = v.get("belief_vs_market_glance")
    g = g_raw if isinstance(g_raw, dict) else None

    if z == "Lower prices":
        band_meaning = (
            "You chose **Lower prices** — this **shape window** emphasizes **lower** **underlying price (USD)** "
            "levels on the **same** priced curves."
        )
    elif z == "Near forward":
        band_meaning = (
            f"You chose **Near forward** — this **shape window** centers the axis **around the forward** "
            f"({_fmt_usd(forward)}) on the **same** priced curves."
        )
    elif z == "Higher prices":
        band_meaning = (
            "You chose **Higher prices** — this **shape window** emphasizes **higher** **underlying price (USD)** "
            "levels on the **same** priced curves."
        )
    else:
        band_meaning = f"**Shape window:** **{z}** — the chart axis is narrowed on **underlying price (USD)**."

    curves = (
        f"In this band (**{band}**), the chart **shows** the **reference** curve (purple fill) and the "
        "**market-implied** curve (orange) on that slice of the axis — **same priced inputs**; descriptive only, not a recommendation."
    )

    glance = ""
    if belief_overlay_enabled:
        glance = (
            " With **My belief** on (green), **Belief vs market — at a glance** below reads on the **same underlying-price axis**."
        )
        if g is not None and g.get("largest_gap_price_usd") is not None:
            try:
                gx = float(g["largest_gap_price_usd"])
            except Exception:
                gx = None
            if gx is not None and lo <= gx <= hi:
                gap_txt = str(g.get("largest_gap_display") or "").strip() or _fmt_usd(gx)
                glance += (
                    f" The digest’s largest **|ΔPDF|** sample on the grid (**{gap_txt}**) **lies inside this shape window** "
                    "(a mismatch descriptor, not a recommendation)."
                )

    chart = f"{band_meaning} {curves}{glance}"
    plain = (
        chart.replace("**", "")
        .replace("  ", " ")
        .strip()
    )
    if len(plain) > 240:
        plain = plain[:237] + "…"
    return chart, plain

