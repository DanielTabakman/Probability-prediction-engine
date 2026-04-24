"""
Streamlit dashboard: market data and prediction market probabilities.
Bitcoin view: price chart with Polymarket questions overlaid, implied value, options & futures.
"""
from __future__ import annotations

import traceback
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parents[2]

import streamlit as st
import pandas as pd

from src.viz.app_cache import (
    CACHE_TTL,
    CACHE_TTL_OPTION_EXPIRIES,
    cached_btc_options_summary as _cached_btc_options_summary,
    cached_bull_spreads as _cached_bull_spreads,
    cached_deribit_index as _cached_deribit_index,
    cached_deribit_summary as _cached_deribit_summary,
    cached_forward_curve as _cached_forward_curve,
    cached_forward_iv as _cached_forward_iv,
    cached_marks_full as _cached_marks_full,
    cached_option_book_marks as _cached_option_book_marks,
    cached_option_expiries as _cached_option_expiries,
    cached_option_instruments as _cached_option_instruments,
    cached_options_for_chart as _cached_options_for_chart,
    cached_polymarket as _cached_polymarket,
    cached_yahoo as _cached_yahoo,
)
from src.engine.implied_distribution import (
    build_distribution_chart_data,
)
from src.probability_engine.services.implied_lab_fetch import fetch_implied_lab_bundle
from src.probability_engine.services.implied_lab_chart import (
    build_implied_lab_distribution_chart_bundle,
)
from src.probability_engine.services.spot_price import resolve_btc_spot_usd
from src.probability_engine.services.strikes import snap_and_order_u4_strikes
from src.engine.strategy_scanner import (
    build_universal_strategy,
    name_universal_strategy,
    payoff_target_to_strikes,
    payoff_target_to_strikes_with_work,
)
from src.probability_engine.services.implied_lab_run import run_implied_lab
from src.viz.decision_ready_review import build_decision_ready_review_payload
from src.viz.implied_lab_provenance import (
    build_trust_strip_lines,
    build_width_vol_candidate_strip_payload,
)
from src.viz.implied_lab_presets import PRESETS, compute_preset_shape, preset_what_changed
from src.viz.implied_lab_last_action import last_action_meaning
from src.viz.belief_uncertainty import (
    move_pct_1sigma_to_sigma_ln,
    sigma_ln_to_move_pct_1sigma,
)
from src.viz.app_sidebar import build_sidebar_state
from src.viz.app_panels import (
    implied_lab_trade_ticket_code_text as _implied_lab_trade_ticket_code_text,
    maybe_append_width_vol_history as _maybe_append_width_vol_history,
    render_belief_vs_market_glance as _render_belief_vs_market_glance,
    render_decision_ready_review as _render_decision_ready_review,
    render_implied_lab_summary_card as _render_implied_lab_summary_card,
    render_implied_lab_trade_ticket_panel as _render_implied_lab_trade_ticket_panel,
    render_implied_lab_verification as _render_implied_lab_verification,
    render_trust_strip as _render_trust_strip,
    render_width_vol_candidate_strip_payload as _render_width_vol_candidate_strip_payload,
    render_width_vol_history_panel as _render_width_vol_history_panel,
    shape_focus_post_interaction_hint as _shape_focus_post_interaction_hint,
)
from src.viz.app_market_context import render_market_context_expander
from src.viz.app_market_reference import render_market_reference_sections
import yaml


st.set_page_config(page_title="Probability Engine", layout="wide")
st.title("Probability Prediction Engine")

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

# Chart toggles (always available; optional Deribit overlays gated until Refresh priced inputs)
is_full = True

