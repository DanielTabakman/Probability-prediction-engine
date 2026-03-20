"""
Streamlit dashboard: market data and prediction market probabilities.
Bitcoin view: price chart with Polymarket questions overlaid, implied value, options & futures.
"""
from __future__ import annotations

import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.data import fetch_yahoo_prices, fetch_polymarket_markets
from src.data.fetch_polymarket import markets_to_probabilities
from src.data.parse_btc_markets import btc_price_questions_from_polymarket
from src.data.fetch_btc_options import fetch_btc_options_summary
from src.data.fetch_deribit import (
    fetch_deribit_btc_options_summary,
    fetch_deribit_btc_options_for_chart,
    fetch_deribit_btc_futures_forward_curve,
    fetch_deribit_btc_tight_bull_spreads,
    fetch_deribit_spreads_around_predictions,
    fetch_deribit_btc_option_expiries,
    fetch_deribit_forward_and_iv_for_expiry,
    fetch_deribit_btc_option_marks_by_expiry,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_btc_index,
)
from src.engine.implied_distribution import (
    build_distribution_chart_data,
    market_implied_density_breeden_litzenberger,
    is_anomalous,
)
from src.engine.strategy_scanner import (
    build_universal_strategy,
    name_universal_strategy,
    payoff_target_to_strikes,
    payoff_target_to_strikes_with_work,
    strategy_payoff_at_prices,
)
from src.viz.implied_lab_state import build_implied_lab_state
from src.viz.implied_lab_derive import derive_lab_outputs
import yaml

st.set_page_config(page_title="Probability Engine", layout="wide")
st.title("Probability Prediction Engine")

# Cached fetches (2 min TTL) — avoids re-fetch on every sidebar change
CACHE_TTL = 120

@st.cache_data(ttl=CACHE_TTL)
def _cached_yahoo(symbols, period):
    return fetch_yahoo_prices(symbols=symbols, period=period)

@st.cache_data(ttl=CACHE_TTL)
def _cached_polymarket(active, closed, limit):
    return fetch_polymarket_markets(active=active, closed=closed, limit=limit)

@st.cache_data(ttl=CACHE_TTL)
def _cached_forward_curve(max_contracts):
    return fetch_deribit_btc_futures_forward_curve(max_contracts=max_contracts)

@st.cache_data(ttl=CACHE_TTL)
def _cached_deribit_index():
    return fetch_deribit_btc_index()

@st.cache_data(ttl=CACHE_TTL)
def _cached_bull_spreads(spot_price, spread_width, max_expiries):
    return fetch_deribit_btc_tight_bull_spreads(spot_price=spot_price, spread_width=spread_width, max_expiries=max_expiries)

@st.cache_data(ttl=CACHE_TTL)
def _cached_options_for_chart():
    return fetch_deribit_btc_options_for_chart()

@st.cache_data(ttl=CACHE_TTL)
def _cached_option_expiries(max_expiries):
    return fetch_deribit_btc_option_expiries(max_expiries=max_expiries)

@st.cache_data(ttl=CACHE_TTL)
def _cached_forward_iv(expiry_ts, spot):
    return fetch_deribit_forward_and_iv_for_expiry(expiry_ts, spot)

@st.cache_data(ttl=CACHE_TTL)
def _cached_marks_full(expiry_ts):
    return fetch_deribit_btc_option_marks_by_expiry_full(expiry_ts)

@st.cache_data(ttl=CACHE_TTL)
def _cached_btc_options_summary():
    return fetch_btc_options_summary()

@st.cache_data(ttl=CACHE_TTL)
def _cached_deribit_summary(max_tickers):
    return fetch_deribit_btc_options_summary(max_tickers=max_tickers)

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
st.sidebar.header("Data")
show_bitcoin_view = st.sidebar.checkbox("Bitcoin view (chart + questions + implied)", value=True)
show_markets = st.sidebar.checkbox("Market prices (Yahoo)", value=True)
show_polymarket = st.sidebar.checkbox("Prediction markets (Polymarket)", value=True)
chart_days = st.sidebar.slider("Chart history (days)", 5, 90, 30)

# Chart toggles (always available; heavy pieces still gated by buttons)
is_full = True
st.sidebar.caption("Chart detail")
show_forward_curve = st.sidebar.checkbox("Show futures forward curve", value=True, help="Deribit futures at expiry dates.")
show_bull_spreads = st.sidebar.checkbox("Show tight bull spreads on chart", value=True, help="Overlay bull call spreads with R:R.")
show_prediction_spreads = st.sidebar.checkbox("Show prediction-aligned spreads on chart", value=True, help="Spreads tied to Polymarket questions (blue).")
show_options_on_chart = st.sidebar.checkbox("Show options on main chart", value=False, help="Overlay option expiries/strikes.")
options_in_separate_chart = st.sidebar.checkbox("Options in separate chart below", value=True, help="Dedicated options chart.")
option_types_on_chart = st.sidebar.multiselect("Option types", ["call", "put"], default=["call", "put"], key="option_types")
min_prob_label_pct = st.sidebar.slider("Show probability labels above (%)", 0, 50, 5, help="Hide small labels.")

