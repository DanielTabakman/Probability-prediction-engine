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
    fetch_deribit_btc_options_instruments,
    fetch_deribit_forward_and_iv_for_expiry,
    fetch_deribit_btc_option_marks_by_expiry,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_btc_option_book_marks,
    fetch_deribit_btc_index,
    last_deribit_instruments_diagnostic,
)
from src.engine.implied_distribution import (
    build_distribution_chart_data,
)
from src.engine.strategy_scanner import (
    build_universal_strategy,
    name_universal_strategy,
    payoff_target_to_strikes,
    payoff_target_to_strikes_with_work,
)
from src.viz.implied_lab_state import build_implied_lab_state
from src.viz.implied_lab_derive import derive_lab_outputs
from src.viz.decision_ready_review import build_decision_ready_review_payload
from src.viz.implied_lab_provenance import build_trust_strip_lines
from src.viz.implied_lab_presets import PRESETS, compute_preset_shape, preset_what_changed
from src.viz.implied_lab_last_action import last_action_meaning
from src.viz.belief_uncertainty import (
    move_pct_1sigma_to_sigma_ln,
    sigma_ln_to_move_pct_1sigma,
)
import yaml


def _render_belief_vs_market_glance(v: dict) -> None:
    """Compact BTC belief vs market card — values trace to verification payload / classification_trace."""
    g = v.get("belief_vs_market_glance") if isinstance(v, dict) else None
    if not isinstance(g, dict):
        return
    with st.container(border=True):
        st.markdown("##### Belief vs market — at a glance")
        st.caption("Disagreement digest vs **market-implied pricing distribution** (same run as the chart).")
        digest = g.get("digest_lines")
        if isinstance(digest, list) and digest:
            st.markdown("###### Main disagreement (scan)")
            st.markdown("\n".join(f"- {line}" for line in digest if str(line).strip()))
        intro = g.get("fit_bridge_intro")
        bullets = g.get("fit_bridge_bullets")
        if isinstance(intro, str) and intro.strip():
            st.markdown("###### Why these fit classes appear")
            st.markdown(intro)
            if isinstance(bullets, list) and bullets:
                st.markdown("\n".join(str(b) for b in bullets))
        st.caption(
            f"**{g.get('fit_note', 'Fit is not recommendation.')}** "
            f"{g.get('illustrative_scope_note', '')}"
        )
        st.divider()
        st.markdown("###### Reference numbers (grid)")
        a, b = st.columns(2)
        with a:
            st.markdown(
                f"- **Market forward:** ${g['forward_usd']:,.0f}\n"
                f"- **Market modal (reference peak):** ${g['market_modal_usd']:,.0f}\n"
                f"- **Your belief peak (mode):** ${g['belief_peak_usd']:,.0f}"
            )
        with b:
            gap_part = (
                f"{g['largest_gap_display']} (grid sample)"
                if g.get("largest_gap_price_usd") is not None
                else "— (see Verification if belief curve unavailable)"
            )
            st.markdown(
                f"- **Width vs market (technical):** {g['width_relation_label']}\n"
                f"- **Main mismatch (largest |ΔPDF| on grid):** {gap_part} · "
                f"L₁ label: **{g['shape_gap_strength']}**\n"
                f"- **Market reference for peak:** {g['market_reference_kind']}"
            )
        with st.expander("Audit trail: classification wording, trace & formulas", expanded=False):
            if g.get("disagreement_type_line"):
                st.markdown(str(g["disagreement_type_line"]))
            st.caption(
                f"As-of (UTC): {g.get('as_of_utc', '—')} · "
                f"Trace: `{g.get('classification_trace_path', '')}` · "
                f"{g.get('formula_caption', '')}"
            )
            st.caption(f"{g.get('overlay_basis_line', '')}")


def _render_trust_strip(verification: dict) -> None:
    """Always-visible provenance strip from verification_summary (Sprint 006)."""
    lines = build_trust_strip_lines(verification if isinstance(verification, dict) else None)
    with st.container(border=True):
        st.markdown("##### Trust / provenance")
        st.caption("\n\n".join(lines))


