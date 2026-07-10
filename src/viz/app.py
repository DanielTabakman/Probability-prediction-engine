"""
Streamlit dashboard: market data and prediction market probabilities.
Bitcoin view: price chart with Polymarket questions overlaid, implied value, options & futures.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Streamlit puts `src/viz` on sys.path; `src.*` imports need the repo root.
_app_root = Path(__file__).resolve().parents[2]
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from src.viz.app_env import APP_ROOT as ROOT, env_flag as _env_flag

if os.environ.get("PPE_APP_IMPORT_SMOKE") == "1":
    raise SystemExit(0)

import streamlit as st
import yaml

from src.viz.app_cache import (
    cached_polymarket as _cached_polymarket,
    cached_yahoo as _cached_yahoo,
)
from src.viz.app_market_reference import render_market_reference_sections
from src.viz.app_sidebar import build_sidebar_state
from src.viz.commercial_wrapper import commercial_surface_copy, resolve_demo_ctas
from src.viz.embed_only_lab import maybe_run_embed_only_early_exit
from src.viz.perf import PerfLog
from src.viz.prefetch import prefetch_status
from src.viz.tutorial import render_tutorial_section

PAGE_TITLE = "Probability Engine"
_snapshots_enabled = _env_flag("PPE_ENABLE_SNAPSHOTS", True)
_show_debug_ui = _env_flag("PPE_SHOW_DEBUG_UI", False)
_commercial_copy = commercial_surface_copy()
_cta_private_url, _research_offer = resolve_demo_ctas(
    snapshots_enabled=_snapshots_enabled,
    private_app_url=os.environ.get("PPE_PRIVATE_APP_URL"),
    offer_url=os.environ.get("PPE_RESEARCH_OFFER_URL"),
    offer_label=os.environ.get("PPE_RESEARCH_OFFER_LABEL"),
)

st.set_page_config(page_title=PAGE_TITLE, page_icon="📈", layout="wide")

if maybe_run_embed_only_early_exit():
    st.stop()

if _cta_private_url:
    hero_left, hero_right = st.columns([3, 1])
    with hero_left:
        st.title(PAGE_TITLE)
        st.caption(_commercial_copy.tagline)
    with hero_right:
        if hasattr(st, "link_button"):
            st.link_button(
                _commercial_copy.private_app_label,
                _cta_private_url,
                use_container_width=True,
            )
        else:
            st.markdown(f"[{_commercial_copy.private_app_label}]({_cta_private_url})")
        st.caption(_commercial_copy.private_app_caption)
    st.info(_commercial_copy.demo_banner)
    if _research_offer:
        _offer_url, _offer_label = _research_offer
        st.markdown(_commercial_copy.research_offer_blurb)
        if hasattr(st, "link_button"):
            st.link_button(_offer_label, _offer_url, use_container_width=False)
        else:
            st.markdown(f"[{_offer_label}]({_offer_url})")
else:
    st.title(PAGE_TITLE)
    st.caption(_commercial_copy.tagline)

_perf = PerfLog()
# First Streamlit run in this session: open intro expander once; later reruns stay collapsed by default.
_tutorial_expanded = "ppe_tutorial_intro_done" not in st.session_state
with st.expander("How to use this demo (~2 min)", expanded=_tutorial_expanded):
    render_tutorial_section(
        show_dev_sections=_show_debug_ui,
        show_demo_cta=bool(_cta_private_url),
    )
if "ppe_tutorial_intro_done" not in st.session_state:
    st.session_state["ppe_tutorial_intro_done"] = True

if _show_debug_ui:
    with st.expander("Debug: performance", expanded=False):
        st.caption("Wall-clock timings for the current rerun (ms).")
        st.json(
            {
                "total_ms": round(_perf.total_ms(), 1),
                **{k: round(v, 1) for k, v in _perf.timings_ms.items()},
            }
        )
        st.caption("Prefetch status (best-effort).")
        st.json(prefetch_status())

config_path = ROOT / "config" / "sources.yaml"
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {}

# --- Bitcoin symbols (spot + futures)
btc_symbols = {"bitcoin": ["BTC-USD", "BTC=F"]}
symbols_full = (config.get("markets") or {}).get("yahoo", {}).get("symbols")
if symbols_full:
    btc_symbols = {"bitcoin": symbols_full.get("bitcoin", ["BTC-USD", "BTC=F"])}

# --- Sidebar
sidebar = build_sidebar_state(show_bitcoin_default=True)
show_bitcoin_view = bool(sidebar["show_bitcoin_view"])
show_markets = bool(sidebar["show_markets"])
show_polymarket = bool(sidebar["show_polymarket"])
chart_days = int(sidebar["chart_days"])
show_forward_curve = bool(sidebar["show_forward_curve"])
show_bull_spreads = bool(sidebar["show_bull_spreads"])
show_prediction_spreads = bool(sidebar["show_prediction_spreads"])
show_options_on_chart = bool(sidebar["show_options_on_chart"])
options_in_separate_chart = bool(sidebar["options_in_separate_chart"])
option_types_on_chart = list(sidebar["option_types_on_chart"])
min_prob_label_pct = int(sidebar["min_prob_label_pct"])
implied_lab_auto_compute = bool(sidebar.get("implied_lab_auto_compute", False))

# Chart toggles (always available; optional Deribit overlays gated until Refresh priced inputs)
is_full = True

# ---------- Bitcoin section: light load first, heavy data on demand ----------
if show_bitcoin_view:
    from src.viz.app_implied_lab_view import render_implied_lab_bitcoin_section

    render_implied_lab_bitcoin_section(
        config=config,
        btc_symbols=btc_symbols,
        chart_days=chart_days,
        is_full=is_full,
        show_debug_ui=_show_debug_ui,
        snapshots_enabled=_snapshots_enabled,
        implied_lab_auto_compute=implied_lab_auto_compute,
        show_forward_curve=show_forward_curve,
        show_bull_spreads=show_bull_spreads,
        show_prediction_spreads=show_prediction_spreads,
        show_options_on_chart=show_options_on_chart,
        options_in_separate_chart=options_in_separate_chart,
        option_types_on_chart=option_types_on_chart,
        min_prob_label_pct=min_prob_label_pct,
        perf=_perf,
    )

render_market_reference_sections(
    config=config,
    show_markets=show_markets,
    show_polymarket=show_polymarket,
    cached_yahoo=_cached_yahoo,
    cached_polymarket=_cached_polymarket,
)

st.sidebar.caption("Phase 1: data ingest. Next: canonical events → probabilities → opportunities.")
# Orch-Smoke relay slice marker — pipeline validation only; no semantic/UI change.
