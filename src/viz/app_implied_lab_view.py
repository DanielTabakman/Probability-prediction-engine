"""
Bitcoin implied-lab view extracted from `src/viz/app.py`.

Preserves Streamlit widget keys, session_state keys, and copy so the extraction
remains behavior-neutral (see `app_market_context.py`, `app_panels.py`).
"""

from __future__ import annotations

import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from functools import partial
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from src.engine.implied_distribution import build_distribution_chart_data
from src.engine.strategy_scanner import (
    build_universal_strategy,
    name_universal_strategy,
    payoff_target_to_strikes,
    payoff_target_to_strikes_with_work,
)
from src.viz.app_cache import (
    CACHE_TTL,
    cached_btc_options_summary as _cached_btc_options_summary,
    cached_bull_spreads as _cached_bull_spreads,
    cached_deribit_index as _cached_deribit_index,
    cached_deribit_summary as _cached_deribit_summary,
    cached_forward_curve as _cached_forward_curve,
    cached_forward_iv as _cached_forward_iv,
    cached_lab_spot as _cached_lab_spot,
    cached_marks_full as _cached_marks_full,
    cached_option_book_marks as _cached_option_book_marks,
    cached_option_expiries as _cached_option_expiries,
    cached_option_instruments as _cached_option_instruments,
    cached_options_for_chart as _cached_options_for_chart,
    cached_polymarket as _cached_polymarket,
    cached_yahoo as _cached_yahoo,
)
from src.viz.app_market_context import (
    _cached_questions_from_events,
    render_market_context_expander,
)
from src.viz.app_panels import (
    compute_mvp1_belief_overlay_state as _compute_mvp1_belief_overlay_state,
    implied_lab_trade_ticket_code_text as _implied_lab_trade_ticket_code_text,
    maybe_append_width_vol_history as _maybe_append_width_vol_history,
    render_belief_vs_market_glance as _render_belief_vs_market_glance,
    render_decision_ready_review as _render_decision_ready_review,
    render_directional_candidate_strip_payload as _render_directional_candidate_strip_payload,
    render_implied_lab_summary_card as _render_implied_lab_summary_card,
    render_implied_lab_trade_ticket_panel as _render_implied_lab_trade_ticket_panel,
    render_implied_lab_verification as _render_implied_lab_verification,
    render_mvp1_friends_first_above_fold as _render_mvp1_friends_first_above_fold,
    render_mvp1_primary_output_compact as _render_mvp1_primary_output_compact,
    render_trust_strip as _render_trust_strip,
    render_width_vol_candidate_strip_payload as _render_width_vol_candidate_strip_payload,
    render_width_vol_history_panel as _render_width_vol_history_panel,
    shape_focus_post_interaction_hint as _shape_focus_post_interaction_hint,
    shape_focus_x_range as _shape_focus_x_range,
)
from src.viz.cross_venue_export import (
    build_cross_venue_panel_rows,
    serialize_cross_venue_export_csv,
)
from src.viz.cross_venue_scan import (
    build_cross_venue_scan_report,
    render_cross_venue_scan_markdown,
)
from src.viz.decision_ready_review import build_decision_ready_review_payload
from src.viz.distribution_export import (
    build_distribution_export_rows,
    serialize_distribution_export_csv,
)
from src.viz.distribution_summary_panel import render_distribution_summary_panel
from src.viz.implied_lab_derive import derive_lab_outputs
from src.viz.product_usage_telemetry import log_product_usage_event
from src.viz.implied_lab_legibility import (
    BELIEF_STRATEGY_HOW_CALCULATED_MARKDOWN,
    CUMULATIVE_CAPTION,
    FAMILY_VS_TICKET_CAPTION,
    METHOD_GLOSSARY_MARKDOWN,
    TRACE_MODEL_BELL,
    TRACE_MODEL_BELL_HELP,
    TRACE_OPTIONS_CHAIN,
    TRACE_OPTIONS_CHAIN_HELP,
    TRACE_STRATEGY_PAYOFF,
    TRACE_USER_BELIEF,
    TRACE_USER_BELIEF_HELP,
    YAXIS_DENSITY_TITLE,
)
from src.viz.implied_lab_last_action import last_action_meaning, shape_window_local_region_story
from src.viz.implied_lab_presets import PRESETS, compute_preset_shape, preset_what_changed
from src.viz.implied_lab_provenance import (
    build_directional_candidate_strip_payload,
    build_trust_strip_lines,
    build_width_vol_candidate_strip_payload,
)
from src.viz.belief_uncertainty import (
    move_pct_1sigma_to_sigma_ln,
    sigma_ln_to_move_pct_1sigma,
)
from src.viz.implied_lab_state import build_implied_lab_state
from src.viz.lab_asset_selection import render_lab_asset_selector
from src.viz.mvp1_lab_ui import (
    apply_implied_lab_preset_to_session,
    ensure_mvp1_lab_default_shape,
    post_mvp1_lab_ui_enabled,
)
from src.viz.perf import PerfLog, timed
from src.viz.plotly_theme import apply_chart_theme
from src.viz.prefetch import maybe_submit_prefetch
from src.viz.tutorial import render_how_it_works_expander