# ---------- Bitcoin section: light load first, heavy data on demand ----------
if show_bitcoin_view:
    st.header("Bitcoin implied lab — market-implied view as the anchor")
    st.caption(
        "**Glance path:** **Market-implied** chart (right) · **User belief** (left column) · "
        "**Disagreement digest** (*Belief vs market — at a glance*) · **Review → trade ticket** (under **Summary**). "
        "Exploration workbench — not a recommendation engine."
    )

    # Top-of-screen anchor: get a spot reference quickly (implied-lab needs this).
    current_btc = resolve_btc_spot_usd(
        get_deribit_index_usd=_cached_deribit_index,
        get_yahoo_prices_df=lambda: _cached_yahoo({"bitcoin": ["BTC-USD"]}, "5d"),
        deribit_timeout_s=3.0,
    )

    # Optional Deribit extras (forward curve, bull spreads, prediction overlays, reference tables).
    # Not auto-loaded: implied-lab fetches its own expiries/marks via _cached_* when that section runs.
    load_deribit = bool(st.session_state.get("load_deribit", False))

    # Market-implied distribution is the top-of-screen anchor (H1-01).
    # 4d) Implied probability distribution — Full view: mounted automatically (own Deribit fetches inside)
    run_implied = bool(is_full)
    if is_full:
        st.subheader("Market-implied distribution (anchor)")
        with st.expander("How to read this chart", expanded=False):
            st.markdown("""
        - **Purple (filled):** Risk-neutral lognormal reference from the **forward price** and **ATM implied volatility**.
        - **Orange (dashed):** **Market-implied pricing distribution** from listed option marks (Breeden–Litzenberger). This is a **priced / risk-neutral** distribution (not a “true expectations” claim and not a recommendation).
        - **Green line (if selected):** **Strategy P&amp;L** at expiry (right axis). At each price level, this is your net profit or loss if you hold that strategy. Negative = loss (e.g. premium paid), positive = profit.
        - **Strikes** for the strategy scanner are chosen from available Deribit options: ATM = strike nearest the forward; spreads use the nearest strikes around the forward so the payoff is relevant to current pricing.
            """)

    if is_full and run_implied and current_btc is not None:
        try:
            with st.spinner("Loading expiries and option marks…"):
                bundle0 = fetch_implied_lab_bundle(
                    spot_usd=float(current_btc),
                    max_expiries=10,
                    selected_expiry_str=None,
                    cached_option_expiries=_cached_option_expiries,
                    cached_forward_iv=_cached_forward_iv,
                    cached_marks_full=_cached_marks_full,
                    quote_cache_ttl_s=CACHE_TTL,
                )
                expiries, expiry_fetch_diag = bundle0.expiries, bundle0.expiry_fetch_diag
            if expiries:
                expiry_options = [e["expiry_date_str"] for e in expiries]
                selected_expiry_str = st.selectbox(
                    "Expiry",
                    expiry_options,
                    index=0,
                    key="implied_dist_expiry",
                )
                selected = next((e for e in expiries if e["expiry_date_str"] == selected_expiry_str), None)
                if selected:
                    # Lay out controls and chart side-by-side to reduce scrolling.
                    col_controls, col_chart = st.columns([1, 2])
                    # Create right-panel slots early so the "live result" area
                    # doesn't get pushed down by the (potentially large) left-column controls.
                    with col_chart:
                        # Dedicated slots: reusing one st.empty() for plot + text replaces the chart (Streamlit replaces slot content).
                        with st.expander("Screen map (optional)", expanded=False):
                            st.caption(
                                "**Right column:** chart → **Summary** → **Trust / provenance** → optional **Belief overlay** "
                                "narrative → **Review & disagreement digest** → **Trade ticket**. "
                                "**Left column:** expiry → **Shape & payoff** (presets + **What changed?**) → optional belief controls."
                            )
                        # Sprint002-Slice001: x-axis window control (declared before chart body uses the same key).
                        # Sprint002-Slice002: remember last non–full-range window for in-session restore (same keys per expiry).
                        _zkey_shape = f"implied_lab_shape_zoom_{selected_expiry_str}"
                        _bookmark_shape = f"implied_lab_shape_zoom_bookmark_{selected_expiry_str}"
                        if _zkey_shape not in st.session_state:
                            st.session_state[_zkey_shape] = "Full range"
                        with st.container(border=True):
                            st.caption(
                                "**Shape focus** — pick the chart’s **shape window**: how much of the **underlying price (USD)** "
                                "axis you see; **same priced inputs**."
                            )
                            st.radio(
                                "Shape window",
                                ("Full range", "Lower prices", "Near forward", "Higher prices"),
                                horizontal=True,
                                key=_zkey_shape,
                                help="Descriptive navigation on the same distribution; not advice about trades.",
                            )
                            _zoom_now = str(st.session_state.get(_zkey_shape, "Full range"))
                            if _zoom_now != "Full range":
                                st.session_state[_bookmark_shape] = _zoom_now
                            _zoom_saved = st.session_state.get(_bookmark_shape)
                            if (
                                isinstance(_zoom_saved, str)
                                and _zoom_saved != "Full range"
                                and _zoom_now != _zoom_saved
                            ):
                                st.caption(
                                    "Same curves with your previous **shape window** on this expiry’s underlying-price axis."
                                )
                                if st.button(
                                    "Return to last shape window",
                                    key=f"implied_lab_shape_zoom_restore_{selected_expiry_str}",
                                    help="Restores your last non–full-range **shape window** from this session (same inputs).",
                                ):
                                    st.session_state[_zkey_shape] = _zoom_saved
                                    st.rerun()
                            _prev_shape_zoom_key = f"implied_lab_shape_zoom_prev_{selected_expiry_str}"
                            if _prev_shape_zoom_key not in st.session_state:
                                st.session_state[_prev_shape_zoom_key] = _zoom_now
                            elif str(st.session_state.get(_prev_shape_zoom_key)) != _zoom_now:
                                _lck = f"implied_lab_last_change_{selected_expiry_str}"
                                st.session_state[_lck] = last_action_meaning(
                                    action_id="shape_window",
                                    shape_window_label=_zoom_now,
                                )
                                st.session_state[_prev_shape_zoom_key] = _zoom_now
                        right_chart_slot = st.empty()
                        strip_local_story_slot = st.empty()
                        right_summary_slot = st.empty()
                        right_width_candidate_slot = st.empty()
                        right_trust_slot = st.empty()
                        right_review_slot = st.empty()
                        right_ticket_slot = st.empty()
                        right_anomaly_slot = st.empty()
                        right_forward_slot = st.empty()
                        right_belief_slot = st.empty()
                        right_verification_slot = st.empty()
                    with col_controls:
                        # Only fetch data for the selected expiry to keep this step fast.
                        bundle = fetch_implied_lab_bundle(
                            spot_usd=float(current_btc),
                            max_expiries=10,
                            selected_expiry_str=selected_expiry_str,
                            cached_option_expiries=_cached_option_expiries,
                            cached_forward_iv=_cached_forward_iv,
                            cached_marks_full=_cached_marks_full,
                            quote_cache_ttl_s=CACHE_TTL,
                        )
                        market_data = bundle.market_data_for_selected_expiry or {}
                        forward = float(market_data["forward"])
                        vol = float(market_data["vol"])
                        T_years = float(market_data["T_years"])
                        price_min = float(market_data["price_min"])
                        price_max = float(market_data["price_max"])
                        data = market_data["dist"]
                        marks_full = market_data["marks_full"]
                        call_marks = market_data["call_marks"]
                        put_marks = market_data["put_marks"]
                        avail_strikes = market_data["avail_strikes"]
                        call_by_k = market_data["call_by_k"]
                        put_by_k = market_data["put_by_k"]
                        base_strategy = build_universal_strategy(forward, call_marks, put_marks)
                        # Restore last exact-strike shape for this expiry if present
                        shape_key = f"u4_shape_{selected_expiry_str}"
                        shape_state = st.session_state.get(shape_key, {})
                        # Sprint 2A: user belief overlay (orthogonal to strike / payoff mode)
                        belief_exp = selected_expiry_str
                        st.caption("Optional belief overlay — compare a simple curve to the market-implied view (right).")
                        with st.expander("My belief vs market", expanded=False):
                            st.caption(
                                "Optional: compare a simple lognormal **belief** (peak = price you set) to the displayed market curve."
                            )
                            st.checkbox(
                                "Show my belief curve",
                                key=f"belief_en_{belief_exp}",
                            )
                            st.number_input(
                                "Belief peak — mode (USD)",
                                min_value=1000.0,
                                max_value=float(max(price_max, 1_000_000)),
                                value=float(forward),
                                step=1000.0,
                                key=f"belief_center_{belief_exp}",
                                format="%.0f",
                            )

                            # Market horizon uncertainty on the same basis (σ_ln)
                            sigma_mkt_horizon = float(vol) * (float(T_years) ** 0.5)
                            mkt_move_pct = sigma_ln_to_move_pct_1sigma(sigma_mkt_horizon)

                            st.markdown("**Uncertainty input mode**")
                            unc_mode_key = f"belief_unc_mode_{belief_exp}"
                            unc_mode = st.radio(
                                "Uncertainty input mode",
                                ["±% move (1σ)", "σ_ln (advanced)"],
                                key=unc_mode_key,
                                horizontal=True,
                                label_visibility="collapsed",
                            )

                            if unc_mode == "±% move (1σ)":
                                pct_key = f"belief_move_pct_{belief_exp}"
                                # Initialize from existing sigma value if present to avoid jumpiness.
                                if pct_key not in st.session_state:
                                    existing_sigma = float(st.session_state.get(f"belief_width_{belief_exp}", 0.2))
                                    st.session_state[pct_key] = float(sigma_ln_to_move_pct_1sigma(existing_sigma))

                                st.slider(
                                    "Uncertainty (±% move, 1σ at expiry)",
                                    1.0,
                                    200.0,
                                    float(st.session_state.get(pct_key, 22.0)),
                                    0.5,
                                    key=pct_key,
                                    help="Human-scaled: a ±1σ move corresponds to multiplying price by exp(±σ_ln).",
                                )
                                sigma_ln = move_pct_1sigma_to_sigma_ln(float(st.session_state.get(pct_key, 0.0)))
                                st.caption(
                                    f"Derived σ_ln: **{sigma_ln:.4f}** · "
                                    f"Market horizon: σ_ln≈**{sigma_mkt_horizon:.4f}** (≈±**{mkt_move_pct:.1f}%** 1σ)"
                                )
                            else:
                                sigma_key = f"belief_width_{belief_exp}"
                                st.slider(
                                    "Uncertainty (σ of ln price at expiry)",
                                    0.02,
                                    0.8,
                                    0.2,
                                    0.005,
                                    key=sigma_key,
                                    help="Advanced: σ of ln(price) at expiry. Compared to market σ≈IV×√T.",
                                )
                                sigma_ln = float(st.session_state.get(sigma_key, 0.2))
                                st.caption(
                                    f"≈±**{sigma_ln_to_move_pct_1sigma(sigma_ln):.1f}%** 1σ move · "
                                    f"Market horizon: σ_ln≈**{sigma_mkt_horizon:.4f}** (≈±**{mkt_move_pct:.1f}%**)"
                                )
                        user_belief_for_state = {
                            "enabled": bool(st.session_state.get(f"belief_en_{belief_exp}", False)),
                            "center_usd": float(st.session_state.get(f"belief_center_{belief_exp}", forward)),
                            # Internal model stays in σ_ln; percent mode is just input/display convenience.
                            "width": float(sigma_ln),
                        }
                        # Sprint 001 — Slice 010 (Phase 2): extend "What changed?" to belief interactions.
                        # Keep it local to this screen + expiry; descriptive only.
                        last_change_key = f"implied_lab_last_change_{selected_expiry_str}"
                        suppress_key = f"implied_lab_last_change_suppress_{selected_expiry_str}"
                        belief_prev_key = f"implied_lab_belief_prev_{selected_expiry_str}"
                        prev_belief = (
                            st.session_state.get(belief_prev_key)
                            if isinstance(st.session_state.get(belief_prev_key), dict)
                            else None
                        )
                        if prev_belief is None:
                            st.session_state[belief_prev_key] = dict(user_belief_for_state)
                        else:
                            if not st.session_state.get(suppress_key, False):
                                prev_en = bool(prev_belief.get("enabled", False))
                                prev_center = float(prev_belief.get("center_usd") or 0.0)
                                prev_width = float(prev_belief.get("width") or 0.0)
                                curr_en = bool(user_belief_for_state["enabled"])
                                curr_center = float(user_belief_for_state["center_usd"])
                                curr_width = float(user_belief_for_state["width"])
                                msg = None
                                if curr_en != prev_en:
                                    msg = last_action_meaning(
                                        action_id="belief_toggle",
                                        belief_enabled=curr_en,
                                    )
                                elif abs(curr_center - prev_center) > 1e-9:
                                    msg = last_action_meaning(
                                        action_id="belief_center",
                                        belief_center_usd=curr_center,
                                    )
                                elif abs(curr_width - prev_width) > 1e-9:
                                    msg = last_action_meaning(
                                        action_id="belief_width",
                                        belief_width_sigma_ln=curr_width,
                                    )
                                if msg:
                                    st.session_state[last_change_key] = msg
                            st.session_state[belief_prev_key] = dict(user_belief_for_state)
                        # Defaults when no strikes (chart + belief still run)
                        qty = int(shape_state.get("qty", 1)) if str(shape_state.get("qty", "")).isdigit() else int(shape_state.get("qty", 1) or 1)
                        selected_strategy = base_strategy
                        outputs = {}
                        strategy_name = selected_strategy.get("name", "Universal 4-leg")
                        breakevens: list = []
                        max_gain = 0.0
                        max_loss = 0.0
                        cost_usd = 0.0
                        debit_credit = "—"
                        payoff_usd: list = []
                        solve_work = None
                        if avail_strikes:
                            lo, hi = int(min(avail_strikes)), int(max(avail_strikes))
                            step = max(1000, (hi - lo) // 50)
                            atm = min(avail_strikes, key=lambda k: abs(k - forward))

                            st.caption("Sprint 001 — Slice 008 (Phase 2)")
                            st.markdown("**Shape & payoff**")
                            st.caption(
                                "Quick start: pick a preset to visibly change the green payoff line (main object). "
                                "Open **Mode & solver** when you need Target payoff vs Exact strikes."
                            )
                            # Mode ownership (Sprint 1A): exact strikes vs target payoff
                            mode_key = f"implied_lab_mode_{selected_expiry_str}"

                            # Sprint 001 Slice 005 — one obvious first move (presets)
                            def _apply_preset(preset_id: str) -> None:
                                shape = compute_preset_shape(
                                    preset_id=preset_id,
                                    forward=float(forward),
                                    avail_strikes=[float(x) for x in avail_strikes],
                                )
                                # Presets are "first move" affordances: switch to an immediately inspectable state.
                                st.session_state[mode_key] = "Exact strikes"
                                last_change_key = f"implied_lab_last_change_{selected_expiry_str}"
                                st.session_state[f"implied_lab_last_preset_{selected_expiry_str}"] = preset_id
                                st.session_state[last_change_key] = (
                                    preset_what_changed(preset_id=preset_id, shape=shape)
                                    + " Mode set to **Exact strikes**."
                                )
                                # Slice 007: avoid immediately overwriting preset meaning via change detection on rerun.
                                st.session_state[f"implied_lab_last_change_suppress_{selected_expiry_str}"] = True
                                st.session_state[shape_key] = {
                                    **(
                                        st.session_state.get(shape_key, {})
                                        if isinstance(st.session_state.get(shape_key, {}), dict)
                                        else {}
                                    ),
                                    "k1": float(shape["k1"]),
                                    "k2": float(shape["k2"]),
                                    "k3": float(shape["k3"]),
                                    "k4": float(shape["k4"]),
                                    "reverse": bool(shape["reverse"]),
                                    "use_k1": bool(shape["use_k1"]),
                                    "use_k2": bool(shape["use_k2"]),
                                    "use_k3": bool(shape["use_k3"]),
                                    "use_k4": bool(shape["use_k4"]),
                                    "qty": int(shape.get("qty", 1)),
                                }

                                # Keep widget keys coherent (so the left-column controls match the derived payoff immediately).
                                strike_key = selected_expiry_str
                                st.session_state[f"u4_k1_{strike_key}"] = int(float(shape["k1"]))
                                st.session_state[f"u4_k2_{strike_key}"] = int(float(shape["k2"]))
                                st.session_state[f"u4_k3_{strike_key}"] = int(float(shape["k3"]))
                                st.session_state[f"u4_k4_{strike_key}"] = int(float(shape["k4"]))
                                st.session_state["u4_use_k1"] = bool(shape["use_k1"])
                                st.session_state["u4_use_k2"] = bool(shape["use_k2"])
                                st.session_state["u4_use_k3"] = bool(shape["use_k3"])
                                st.session_state["u4_use_k4"] = bool(shape["use_k4"])
                                st.session_state["u4_reverse"] = bool(shape["reverse"])
                                st.rerun()

                            preset_cols = st.columns(3)
                            for i, pid in enumerate(list(PRESETS.keys())[:3]):
                                with preset_cols[i]:
                                    if st.button(
                                        PRESETS[pid].label,
                                        use_container_width=True,
                                        key=f"btn_implied_preset_{selected_expiry_str}_{pid}",
                                    ):
                                        _apply_preset(pid)

                            last_change_key = f"implied_lab_last_change_{selected_expiry_str}"
                            with st.container(border=True):
                                st.markdown("###### What changed?")
                                st.caption("Sprint 001 — Slice 010 (Phase 2) · belief + target-payoff interactions")
                                st.caption(
                                    "This updates after each meaningful change you make (preset, mode, strikes, legs, quantity, "
                                    "**shape window**). Descriptive only — not a recommendation."
                                )
                                last_msg = st.session_state.get(last_change_key)
                                if isinstance(last_msg, str) and last_msg.strip():
                                    st.markdown(last_msg)
                                    st.write("")
                                    st.markdown("**Try next (one click):**")

                                    try_cols = st.columns(3)

                                    last_preset = st.session_state.get(f"implied_lab_last_preset_{selected_expiry_str}")
                                    preset_ids = list(PRESETS.keys())
                                    if len(preset_ids) >= 2:
                                        if isinstance(last_preset, str) and last_preset in preset_ids:
                                            idx = preset_ids.index(last_preset)
                                            next_pid = preset_ids[(idx + 1) % len(preset_ids)]
                                        else:
                                            next_pid = preset_ids[1]
                                        with try_cols[0]:
                                            if st.button(
                                                f"Compare preset: {PRESETS[next_pid].label}",
                                                use_container_width=True,
                                                key=f"btn_try_next_preset_{selected_expiry_str}_{next_pid}",
                                            ):
                                                _apply_preset(next_pid)

                                    current_mode_label = st.session_state.get(mode_key, "Exact strikes")
                                    next_mode = "Target payoff" if current_mode_label == "Exact strikes" else "Exact strikes"
                                    with try_cols[1]:
                                        if st.button(
                                            f"Mode: {next_mode}",
                                            use_container_width=True,
                                            key=f"btn_try_next_mode_{selected_expiry_str}_{next_mode}",
                                        ):
                                            st.session_state[mode_key] = next_mode
                                            st.session_state[last_change_key] = last_action_meaning(
                                                action_id="mode_switch",
                                                mode_label=next_mode,
                                            )
                                            st.rerun()

                                    with try_cols[2]:
                                        if current_mode_label == "Exact strikes":
                                            if st.button(
                                                "Polarity: flip long/short",
                                                use_container_width=True,
                                                key=f"btn_try_next_polarity_{selected_expiry_str}",
                                            ):
                                                new_reverse = not bool(st.session_state.get("u4_reverse", False))
                                                st.session_state["u4_reverse"] = new_reverse
                                                st.session_state[last_change_key] = last_action_meaning(
                                                    action_id="polarity_reverse",
                                                    reverse=bool(new_reverse),
                                                )
                                                st.rerun()
                                        else:
                                            payoff_key = selected_expiry_str
                                            net_key = f"netpnl_mode_{payoff_key}"
                                            net_label = "Net P&L mode: on" if bool(st.session_state.get(net_key, True)) else "Net P&L mode: off"
                                            if st.button(
                                                net_label,
                                                use_container_width=True,
                                                key=f"btn_try_next_netpnl_{selected_expiry_str}",
                                            ):
                                                new_net = not bool(st.session_state.get(net_key, True))
                                                st.session_state[net_key] = new_net
                                                st.session_state[last_change_key] = last_action_meaning(
                                                    action_id="net_pnl_mode_toggle",
                                                    net_pnl_mode=bool(new_net),
                                                )
                                                st.rerun()
                                else:
                                    st.caption(
                                        "Pick a preset above **or change the chart shape window** to see a plain-English summary. "
                                        "Then try a second and third interaction — this panel will keep updating."
                                    )
                            # Important: do not pass a computed `index` derived from session_state.
                            # Streamlit can treat the widget as "already initialized" and keep it effectively locked.
                            with st.expander("Mode & solver (Exact strikes vs Target payoff)", expanded=False):
                                mode = st.radio(
                                    "Mode",
                                    ["Exact strikes", "Target payoff"],
                                    key=mode_key,
                                    horizontal=True,
                                )
                            mode_norm = "exact_strikes" if mode == "Exact strikes" else "target_payoff"
                            prev_mode_key = f"{mode_key}__prev"

                            # Defaults for strike truth (from persisted exact-strike state)
                            k1d_raw = shape_state.get("k1") or min(avail_strikes)
                            k2d_raw = shape_state.get("k2") or atm
                            k3d_raw = shape_state.get("k3") or atm
                            k4d_raw = shape_state.get("k4") or max(avail_strikes)
                            k1d, k2d, k3d, k4d = snap_and_order_u4_strikes(
                                k1d_raw,
                                k2d_raw,
                                k3d_raw,
                                k4d_raw,
                                avail_strikes=avail_strikes,
                            )

                            # Persisted payoff targets (truth only in target_payoff mode)
                            payoff_targets_key = f"u4_payoff_targets_{selected_expiry_str}"
                            payoff_defaults = st.session_state.get(payoff_targets_key, {}) if isinstance(st.session_state.get(payoff_targets_key, {}), dict) else {}
                            payoff_targets = {
                                "body_left": float(payoff_defaults.get("body_left", k2d)),
                                "body_right": float(payoff_defaults.get("body_right", k3d)),
                                "left_wing": float(payoff_defaults.get("left_wing", max(0.0, k2d - k1d))),
                                "right_wing": float(payoff_defaults.get("right_wing", max(0.0, k4d - k3d))),
                            }

                            # Shared leg toggles + polarity (persisted in exact-shape state)
                            use_k1 = bool(shape_state.get("use_k1", True))
                            use_k2 = bool(shape_state.get("use_k2", True))
                            use_k3 = bool(shape_state.get("use_k3", True))
                            use_k4 = bool(shape_state.get("use_k4", True))
                            reverse = bool(shape_state.get("reverse", False))
                            qty = int(shape_state.get("qty", 1)) if str(shape_state.get("qty", "")).isdigit() else int(shape_state.get("qty", 1) or 1)

                            # Slice 007: "last action" meaning beyond presets (mode switch + exact-strikes controls).
                            suppress_key = f"implied_lab_last_change_suppress_{selected_expiry_str}"
                            if st.session_state.get(suppress_key, False):
                                st.session_state[suppress_key] = False
                                st.session_state[prev_mode_key] = mode
                            else:
                                prev_mode = st.session_state.get(prev_mode_key)
                                if isinstance(prev_mode, str) and prev_mode and prev_mode != mode:
                                    st.session_state[last_change_key] = last_action_meaning(
                                        action_id="mode_switch",
                                        mode_label=mode,
                                    )
                                st.session_state[prev_mode_key] = mode

                            # --- Payoff → strikes (editable truth only in target_payoff mode) ---
                            with st.expander("Payoff → strikes", expanded=False):
                                st.caption("Use this to *calculate* which strikes (K1–K4) produce the payoff/P&L shape you want. **Chain:** Payoff → strikes → chart.")
                                st.caption(
                                    "Editable in current mode" if mode_norm == "target_payoff"
                                    else "Derived / locked in current mode"
                                )
                                payoff_key = selected_expiry_str  # per-expiry widget keys to prevent drift
                                payoff_work_key = f"payoff_work_{payoff_key}"
                                net_pnl_mode = st.checkbox(
                                    "Net P&L mode (cost-aware)",
                                    value=bool(st.session_state.get(f"netpnl_mode_{payoff_key}", True)),
                                    key=f"netpnl_mode_{payoff_key}",
                                    disabled=(mode_norm != "target_payoff"),
                                )

                                max_wing = int(max(0, hi - lo))
                                wing_abs = int(min(2_000_000, max(1_000, int(abs(payoff_targets["left_wing"])), int(abs(payoff_targets["right_wing"]))) * 2))

                                # Avoid Streamlit "default + session_state set" warnings:
                                # only provide defaults when a widget key isn't already in session_state.
                                key_body_left = f"payoff_body_left_{payoff_key}"
                                key_body_right = f"payoff_body_right_{payoff_key}"
                                key_left_wing = f"payoff_left_wing_{payoff_key}"
                                key_right_wing = f"payoff_right_wing_{payoff_key}"

                                st.markdown("**Inputs (payoff → strikes)**")
                                st.markdown(
                                    "- **BodyLeft / BodyRight**: " + (
                                        "net breakeven prices (where green line crosses 0)." if net_pnl_mode else "where the *flat middle* starts/ends."
                                    ) + "\n" +
                                    "- **LeftWingUSD / RightWingUSD**: " + (
                                        "net profit plateaus in the wings (green line height, after premium)." if net_pnl_mode else
                                        "the **width** of each wing (in USD). Bigger width pushes K1 further left and K4 further right."
                                    )
                                )

                                # Slider UI (same feel as strike dials)
                                bl_col, br_col = st.columns(2)
                                with bl_col:
                                    body_left = st.slider(
                                        "Body left (price $)",
                                        lo,
                                        hi,
                                        value=int(payoff_targets["body_left"]),
                                        step=step,
                                        key=key_body_left,
                                        disabled=(mode_norm != "target_payoff"),
                                    )
                                with br_col:
                                    body_right = st.slider(
                                        "Body right (price $)",
                                        lo,
                                        hi,
                                        value=int(payoff_targets["body_right"]),
                                        step=step,
                                        key=key_body_right,
                                        disabled=(mode_norm != "target_payoff"),
                                    )

                                lw_col, rw_col = st.columns(2)
                                with lw_col:
                                    if net_pnl_mode:
                                        left_wing_usd = st.slider(
                                            "Left wing net profit (USD)",
                                            -wing_abs,
                                            wing_abs,
                                            value=int(payoff_targets["left_wing"]),
                                            step=step,
                                            key=key_left_wing,
                                            disabled=(mode_norm != "target_payoff"),
                                        )
                                    else:
                                        left_wing_usd = st.slider(
                                            "Left wing width (USD)",
                                            0,
                                            max_wing,
                                            value=int(max(0.0, payoff_targets["left_wing"])),
                                            step=step,
                                            key=key_left_wing,
                                            disabled=(mode_norm != "target_payoff"),
                                        )
                                with rw_col:
                                    if net_pnl_mode:
                                        right_wing_usd = st.slider(
                                            "Right wing net profit (USD)",
                                            -wing_abs,
                                            wing_abs,
                                            value=int(payoff_targets["right_wing"]),
                                            step=step,
                                            key=key_right_wing,
                                            disabled=(mode_norm != "target_payoff"),
                                        )
                                    else:
                                        right_wing_usd = st.slider(
                                            "Right wing width (USD)",
                                            0,
                                            max_wing,
                                            value=int(max(0.0, payoff_targets["right_wing"])),
                                            step=step,
                                            key=key_right_wing,
                                            disabled=(mode_norm != "target_payoff"),
                                        )

                                # Persist payoff target truth only in target-payoff mode
                                if mode_norm == "target_payoff":
                                    # Sprint 001 — Slice 010 (Phase 2): extend "What changed?" to target-payoff interactions.
                                    payoff_prev_key = f"implied_lab_payoff_prev_{selected_expiry_str}"
                                    prev_payoff = (
                                        st.session_state.get(payoff_prev_key)
                                        if isinstance(st.session_state.get(payoff_prev_key), dict)
                                        else None
                                    )
                                    curr_payoff = {
                                        "net_pnl_mode": bool(net_pnl_mode),
                                        "body_left": float(body_left),
                                        "body_right": float(body_right),
                                        "left_wing": float(left_wing_usd),
                                        "right_wing": float(right_wing_usd),
                                    }
                                    if prev_payoff is None:
                                        st.session_state[payoff_prev_key] = dict(curr_payoff)
                                    else:
                                        if not st.session_state.get(suppress_key, False):
                                            msg = None
                                            if bool(curr_payoff["net_pnl_mode"]) != bool(prev_payoff.get("net_pnl_mode", curr_payoff["net_pnl_mode"])):
                                                msg = last_action_meaning(
                                                    action_id="net_pnl_mode_toggle",
                                                    net_pnl_mode=bool(curr_payoff["net_pnl_mode"]),
                                                )
                                            elif abs(float(curr_payoff["body_left"]) - float(prev_payoff.get("body_left", curr_payoff["body_left"]))) > 1e-9:
                                                msg = last_action_meaning(
                                                    action_id="target_payoff_edit",
                                                    target_id="Body left",
                                                    target_value=float(curr_payoff["body_left"]),
                                                )
                                            elif abs(float(curr_payoff["body_right"]) - float(prev_payoff.get("body_right", curr_payoff["body_right"]))) > 1e-9:
                                                msg = last_action_meaning(
                                                    action_id="target_payoff_edit",
                                                    target_id="Body right",
                                                    target_value=float(curr_payoff["body_right"]),
                                                )
                                            elif abs(float(curr_payoff["left_wing"]) - float(prev_payoff.get("left_wing", curr_payoff["left_wing"]))) > 1e-9:
                                                msg = last_action_meaning(
                                                    action_id="target_payoff_edit",
                                                    target_id="Left wing",
                                                    target_value=float(curr_payoff["left_wing"]),
                                                )
                                            elif abs(float(curr_payoff["right_wing"]) - float(prev_payoff.get("right_wing", curr_payoff["right_wing"]))) > 1e-9:
                                                msg = last_action_meaning(
                                                    action_id="target_payoff_edit",
                                                    target_id="Right wing",
                                                    target_value=float(curr_payoff["right_wing"]),
                                                )
                                            if msg:
                                                st.session_state[last_change_key] = msg
                                        st.session_state[payoff_prev_key] = dict(curr_payoff)
                                    st.session_state[payoff_targets_key] = {
                                        "body_left": float(body_left),
                                        "body_right": float(body_right),
                                        "left_wing": float(left_wing_usd),
                                        "right_wing": float(right_wing_usd),
                                    }

                            # --- Adjust strategy shape (editable truth only in exact_strikes mode) ---
                            with st.expander("Adjust strategy shape", expanded=False):
                                st.caption(
                                    "Editable in current mode" if mode_norm == "exact_strikes"
                                    else "Derived / locked in current mode"
                                )
                                qty = st.slider(
                                    "Contracts (scale height)",
                                    1,
                                    10,
                                    int(qty),
                                    help="Multiply payoff by number of contracts.",
                                    disabled=(mode_norm != "exact_strikes"),
                                )
                                k1, k2, k3, k4 = k1d, k2d, k3d, k4d
                                st.caption("**Bodies on top, wings below.** Use +/- inputs for exact levels (snaps to strikes). Checkboxes turn legs on/off.")
                                strike_key = selected_expiry_str  # per-expiry widget keys prevent cross-expiry drift
                                # Bodies row (K2, K3) — +/- number inputs
                                b_left, b_right = st.columns(2)
                                with b_left:
                                    k2_key = f"u4_k2_{strike_key}"
                                    k2_input = st.number_input(
                                        "K2 — left body $",
                                        min_value=lo,
                                        max_value=hi,
                                        value=int(k2),
                                        step=step,
                                        key=k2_key,
                                        disabled=(mode_norm != "exact_strikes"),
                                    )
                                with b_right:
                                    k3_key = f"u4_k3_{strike_key}"
                                    k3_input = st.number_input(
                                        "K3 — right body $",
                                        min_value=lo,
                                        max_value=hi,
                                        value=int(k3),
                                        step=step,
                                        key=k3_key,
                                        disabled=(mode_norm != "exact_strikes"),
                                    )

                                # Wings row (K1, K4) — +/- number inputs
                                w_left, w_right = st.columns(2)
                                with w_left:
                                    k1_key = f"u4_k1_{strike_key}"
                                    k1_input = st.number_input(
                                        "K1 — left wing $",
                                        min_value=lo,
                                        max_value=hi,
                                        value=int(k1),
                                        step=step,
                                        key=k1_key,
                                        disabled=(mode_norm != "exact_strikes"),
                                    )
                                with w_right:
                                    k4_key = f"u4_k4_{strike_key}"
                                    k4_input = st.number_input(
                                        "K4 — right wing $",
                                        min_value=lo,
                                        max_value=hi,
                                        value=int(k4),
                                        step=step,
                                        key=k4_key,
                                        disabled=(mode_norm != "exact_strikes"),
                                    )

                                # Snap to nearest available strikes
                                k1_sel, k2_sel, k3_sel, k4_sel = snap_and_order_u4_strikes(
                                    int(k1_input),
                                    int(k2_input),
                                    int(k3_input),
                                    int(k4_input),
                                    avail_strikes=avail_strikes,
                                )
                                # Per-leg include toggles and polarity
                                st.caption("**Polarity & legs:** Long = pay premium, short = receive. Base: short K1, long K2, long K3, short K4.")
                                leg_cols = st.columns(4)
                                with leg_cols[0]:
                                    use_k1 = st.checkbox("Use K1", value=use_k1, key="u4_use_k1", disabled=(mode_norm != "exact_strikes"))
                                with leg_cols[1]:
                                    use_k2 = st.checkbox("Use K2", value=use_k2, key="u4_use_k2", disabled=(mode_norm != "exact_strikes"))
                                with leg_cols[2]:
                                    use_k3 = st.checkbox("Use K3", value=use_k3, key="u4_use_k3", disabled=(mode_norm != "exact_strikes"))
                                with leg_cols[3]:
                                    use_k4 = st.checkbox("Use K4", value=use_k4, key="u4_use_k4", disabled=(mode_norm != "exact_strikes"))

                                st.write("")
                                # Reverse polarity toggle
                                reverse = st.checkbox(
                                    "Reverse the polarity (flip long/short)",
                                    value=bool(reverse),
                                    key="u4_reverse",
                                    disabled=(mode_norm != "exact_strikes"),
                                )
                                # Slice 007: update "What changed?" for main non-preset interactions (Exact strikes mode).
                                if mode_norm == "exact_strikes" and not st.session_state.get(suppress_key, False):
                                    prev_qty = int(shape_state.get("qty", 1) or 1)
                                    prev_reverse = bool(shape_state.get("reverse", False))
                                    prev_use = {
                                        "K1": bool(shape_state.get("use_k1", True)),
                                        "K2": bool(shape_state.get("use_k2", True)),
                                        "K3": bool(shape_state.get("use_k3", True)),
                                        "K4": bool(shape_state.get("use_k4", True)),
                                    }
                                    prev_strikes = {
                                        "k1": float(shape_state.get("k1", k1_sel)),
                                        "k2": float(shape_state.get("k2", k2_sel)),
                                        "k3": float(shape_state.get("k3", k3_sel)),
                                        "k4": float(shape_state.get("k4", k4_sel)),
                                    }

                                    msg: str | None = None
                                    if int(qty) != int(prev_qty):
                                        msg = last_action_meaning(action_id="quantity", qty=int(qty))
                                    elif bool(reverse) != bool(prev_reverse):
                                        msg = last_action_meaning(action_id="polarity_reverse", reverse=bool(reverse))
                                    else:
                                        curr_use = {"K1": use_k1, "K2": use_k2, "K3": use_k3, "K4": use_k4}
                                        for leg_id, enabled in curr_use.items():
                                            if bool(enabled) != bool(prev_use.get(leg_id, enabled)):
                                                msg = last_action_meaning(
                                                    action_id="leg_toggle",
                                                    leg=leg_id,
                                                    leg_enabled=bool(enabled),
                                                )
                                                break
                                    if msg is None:
                                        curr_strikes = {"k1": float(k1_sel), "k2": float(k2_sel), "k3": float(k3_sel), "k4": float(k4_sel)}
                                        if any(abs(float(curr_strikes[k]) - float(prev_strikes.get(k, curr_strikes[k]))) > 1e-9 for k in ("k1", "k2", "k3", "k4")):
                                            msg = last_action_meaning(action_id="strike_edit", strikes=curr_strikes)
                                    if msg:
                                        st.session_state[last_change_key] = msg
                                # Persist exact-strike truth only in exact-strikes mode
                                if mode_norm == "exact_strikes":
                                    st.session_state[shape_key] = {
                                        **st.session_state.get(shape_key, {}),
                                        "k1": k1_sel,
                                        "k2": k2_sel,
                                        "k3": k3_sel,
                                        "k4": k4_sel,
                                        "reverse": reverse,
                                        "use_k1": use_k1,
                                        "use_k2": use_k2,
                                        "use_k3": use_k3,
                                        "use_k4": use_k4,
                                        "qty": int(qty),
                                    }

                            # Centralized state (user truth only) + pure derived outputs (Sprint 1A)
                            strikes_exact = {"k1": float(k1_sel), "k2": float(k2_sel), "k3": float(k3_sel), "k4": float(k4_sel)}
                            payoff_targets = {
                                "body_left": float(st.session_state.get(key_body_left, payoff_targets["body_left"])),
                                "body_right": float(st.session_state.get(key_body_right, payoff_targets["body_right"])),
                                "left_wing": float(st.session_state.get(key_left_wing, payoff_targets["left_wing"])),
                                "right_wing": float(st.session_state.get(key_right_wing, payoff_targets["right_wing"])),
                            }
                            outputs = run_implied_lab(
                                expiry_str=selected_expiry_str,
                                mode=mode_norm,
                                qty=int(qty),
                                strikes_exact=strikes_exact,
                                payoff_targets=payoff_targets,
                                legs_enabled={"use_k1": use_k1, "use_k2": use_k2, "use_k3": use_k3, "use_k4": use_k4},
                                reverse=bool(reverse),
                                net_pnl_mode=bool(net_pnl_mode),
                                user_belief=user_belief_for_state,
                                market_data=market_data,
                            )
                            selected_strategy = outputs.get("strategy") or base_strategy
                            payoff_usd = outputs.get("overlay", {}).get("payoff_usd", []) or []
                            breakevens = outputs.get("summary", {}).get("breakevens", []) or []
                            max_gain = outputs.get("summary", {}).get("max_gain", 0.0) or 0.0
                            max_loss = outputs.get("summary", {}).get("max_loss", 0.0) or 0.0
                            cost_usd = outputs.get("summary", {}).get("cost_usd", 0.0) or 0.0
                            debit_credit = outputs.get("summary", {}).get("debit_credit", "")
                            strategy_name = outputs.get("summary", {}).get("name", selected_strategy.get("name", "Universal 4-leg"))
                            solve_work = outputs.get("solve_work")
                        else:
                            ph = float(forward)
                            outputs = run_implied_lab(
                                expiry_str=selected_expiry_str,
                                mode="exact_strikes",
                                qty=1,
                                strikes_exact={"k1": ph, "k2": ph, "k3": ph, "k4": ph},
                                payoff_targets={
                                    "body_left": ph,
                                    "body_right": ph,
                                    "left_wing": 0.0,
                                    "right_wing": 0.0,
                                },
                                legs_enabled={"use_k1": False, "use_k2": False, "use_k3": False, "use_k4": False},
                                reverse=False,
                                net_pnl_mode=False,
                                user_belief=user_belief_for_state,
                                market_data=market_data,
                            )
                            selected_strategy = base_strategy
                    # Everything below (distribution chart, summary, scanner) goes in the chart column
                    call_marks = marks_full.get("calls") or []
                    ch = outputs.get("chart_helpers") or {}
                    _zkey_shape = f"implied_lab_shape_zoom_{selected_expiry_str}"
                    _zoom_choice = str(st.session_state.get(_zkey_shape, "Full range"))
                    chart_bundle = build_implied_lab_distribution_chart_bundle(
                        selected_expiry_str=selected_expiry_str,
                        dist_data=data,
                        outputs=outputs,
                        forward=float(forward),
                        vol=float(vol),
                        T_years=float(T_years),
                        price_min=float(price_min),
                        price_max=float(price_max),
                        zoom_choice=_zoom_choice,
                        user_belief_for_state=user_belief_for_state,
                    )
                    if chart_bundle.local_story_strip:
                        with strip_local_story_slot.container():
                            st.caption(chart_bundle.local_story_strip)
                    else:
                        strip_local_story_slot.empty()

                    with right_chart_slot.container():
                        st.markdown("##### Market-implied view (chart)")
                        with st.container(border=True):
                            st.caption(
                                "**Belief vs market — at a glance** (digest + reference numbers) lives in **Review & disagreement digest** "
                                "below this column — same run as the chart."
                            )
                            _lc_key_sf = f"implied_lab_last_change_{selected_expiry_str}"
                            _last_sf = st.session_state.get(_lc_key_sf)
                            if isinstance(_last_sf, str) and _last_sf.strip():
                                st.markdown(_shape_focus_post_interaction_hint(outputs.get("verification"), float(forward)))
                            else:
                                st.caption(
                                    "After a preset, belief control, or strategy control on the left, this adds a short "
                                    "**where-to-look** cue on the **same underlying-price axis** as your **shape window** "
                                    "(descriptive, not advisory)."
                                )
                        st.markdown("###### Local region (descriptive)")
                        if _zoom_choice == "Full range":
                            st.caption(
                                chart_bundle.local_story_md.replace("**", "").replace("  ", " ").strip()
                            )
                        else:
                            st.markdown(chart_bundle.local_story_md)
                        st.caption(
                            "Purple: **risk-neutral distribution** reference · Orange: **market-implied pricing distribution** "
                            "(Breeden–Litzenberger from marks) · Green: **strategy P&L** at expiry when legs are set."
                        )
                        st.plotly_chart(chart_bundle.fig, use_container_width=True)

                    right_forward_slot.caption(chart_bundle.forward_caption)

                    if not avail_strikes:
                        right_summary_slot.info("No option strikes for this expiry — the strategy overlay is unavailable.")
                    # Summary card (Sprint 001): single-source-of-truth from derived outputs.
                    with right_summary_slot.container():
                        _render_implied_lab_summary_card(outputs)
                    _v_pay = outputs.get("verification") if isinstance(outputs.get("verification"), dict) else None
                    _wv_strip = build_width_vol_candidate_strip_payload(_v_pay)
                    if _wv_strip:
                        with right_width_candidate_slot.container():
                            _maybe_append_width_vol_history(
                                verification=_v_pay or {},
                                selected_expiry_str=selected_expiry_str,
                            )
                            _render_width_vol_candidate_strip_payload(_wv_strip)
                            _render_width_vol_history_panel(selected_expiry_str=selected_expiry_str)
                    else:
                        right_width_candidate_slot.empty()
                    with right_trust_slot.container():
                        _render_trust_strip(outputs.get("verification") or {})
                    with right_belief_slot.container():
                        if chart_bundle.belief_block_markdown:
                            with st.expander("Belief overlay (this run)", expanded=False):
                                st.markdown(chart_bundle.belief_block_markdown)
                    with right_review_slot.container():
                        with st.expander("Review & disagreement digest", expanded=False):
                            _render_decision_ready_review(outputs.get("verification") or {})
                            _render_belief_vs_market_glance(outputs.get("verification") or {})
                    with right_ticket_slot.container():
                        if selected_strategy and selected_strategy.get("k1") is not None:
                            _render_implied_lab_trade_ticket_panel(
                                selected_expiry_str=selected_expiry_str,
                                qty=int(qty),
                                forward=forward,
                                selected_strategy=selected_strategy,
                                put_by_k=put_by_k,
                                call_by_k=call_by_k,
                                summary=outputs.get("summary") or {},
                            )
                    if chart_bundle.anomalous:
                        right_anomaly_slot.warning(
                            "Anomalous: market-implied pricing distribution differs from the lognormal reference (see Verification)."
                        )

                    with right_verification_slot:
                        with st.expander("Verification", expanded=False):
                            _render_implied_lab_verification(outputs.get("verification") or {})

                    # Strategy details are useful, but not part of the top-of-screen story.
                    with st.expander("Strategy details (optional)", expanded=False):
                        if not (selected_strategy and selected_strategy.get("k1") is not None):
                            if avail_strikes:
                                st.caption("Set strikes in the **left column** (open **Adjust strategy shape**) to see payoff and name above.")
                            else:
                                st.caption("No strikes available for this expiry; use **Refresh priced inputs (Deribit)** or pick another expiry.")
                        else:
                            summary = outputs.get("summary") or {}
                            name = str(summary.get("name") or selected_strategy.get("name") or "Universal 4-leg")
                            cost = float(summary.get("cost_usd") or 0.0)
                            max_gain = float(summary.get("max_gain") or 0.0)
                            max_loss = float(summary.get("max_loss") or 0.0)
                            breakevens = summary.get("breakevens") or []

                            st.dataframe(
                                pd.DataFrame([{
                                    "Strategy": name,
                                    "Cost (USD)": f"{cost:,.0f}" if cost >= 0 else f"-{abs(cost):,.0f}",
                                    "Legs": selected_strategy.get("legs_desc", ""),
                                }]),
                                use_container_width=True,
                                hide_index=True,
                            )
                            st.caption(
                                "**Trade ticket (copy/paste)** is **above** (under **Review & disagreement digest**) — "
                                "same leg list and optional **Show calculations** — illustrative only, not a recommendation."
                            )
            else:
                st.caption("No Deribit option expiries. Check API.")
                with st.expander("Debug (expiries fetch)", expanded=False):
                    st.code(
                        expiry_fetch_diag
                        or "No failure detail stored. If this persists, use the app menu → Clear cache, then Rerun.",
                        language="text",
                    )
        except Exception as e:
            st.caption(f"Implied distribution unavailable: {e}")
            with st.expander("Debug (last error)", expanded=False):
                st.markdown(f"**Exception type:** `{type(e).__name__}`")
                st.markdown(f"**Message:** `{e!s}`")
                st.code(traceback.format_exc(), language="text")
    elif is_full and run_implied and current_btc is None:
        st.caption("Need BTC spot price for implied distribution.")

    st.divider()

    render_market_context_expander(
        config=config,
        btc_symbols=btc_symbols,
        chart_days=chart_days,
        cached_yahoo=_cached_yahoo,
        cached_polymarket=_cached_polymarket,
        cached_forward_curve=_cached_forward_curve,
        cached_option_instruments=_cached_option_instruments,
        cached_option_book_marks=_cached_option_book_marks,
        cached_bull_spreads=_cached_bull_spreads,
        cached_options_for_chart=_cached_options_for_chart,
        is_full=is_full,
        load_deribit=load_deribit,
        current_btc=current_btc,
        show_forward_curve=show_forward_curve,
        show_bull_spreads=show_bull_spreads,
        show_prediction_spreads=show_prediction_spreads,
        show_options_on_chart=show_options_on_chart,
        options_in_separate_chart=options_in_separate_chart,
        option_types_on_chart=option_types_on_chart,
        min_prob_label_pct=min_prob_label_pct,
    )

    st.divider()

render_market_reference_sections(
    config=config,
    show_markets=show_markets,
    show_polymarket=show_polymarket,
    cached_yahoo=_cached_yahoo,
    cached_polymarket=_cached_polymarket,
)

st.sidebar.caption("Phase 1: data ingest. Next: canonical events → probabilities → opportunities.")
