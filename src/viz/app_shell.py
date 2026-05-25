"""
Global Streamlit shell: page config, hero/CTA, tutorial, debug perf panel.

See docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md (L0).
"""

from __future__ import annotations

import os

import streamlit as st

from src.viz.app_env import env_flag as _env_flag
from src.viz.perf import PerfLog
from src.viz.prefetch import prefetch_status
from src.viz.signup_cta import private_app_cta_url, research_offer_cta
from src.viz.tutorial import render_tutorial_section

PAGE_TITLE = "Probability Engine"
_APP_TAGLINE = (
    "Market-implied distributions and prediction markets — exploration, not advice."
)


def render_app_shell() -> tuple[PerfLog, bool]:
    """Render L0 shell UI; return perf logger and debug flag for downstream pages."""
    snapshots_enabled = _env_flag("PPE_ENABLE_SNAPSHOTS", True)
    show_debug_ui = _env_flag("PPE_SHOW_DEBUG_UI", False)
    cta_private_url = private_app_cta_url(
        snapshots_enabled=snapshots_enabled,
        private_app_url=os.environ.get("PPE_PRIVATE_APP_URL"),
    )
    research_offer = research_offer_cta(
        snapshots_enabled=snapshots_enabled,
        offer_url=os.environ.get("PPE_RESEARCH_OFFER_URL"),
        offer_label=os.environ.get("PPE_RESEARCH_OFFER_LABEL"),
    )

    st.set_page_config(page_title=PAGE_TITLE, page_icon="📈", layout="wide")

    if cta_private_url:
        hero_left, hero_right = st.columns([3, 1])
        with hero_left:
            st.title(PAGE_TITLE)
            st.caption(_APP_TAGLINE)
        with hero_right:
            if hasattr(st, "link_button"):
                st.link_button(
                    "Get full access",
                    cta_private_url,
                    use_container_width=True,
                )
            else:
                st.markdown(f"[Get full access]({cta_private_url})")
            st.caption("Sign in on the full app to save snapshots and reviews.")
        st.info(
            "**Public demo:** no saved snapshot history here. "
            "**Get full access** opens the full app with saves and reviews."
        )
        if research_offer:
            offer_url, offer_label = research_offer
            st.markdown(
                "**Research beta (v0):** BTC options market-structure readouts and anomaly inspection — "
                "decision support only, not investment advice or guaranteed returns."
            )
            if hasattr(st, "link_button"):
                st.link_button(offer_label, offer_url, use_container_width=False)
            else:
                st.markdown(f"[{offer_label}]({offer_url})")
    else:
        st.title(PAGE_TITLE)
        st.caption(_APP_TAGLINE)

    perf = PerfLog()
    tutorial_expanded = "ppe_tutorial_intro_done" not in st.session_state
    with st.expander("How to use this demo (~2 min)", expanded=tutorial_expanded):
        render_tutorial_section(
            show_dev_sections=show_debug_ui,
            show_demo_cta=bool(cta_private_url),
        )
    if "ppe_tutorial_intro_done" not in st.session_state:
        st.session_state["ppe_tutorial_intro_done"] = True

    if show_debug_ui:
        with st.expander("Debug: performance", expanded=False):
            st.caption("Wall-clock timings for the current rerun (ms).")
            st.json(
                {
                    "total_ms": round(perf.total_ms(), 1),
                    **{k: round(v, 1) for k, v in perf.timings_ms.items()},
                }
            )
            st.caption("Prefetch status (best-effort).")
            st.json(prefetch_status())

    return perf, show_debug_ui