def render_implied_lab_bitcoin_section(
    *,
    config: dict[str, Any],
    btc_symbols: dict[str, list[str]],
    chart_days: int,
    is_full: bool,
    show_debug_ui: bool,
    snapshots_enabled: bool,
    implied_lab_auto_compute: bool,
    show_forward_curve: bool,
    show_bull_spreads: bool,
    show_prediction_spreads: bool,
    show_options_on_chart: bool,
    options_in_separate_chart: bool,
    option_types_on_chart: list[str],
    min_prob_label_pct: int,
    perf: PerfLog,
) -> None:
    post_mvp_implied_lab_ui = post_mvp1_lab_ui_enabled()
    if not st.session_state.get("_ppe_streamlit_lab_view_logged"):
        st.session_state["_ppe_streamlit_lab_view_logged"] = True
        log_product_usage_event("streamlit_lab_view", path="/implied-lab")
    st.header("Bitcoin implied lab — market-implied view as the anchor")
    st.caption(
        "**Read in order:** market-implied chart → your **belief** (left) → **Belief vs market** for the disagreement "
        "story. Exploration only — not advice."
    )
    render_how_it_works_expander(expanded=False)
    if show_debug_ui:
        _glance_suffix = (
            "**Review → trade ticket** (under **Summary**). "
            if post_mvp_implied_lab_ui
            else "**Review** digest only (MVP1: strike/payoff/ticket UI hidden — set **PPE_POST_MVP1_LAB_UI=1** for full lab). "
        )
        st.caption(
            "Dev — **Glance path:** **Market-implied** (right) · **User belief** (left) · "
            "**Disagreement digest** (*Belief vs market — at a glance*) · "
            + _glance_suffix
            + "Exploration workbench — not a recommendation engine."
        )

    # Top-of-screen anchor: get a spot reference quickly (implied-lab needs this).
    current_btc = None
    if is_full:
        try:
            # Bounded wait: Deribit index can hang; fall through to Yahoo so the lab can mount.
            with ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(_cached_deribit_index)
                done, _ = wait([fut], timeout=3.0)
                if done:
                    current_btc = fut.result()
        except Exception:
            current_btc = None
    if current_btc is None:
        try:
            fallback_df = _cached_yahoo({"bitcoin": ["BTC-USD"]}, "5d")
            if fallback_df is not None and not fallback_df.empty:
                spot_rows = fallback_df[fallback_df["symbol"] == "BTC-USD"]
                if len(spot_rows):
                    for col in ("close", "Close"):
                        if col in spot_rows.columns:
                            current_btc = float(spot_rows.sort_values("timestamp")[col].iloc[-1])
                            break
        except Exception:
            current_btc = None

    # Optional Deribit extras (forward curve, bull spreads, prediction overlays, reference tables).
    # Not auto-loaded: implied-lab fetches its own expiries/marks via _cached_* when that section runs.
    load_deribit = bool(st.session_state.get("load_deribit", False))

    # Background cache warming (best-effort): likely timeframe windows + key Deribit endpoints.
    # This improves perceived speed on the next rerun (e.g., switching chart_days).
    try:
        for _d in (5, 30, 90):
            maybe_submit_prefetch(
                key=f"yahoo_btc_{_d}d",
                label=f"yahoo BTC {_d}d",
                fn=lambda d=_d: _cached_yahoo({"bitcoin": ["BTC-USD", "BTC=F"]}, f"{int(d)}d"),
            )
        maybe_submit_prefetch(
            key="polymarket_ref",
            label="polymarket (active)",
            fn=lambda: _cached_polymarket(True, False, 150),
        )
        if load_deribit:
            maybe_submit_prefetch(
                key="deribit_option_instruments",
                label="deribit option instruments",
                fn=lambda: _cached_option_instruments(),
            )
            maybe_submit_prefetch(
                key="deribit_option_book_marks",
                label="deribit option book marks",
                fn=lambda: _cached_option_book_marks(),
            )
            maybe_submit_prefetch(
                key="deribit_option_expiries",
                label="deribit option expiries",
                fn=lambda: _cached_option_expiries(),
            )
    except Exception:
        pass

    # Market-implied distribution is the top-of-screen anchor (H1-01).
    # 4d) Implied probability distribution — Full view: mounted automatically (own Deribit fetches inside)
    run_implied = bool(is_full)
    if is_full:
        st.subheader("Market-implied distribution (anchor)")
        with st.expander("How to read this chart", expanded=False):
            st.markdown(METHOD_GLOSSARY_MARKDOWN)
            st.caption(
                "Green payoff line (when shown): net strategy P&L at expiry from exact strikes on this run — "
                "not the same as illustrative strategy families in the belief panel."
            )

    lab_asset_id = render_lab_asset_selector(key="implied_lab_asset_id") if is_full else "BTC"
    lab_spot_raw = _cached_lab_spot(lab_asset_id) if is_full else None
    if isinstance(lab_spot_raw, (int, float)):
        lab_spot = float(lab_spot_raw)
    elif isinstance(lab_spot_raw, dict):
        _raw = lab_spot_raw.get("index") or lab_spot_raw.get("price")
        lab_spot = float(_raw) if _raw is not None else None
    else:
        lab_spot = None
    implied_anchor_spot = lab_spot if lab_spot and lab_spot > 0 else current_btc

    if is_full and run_implied and implied_anchor_spot is not None:
        try:
            with st.spinner("Loading expiries and option marks…"):
                expiries, expiry_fetch_diag = _cached_option_expiries(asset_id=lab_asset_id)
            if expiries:
                run_ts_export = pd.Timestamp.now(tz="UTC")
                as_of_export = run_ts_export.isoformat()
                now_ms_export = run_ts_export.timestamp() * 1000
                _fwd_iv = partial(_cached_forward_iv, asset_id=lab_asset_id)
                _marks = partial(_cached_marks_full, asset_id=lab_asset_id)
                export_rows = build_distribution_export_rows(
                    as_of_utc=as_of_export,
                    spot_usd=float(implied_anchor_spot),
                    expiries=expiries,
                    forward_iv_fn=_fwd_iv,
                    marks_full_fn=_marks,
                    now_ms=now_ms_export,
                    asset_id=lab_asset_id,
                )
                render_distribution_summary_panel(export_rows)
                _export_slug = lab_asset_id.lower()
                st.download_button(
                    "Download distribution stats (CSV)",
                    data=serialize_distribution_export_csv(export_rows).encode("utf-8"),
                    file_name=f"ppe_{_export_slug}_distribution_stats.csv",
                    mime="text/csv",
                    key="implied_dist_export_csv",
                    on_click=log_product_usage_event,
                    args=("streamlit_distribution_export",),
                    kwargs={"path": "/implied-lab", "asset_id": lab_asset_id},
                )
                if load_deribit:
                    keywords = (
                        (config.get("prediction_markets") or {})
                        .get("polymarket", {})
                        .get("topic_keywords")
                        or ["bitcoin", "btc"]
                    )
                    try:
                        pm_events = _cached_polymarket(True, False, 150) or []
                        btc_questions = (
                            _cached_questions_from_events(pm_events, keywords)
                            if pm_events
                            else []
                        )
                        if btc_questions:
                            cv_rows = build_cross_venue_panel_rows(
                                as_of_utc=as_of_export,
                                spot_usd=float(implied_anchor_spot),
                                btc_questions=btc_questions,
                                forward_iv_fn=_fwd_iv,
                                marks_full_fn=_marks,
                                instruments_fn=_cached_option_instruments,
                                option_book_marks_fn=_cached_option_book_marks,
                            )
                            if cv_rows:
                                st.download_button(
                                    "Download cross-venue prob panel (CSV)",
                                    data=serialize_cross_venue_export_csv(cv_rows).encode(
                                        "utf-8"
                                    ),
                                    file_name="ppe_cross_venue_prob_panel.csv",
                                    mime="text/csv",
                                    key="cross_venue_prob_panel_csv",
                                )
                                scan_report = build_cross_venue_scan_report(cv_rows, max_rows=8)
                                with st.expander("Cross-venue gap scan (top matches)", expanded=bool(scan_report.get("row_count"))):
                                    if scan_report.get("row_count"):
                                        st.markdown(render_cross_venue_scan_markdown(scan_report))
                                        st.caption("Headless: python scripts/run_cross_venue_scan.py")
                                    else:
                                        st.caption("No rankable gaps (check match_status / BL marks).")
                    except Exception:
                        pass
                expiry_options = [e["expiry_date_str"] for e in expiries]
                selected_expiry_str = st.selectbox(
                    "Expiry",
                    expiry_options,
                    index=0,
                    key="implied_dist_expiry",
                )
                selected = next((e for e in expiries if e["expiry_date_str"] == selected_expiry_str), None)
                if selected:
                    from src.viz.app_implied_lab_expiry_workspace import render_implied_lab_expiry_workspace

                    render_implied_lab_expiry_workspace(
                        selected=selected,
                        selected_expiry_str=selected_expiry_str,
                        post_mvp_implied_lab_ui=post_mvp_implied_lab_ui,
                        show_debug_ui=show_debug_ui,
                        snapshots_enabled=snapshots_enabled,
                        implied_lab_auto_compute=implied_lab_auto_compute,
                        lab_asset_id=lab_asset_id,
                        implied_anchor_spot=float(implied_anchor_spot),
                        config=config,
                        load_deribit=load_deribit,
                        perf=perf,
                    )
            else:
                st.caption("No Deribit option expiries. Check API.")
                if show_debug_ui:
                    with st.expander("Debug (expiries fetch)", expanded=False):
                        st.code(
                            expiry_fetch_diag
                            or "No failure detail stored. If this persists, use the app menu → Clear cache, then Rerun.",
                            language="text",
                        )
        except Exception as e:
            st.caption(f"Implied distribution unavailable: {e}")
            if show_debug_ui:
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