def _render_implied_lab_verification(v: dict) -> None:
    """Structured display for outputs['verification'] (contract-driven summary + demoted detail)."""
    if not v:
        st.caption("Verification payload not available for this run.")
        return

    vs = v.get("verification_summary")
    if isinstance(vs, dict) and vs:
        st.markdown("##### Verification summary")
        a, b = st.columns(2)
        with a:
            st.write("**Contract schema version:**", vs.get("contract_schema_version", "—"))
            st.write("**As-of (UTC):**", vs.get("as_of_utc", "—"))
            st.write("**Data sources:**", ", ".join(str(x) for x in (vs.get("data_sources") or [])))
            st.write("**Trace reference:**", vs.get("classification_trace_reference", "—"))
        with b:
            lm = vs.get("lab_mode")
            st.write(
                "**Overlay input mode:**",
                "Target payoff → strikes on grid" if lm == "target_payoff" else (
                    "Exact strikes (K1–K4)" if lm == "exact_strikes" else str(lm or "—")
                ),
            )
            st.write("**Disagreement category:**", vs.get("disagreement_category_id", "—"))
            if vs.get("disagreement_type_line"):
                st.markdown(vs.get("disagreement_type_line"))
            st.caption(vs.get("classification_dimensions", ""))
        st.caption(vs.get("overlay_basis", ""))
        st.caption(vs.get("strategy_families_scope", ""))
        dp = vs.get("derivation_paths") or {}
        if dp:
            st.markdown("**Formula / derivation paths**")
            for _k, line in dp.items():
                st.caption(f"• {line}")

    with st.expander("As-of, cache policy & snapshot notes", expanded=False):
        st.caption(v.get("snapshot_note") or "")
        st.caption(v.get("cache_note") or "")
        st.write("**Quote cache TTL (s):**", v.get("quote_cache_ttl_s", "—"))

    dens = v.get("density") or {}
    ref = dens.get("reference_risk_neutral") or {}
    mi = dens.get("market_implied") or {}
    belief = v.get("belief")
    with st.expander("Distribution & belief inputs (numeric)", expanded=False):
        st.markdown("##### Risk-neutral distribution (reference, purple)")
        st.caption(ref.get("method", ""))
        c1, c2 = st.columns(2)
        with c1:
            st.write("Forward (USD):", f"{ref.get('forward_usd', 0):,.2f}")
            st.write("ATM IV (annual):", f"{ref.get('atm_iv_annual', 0):.4f}")
            st.write("T (years):", f"{ref.get('T_years', 0):.4f}")
        with c2:
            st.write("Grid min (USD):", f"{ref.get('grid_price_min_usd', 0):,.2f}")
            st.write("Grid max (USD):", f"{ref.get('grid_price_max_usd', 0):,.2f}")
            st.write("Grid points:", ref.get("grid_points"))

        st.markdown("##### Market-implied pricing distribution (orange)")
        st.caption(mi.get("method_when_computed") or "")
        st.write("**Call marks count:**", mi.get("call_marks_count"))
        st.write("**Breeden–Litzenberger:**", mi.get("breeden_litzenberger"))
        if mi.get("skip_reason"):
            st.caption(mi["skip_reason"])

        if belief:
            st.markdown("##### User belief overlay (teal)")
            if belief.get("invalid"):
                st.warning(belief.get("invalid_reason") or "Invalid belief parameters.")
            st.write("Center / mode (USD):", f"{belief.get('center_mode_usd', 0):,.2f}")
            st.write("σ of ln price:", f"{belief.get('sigma_ln_of_price', 0):.4f}")
            st.write("σ at horizon (ATM-implied, same scale):", f"{belief.get('sigma_mkt_at_horizon', 0):.4f}")
            st.caption(belief.get("note") or "")

    bdv = v.get("belief_disagreement_verification")
    if bdv and isinstance(bdv, dict):
        with st.expander("Full disagreement classification (trace)", expanded=False):
            st.markdown(bdv.get("human_readable") or "")
        with st.expander("Raw classification trace (debug)", expanded=False):
            st.json(bdv.get("raw") or {})

    bd_contract = v.get("belief_disagreement")
    if bd_contract:
        with st.expander("Belief vs market — disagreement contract (structured)", expanded=False):
            st.caption(
                "Fit classes and illustrative patterns for exploration only — not financial advice "
                "and not optimized strikes from your belief."
            )
            st.json(bd_contract)

    ss = v.get("strategy_summary") or {}
    with st.expander("Strategy overlay P&L (net cost, breakevens, max gain / loss)", expanded=False):
        if ss.get("error"):
            st.error(str(ss["error"]))
        vals = ss.get("values") or {}
        notes = ss.get("calculation_notes") or {}
        if not ss.get("applicable"):
            st.caption(
                "No strategy P&L on the chart for this run (invalid targets, missing strikes, or empty overlay)."
            )
        else:
            st.write("**Strategy name:**", vals.get("name"))
            st.write("**Qty:**", vals.get("qty"))
            st.write(
                "**Net cost (USD):**",
                f"{vals.get('net_cost_usd', 0):,.2f}",
                f"({vals.get('debit_credit')})",
            )
            st.write("**Max gain (USD):**", f"{vals.get('max_gain_usd', 0):,.2f}")
            st.write("**Max loss (USD):**", f"{vals.get('max_loss_usd', 0):,.2f}")
            be = vals.get("breakevens_usd") or []
            st.write(
                "**Breakevens (USD):**",
                ", ".join(f"{x:,.2f}" for x in be) if be else "—",
            )
        with st.expander("Calculation notes", expanded=False):
            st.write("**Net cost / credit:**", notes.get("net_cost", ""))
            st.write("**Max gain / max loss:**", notes.get("max_gain_loss", ""))
            st.write("**Breakevens:**", notes.get("breakevens", ""))


