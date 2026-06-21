"""Chromeless Streamlit surface for Strategy Lab distribution embed."""

from __future__ import annotations

import json
from typing import Any

import plotly.graph_objects as go
import streamlit as st

from src.viz.app_cache import (
    CACHE_TTL,
    cached_deribit_index,
    cached_forward_iv,
    cached_marks_full,
    cached_option_expiries,
)
from src.viz.distribution_export import build_distribution_export_rows
from src.viz.distribution_summary_panel import render_distribution_summary_panel
from src.viz.embed_display_boundary import (
    EMBED_JSON_QUERY_PARAM,
    EMBED_JSON_QUERY_VALUE,
    EMBED_ONLY_QUERY_PARAM,
    build_distribution_display_payload,
    serialize_distribution_display_payload,
)
from src.viz.implied_lab_legibility import TRACE_MODEL_BELL, YAXIS_DENSITY_TITLE
from src.viz.plotly_theme import apply_chart_theme

_EMBED_ONLY_CSS = """
<style>
[data-testid="stSidebar"] {display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
header[data-testid="stHeader"] {visibility: hidden; height: 0;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
.block-container {padding-top: 1rem;}
</style>
"""


def _query_flag(name: str, *values: str) -> bool:
    raw = st.query_params.get(name)
    if raw is None:
        return False
    if isinstance(raw, list):
        text = (raw[0] if raw else "") or ""
    else:
        text = str(raw)
    text = text.strip().lower()
    if not values:
        return text in ("1", "true", "yes", "on")
    return text in {v.lower() for v in values}


def embed_only_requested() -> bool:
    from src.viz.app_env import env_flag

    return env_flag("PPE_EMBED_ONLY", False) or _query_flag(EMBED_ONLY_QUERY_PARAM)


def json_payload_requested() -> bool:
    return _query_flag(EMBED_JSON_QUERY_PARAM, EMBED_JSON_QUERY_VALUE)


def _spot_from_cached_deribit_index() -> float:
    """``cached_deribit_index`` returns ``float | None`` (not a ticker dict)."""
    index = cached_deribit_index()
    if index is None:
        return 0.0
    if isinstance(index, (int, float)):
        return float(index)
    if isinstance(index, dict):
        raw = index.get("index") or index.get("price") or index.get("index_price")
        if raw is not None:
            return float(raw)
    return 0.0


def _load_export_rows() -> tuple[str, float, list[dict[str, str]]]:
    import pandas as pd

    spot = _spot_from_cached_deribit_index()
    if spot <= 0:
        raise RuntimeError("Deribit BTC index unavailable for embed display boundary.")
    expiries, _diag = cached_option_expiries(10)
    if not expiries:
        raise RuntimeError("No option expiries available for embed display boundary.")
    run_ts = pd.Timestamp.now(tz="UTC")
    as_of_utc = run_ts.isoformat()
    now_ms = run_ts.timestamp() * 1000
    rows = build_distribution_export_rows(
        as_of_utc=as_of_utc,
        spot_usd=spot,
        expiries=expiries,
        forward_iv_fn=cached_forward_iv,
        marks_full_fn=cached_marks_full,
        now_ms=now_ms,
    )
    return as_of_utc, spot, rows


def build_distribution_chart_figure(series: dict[str, Any]) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=series["prices_usd"],
            y=series["pdf_pct"],
            mode="lines",
            name=TRACE_MODEL_BELL,
            line=dict(color="rgba(138, 43, 226, 0.9)", width=2),
            fill="tozeroy",
        )
    )
    expiry = series.get("expiry_date") or "expiry"
    fig.update_layout(
        title=f"BTC — Underlying price on {expiry}",
        xaxis_title="Underlying price (USD)",
        yaxis_title=YAXIS_DENSITY_TITLE,
        height=320,
        margin=dict(b=40),
        showlegend=True,
        xaxis=dict(tickformat=",d", gridcolor="rgba(128,128,128,0.2)"),
        yaxis=dict(ticksuffix="%", range=[0, 30], gridcolor="rgba(128,128,128,0.2)"),
    )
    apply_chart_theme(fig)
    return fig


def render_embed_only_distribution(
    *,
    as_of_utc: str,
    spot_usd: float,
    export_rows: list[dict[str, str]],
) -> None:
    """Minimal distribution summary + chart (no sidebar, no MSOS chrome duplication)."""
    st.markdown(_EMBED_ONLY_CSS, unsafe_allow_html=True)
    payload = build_distribution_display_payload(
        as_of_utc=as_of_utc,
        spot_usd=spot_usd,
        export_rows=export_rows,
    )
    if json_payload_requested():
        st.markdown(
            f'<script type="application/json" id="ppe-display-payload">'
            f"{serialize_distribution_display_payload(payload)}"
            f"</script>",
            unsafe_allow_html=True,
        )
        st.json(payload)
        return

    st.caption(f"As of {as_of_utc} · Spot ${spot_usd:,.0f} · quote cache TTL {CACHE_TTL}s")
    render_distribution_summary_panel(export_rows)
    series_list = payload.get("series_by_expiry") or []
    if not series_list:
        st.info("Distribution curve unavailable — summary table only.")
        return
    primary = series_list[0]
    st.plotly_chart(build_distribution_chart_figure(primary), use_container_width=True)


def run_embed_only_lab_page() -> None:
    try:
        as_of_utc, spot, export_rows = _load_export_rows()
    except RuntimeError as exc:
        st.error(str(exc))
        return
    render_embed_only_distribution(
        as_of_utc=as_of_utc,
        spot_usd=spot,
        export_rows=export_rows,
    )


def maybe_run_embed_only_early_exit() -> bool:
    """When ``?embed_only=1`` on full app entry, render chromeless view and stop."""
    if not embed_only_requested():
        return False
    run_embed_only_lab_page()
    return True
