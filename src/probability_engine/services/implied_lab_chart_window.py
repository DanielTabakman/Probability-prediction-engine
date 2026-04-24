from __future__ import annotations

from typing import Any


def _fmt_usd(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "—"
    if abs(v) >= 1000:
        return f"${v:,.0f}"
    return f"${v:.2f}"


def shape_focus_x_range(
    choice: str,
    price_min: float,
    price_max: float,
    forward: float,
) -> tuple[float, float]:
    """Map UI labels to chart x-axis window (descriptive navigation only)."""
    lo, hi = float(price_min), float(price_max)
    fw = float(forward)
    if hi <= lo:
        return lo, hi
    if choice == "Lower prices":
        upper = min(hi, fw * 1.1)
        return lo, max(lo + 1.0, upper)
    if choice == "Near forward":
        a = max(lo, fw * 0.82)
        b = min(hi, fw * 1.18)
        if b <= a + 1.0:
            return lo, hi
        return a, b
    if choice == "Higher prices":
        lower = max(lo, fw * 0.9)
        return lower, hi
    # "Full range" and any unknown value
    return lo, hi


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
    One compact descriptive read for the active chart **shape window**.

    Returns ``(markdown_for_chart_column, plain_text_for_shape_strip)``.
    Strip text is empty when there is no narrowed-window story to echo in the strip.
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
    plain = chart.replace("**", "").replace("  ", " ").strip()
    if len(plain) > 240:
        plain = plain[:237] + "…"
    return chart, plain

