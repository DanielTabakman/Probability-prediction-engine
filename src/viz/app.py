"""
Streamlit dashboard entry (thin shell).

Bitcoin implied lab layout: src/viz/app_bitcoin_implied_lab.py
See docs/SOP/VIZ_LAYER_DISCIPLINE_V1.md
"""
from __future__ import annotations

import sys
from pathlib import Path

# Streamlit puts `src/viz` on sys.path; `src.*` imports need the repo root.
_app_root = Path(__file__).resolve().parents[2]
if str(_app_root) not in sys.path:
    sys.path.insert(0, str(_app_root))

from src.viz.app_env import APP_ROOT as ROOT

import streamlit as st
import yaml

from src.viz.app_bitcoin_implied_lab import render_bitcoin_implied_lab_page
from src.viz.app_cache import cached_polymarket as _cached_polymarket, cached_yahoo as _cached_yahoo
from src.viz.app_market_reference import render_market_reference_sections
from src.viz.app_shell import render_app_shell
from src.viz.app_sidebar import build_sidebar_state

_perf, _show_debug_ui = render_app_shell()

config_path = ROOT / "config" / "sources.yaml"
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
else:
    config = {}

btc_symbols = {"bitcoin": ["BTC-USD", "BTC=F"]}
symbols_full = (config.get("markets") or {}).get("yahoo", {}).get("symbols")
if symbols_full:
    btc_symbols = {"bitcoin": symbols_full.get("bitcoin", ["BTC-USD", "BTC=F"])}

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

is_full = True

if show_bitcoin_view:
    render_bitcoin_implied_lab_page(
        root=ROOT,
        config=config,
        btc_symbols=btc_symbols,
        chart_days=chart_days,
        show_forward_curve=show_forward_curve,
        show_bull_spreads=show_bull_spreads,
        show_prediction_spreads=show_prediction_spreads,
        show_options_on_chart=show_options_on_chart,
        options_in_separate_chart=options_in_separate_chart,
        option_types_on_chart=option_types_on_chart,
        min_prob_label_pct=min_prob_label_pct,
        implied_lab_auto_compute=implied_lab_auto_compute,
        perf=_perf,
        show_debug_ui=_show_debug_ui,
        is_full=is_full,
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