def _render_decision_ready_review(verification: dict) -> None:
    """Sprint 005: plain-language structure + payoff read + disagreement/ticket linkage."""
    payload = build_decision_ready_review_payload(verification)
    if not payload:
        return
    with st.container(border=True):
        st.markdown("##### Decision-ready review")
        st.caption("Connects **Summary** to the glance digest and **Trade ticket** next — descriptive only.")
        st.markdown(payload["structure_line"])
        st.markdown(payload["payoff_line"])
        st.markdown(payload["linkage_line"])
        for line in payload.get("bullets") or []:
            st.markdown(line)
        st.caption(payload.get("fit_caption") or "")


def _implied_lab_trade_ticket_code_text(
    *,
    selected_expiry_str: str,
    qty: int,
    forward: float,
    selected_strategy: dict,
    put_by_k: dict,
    call_by_k: dict,
    summary: dict,
) -> tuple[str, tuple[float, float, float, float], tuple[str, str, str, str]]:
    """
    FS-007: deterministic copy-paste ticket body plus per-leg premia (for Show calculations).

    Returns (ticket_text, (prem_k1..4), (side_put1, side_put2, side_call3, side_call4)).
    """
    cost = float(summary.get("cost_usd") or 0.0)
    max_gain = float(summary.get("max_gain") or 0.0)
    max_loss = float(summary.get("max_loss") or 0.0)
    breakevens = summary.get("breakevens") or []

    side_put1 = "Long" if selected_strategy.get("long_k1", False) else "Short"
    side_put2 = "Long" if selected_strategy.get("long_k2", True) else "Short"
    side_call3 = "Long" if selected_strategy.get("long_k3", True) else "Short"
    side_call4 = "Long" if selected_strategy.get("long_k4", False) else "Short"
    k1 = selected_strategy.get("k1")
    k2 = selected_strategy.get("k2")
    k3 = selected_strategy.get("k3")
    k4 = selected_strategy.get("k4")
    prem_k1 = put_by_k.get(k1, 0.0) * forward if k1 is not None else 0.0
    prem_k2 = put_by_k.get(k2, 0.0) * forward if k2 is not None else 0.0
    prem_k3 = call_by_k.get(k3, 0.0) * forward if k3 is not None else 0.0
    prem_k4 = call_by_k.get(k4, 0.0) * forward if k4 is not None else 0.0

    ticket_text = (
        f"Expiry: {selected_expiry_str}\n"
        f"Size: {qty}x\n"
        f"{side_put1} {qty} PUT @ {k1:,.0f}  (≈ {prem_k1:,.0f} USD per 1x)\n"
        f"{side_put2} {qty} PUT @ {k2:,.0f}  (≈ {prem_k2:,.0f} USD per 1x)\n"
        f"{side_call3} {qty} CALL @ {k3:,.0f} (≈ {prem_k3:,.0f} USD per 1x)\n"
        f"{side_call4} {qty} CALL @ {k4:,.0f} (≈ {prem_k4:,.0f} USD per 1x)\n"
        f"Net premium: {cost:,.0f} USD ({'debit' if cost >= 0 else 'credit'})\n"
        f"Max gain (approx): {max_gain:,.0f} USD\n"
        f"Max loss (approx): {max_loss:,.0f} USD\n"
        + (
            f"Breakevens: {', '.join(f'{be:,.0f}' for be in breakevens[:3])} USD\n"
            if breakevens
            else ""
        )
    )
    return ticket_text, (prem_k1, prem_k2, prem_k3, prem_k4), (side_put1, side_put2, side_call3, side_call4)


