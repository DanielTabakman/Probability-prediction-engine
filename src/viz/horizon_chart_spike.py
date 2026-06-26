"""
Streamlit spike for Options Horizon chart payload (read-only).

Run via Streamlit only when debugging; not linked from main app nav.
"""

from __future__ import annotations

import streamlit as st

from src.viz.horizon_chart_payload import build_horizon_chart_payload


def render_horizon_chart_spike() -> None:
    st.subheader("Options Horizon — chart payload spike")
    st.caption("Simulation only. Pre-execution preview of chart JSON sections.")
    try:
        payload = build_horizon_chart_payload()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    hist = payload.get("historical") or {}
    st.write(f"Historical points: {len(hist.get('series') or [])}")
    st.write(f"Forward curve points: {len((payload.get('forward') or {}).get('curve') or [])}")
    implied = payload.get("implied") or {}
    st.write(f"Implied expiry: {implied.get('expiry_date')}")
    st.json(payload)
