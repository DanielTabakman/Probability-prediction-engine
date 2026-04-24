from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import plotly.graph_objects as go

from src.probability_engine.services.implied_lab_chart_window import (
    shape_focus_x_range as _shape_focus_x_range,
    shape_window_local_region_story,
)


@dataclass(frozen=True)
class ImpliedLabChartBundle:
    fig: go.Figure
    xr0: float
    xr1: float
    local_story_md: str
    local_story_strip: str
    forward_caption: str
    belief_block_markdown: str
    anomalous: bool


def build_implied_lab_distribution_chart_bundle(
    *,
    selected_expiry_str: str,
    dist_data: dict[str, Any],
    outputs: dict[str, Any],
    forward: float,
    vol: float,
    T_years: float,
    price_min: float,
    price_max: float,
    zoom_choice: str,
    user_belief_for_state: dict[str, Any],
) -> ImpliedLabChartBundle:
    """
    Build the Plotly figure + derived captions/strings for the implied-lab anchor chart.

    Streamlit stays in the UI layer; this returns pure render inputs.
    """
    data = dist_data
    ch = outputs.get("chart_helpers") or {}
    anomalous = bool(ch.get("anomalous", False))

    fig_dist = go.Figure()
    fig_dist.add_trace(
        go.Scatter(
            x=data["prices"],
            y=data["pdf_pct"],
            mode="lines",
            name="Lognormal (forward + IV)",
            line=dict(color="rgba(138, 43, 226, 0.9)", width=2),
            fill="tozeroy",
        )
    )
    market_pct = ch.get("market_pct") or []
    if market_pct and len(market_pct) == len(data["prices"]):
        fig_dist.add_trace(
            go.Scatter(
                x=data["prices"],
                y=market_pct,
                mode="lines",
                name="Market-implied pricing distribution (options)",
                line=dict(color="rgba(255, 140, 0, 0.9)", width=2, dash="dash"),
            )
        )
    user_belief_pct = ch.get("user_belief_pct") or []
    if user_belief_pct and len(user_belief_pct) == len(data["prices"]):
        fig_dist.add_trace(
            go.Scatter(
                x=data["prices"],
                y=user_belief_pct,
                mode="lines",
                name="My belief",
                line=dict(color="rgba(0, 160, 160, 0.95)", width=2, dash="dot"),
            )
        )

    title = f"BTC — Underlying price on {selected_expiry_str}"
    if anomalous:
        title += " — Anomalous"

    payoff_usd = (outputs.get("overlay") or {}).get("payoff_usd") or []
    strategy = outputs.get("strategy") or {}
    if strategy and strategy.get("k1") is not None and payoff_usd:
        fig_dist.add_trace(
            go.Scatter(
                x=data["prices"],
                y=payoff_usd,
                mode="lines",
                name=f"Payoff: {strategy.get('name', 'Universal 4-leg')}",
                line=dict(color="rgba(34, 139, 34, 0.9)", width=2),
                yaxis="y2",
            )
        )

    layout_kw: dict[str, Any] = {
        "title": title,
        "xaxis_title": "Underlying price (USD)",
        "yaxis_title": "Probability (scaled)",
        "height": 340,
        "margin": dict(b=40),
        "showlegend": True,
        "xaxis": dict(tickformat=",d", gridcolor="rgba(128,128,128,0.2)"),
        "yaxis": dict(ticksuffix="%", range=[0, 30], gridcolor="rgba(128,128,128,0.2)"),
    }
    if strategy and strategy.get("k1") is not None:
        layout_kw["yaxis2"] = dict(
            title="Strategy P&L (USD)",
            overlaying="y",
            side="right",
            showgrid=False,
        )
    fig_dist.update_layout(**layout_kw)

    xr0, xr1 = _shape_focus_x_range(
        str(zoom_choice), float(price_min), float(price_max), float(forward)
    )
    local_story_md, local_story_strip = shape_window_local_region_story(
        zoom_choice=str(zoom_choice),
        xr0=float(xr0),
        xr1=float(xr1),
        forward=float(forward),
        belief_overlay_enabled=bool(user_belief_for_state.get("enabled")),
        verification=outputs.get("verification") if isinstance(outputs.get("verification"), dict) else None,
    )
    fig_dist.update_xaxes(range=[float(xr0), float(xr1)])

    gap_x = ch.get("belief_largest_gap_price")
    if (
        user_belief_for_state.get("enabled")
        and gap_x is not None
        and isinstance(gap_x, (int, float))
    ):
        fig_dist.add_shape(
            type="line",
            xref="x",
            yref="paper",
            x0=float(gap_x),
            x1=float(gap_x),
            y0=0,
            y1=1,
            line=dict(color="rgba(110, 110, 110, 0.5)", width=1, dash="dash"),
            layer="below",
        )

    for price, cdf_pct in data["cumulative_at"]:
        fig_dist.add_annotation(
            x=price,
            y=-0.06,
            text=f"{cdf_pct:.1f}%",
            showarrow=False,
            yref="paper",
            font=dict(size=9),
        )

    forward_caption = f"Forward ${forward:,.0f} · ATM IV {vol*100:.1f}% · T = {T_years:.2f} yr"
    disagreement = ch.get("belief_disagreement_strength")
    if user_belief_for_state.get("enabled") and disagreement:
        forward_caption += f" · Belief disagreement: **{disagreement}**"

    belief_summary = outputs.get("belief_summary") or {}
    belief_txt = belief_summary.get("text") or ""
    belief_hints = belief_summary.get("hints_markdown") or ""
    belief_block = ""
    if belief_txt or belief_hints:
        belief_block = str(belief_txt)
        if belief_hints:
            belief_block += (("\n\n" if belief_txt else "") + str(belief_hints))

    return ImpliedLabChartBundle(
        fig=fig_dist,
        xr0=float(xr0),
        xr1=float(xr1),
        local_story_md=str(local_story_md),
        local_story_strip=str(local_story_strip or ""),
        forward_caption=str(forward_caption),
        belief_block_markdown=str(belief_block),
        anomalous=bool(anomalous),
    )