def _render_implied_lab_trade_ticket_panel(
    *,
    selected_expiry_str: str,
    qty: int,
    forward: float,
    selected_strategy: dict,
    put_by_k: dict,
    call_by_k: dict,
    summary: dict,
) -> None:
    """
    FS-007: copy-ready trade ticket one expander deep (same code path as pre-slice Strategy details).

    Illustrative / export-style only — not a recommendation.
    """
    if not selected_strategy or selected_strategy.get("k1") is None:
        return
    ticket_text, (prem_k1, prem_k2, prem_k3, prem_k4), (side_put1, side_put2, side_call3, side_call4) = (
        _implied_lab_trade_ticket_code_text(
            selected_expiry_str=selected_expiry_str,
            qty=qty,
            forward=forward,
            selected_strategy=selected_strategy,
            put_by_k=put_by_k,
            call_by_k=call_by_k,
            summary=summary,
        )
    )
    cost = float(summary.get("cost_usd") or 0.0)
    max_gain = float(summary.get("max_gain") or 0.0)
    max_loss = float(summary.get("max_loss") or 0.0)
    breakevens = summary.get("breakevens") or []

    st.caption("Illustrative leg list — not a recommendation.")
    with st.expander("Trade ticket (copy/paste)", expanded=False):
        st.code(ticket_text, language="text")
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
            st.markdown(
                f"**Net cost = " + sum_txt + f" = {cost:,.0f} USD** ({'debit' if cost >= 0 else 'credit'})"
            )
            st.markdown("**2. Max gain / max loss**")
            st.markdown(
                "We evaluate the 4-leg payoff at each price on the chart (same formula as the green line). "
                "Max gain = highest point, max loss = lowest point."
            )
            st.markdown(f"- **Max gain** = max(payoff curve) ≈ **{max_gain:,.0f} USD**")
            st.markdown(f"- **Max loss** = min(payoff curve) ≈ **{max_loss:,.0f} USD**")
            st.markdown("**3. Breakevens**")
            if breakevens:
                st.markdown(
                    "Prices where the payoff curve crosses zero (we find sign changes between adjacent "
                    "grid points and interpolate)."
                )
                st.markdown("**Breakevens:** " + ", ".join(f"{be:,.0f} USD" for be in breakevens[:3]))
            else:
                st.markdown("Payoff curve does not cross zero in the chart range (always profit or always loss).")