# ---------- Bitcoin section: light load first, heavy data on demand ----------
if show_bitcoin_view:
    st.header("Bitcoin: price, prediction questions & implied value")

    # 1) Light load: Yahoo + Polymarket in parallel (no Deribit)
    btc_prices = None
    events = []
    with ThreadPoolExecutor(max_workers=2) as ex:
        f_yahoo = ex.submit(_cached_yahoo, btc_symbols, f"{chart_days}d")
        f_pm = ex.submit(_cached_polymarket, True, False, 150)
        wait([f_yahoo, f_pm])
        try:
            btc_prices = f_yahoo.result()
        except Exception:
            pass
        try:
            events = f_pm.result() or []
        except Exception as e:
            st.warning(
                f"Polymarket API unavailable ({type(e).__name__}). "
                "Bitcoin chart and other data still work; only Polymarket prediction data is missing."
            )
    if btc_prices is not None and not btc_prices.empty:
        btc_spot = btc_prices[btc_prices["symbol"] == "BTC-USD"]
        btc_fut = btc_prices[btc_prices["symbol"] == "BTC=F"]
    else:
        btc_spot = pd.DataFrame()
        btc_fut = pd.DataFrame()

    keywords = (config.get("prediction_markets") or {}).get("polymarket", {}).get("topic_keywords") or ["bitcoin", "btc"]
    all_probs = markets_to_probabilities(events, topic_keywords=keywords)
    btc_questions = btc_price_questions_from_polymarket(all_probs) if all_probs else []

    current_btc = float(btc_spot["close"].iloc[-1]) if len(btc_spot) else None
    if current_btc is None and len(btc_fut):
        try:
            current_btc = float(btc_fut.sort_values("timestamp")["close"].iloc[-1])
        except Exception:
            pass
    if current_btc is None and is_full:
        try:
            current_btc = _cached_deribit_index()
        except Exception:
            pass
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
            pass

    # Deribit data only when user clicks "Load Deribit data" (Full view)
    load_deribit = st.session_state.get("load_deribit", False)
    if is_full and st.sidebar.button("Load Deribit data (spreads, options)", key="btn_deribit"):
        load_deribit = True
        st.session_state["load_deribit"] = True
    if is_full and load_deribit:
        st.session_state["load_deribit"] = True

    forward_curve = []
    bull_spreads = []
    prediction_spreads = []
    if is_full and load_deribit and current_btc is not None:
        with st.spinner("Loading Deribit (forward curve, spreads, options)…"):
            try:
                forward_curve = _cached_forward_curve(10) or []
            except Exception:
                pass
            try:
                bull_spreads = _cached_bull_spreads(current_btc, 5000.0, 5) or []
            except Exception:
                pass
            if btc_questions:
                try:
                    eligible = [q for q in btc_questions if (q.get("strike") or 0) >= 10000]
                    eligible.sort(key=lambda q: q.get("strike") or 0, reverse=True)
                    prediction_spreads = fetch_deribit_spreads_around_predictions(
                        btc_questions=eligible or btc_questions, current_spot=current_btc, max_questions=8
                    ) or []
                except Exception:
                    pass

    # Toggles: which "will it hit" questions to show on chart
    question_labels = []
    for q in btc_questions:
        s, r = q.get("strike"), q.get("resolution_date")
        if s is not None and r:
            question_labels.append(f"${s:,.0f} by {r}")
    question_labels = list(dict.fromkeys(question_labels))  # preserve order, no dupes
    # Default: fewer questions so chart isn’t crowded (e.g. first 4–5 unique strikes)
    _default = question_labels if len(question_labels) <= 5 else question_labels[:5]
    selected_questions = st.sidebar.multiselect(
        "Price-target questions on chart",
        question_labels,
        default=_default,
        key="chart_questions",
    )
    # Filter to selected: keep q if its label is in selected_questions
    def _q_label(q):
        s, r = q.get("strike"), q.get("resolution_date")
        return f"${s:,.0f} by {r}" if (s is not None and r) else None
    btc_questions_filtered = [q for q in btc_questions if _q_label(q) in selected_questions]

    # 3) Plotly chart: price + overlay of questions + optional options
    fig = go.Figure()
    if not btc_spot.empty:
        btc_spot = btc_spot.sort_values("timestamp")
        fig.add_trace(
            go.Scatter(
                x=btc_spot["timestamp"],
                y=btc_spot["close"],
                name="BTC spot",
                line=dict(color="rgb(247, 147, 26)", width=2),
            )
        )
    # Forward curve and spreads only when Deribit loaded (Full view)
    if is_full and load_deribit and show_forward_curve and forward_curve and current_btc is not None:
        today = pd.Timestamp.now(tz="UTC").normalize()
        x_fwd = [today] + [f["expiry_date"] for f in forward_curve]
        y_fwd = [current_btc] + [f["mark_price"] for f in forward_curve]
        fig.add_trace(
            go.Scatter(
                x=x_fwd,
                y=y_fwd,
                mode="lines+markers",
                name="Futures (forward curve)",
                line=dict(color="rgb(80, 160, 255)", width=2, dash="dot"),
                marker=dict(size=8, symbol="diamond", line=dict(width=1)),
                hovertemplate="%{x|%Y-%m-%d}<br>%{y:,.0f} USD<extra></extra>",
            )
        )
    elif not btc_fut.empty:
        # Fallback: single CME futures series if Deribit forward curve unavailable
        btc_fut = btc_fut.sort_values("timestamp")
        fig.add_trace(
            go.Scatter(
                x=btc_fut["timestamp"],
                y=btc_fut["close"],
                name="BTC futures (CME)",
                line=dict(color="rgb(100, 180, 255)", width=1.5),
            )
        )

    # Options on main chart (Full + Deribit loaded)
    chart_options = []
    if is_full and load_deribit and show_options_on_chart and option_types_on_chart and not options_in_separate_chart:
        try:
            all_opts = _cached_options_for_chart()
            chart_options = [o for o in all_opts if o.get("option_type") in option_types_on_chart]
            # Sample: one point per (expiry, strike_rounded_to_5k) to reduce clutter
            if len(chart_options) > 200:
                by_bucket = {}
                for o in chart_options:
                    exp = o["expiry_date"]
                    strike_bucket = round(o["strike"] / 5000) * 5000
                    key = (exp, strike_bucket, o.get("option_type"))
                    if key not in by_bucket:
                        by_bucket[key] = o
                chart_options = list(by_bucket.values())
        except Exception:
            chart_options = []
    y_vals = []
    if not btc_spot.empty:
        y_vals.extend(btc_spot["close"].dropna().tolist())
    if not btc_fut.empty:
        y_vals.extend(btc_fut["close"].dropna().tolist())
    if forward_curve:
        y_vals.extend([f["mark_price"] for f in forward_curve])
    if current_btc is not None:
        y_vals.append(current_btc)
    strikes = [q.get("strike") for q in btc_questions_filtered if q.get("strike") is not None]
    strikes = strikes + [o["strike"] for o in chart_options]  # only when options on main chart
    if bull_spreads:
        for s in bull_spreads:
            strikes.extend([s["K_low"], s["K_high"]])
    if prediction_spreads:
        for s in prediction_spreads:
            strikes.extend([s["K_low"], s["K_high"]])
    y_max = max(y_vals + strikes) if (y_vals or strikes) else (current_btc or 70000)
    y_min = min(y_vals) if y_vals else (current_btc or 60000) * 0.85
    if strikes:
        y_min = min(y_min, min(strikes) * 0.95)
    y_span = max(y_max - y_min, 1000)

    # Horizontal lines at each strike (e.g. 150k) and probability label on that line at resolution date (filtered)
    seen_strikes = set()
    for q in btc_questions_filtered:
        res = q.get("resolution_date")
        strike = q.get("strike")
        prob = q.get("yes_probability")
        if not res or strike is None or prob is None:
            continue
        try:
            res_ts = pd.Timestamp(res)
        except Exception:
            continue
        # One horizontal line per unique strike
        if strike not in seen_strikes:
            seen_strikes.add(strike)
            fig.add_hline(
                y=strike,
                line_dash="dash",
                line_color="rgba(100, 100, 100, 0.8)",
                annotation_text=f"${strike:,.0f}",
                annotation_position="left",
                annotation_font_size=11,
            )
        # Probability label only if above threshold (reduces 0% / 1% clutter)
        pct = (prob or 0) * 100
        if pct >= min_prob_label_pct:
            fig.add_annotation(
                x=res_ts,
                y=strike,
                text=f"{pct:.0f}% Yes",
                showarrow=False,
                font=dict(size=11, color="darkblue"),
                xanchor="left",
                xshift=5,
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="gray",
                borderwidth=1,
            )
        # Light vertical guide at resolution date (subtle)
        fig.add_vline(x=res_ts, line_dash="dot", line_color="lightgray", opacity=0.35)

    # Prediction-aligned spread overlay (Full + Deribit loaded)
    if is_full and load_deribit and show_prediction_spreads and prediction_spreads:
        for s in prediction_spreads:
            try:
                res_ts = pd.Timestamp(s["resolution_date"][:10])
            except Exception:
                continue
            k_lo, k_hi = s["K_low"], s["K_high"]
            rr = s.get("rr_ratio") or 0
            pm_pct = s.get("polymarket_yes_pct") or 0
            opt_pct = s.get("approx_implied_prob_pct")
            lbl = f"{k_lo/1000:.0f}k/{k_hi/1000:.0f}k R:R 1:{rr:.1f}"
            if opt_pct is not None:
                lbl += f" | opt~{opt_pct:.0f}%"
            fig.add_shape(
                type="line",
                x0=res_ts, x1=res_ts, y0=k_lo, y1=k_hi,
                line=dict(color="rgba(50, 100, 200, 0.75)", width=4, dash="solid"),
            )
            fig.add_annotation(
                x=res_ts, y=(k_lo + k_hi) / 2,
                text=lbl,
                showarrow=False, font=dict(size=9), xanchor="left", xshift=6,
                bgcolor="rgba(200,220,255,0.9)", bordercolor="blue", borderwidth=1,
            )

    # Bull spread overlay (Full + Deribit loaded)
    if is_full and load_deribit and show_bull_spreads and bull_spreads:
        for s in bull_spreads:
            exp = s["expiry_date"]
            k_lo, k_hi = s["K_low"], s["K_high"]
            rr = s.get("rr_ratio") or 0
            fig.add_shape(
                type="line",
                x0=exp, x1=exp, y0=k_lo, y1=k_hi,
                line=dict(color="rgba(0, 150, 80, 0.7)", width=4, dash="solid"),
            )
            fig.add_annotation(
                x=exp, y=(k_lo + k_hi) / 2,
                text=f"{k_lo/1000:.0f}k/{k_hi/1000:.0f}k R:R 1:{rr:.1f}",
                showarrow=False, font=dict(size=9), xanchor="left", xshift=6,
                bgcolor="rgba(200,255,200,0.9)", bordercolor="green", borderwidth=1,
            )

    # Options overlay on main chart: only if enabled and not using separate chart; sampled & subtle
    if show_options_on_chart and chart_options and not options_in_separate_chart:
        for opt_type in option_types_on_chart:
            subset = [o for o in chart_options if o.get("option_type") == opt_type]
            if not subset:
                continue
            x = [o["expiry_date"] for o in subset]
            y = [o["strike"] for o in subset]
            color = "rgba(0, 160, 90, 0.45)" if opt_type == "call" else "rgba(200, 70, 70, 0.45)"
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    name=f"Options ({opt_type}s)",
                    marker=dict(size=4, color=color, symbol="diamond-open" if opt_type == "put" else "circle-open", line=dict(width=0.5)),
                    hovertemplate="%{x|%Y-%m-%d}<br>Strike: %{y:,.0f}<extra></extra>",
                )
            )

    fig.update_layout(
        title="BTC price — dashed lines = price targets; labels = probability (filtered by slider)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        yaxis=dict(range=[y_min, y_max + y_span * 0.05]),
        hovermode="x unified",
        height=480,
        margin=dict(b=60),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Separate options chart (Full + Deribit loaded)
    if is_full and load_deribit and options_in_separate_chart and option_types_on_chart:
        with st.expander("Separate options chart (optional)", expanded=False):
            try:
                opts_for_fig = _cached_options_for_chart()
                opts_for_fig = [o for o in opts_for_fig if o.get("option_type") in option_types_on_chart]
                if len(opts_for_fig) > 400:
                    by_bucket = {}
                    for o in opts_for_fig:
                        key = (o["expiry_date"], round(o["strike"] / 2000) * 2000, o.get("option_type"))
                        if key not in by_bucket:
                            by_bucket[key] = o
                    opts_for_fig = list(by_bucket.values())
                if opts_for_fig:
                    fig_opts = go.Figure()
                    for opt_type in option_types_on_chart:
                        subset = [o for o in opts_for_fig if o.get("option_type") == opt_type]
                        if not subset:
                            continue
                        fig_opts.add_trace(
                            go.Scatter(
                                x=[o["expiry_date"] for o in subset],
                                y=[o["strike"] for o in subset],
                                mode="markers",
                                name=f"{opt_type}s",
                                marker=dict(size=5, color="green" if opt_type == "call" else "red", symbol="circle-open" if opt_type == "call" else "diamond-open"),
                                hovertemplate="%{x|%Y-%m-%d}<br>Strike: %{y:,.0f}<extra></extra>",
                            )
                        )
                    fig_opts.update_layout(
                        title="Deribit BTC options — expiry date vs strike",
                        xaxis_title="Expiry",
                        yaxis_title="Strike (USD)",
                        height=320,
                        margin=dict(b=50),
                        showlegend=True,
                        legend=dict(orientation="h"),
                    )
                    st.plotly_chart(fig_opts, use_container_width=True)
            except Exception:
                pass

    with st.expander("Supporting derived tables (optional)", expanded=False):
        # 4) Implied value table + risk/reward for questions
        st.subheader("Implied value: Bitcoin price-target questions (with risk/reward)")
        if btc_questions and current_btc is not None:
            rows = []
            for q in btc_questions:
                strike = q.get("strike") or 0
                prob = q.get("yes_probability") or 0
                # Risk/reward: bet 1 unit on Yes at price p. If Yes get 1/p, profit (1/p - 1). If No lose 1. So risk=1, reward=(1/p)-1, R:R = (1/p - 1) : 1
                reward_if_yes = (1.0 / prob - 1.0) if prob > 0 else 0
                rr_ratio = reward_if_yes  # per 1 unit risk
                rows.append({
                    "Question": (q.get("market_question") or "")[:50] + ("..." if len((q.get("market_question") or "")) > 50 else ""),
                    "Strike ($)": f"{strike:,.0f}",
                    "Yes %": f"{prob*100:.1f}",
                    "Resolution": q.get("resolution_date") or "",
                    "Risk (1 unit)": "1",
                    "Reward if Yes": f"{reward_if_yes:.2f}",
                    "R:R": f"1:{rr_ratio:.2f}",
                    "Spread vs spot": f"{strike - current_btc:,.0f}",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No Bitcoin price-target questions parsed from Polymarket, or no spot price.")

        # 4b) Tight bull spreads table — only when Deribit loaded
        if is_full and load_deribit:
            st.subheader("Tight bull spreads (Deribit) — risk/reward")
        if is_full and load_deribit and bull_spreads:
            spread_rows = []
            for s in bull_spreads:
                spread_rows.append({
                    "Expiry": s["expiry_date"].strftime("%Y-%m-%d") if hasattr(s["expiry_date"], "strftime") else str(s["expiry_date"])[:10],
                    "K_low": f"{s['K_low']:,.0f}",
                    "K_high": f"{s['K_high']:,.0f}",
                    "Cost (USD)": f"{s['cost_usd']:,.0f}",
                    "Max loss": f"{s['max_loss']:,.0f}",
                    "Max gain": f"{s['max_gain']:,.0f}",
                    "R:R": f"1:{s['rr_ratio']:.2f}",
                })
            st.dataframe(pd.DataFrame(spread_rows), use_container_width=True, hide_index=True)
        elif is_full and load_deribit:
            st.caption("No tight bull spreads (Deribit calls). Check spot price and API.")

        # 4c) Spreads around predictions — only when Deribit loaded
        if is_full and load_deribit:
            st.subheader("Spreads around predictions — Polymarket vs options")
        if is_full and load_deribit and prediction_spreads:
            pred_rows = []
            for s in prediction_spreads:
                pred_rows.append({
                    "Target": f"${s['target']:,.0f}",
                    "Resolution": s["resolution_date"][:10],
                    "Polymarket Yes %": f"{s.get('polymarket_yes_pct', 0):.1f}",
                    "Spread": f"{s['K_low']/1000:.0f}k/{s['K_high']/1000:.0f}k",
                    "Cost (USD)": f"{s['cost_usd']:,.0f}",
                    "R:R": f"1:{s['rr_ratio']:.2f}",
                    "Opt ~implied %": f"{s.get('approx_implied_prob_pct') or 0:.1f}" if s.get("approx_implied_prob_pct") is not None else "—",
                })
            st.dataframe(pd.DataFrame(pred_rows), use_container_width=True, hide_index=True)
            st.caption("Opt ~implied % = approximate from spread cost (simplified). Compare to Polymarket Yes %.")
        elif is_full and load_deribit:
            st.caption("No prediction-aligned spreads (need Polymarket questions + Deribit options at matching strikes/expiries).")

    if is_full and not load_deribit:
        st.info("To see Deribit spreads, forward curve, and options on the chart, click **Load Deribit data (spreads, options)** in the sidebar.")

    # 4d) Implied probability distribution — on demand (Full view only)
    run_implied = st.session_state.get("run_implied", False)
    if is_full and st.sidebar.button("Run implied distribution & strategies", key="btn_implied"):
        st.session_state["run_implied"] = True
        run_implied = True
    if is_full:
        run_implied = st.session_state.get("run_implied", False)
    if is_full and load_deribit and not run_implied:
        st.info("Click **Run implied distribution & strategies** in the sidebar to see the probability distribution chart and strategy scanner.")
    if is_full and run_implied:
        st.subheader("Implied probability distribution")
        with st.expander("How to read this chart"):
            st.markdown("""
        - **Purple (filled):** Lognormal distribution from the **forward price** and **ATM implied volatility** — the standard model for “where price might be” at expiry.
        - **Orange (dashed):** **Market-implied** distribution from option prices (Breeden–Litzenberger). When it diverges from the purple curve, the chart is marked **Anomalous**.
        - **Green line (if selected):** **Strategy P&amp;L** at expiry (right axis). At each price level, this is your net profit or loss if you hold that strategy. Negative = loss (e.g. premium paid), positive = profit.
        - **Strikes** for the strategy scanner are chosen from available Deribit options: ATM = strike nearest the forward; spreads use the nearest strikes around the forward so the payoff is relevant to current pricing.
            """)
        st.caption("Risk-neutral distribution for BTC at expiry (lognormal from Deribit forward + ATM IV).")

    if is_full and run_implied and current_btc is not None:
        try:
            with st.spinner("Loading expiries and option marks…"):
                expiries = _cached_option_expiries(10)
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
                        right_summary_slot = st.empty()
                        # Dedicated slots: reusing one st.empty() for plot + text replaces the chart (Streamlit replaces slot content).
                        right_chart_slot = st.empty()
                        right_anomaly_slot = st.empty()
                        right_forward_slot = st.empty()
                        right_belief_slot = st.empty()
                    with col_controls:
                        # Only fetch data for the selected expiry to keep this step fast.
                        fwd_iv = _cached_forward_iv(selected["expiry_ts"], current_btc)
                        forward = (fwd_iv.get("forward") or current_btc) if fwd_iv else current_btc
                        vol = (fwd_iv.get("atm_iv") or 0.6) if fwd_iv else 0.6
                        if vol <= 0:
                            vol = 0.6
                        now_ts = pd.Timestamp.now(tz="UTC").timestamp() * 1000
                        T_years = max(0.0, (selected["expiry_ts"] - now_ts) / 1000 / (365.25 * 24 * 3600))
                        # Avoid degenerate near-zero T: use at least ~1 week so the bell is visible
                        T_years = max(T_years, 0.02)
                        price_min = max(1000, forward * 0.4)
                        price_max = forward * 2.2
                        data = build_distribution_chart_data(
                            forward=forward,
                            vol_annual=vol,
                            T_years=T_years,
                            price_min=price_min,
                            price_max=price_max,
                            num_points=100,
                        )
                        # One book summary for both chart and strategy scanner
                        marks_full = _cached_marks_full(selected["expiry_ts"])
                        call_marks = marks_full.get("calls") or []
                        put_marks = marks_full.get("puts") or []
                        base_strategy = build_universal_strategy(forward, call_marks, put_marks)
                        # Restore last exact-strike shape for this expiry if present
                        shape_key = f"u4_shape_{selected_expiry_str}"
                        shape_state = st.session_state.get(shape_key, {})
                        avail_strikes = sorted(set(m["strike"] for m in call_marks + put_marks))
                        call_by_k = {m["strike"]: float(m.get("mark_btc") or 0) for m in call_marks}
                        put_by_k = {m["strike"]: float(m.get("mark_btc") or 0) for m in put_marks}

                        # Separate user state vs market_data (Sprint 1A contract)
                        market_data = {
                            "forward": forward,
                            "vol": vol,
                            "T_years": T_years,
                            "price_min": price_min,
                            "price_max": price_max,
                            "dist": data,
                            "marks_full": marks_full,
                            "call_marks": call_marks,
                            "put_marks": put_marks,
                            "avail_strikes": avail_strikes,
                            "call_by_k": call_by_k,
                            "put_by_k": put_by_k,
                        }
                        # Sprint 2A: user belief overlay (orthogonal to strike / payoff mode)
                        belief_exp = selected_expiry_str
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
                            st.slider(
                                "Uncertainty (σ of ln price at expiry)",
                                0.02,
                                0.8,
                                0.2,
                                0.01,
                                key=f"belief_width_{belief_exp}",
                                help="Larger σ = fatter tails / wider distribution. Compared to ATM-implied σ≈√T × IV.",
                            )
                        user_belief_for_state = {
                            "enabled": bool(st.session_state.get(f"belief_en_{belief_exp}", False)),
                            "center_usd": float(st.session_state.get(f"belief_center_{belief_exp}", forward)),
                            "width": float(st.session_state.get(f"belief_width_{belief_exp}", 0.2)),
                        }
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

                            # Mode ownership (Sprint 1A): exact strikes vs target payoff
                            mode_key = f"implied_lab_mode_{selected_expiry_str}"
                            # Important: do not pass a computed `index` derived from session_state.
                            # Streamlit can treat the widget as "already initialized" and keep it effectively locked.
                            mode = st.radio(
                                "Mode",
                                ["Exact strikes", "Target payoff"],
                                key=mode_key,
                                horizontal=True,
                            )
                            mode_norm = "exact_strikes" if mode == "Exact strikes" else "target_payoff"

                            # Defaults for strike truth (from persisted exact-strike state)
                            k1d = shape_state.get("k1") or min(avail_strikes)
                            k2d = shape_state.get("k2") or atm
                            k3d = shape_state.get("k3") or atm
                            k4d = shape_state.get("k4") or max(avail_strikes)
                            k1d = min(avail_strikes, key=lambda k: abs(k - k1d))
                            k2d = min(avail_strikes, key=lambda k: abs(k - k2d))
                            k3d = min(avail_strikes, key=lambda k: abs(k - k3d))
                            k4d = min(avail_strikes, key=lambda k: abs(k - k4d))
                            if not (k1d <= k2d <= k3d <= k4d):
                                k2d, k3d, k4d = max(k2d, k1d), max(k3d, k2d), max(k4d, k3d)

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
                                    st.session_state[payoff_targets_key] = {
                                        "body_left": float(body_left),
                                        "body_right": float(body_right),
                                        "left_wing": float(left_wing_usd),
                                        "right_wing": float(right_wing_usd),
                                    }

                            # --- Adjust strategy shape (editable truth only in exact_strikes mode) ---
                            with st.expander("Adjust strategy shape", expanded=True):
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
                                k1_sel = min(avail_strikes, key=lambda k: abs(k - int(k1_input)))
                                k2_sel = min(avail_strikes, key=lambda k: abs(k - int(k2_input)))
                                k3_sel = min(avail_strikes, key=lambda k: abs(k - int(k3_input)))
                                k4_sel = min(avail_strikes, key=lambda k: abs(k - int(k4_input)))
                                if k4_sel < k3_sel:
                                    k4_sel = k3_sel
                                # Enforce ordering again after any numeric overrides
                                if not (k1_sel <= k2_sel <= k3_sel <= k4_sel):
                                    k2_sel = max(k2_sel, k1_sel)
                                    k3_sel = max(k3_sel, k2_sel)
                                    k4_sel = max(k4_sel, k3_sel)
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
                            state = build_implied_lab_state(
                                expiry_str=selected_expiry_str,
                                mode=mode_norm,
                                qty=int(qty),
                                strikes_exact=strikes_exact,
                                payoff_targets=payoff_targets,
                                legs_enabled={"use_k1": use_k1, "use_k2": use_k2, "use_k3": use_k3, "use_k4": use_k4},
                                reverse=reverse,
                                net_pnl_mode=bool(net_pnl_mode),
                                user_belief=user_belief_for_state,
                            )
                            outputs = derive_lab_outputs(state, market_data)
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
                            state_min = build_implied_lab_state(
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
                            )
                            outputs = derive_lab_outputs(state_min, market_data)
                            selected_strategy = base_strategy
                    # Everything below (distribution chart, summary, scanner) goes in the chart column
                    if not avail_strikes:
                        right_summary_slot.info("No option strikes for this expiry — the strategy overlay is unavailable.")

                    # Compact "at a glance" trade summary (Sprint 1B)
                    be_preview = ", ".join(f"{be:,.0f}" for be in breakevens[:3]) if breakevens else "—"
                    cost_label = f"{cost_usd:,.0f} USD" if isinstance(cost_usd, (int, float)) else "—"
                    dc_label = debit_credit.title() if debit_credit in ("debit", "credit") else "—"
                    right_summary_slot.info(
                        f"**{strategy_name}**\n\n"
                        f"- **{dc_label}**: {cost_label}\n"
                        f"- **Max gain**: {float(max_gain):,.0f} USD\n"
                        f"- **Max loss**: {float(max_loss):,.0f} USD\n"
                        f"- **Breakevens**: {be_preview} USD"
                    )

                    call_marks = marks_full.get("calls") or []
                    market_pdf_raw = []
                    anomalous = False
                    if len(call_marks) >= 3:
                        strikes = [m["strike"] for m in call_marks]
                        call_usd = [m["mark_btc"] * forward for m in call_marks]
                        market_pdf_raw = market_implied_density_breeden_litzenberger(
                            strikes, call_usd, data["prices"]
                        )
                        if market_pdf_raw:
                            anomalous = is_anomalous(
                                data["prices"], data["pdf_raw"], market_pdf_raw, threshold=0.015
                            )
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
                    if market_pdf_raw:
                        max_mkt = max(market_pdf_raw) if market_pdf_raw else 1.0
                        market_pct = [(d / max_mkt * 25.0) if max_mkt > 0 else 0.0 for d in market_pdf_raw]
                        fig_dist.add_trace(
                            go.Scatter(
                                x=data["prices"],
                                y=market_pct,
                                mode="lines",
                                name="Market-implied (options)",
                                line=dict(color="rgba(255, 140, 0, 0.9)", width=2, dash="dash"),
                            )
                        )
                    user_belief_pct = (outputs.get("chart_helpers") or {}).get("user_belief_pct") or []
                    if (
                        user_belief_pct
                        and len(user_belief_pct) == len(data["prices"])
                    ):
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
                    payoff_usd = []
                    if selected_strategy and selected_strategy.get("k1") is not None:
                        payoff_usd = [qty * p for p in strategy_payoff_at_prices(selected_strategy, data["prices"])]
                        fig_dist.add_trace(
                            go.Scatter(
                                x=data["prices"],
                                y=payoff_usd,
                                mode="lines",
                                name=f"Payoff: {selected_strategy.get('name', 'Universal 4-leg')}",
                                line=dict(color="rgba(34, 139, 34, 0.9)", width=2),
                                yaxis="y2",
                            )
                        )
                    layout_kw = {
                        "title": title,
                        "xaxis_title": "Underlying price (USD)",
                        "yaxis_title": "Probability (scaled)",
                        "height": 340,
                        "margin": dict(b=40),
                        "showlegend": True,
                        "xaxis": dict(tickformat=",d", gridcolor="rgba(128,128,128,0.2)"),
                        "yaxis": dict(ticksuffix="%", range=[0, 30], gridcolor="rgba(128,128,128,0.2)"),
                    }
                    if selected_strategy and selected_strategy.get("k1") is not None:
                        layout_kw["yaxis2"] = dict(
                            title="Strategy P&L (USD)",
                            overlaying="y",
                            side="right",
                            showgrid=False,
                        )
                    fig_dist.update_layout(**layout_kw)
                    # Cumulative % labels below x-axis (y in paper coords, 0–1)
                    for price, cdf_pct in data["cumulative_at"]:
                        fig_dist.add_annotation(
                            x=price,
                            y=-0.06,
                            text=f"{cdf_pct:.1f}%",
                            showarrow=False,
                            yref="paper",
                            font=dict(size=9),
                        )
                    right_chart_slot.plotly_chart(fig_dist, use_container_width=True)
                    if anomalous:
                        right_anomaly_slot.warning(
                            "Anomalous: market-implied distribution differs from lognormal (use multi-leg strategies to reshape)."
                        )
                    right_forward_slot.caption(f"Forward ${forward:,.0f} · ATM IV {vol*100:.1f}% · T = {T_years:.2f} yr")
                    belief_txt = (outputs.get("belief_summary") or {}).get("text") or ""
                    if belief_txt:
                        right_belief_slot.markdown(belief_txt)

                    # Quick summary and payout stats under sliders
                    if selected_strategy and selected_strategy.get("k1") is not None:
                        name = selected_strategy.get("name", "Universal 4-leg")
                        cost = selected_strategy.get("cost_usd", 0.0)
                        wings = []
                        if selected_strategy.get("use_k1", True):
                            wings.append("left")
                        if selected_strategy.get("use_k4", True):
                            wings.append("right")
                        wings_txt = "both wings" if len(wings) == 2 else (wings[0] + " wing" if wings else "no wings")
                        # Derive simple stats from payoff curve (per total qty)
                        max_gain = max(payoff_usd) if payoff_usd else 0.0
                        max_loss = min(payoff_usd) if payoff_usd else 0.0
                        # breakevens = price levels where sign changes
                        breakevens = []
                        if payoff_usd:
                            for i in range(1, len(payoff_usd)):
                                if payoff_usd[i - 1] == 0:
                                    breakevens.append(data["prices"][i - 1])
                                elif payoff_usd[i] == 0:
                                    breakevens.append(data["prices"][i])
                                elif payoff_usd[i - 1] * payoff_usd[i] < 0:
                                    # linear interpolation between grid points
                                    x0, x1 = data["prices"][i - 1], data["prices"][i]
                                    y0, y1 = payoff_usd[i - 1], payoff_usd[i]
                                    if y1 != y0:
                                        x_be = x0 + (0 - y0) * (x1 - x0) / (y1 - y0)
                                        breakevens.append(x_be)
                        if breakevens:
                            be_txt = " · Breakeven" + ("s " if len(breakevens) > 1 else " ") + ", ".join(f"{be:,.0f}" for be in breakevens[:3])
                        else:
                            be_txt = ""
                        st.caption(
                            f"**Current shape:** {name} · Cost ≈ "
                            f"{cost:,.0f} USD ({'debit' if cost >= 0 else 'credit'}) · {wings_txt} active."
                            f" · Max gain ≈ {max_gain:,.0f} · Max loss ≈ {max_loss:,.0f}{be_txt}."
                        )

                    # Strategy analysis: single universal 4-leg — show named strategy and summary table
                    st.subheader("Strategy analysis")
                    if selected_strategy and selected_strategy.get("k1") is not None:
                        name = selected_strategy.get("name", "Universal 4-leg")
                        cost = selected_strategy.get("cost_usd", 0)
                        st.dataframe(
                            pd.DataFrame([{
                                "Strategy": name,
                                "Cost (USD)": f"{cost:,.0f}" if cost >= 0 else f"-{abs(cost):,.0f}",
                                "Legs": selected_strategy.get("legs_desc", ""),
                            }]),
                            use_container_width=True,
                            hide_index=True,
                        )
                        # Export-style trade ticket summary
                        side_put1 = "Long" if selected_strategy.get("long_k1", False) else "Short"
                        side_put2 = "Long" if selected_strategy.get("long_k2", True) else "Short"
                        side_call3 = "Long" if selected_strategy.get("long_k3", True) else "Short"
                        side_call4 = "Long" if selected_strategy.get("long_k4", False) else "Short"
                        k1 = selected_strategy.get("k1")
                        k2 = selected_strategy.get("k2")
                        k3 = selected_strategy.get("k3")
                        k4 = selected_strategy.get("k4")
                        # Per-leg mark in USD (per 1x)
                        prem_k1 = put_by_k.get(k1, 0.0) * forward if k1 is not None else 0.0
                        prem_k2 = put_by_k.get(k2, 0.0) * forward if k2 is not None else 0.0
                        prem_k3 = call_by_k.get(k3, 0.0) * forward if k3 is not None else 0.0
                        prem_k4 = call_by_k.get(k4, 0.0) * forward if k4 is not None else 0.0
                        with st.expander("Trade ticket (copy/paste)", expanded=False):
                            st.code(
                                f"Expiry: {selected_expiry_str}\n"
                                f"Size: {qty}x\n"
                                f"{side_put1} {qty} PUT @ {k1:,.0f}  (≈ {prem_k1:,.0f} USD per 1x)\n"
                                f"{side_put2} {qty} PUT @ {k2:,.0f}  (≈ {prem_k2:,.0f} USD per 1x)\n"
                                f"{side_call3} {qty} CALL @ {k3:,.0f} (≈ {prem_k3:,.0f} USD per 1x)\n"
                                f"{side_call4} {qty} CALL @ {k4:,.0f} (≈ {prem_k4:,.0f} USD per 1x)\n"
                                f"Net premium: {cost:,.0f} USD ({'debit' if cost >= 0 else 'credit'})\n"
                                f"Max gain (approx): {max_gain:,.0f} USD\n"
                                f"Max loss (approx): {max_loss:,.0f} USD\n"
                                + (f"Breakevens: {', '.join(f'{be:,.0f}' for be in breakevens[:3])} USD\n" if breakevens else ""),
                                language="text",
                            )

                            # Calculation breakdown: show how we get cost, max gain/loss, breakevens
                            with st.expander("**Show calculations**", expanded=False):
                                u1 = 1 if selected_strategy.get("use_k1", True) else 0
                                u2 = 1 if selected_strategy.get("use_k2", True) else 0
                                u3 = 1 if selected_strategy.get("use_k3", True) else 0
                                u4 = 1 if selected_strategy.get("use_k4", True) else 0
                                sign1 = (1 if selected_strategy.get("long_k1", False) else -1) * u1
                                sign2 = (1 if selected_strategy.get("long_k2", True) else -1) * u2
                                sign3 = (1 if selected_strategy.get("long_k3", True) else -1) * u3
                                sign4 = (1 if selected_strategy.get("long_k4", False) else -1) * u4
                                c1 = sign1 * prem_k1
                                c2 = sign2 * prem_k2
                                c3 = sign3 * prem_k3
                                c4 = sign4 * prem_k4
                                st.markdown("**1. Net cost (premium)**")
                                st.markdown("Per leg we use mark × forward (USD). Long = you pay (+), short = you receive (−).")
                                st.latex(r"\text{Cost} = \sum_{\text{legs}} (\pm \text{premium})")
                                lines = []
                                if u1:
                                    lines.append(f"K1 put ({side_put1}): {sign1:+.0f} × {prem_k1:,.0f} = {c1:+,.0f} USD")
                                if u2:
                                    lines.append(f"K2 put ({side_put2}): {sign2:+.0f} × {prem_k2:,.0f} = {c2:+,.0f} USD")
                                if u3:
                                    lines.append(f"K3 call ({side_call3}): {sign3:+.0f} × {prem_k3:,.0f} = {c3:+,.0f} USD")
                                if u4:
                                    lines.append(f"K4 call ({side_call4}): {sign4:+.0f} × {prem_k4:,.0f} = {c4:+,.0f} USD")
                                st.code("\n".join(lines), language="text")
                                sum_txt = " + ".join(f"{x:+,.0f}" for x in [c1, c2, c3, c4])
                                st.markdown(f"**Net cost = " + sum_txt + f" = {cost:,.0f} USD** ({'debit' if cost >= 0 else 'credit'})")
                                st.markdown("**2. Max gain / max loss**")
                                st.markdown("We evaluate the 4-leg payoff at each price on the chart (same formula as the green line). Max gain = highest point, max loss = lowest point.")
                                st.markdown(f"- **Max gain** = max(payoff curve) ≈ **{max_gain:,.0f} USD**")
                                st.markdown(f"- **Max loss** = min(payoff curve) ≈ **{max_loss:,.0f} USD**")
                                st.markdown("**3. Breakevens**")
                                if breakevens:
                                    st.markdown("Prices where the payoff curve crosses zero (we find sign changes between adjacent grid points and interpolate).")
                                    st.markdown(f"**Breakevens:** " + ", ".join(f"{be:,.0f} USD" for be in breakevens[:3]))
                                else:
                                    st.markdown("Payoff curve does not cross zero in the chart range (always profit or always loss).")
                    else:
                        if avail_strikes:
                            st.caption("Set strikes in the **left column** (open **Adjust strategy shape**) to see payoff and name above.")
                        else:
                            st.caption("No strikes available for this expiry; load Deribit data and choose an expiry with options.")
            else:
                st.caption("No Deribit option expiries. Check API.")
        except Exception as e:
            st.caption(f"Implied distribution unavailable: {e}")
            with st.expander("Debug (last error)", expanded=False):
                st.markdown(f"**Exception type:** `{type(e).__name__}`")
                st.markdown(f"**Message:** `{e!s}`")
                st.code(traceback.format_exc(), language="text")
    elif is_full and run_implied and current_btc is None:
        st.caption("Need BTC spot price for implied distribution.")

    # 5) BTC options & futures summary — only when Deribit loaded
    if is_full and load_deribit:
        with st.expander("BTC options & futures (reference)", expanded=False):
            st.subheader("BTC options & futures")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("**Futures**")
                if forward_curve:
                    st.metric("Forward curve (Deribit)", f"{len(forward_curve)} expiries", None)
                    st.caption("Chart: spot → today, then points at each expiry (see into the future).")
                elif not btc_fut.empty:
                    last = btc_fut.sort_values("timestamp").iloc[-1]
                    st.metric("BTC=F (CME) last", f"${last['close']:,.2f}", None)
                else:
                    st.caption("Futures: enable Deribit forward curve or Yahoo BTC=F.")
            with col2:
                st.markdown("**Options (Yahoo)**")
                opt_sum = _cached_btc_options_summary()
                if opt_sum.get("available"):
                    st.metric("Nearest expiry", opt_sum.get("nearest_expiry", "—"), None)
                    st.caption(f"Calls: {opt_sum.get('calls_count', 0)}, Puts: {opt_sum.get('puts_count', 0)}")
                else:
                    st.caption("Options for BTC-USD often unavailable from Yahoo. Use Deribit below.")
            with col3:
                st.markdown("**Options (Deribit)**")
                deribit = _cached_deribit_summary(12)
                if deribit.get("available"):
                    st.metric("BTC options", f"{deribit.get('total_count', 0)} total", None)
                    st.caption(f"Calls: {deribit.get('calls_count', 0)}, Puts: {deribit.get('puts_count', 0)}")
                    if deribit.get("expiries"):
                        st.caption("Expiries: " + ", ".join(deribit["expiries"][:5]) + ("…" if len(deribit["expiries"]) > 5 else ""))
                else:
                    st.caption("Deribit API unavailable. Check network.")

            if deribit.get("sample"):
                with st.expander("Deribit BTC options sample (nearest expiry, mark price)"):
                    sample_df = pd.DataFrame(deribit["sample"])
                    if not sample_df.empty:
                        sample_df = sample_df.rename(columns={"instrument": "Instrument", "strike": "Strike", "type": "Type", "mark_price": "Mark ($)"})
                        def _fmt_mark(v):
                            if v is None or (isinstance(v, float) and pd.isna(v)):
                                return "—"
                            try:
                                return f"{float(v):,.2f}"
                            except (TypeError, ValueError):
                                return "—"
                        sample_df["Mark ($)"] = sample_df["Mark ($)"].apply(_fmt_mark)
                        sample_df["Strike"] = sample_df["Strike"].apply(lambda x: f"{x:,.0f}" if x is not None and pd.notna(x) else "—")
                        st.dataframe(sample_df[["Instrument", "Strike", "Type", "Mark ($)"]], use_container_width=True, hide_index=True)

    st.divider()

# ---------- Original market prices (all assets) ----------
if show_markets:
    with st.expander("Market prices (reference)", expanded=False):
        st.subheader("Market prices (Gold, Silver, Bitcoin)")
        symbols = (config.get("markets") or {}).get("yahoo", {}).get("symbols")
        df = _cached_yahoo(symbols, "5d")
        if df is not None and not df.empty:
            latest = df.sort_values("timestamp").groupby("symbol").last().reset_index()
            st.dataframe(latest[["symbol", "asset", "close", "timestamp"]].style.format({"close": "{:.2f}"}), use_container_width=True)
            st.line_chart(
                df.set_index("timestamp").pivot(columns="symbol", values="close").dropna(how="all")
            )
        else:
            st.info("No market data returned. Check symbols and network.")

if show_polymarket:
    with st.expander("Prediction markets (reference)", expanded=False):
        st.subheader("Prediction markets (Polymarket)")
        keywords = (config.get("prediction_markets") or {}).get("polymarket", {}).get("topic_keywords") or ["bitcoin", "gold", "silver"]
        events = []
        polymarket_failed = False
        try:
            events = _cached_polymarket(True, False, 100)
        except Exception as e:
            polymarket_failed = True
            st.warning(
                f"Polymarket API unavailable ({type(e).__name__}). "
                "The rest of the app works; only prediction market data is missing. Try again later or check your network."
            )
        probs = markets_to_probabilities(events, topic_keywords=keywords) if events else []
        if probs:
            pm_df = pd.DataFrame(probs)
            st.dataframe(
                pm_df[["event_title", "market_question", "outcome", "probability", "end_date_iso"]].head(50),
                use_container_width=True,
            )
        elif polymarket_failed:
            st.caption("Prediction market data will appear here once Polymarket is reachable.")
        else:
            st.info("No matching Polymarket events. Try adjusting topic_keywords in config/sources.yaml.")

st.sidebar.caption("Phase 1: data ingest. Next: canonical events → probabilities → opportunities.")
