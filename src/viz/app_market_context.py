"""
Market-context (reference-only) expander extracted from `src/viz/app.py`.

This module intentionally preserves Streamlit widget keys and UI behavior so the
extraction remains behavior-neutral.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait
from typing import Any, Callable

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.data.fetch_polymarket import markets_to_probabilities
from src.data.parse_btc_markets import btc_price_questions_from_polymarket
from src.data.fetch_deribit import fetch_deribit_spreads_around_predictions


def _q_label(q: dict) -> str | None:
    s, r = q.get("strike"), q.get("resolution_date")
    return f"${s:,.0f} by {r}" if (s is not None and r) else None


def render_market_context_expander(
    *,
    config: dict[str, Any],
    btc_symbols: dict[str, list[str]],
    chart_days: int,
    # Cached callables (existing wrappers from app_cache).
    cached_yahoo: Callable[[Any, str], pd.DataFrame],
    cached_polymarket: Callable[[bool, bool, int], list[dict[str, Any]]],
    cached_forward_curve: Callable[[int], list[dict[str, Any]]],
    cached_option_instruments: Callable[[], Any],
    cached_option_book_marks: Callable[[], Any],
    cached_bull_spreads: Callable[[float, float, int], list[dict[str, Any]]],
    cached_options_for_chart: Callable[[], list[dict[str, Any]]],
    # State / toggles from sidebar + session.
    is_full: bool,
    load_deribit: bool,
    current_btc: float | None,
    show_forward_curve: bool,
    show_bull_spreads: bool,
    show_prediction_spreads: bool,
    show_options_on_chart: bool,
    options_in_separate_chart: bool,
    option_types_on_chart: list[str],
    min_prob_label_pct: int,
) -> None:
    # Demoted context (price/prediction framing should not dominate first screen).
    with st.expander(
        "Market context (price chart + prediction questions) — reference only",
        expanded=False,
    ):
        # 1) Light load: Yahoo + Polymarket in parallel (no Deribit)
        btc_prices = None
        events: list[dict[str, Any]] = []
        with ThreadPoolExecutor(max_workers=2) as ex:
            f_yahoo = ex.submit(cached_yahoo, btc_symbols, f"{chart_days}d")
            f_pm = ex.submit(cached_polymarket, True, False, 150)
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

        keywords = (
            (config.get("prediction_markets") or {})
            .get("polymarket", {})
            .get("topic_keywords")
            or ["bitcoin", "btc"]
        )
        all_probs = markets_to_probabilities(events, topic_keywords=keywords)
        btc_questions = btc_price_questions_from_polymarket(all_probs) if all_probs else []

        # Deribit context overlays (only when user refreshes priced inputs).
        forward_curve: list[dict[str, Any]] = []
        bull_spreads: list[dict[str, Any]] = []
        prediction_spreads: list[dict[str, Any]] = []
        if is_full and load_deribit and current_btc is not None:
            with st.spinner("Loading Deribit (forward curve, spreads, options)…"):
                try:
                    with ThreadPoolExecutor(max_workers=3) as ex:
                        f_fwd = ex.submit(cached_forward_curve, 10)
                        f_inst = ex.submit(cached_option_instruments)
                        f_marks = ex.submit(cached_option_book_marks)
                        wait([f_fwd, f_inst, f_marks])
                        forward_curve = f_fwd.result() or []
                        _ = f_inst.result()
                        _ = f_marks.result()
                except Exception:
                    pass
                try:
                    bull_spreads = cached_bull_spreads(current_btc, 5000.0, 5) or []
                except Exception:
                    pass
                if btc_questions:
                    try:
                        eligible = [q for q in btc_questions if (q.get("strike") or 0) >= 10000]
                        eligible.sort(key=lambda q: q.get("strike") or 0, reverse=True)
                        prediction_spreads = fetch_deribit_spreads_around_predictions(
                            btc_questions=eligible or btc_questions,
                            current_spot=current_btc,
                            max_questions=8,
                            instruments=cached_option_instruments(),
                            option_book_marks=cached_option_book_marks(),
                        ) or []
                    except Exception:
                        pass

        # Toggles: which "will it hit" questions to show on chart (local to this expander)
        question_labels: list[str] = []
        for q in btc_questions:
            s, r = q.get("strike"), q.get("resolution_date")
            if s is not None and r:
                question_labels.append(f"${s:,.0f} by {r}")
        question_labels = list(dict.fromkeys(question_labels))  # preserve order, no dupes
        _default = question_labels if len(question_labels) <= 5 else question_labels[:5]
        selected_questions = st.multiselect(
            "Price-target questions on chart",
            question_labels,
            default=_default,
            key="chart_questions",
            help="Optional overlay for context; this is not the implied-lab anchor.",
        )

        btc_questions_filtered = [
            q for q in btc_questions if _q_label(q) in selected_questions
        ]

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
        chart_options: list[dict[str, Any]] = []
        if (
            is_full
            and load_deribit
            and show_options_on_chart
            and option_types_on_chart
            and not options_in_separate_chart
        ):
            try:
                all_opts = cached_options_for_chart()
                chart_options = [
                    o for o in all_opts if o.get("option_type") in option_types_on_chart
                ]
                if len(chart_options) > 200:
                    by_bucket: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
                    for o in chart_options:
                        exp = o["expiry_date"]
                        strike_bucket = round(o["strike"] / 5000) * 5000
                        key = (exp, strike_bucket, o.get("option_type"))
                        if key not in by_bucket:
                            by_bucket[key] = o
                    chart_options = list(by_bucket.values())
            except Exception:
                chart_options = []

        y_vals: list[float] = []
        if not btc_spot.empty:
            y_vals.extend(btc_spot["close"].dropna().tolist())
        if not btc_fut.empty:
            y_vals.extend(btc_fut["close"].dropna().tolist())
        if forward_curve:
            y_vals.extend([float(f["mark_price"]) for f in forward_curve])
        if current_btc is not None:
            y_vals.append(float(current_btc))
        strikes = [q.get("strike") for q in btc_questions_filtered if q.get("strike") is not None]
        strikes = strikes + [o["strike"] for o in chart_options]
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

        # Horizontal lines at each strike and probability labels at resolution dates.
        seen_strikes: set[float] = set()
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

        # Options overlay on main chart (sampled & subtle)
        if show_options_on_chart and chart_options and not options_in_separate_chart:
            for opt_type in option_types_on_chart:
                subset = [o for o in chart_options if o.get("option_type") == opt_type]
                if not subset:
                    continue
                x = [o["expiry_date"] for o in subset]
                y = [o["strike"] for o in subset]
                color = (
                    "rgba(0, 160, 90, 0.45)"
                    if opt_type == "call"
                    else "rgba(200, 70, 70, 0.45)"
                )
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode="markers",
                        name=f"Options ({opt_type}s)",
                        marker=dict(
                            size=4,
                            color=color,
                            symbol="diamond-open" if opt_type == "put" else "circle-open",
                            line=dict(width=0.5),
                        ),
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
                    opts_for_fig = cached_options_for_chart()
                    opts_for_fig = [
                        o for o in opts_for_fig if o.get("option_type") in option_types_on_chart
                    ]
                    if len(opts_for_fig) > 400:
                        by_bucket: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
                        for o in opts_for_fig:
                            key = (
                                o["expiry_date"],
                                round(o["strike"] / 2000) * 2000,
                                o.get("option_type"),
                            )
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
                                    marker=dict(
                                        size=5,
                                        color="green" if opt_type == "call" else "red",
                                        symbol="circle-open"
                                        if opt_type == "call"
                                        else "diamond-open",
                                    ),
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
            st.subheader("Implied value: Bitcoin price-target questions (with risk/reward)")
            if btc_questions and current_btc is not None:
                rows: list[dict[str, Any]] = []
                for q in btc_questions:
                    strike = q.get("strike") or 0
                    prob = q.get("yes_probability") or 0
                    reward_if_yes = (1.0 / prob - 1.0) if prob > 0 else 0
                    rr_ratio = reward_if_yes
                    rows.append(
                        {
                            "Question": (q.get("market_question") or "")[:50]
                            + (
                                "..."
                                if len((q.get("market_question") or "")) > 50
                                else ""
                            ),
                            "Strike ($)": f"{strike:,.0f}",
                            "Yes %": f"{prob*100:.1f}",
                            "Resolution": q.get("resolution_date") or "",
                            "Risk (1 unit)": "1",
                            "Reward if Yes": f"{reward_if_yes:.2f}",
                            "R:R": f"1:{rr_ratio:.2f}",
                            "Spread vs spot": f"{strike - current_btc:,.0f}",
                        }
                    )
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No Bitcoin price-target questions parsed from Polymarket, or no spot price.")

            if is_full and load_deribit:
                st.subheader("Tight bull spreads (Deribit) — risk/reward")
            if is_full and load_deribit and bull_spreads:
                spread_rows: list[dict[str, Any]] = []
                for s in bull_spreads:
                    spread_rows.append(
                        {
                            "Expiry": s["expiry_date"].strftime("%Y-%m-%d")
                            if hasattr(s["expiry_date"], "strftime")
                            else str(s["expiry_date"])[:10],
                            "K_low": f"{s['K_low']:,.0f}",
                            "K_high": f"{s['K_high']:,.0f}",
                            "Cost (USD)": f"{s['cost_usd']:,.0f}",
                            "Max loss": f"{s['max_loss']:,.0f}",
                            "Max gain": f"{s['max_gain']:,.0f}",
                            "R:R": f"1:{s['rr_ratio']:.2f}",
                        }
                    )
                st.dataframe(pd.DataFrame(spread_rows), use_container_width=True, hide_index=True)
            elif is_full and load_deribit:
                st.caption("No tight bull spreads (Deribit calls). Check spot price and API.")

            if is_full and load_deribit:
                st.subheader("Spreads around predictions — Polymarket vs options")
            if is_full and load_deribit and prediction_spreads:
                pred_rows: list[dict[str, Any]] = []
                for s in prediction_spreads:
                    pred_rows.append(
                        {
                            "Target": f"${s['target']:,.0f}",
                            "Resolution": s["resolution_date"][:10],
                            "Polymarket Yes %": f"{s.get('polymarket_yes_pct', 0):.1f}",
                            "Spread": f"{s['K_low']/1000:.0f}k/{s['K_high']/1000:.0f}k",
                            "Cost (USD)": f"{s['cost_usd']:,.0f}",
                            "R:R": f"1:{s['rr_ratio']:.2f}",
                            "Opt ~implied %": f"{s.get('approx_implied_prob_pct') or 0:.1f}"
                            if s.get("approx_implied_prob_pct") is not None
                            else "—",
                        }
                    )
                st.dataframe(pd.DataFrame(pred_rows), use_container_width=True, hide_index=True)
                st.caption(
                    "Opt ~implied % = approximate from spread cost (simplified). Compare to Polymarket Yes %."
                )
            elif is_full and load_deribit:
                st.caption(
                    "No prediction-aligned spreads (need Polymarket questions + Deribit options at matching strikes/expiries)."
                )

        if is_full and not load_deribit:
            st.caption(
                "Optional: use **Refresh priced inputs (Deribit)** in the sidebar to load the forward curve, "
                "spread overlays on the chart, and Deribit reference tables."
            )