def _render_implied_lab_summary_card(outputs: dict) -> None:
    """
    Compact trade summary for the implied lab.
    Single-source-of-truth: uses derived `outputs` (esp. verification.strategy_summary).
    """
    v = outputs.get("verification") if isinstance(outputs, dict) else {}
    ss = (v.get("strategy_summary") or {}) if isinstance(v, dict) else {}
    vals = ss.get("values") or {}

    name = vals.get("name") or "—"
    net_cost = vals.get("net_cost_usd")
    debit_credit = vals.get("debit_credit") or "—"
    max_gain = vals.get("max_gain_usd")
    max_loss = vals.get("max_loss_usd")
    breakevens = vals.get("breakevens_usd") or []

    dc_label = str(debit_credit).title() if str(debit_credit) in ("debit", "credit") else "—"
    cost_label = f"{float(net_cost):,.0f} USD" if isinstance(net_cost, (int, float)) else "—"
    max_gain_label = f"{float(max_gain):,.0f} USD" if isinstance(max_gain, (int, float)) else "—"
    max_loss_label = f"{float(max_loss):,.0f} USD" if isinstance(max_loss, (int, float)) else "—"
    be_preview = (
        ", ".join(f"{float(be):,.0f}" for be in breakevens[:3]) + ("…" if len(breakevens) > 3 else "")
        if breakevens
        else "—"
    )

    with st.container(border=True):
        st.markdown("##### Summary")
        st.caption(
            "Payoff snapshot for the green line — same strikes and premiums as **Trade ticket (copy/paste)**."
        )
        st.markdown(f"**{name}**")
        a, b, c = st.columns(3)
        with a:
            st.metric(f"{dc_label}", cost_label)
        with b:
            st.metric("Max gain", max_gain_label)
        with c:
            st.metric("Max loss", max_loss_label)
        st.caption(f"**Breakevens (USD):** {be_preview}")
        st.caption("**Fit quality:** — (not available in the current contract)")


st.set_page_config(page_title="Probability Engine", layout="wide")
st.title("Probability Prediction Engine")

# Cached fetches (2 min TTL) — avoids re-fetch on every sidebar change
CACHE_TTL = 120
# Shorter TTL for option expiries so a transient empty result is not stuck as long.
CACHE_TTL_OPTION_EXPIRIES = 30

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
def _cached_option_instruments():
    """Single get_instruments(option) payload; reused for spreads + options chart."""
    return fetch_deribit_btc_options_instruments(expired=False)

@st.cache_data(ttl=CACHE_TTL)
def _cached_option_book_marks():
    """Single get_book_summary_by_currency(BTC, option); reused for spread marks (no per-ticker storm)."""
    return fetch_deribit_btc_option_book_marks()

@st.cache_data(ttl=CACHE_TTL)
def _cached_bull_spreads(spot_price, spread_width, max_expiries):
    inst = _cached_option_instruments()
    marks = _cached_option_book_marks()
    return fetch_deribit_btc_tight_bull_spreads(
        spot_price=spot_price,
        spread_width=spread_width,
        max_expiries=max_expiries,
        instruments=inst,
        option_book_marks=marks,
    )

@st.cache_data(ttl=CACHE_TTL)
def _cached_options_for_chart():
    inst = _cached_option_instruments()
    return fetch_deribit_btc_options_for_chart(instruments=inst)

@st.cache_data(ttl=CACHE_TTL_OPTION_EXPIRIES)
def _cached_option_expiries(max_expiries):
    rows = fetch_deribit_btc_option_expiries(max_expiries=max_expiries)
    return rows, last_deribit_instruments_diagnostic()

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

# Chart toggles (always available; optional Deribit overlays gated until Refresh priced inputs)
is_full = True
st.sidebar.caption("Chart detail")
show_forward_curve = st.sidebar.checkbox("Show futures forward curve", value=True, help="Deribit futures at expiry dates.")
show_bull_spreads = st.sidebar.checkbox("Show tight bull spreads on chart", value=True, help="Overlay bull call spreads with R:R.")
show_prediction_spreads = st.sidebar.checkbox("Show prediction-aligned spreads on chart", value=True, help="Spreads tied to Polymarket questions (blue).")
show_options_on_chart = st.sidebar.checkbox("Show options on main chart", value=False, help="Overlay option expiries/strikes.")
options_in_separate_chart = st.sidebar.checkbox("Options in separate chart below", value=True, help="Dedicated options chart.")
option_types_on_chart = st.sidebar.multiselect("Option types", ["call", "put"], default=["call", "put"], key="option_types")
min_prob_label_pct = st.sidebar.slider("Show probability labels above (%)", 0, 50, 5, help="Hide small labels.")

