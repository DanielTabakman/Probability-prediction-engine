"""Plotly layout defaults aligned with Streamlit dark theme (.streamlit/config.toml)."""

from __future__ import annotations

import plotly.graph_objects as go

PLOTLY_TEMPLATE = "plotly_dark"


def apply_chart_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(template=PLOTLY_TEMPLATE)
    return fig