if show_bitcoin_view:
    st.sidebar.markdown("---")
    st.sidebar.caption("Implied lab — priced inputs")
    if st.sidebar.button("Refresh priced inputs (Deribit)", key="btn_refresh_priced"):
        st.cache_data.clear()
        st.session_state["load_deribit"] = True
        st.rerun()
    st.sidebar.caption("Reloads exchange quotes and chart overlays. Does not reset your belief sliders.")
    if not st.session_state.get("load_deribit", False):
        st.sidebar.caption(
            "Deribit forward curve and spread overlays on the main chart load after the first refresh above."
        )

# ---------- Bitcoin section: light load first, heavy data on demand ----------
if show_bitcoin_view:
    st.header("Bitcoin implied lab — market-implied view as the anchor")
    st.caption(
        "**Glance path:** **Market-implied** chart (right) · **User belief** (left column) · "
        "**Disagreement digest** (*Belief vs market — at a glance*) · **Review → trade ticket** (under **Summary**). "
        "Exploration workbench — not a recommendation engine."
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
                expiries, expiry_fetch_diag = _cached_option_expiries(10)
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
                        right_chart_slot = st.empty()
                        right_summary_slot = st.empty()
                        right_trust_slot = st.empty()
                        right_review_slot = st.empty()
                        right_ticket_slot = st.empty()
                        right_anomaly_slot = st.empty()
                        right_forward_slot = st.empty()
                        right_belief_slot = st.empty()
                        right_verification_slot = st.empty()
                    with col_controls:
                        # Only fetch data for the selected expiry to keep this step fast.
                        fwd_iv = _cached_forward_iv(selected["expiry_ts"], current_btc)
                        forward = (fwd_iv.get("forward") or current_btc) if fwd_iv else current_btc
                        vol = (fwd_iv.get("atm_iv") or 0.6) if fwd_iv else 0.6
                        if vol <= 0:
                            vol = 0.6
                        run_ts_utc = pd.Timestamp.now(tz="UTC")
                        now_ts = run_ts_utc.timestamp() * 1000
                        as_of_utc = run_ts_utc.isoformat()
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
                            "data_sources": [
                                "Deribit (BTC index, forward, ATM IV, option marks)",
                            ],
                            "as_of_utc": as_of_utc,
                            "quote_cache_ttl_s": CACHE_TTL,
                        }
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
                                    "This updates after each meaningful change you make (preset, mode, strikes, legs, quantity). "
                                    "Descriptive only — not a recommendation."
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
                                        "Pick a preset above to see a plain-English summary of what changed. "
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
                    call_marks = marks_full.get("calls") or []
                    ch = outputs.get("chart_helpers") or {}
                    anomalous = bool(ch.get("anomalous", False))
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
                    market_pct = ch.get("market_pct") or []
                    if market_pct and len(market_pct) == len(data["prices"]):
                        fig_dist.add_trace(
                            go.Scatter(
                                x=data["prices"],
                                y=market_pct,
                                mode="lines",
                                name="Market-implied pricing distribution (options)",
                                line=dict(color="rgba(255, 140, 0, 0.9)", width=2, dash="dash"),
                            )
                        )
                    user_belief_pct = ch.get("user_belief_pct") or []
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
                    payoff_usd = (outputs.get("overlay") or {}).get("payoff_usd") or []
                    if selected_strategy and selected_strategy.get("k1") is not None and payoff_usd:
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
                    _gap_x = ch.get("belief_largest_gap_price")
                    if (
                        user_belief_for_state.get("enabled")
                        and _gap_x is not None
                        and isinstance(_gap_x, (int, float))
                    ):
                        fig_dist.add_shape(
                            type="line",
                            xref="x",
                            yref="paper",
                            x0=float(_gap_x),
                            x1=float(_gap_x),
                            y0=0,
                            y1=1,
                            line=dict(color="rgba(110, 110, 110, 0.5)", width=1, dash="dash"),
                            layer="below",
                        )
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
                    _fwd_cap = (
                        f"Forward ${forward:,.0f} · ATM IV {vol*100:.1f}% · T = {T_years:.2f} yr"
                    )
                    _dg = ch.get("belief_disagreement_strength")
                    if user_belief_for_state.get("enabled") and _dg:
                        _fwd_cap += f" · Belief disagreement: **{_dg}**"
                    _bs = outputs.get("belief_summary") or {}
                    belief_txt = _bs.get("text") or ""
                    belief_hints = _bs.get("hints_markdown") or ""
                    _belief_block = ""
                    if belief_txt or belief_hints:
                        _belief_block = belief_txt
                        if belief_hints:
                            _belief_block += (
                                ("\n\n" if belief_txt else "") + belief_hints
                            )

                    with right_chart_slot.container():
                        st.markdown("##### Market-implied view (chart)")
                        st.caption(
                            "Purple: **risk-neutral distribution** reference · Orange: **market-implied pricing distribution** "
                            "(Breeden–Litzenberger from marks) · Green: **strategy P&L** at expiry when legs are set."
                        )
                        st.plotly_chart(fig_dist, use_container_width=True)

                    right_forward_slot.caption(_fwd_cap)

                    if not avail_strikes:
                        right_summary_slot.info("No option strikes for this expiry — the strategy overlay is unavailable.")
                    # Summary card (Sprint 001): single-source-of-truth from derived outputs.
                    with right_summary_slot.container():
                        _render_implied_lab_summary_card(outputs)
                    with right_trust_slot.container():
                        _render_trust_strip(outputs.get("verification") or {})
                    with right_belief_slot.container():
                        if _belief_block:
                            with st.expander("Belief overlay (this run)", expanded=False):
                                st.markdown(_belief_block)
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
                    if anomalous:
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

    # Demoted context (price/prediction framing should not dominate first screen).
    with st.expander("Market context (price chart + prediction questions) — reference only", expanded=False):
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

        # Deribit context overlays (only when user refreshes priced inputs).
        forward_curve = []
        bull_spreads = []
        prediction_spreads = []
        if is_full and load_deribit and current_btc is not None:
            with st.spinner("Loading Deribit (forward curve, spreads, options)…"):
                try:
                    with ThreadPoolExecutor(max_workers=3) as ex:
                        f_fwd = ex.submit(_cached_forward_curve, 10)
                        f_inst = ex.submit(_cached_option_instruments)
                        f_marks = ex.submit(_cached_option_book_marks)
                        wait([f_fwd, f_inst, f_marks])
                        forward_curve = f_fwd.result() or []
                        _ = f_inst.result()
                        _ = f_marks.result()
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
                            btc_questions=eligible or btc_questions,
                            current_spot=current_btc,
                            max_questions=8,
                            instruments=_cached_option_instruments(),
                            option_book_marks=_cached_option_book_marks(),
                        ) or []
                    except Exception:
                        pass

        # Toggles: which "will it hit" questions to show on chart (local to this expander)
        question_labels = []
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
            st.subheader("Implied value: Bitcoin price-target questions (with risk/reward)")
            if btc_questions and current_btc is not None:
                rows = []
                for q in btc_questions:
                    strike = q.get("strike") or 0
                    prob = q.get("yes_probability") or 0
                    reward_if_yes = (1.0 / prob - 1.0) if prob > 0 else 0
                    rr_ratio = reward_if_yes
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
            st.caption(
                "Optional: use **Refresh priced inputs (Deribit)** in the sidebar to load the forward curve, "
                "spread overlays on the chart, and Deribit reference tables."
            )

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
