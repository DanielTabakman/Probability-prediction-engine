"""
Reusable Streamlit panels and small UI helpers extracted from `src/viz/app.py`.

This module intentionally preserves:
- widget keys
- session_state keys
- copy/text wording

so extraction remains behavior-neutral.
"""

from __future__ import annotations

import streamlit as st

from src.viz.belief_uncertainty import (
    move_pct_1sigma_to_sigma_ln,
    sigma_ln_to_move_pct_1sigma,
)
from src.viz.commercial_wrapper import COMMERCIAL_BOUNDARY_CAPTION
from src.viz.decision_ready_review import build_decision_ready_review_payload
from src.viz.implied_lab_provenance import TRUST_STRIP_FALLBACK_LINE, build_trust_strip_lines
from src.viz.mvp1_feedback_ui import render_mvp1_feedback_panel


def compute_mvp1_belief_overlay_state(
    *,
    belief_exp: str,
    forward: float,
    price_max: float,
    vol: float,
    T_years: float,
) -> dict:
    """
    MVP1-friendly belief controls (§15B slice 3): human labels, ±% default, σ_ln nested.
    Returns user_belief dict for `build_implied_lab_state` (width is σ_ln internally).
    """
    st.caption(
        "Optional: add **your** view on where price might land — compare to the market curve (right)."
    )
    with st.expander("My belief vs market", expanded=False):
        st.caption(
            "Turn on a simple belief curve. This is not a forecast or trade recommendation."
        )
        st.checkbox(
            "Show my belief curve",
            key=f"belief_en_{belief_exp}",
        )
        st.number_input(
            "Where you think price lands (USD peak)",
            min_value=1000.0,
            max_value=float(max(price_max, 1_000_000)),
            value=float(forward),
            step=1000.0,
            key=f"belief_center_{belief_exp}",
            format="%.0f",
            help="Your best single price level for this expiry (mode of your belief curve).",
        )

        sigma_mkt_horizon = float(vol) * (float(T_years) ** 0.5)
        mkt_move_pct = sigma_ln_to_move_pct_1sigma(sigma_mkt_horizon)
        unc_mode_key = f"belief_unc_mode_{belief_exp}"
        pct_key = f"belief_move_pct_{belief_exp}"
        if pct_key not in st.session_state:
            existing_sigma = float(st.session_state.get(f"belief_width_{belief_exp}", 0.2))
            st.session_state[pct_key] = float(sigma_ln_to_move_pct_1sigma(existing_sigma))

        st.markdown("**How unsure are you?**")
        st.slider(
            "Typical move by expiry (±% about 2/3 of the time, 1σ)",
            1.0,
            200.0,
            float(st.session_state.get(pct_key, 22.0)),
            0.5,
            key=pct_key,
            help="How far price might move up or down by expiry (one standard deviation).",
        )

        with st.expander("Advanced uncertainty (technical)", expanded=False):
            st.radio(
                "Uncertainty input mode",
                ["±% move (1σ)", "σ_ln (advanced)"],
                key=unc_mode_key,
                horizontal=True,
                label_visibility="collapsed",
            )
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

        unc_mode = str(st.session_state.get(unc_mode_key, "±% move (1σ)"))
        if unc_mode == "σ_ln (advanced)":
            sigma_ln = float(st.session_state.get(f"belief_width_{belief_exp}", 0.2))
        else:
            sigma_ln = move_pct_1sigma_to_sigma_ln(float(st.session_state.get(pct_key, 22.0)))

        st.caption(
            f"Active uncertainty σ_ln ≈ **{sigma_ln:.4f}** · "
            f"Market horizon σ_ln ≈ **{sigma_mkt_horizon:.4f}** (≈±**{mkt_move_pct:.1f}%** 1σ)"
        )

    return {
        "enabled": bool(st.session_state.get(f"belief_en_{belief_exp}", False)),
        "center_usd": float(st.session_state.get(f"belief_center_{belief_exp}", forward)),
        "width": float(sigma_ln),
    }


def format_mvp1_materiality_caption(mvp1: dict) -> str | None:
    """Single-line width-gap witness from `mvp1_decision.materiality` (parity across panels)."""
    mat = mvp1.get("materiality") if isinstance(mvp1, dict) else None
    if not isinstance(mat, dict):
        return None
    return (
        f"Width gap: market {mat.get('market_width_1sigma_move_pct', '—')}% vs "
        f"benchmark {mat.get('benchmark_width_1sigma_move_pct', '—')}% · "
        f"M_ratio={mat.get('m_ratio', '—')} ({mat.get('materiality_rule_version', '')})"
    )


def _primary_output_state_label(mvp1: dict) -> str:
    return str(mvp1.get("primary_output_state", "")).replace("_", " ")


def _render_mvp1_decision_digest(mvp1: dict, *, bordered: bool, friends_first: bool = False) -> None:
    """Shared MVP1 decision fields from verification `mvp1_decision` payload."""
    state = _primary_output_state_label(mvp1)
    title = f"**{state}**" if friends_first else f"##### MVP1 output: **{state}**"
    reason = mvp1.get("primary_output_reason") or ""

    def _body() -> None:
        if friends_first:
            st.markdown(title)
            if reason:
                st.caption(reason)
        else:
            st.markdown(title)
            st.caption(reason)
        c1, c2, c3 = st.columns(3)
        dq_label = "MVP1 data quality" if friends_first else "Data quality"
        with c1:
            st.write(f"**{dq_label}:**", mvp1.get("data_quality", "—"))
        with c2:
            st.write("**Classification:**", mvp1.get("classification_label", "—"))
        with c3:
            st.write("**Expression family:**", mvp1.get("expression_family", "—"))
        mat_cap = format_mvp1_materiality_caption(mvp1)
        if mat_cap:
            st.caption(mat_cap)

    if bordered:
        with st.container(border=True):
            _body()
    else:
        _body()


def render_belief_vs_market_glance(v: dict) -> None:
    """Compact BTC belief vs market card — values trace to verification payload / classification_trace."""
    g = v.get("belief_vs_market_glance") if isinstance(v, dict) else None
    if not isinstance(g, dict):
        return
    with st.container(border=True):
        st.markdown("##### Belief vs market — at a glance")
        st.caption(
            "Digest vs **market-implied pricing distribution** on the **same underlying-price axis** as the chart "
            "(your **shape window** control above), same run."
        )
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


def shape_focus_x_range(
    choice: str,
    price_min: float,
    price_max: float,
    forward: float,
) -> tuple[float, float]:
    """Sprint002-Slice001: map UI labels to chart x-axis window (descriptive navigation only)."""
    lo, hi = float(price_min), float(price_max)
    fw = float(forward)
    if hi <= lo:
        return lo, hi
    if choice == "Lower prices":
        upper = min(hi, fw * 1.1)
        return lo, max(lo + 1.0, upper)
    if choice == "Near forward":
        a = max(lo, fw * 0.82)
        b = min(hi, fw * 1.18)
        if b <= a + 1.0:
            return lo, hi
        return a, b
    if choice == "Higher prices":
        lower = max(lo, fw * 0.9)
        return lower, hi
    # "Full range" and any unknown value
    return lo, hi


def shape_focus_post_interaction_hint(verification: dict | None, forward: float) -> str:
    """Short descriptive copy; uses existing glance fields only (no new metrics)."""
    v = verification if isinstance(verification, dict) else {}
    g = v.get("belief_vs_market_glance")
    base = (
        "**Where to look:** the horizontal axis is **underlying price (USD)** — the same **shape window** "
        "you chose above. "
        "**Purple (filled)** is the reference distribution; **orange (dashed)** is the market-implied curve from marks."
    )
    if isinstance(g, dict) and g.get("largest_gap_price_usd") is not None:
        gap_txt = str(g.get("largest_gap_display") or "").strip() or (
            f"${float(g['largest_gap_price_usd']):,.0f}"
        )
        return (
            base + " "
            f"When the optional belief overlay is on, **Belief vs market — at a glance** reports where "
            f"the sample grid shows the largest **|ΔPDF|** around **{gap_txt}** on that **same underlying-price axis** "
            f"(a mismatch descriptor, not a recommendation)."
        )
    return (
        base + " "
        "When the optional belief overlay is on, open **Review & disagreement digest** below for "
        "**Belief vs market — at a glance** on the **same underlying-price axis** as this chart."
    )


def render_trust_strip(verification: dict) -> None:
    """Always-visible provenance strip from verification_summary (Sprint 006)."""
    lines = build_trust_strip_lines(verification if isinstance(verification, dict) else None)
    with st.container(border=True):
        st.markdown("##### Trust / provenance")
        st.caption("\n\n".join(lines))


def trust_strip_at_a_glance_lines(verification: dict | None, *, max_lines: int = 4) -> list[str]:
    """Compact trust lines for above-fold MVP1 (no duplicate primary-output lines)."""
    lines = build_trust_strip_lines(verification if isinstance(verification, dict) else None)
    compact: list[str] = []
    for line in lines:
        if "MVP1 primary output" in line:
            continue
        if "expand **Verification**" in line:
            continue
        compact.append(line)
        if len(compact) >= max_lines:
            break
    return compact if compact else [TRUST_STRIP_FALLBACK_LINE]


def render_trust_strip_at_a_glance(verification: dict) -> None:
    """Compact trust lines for above-fold MVP1 (no duplicate primary-output lines)."""
    compact = trust_strip_at_a_glance_lines(verification)
    st.markdown("##### Trust / provenance")
    st.markdown("\n\n".join(compact))


def render_mvp1_friends_first_above_fold(verification: dict) -> None:
    """
    Above-fold MVP1 block: what this run is saying + compact decision + trust (before chart).
  """
    if not isinstance(verification, dict):
        return
    mvp1 = verification.get("mvp1_decision")
    if not isinstance(mvp1, dict) or not mvp1.get("primary_output_state"):
        return
    with st.container(border=True):
        st.markdown("##### What this run is saying")
        st.caption(
            "Plain-English read from this marks snapshot — research insight, not trade advice."
        )
        st.caption(COMMERCIAL_BOUNDARY_CAPTION)
        _render_mvp1_decision_digest(mvp1, bordered=False, friends_first=True)
        st.divider()
        render_trust_strip_at_a_glance(verification)
        with st.expander("Verification", expanded=False):
            vs = verification.get("verification_summary")
            if isinstance(vs, dict) and vs:
                st.markdown("##### Verification summary")
                st.write("**Disagreement category:**", vs.get("disagreement_category_id", "—"))
                if vs.get("disagreement_type_line"):
                    st.markdown(vs.get("disagreement_type_line"))
                st.caption(vs.get("classification_dimensions", ""))
            else:
                st.caption("Verification payload not available for this run.")
        render_mvp1_feedback_panel(verification=verification)


def render_width_vol_candidate_strip_payload(payload: dict) -> None:
    """Sprint 004 — width_vol-only hypothesis strip (does not use right_anomaly_slot)."""
    with st.container(border=True):
        st.markdown("##### Candidate to inspect (width-shaped, v0)")
        st.caption(
            "Hypothesis-oriented readout for **width / volatility tension** — inspect the shape, "
            "then cross-check **Verification**. **Fit exploration only** — not a trade recommendation."
        )
        st.markdown(payload["anomaly_md"])
        st.markdown(payload["why_md"])
        st.markdown(payload["confidence_md"])
        st.markdown(payload["trust_artifact_md"])
        st.markdown(payload["expression_families_md"])
        st.markdown(payload["falsification_md"])


def render_directional_candidate_strip_payload(payload: dict) -> None:
    """Sprint 004 — directional/mixed hypothesis strip (location-shaped tension)."""
    with st.container(border=True):
        st.markdown("##### Location-shaped tension — hypothesis to inspect")
        st.caption(
            "Hypothesis-oriented readout for **peak-location tension** vs the market reference modal. "
            "**Fit exploration only** — not a trade recommendation."
        )
        st.markdown(payload["anomaly_md"])
        st.markdown(payload["why_md"])
        st.markdown(payload["confidence_md"])
        st.markdown(payload["trust_artifact_md"])
        st.markdown(payload["expression_families_md"])
        st.markdown(payload["falsification_md"])


def _width_vol_history_entry(*, verification: dict, selected_expiry_str: str) -> dict:
    """
    Sprint004-Slice003 (v0): session-local, width_vol-only appearance history.
    Stores only already-derived, descriptive fields; no persistence.
    """
    v = verification if isinstance(verification, dict) else {}
    vs = v.get("verification_summary") if isinstance(v.get("verification_summary"), dict) else {}
    g = v.get("belief_vs_market_glance") if isinstance(v.get("belief_vs_market_glance"), dict) else {}
    return {
        "as_of_utc": vs.get("as_of_utc"),
        "expiry": selected_expiry_str,
        "disagreement_category_id": vs.get("disagreement_category_id"),
        "classification_dimensions": vs.get("classification_dimensions"),
        "width_band": g.get("width_band"),
        "shape_gap_strength": g.get("shape_gap_strength"),
        "market_reference_kind": g.get("market_reference_kind"),
        "overlay_basis": vs.get("overlay_basis"),
        "data_sources": vs.get("data_sources"),
    }


def _width_vol_history_fingerprint(entry: dict) -> str:
    """
    Session-local de-dupe token so a single width_vol strip doesn't spam history on reruns.
    Intentionally small: stable across reruns of the same run snapshot.
    """
    parts = (
        str(entry.get("as_of_utc") or ""),
        str(entry.get("expiry") or ""),
        str(entry.get("classification_dimensions") or ""),
        str(entry.get("overlay_basis") or ""),
    )
    return "|".join(parts)


def maybe_append_width_vol_history(*, verification: dict, selected_expiry_str: str) -> None:
    """Append a single entry when the width_vol candidate strip appears (session-local only)."""
    hist_key = "implied_lab_width_vol_history_v0"
    last_fp_key = "implied_lab_width_vol_history_last_fp_v0"
    cap = 20

    if hist_key not in st.session_state:
        st.session_state[hist_key] = []
    hist = st.session_state.get(hist_key)
    if not isinstance(hist, list):
        hist = []
        st.session_state[hist_key] = hist

    entry = _width_vol_history_entry(
        verification=verification if isinstance(verification, dict) else {},
        selected_expiry_str=str(selected_expiry_str),
    )
    fp = _width_vol_history_fingerprint(entry)
    if fp and fp == str(st.session_state.get(last_fp_key) or ""):
        return

    hist.append(entry)
    if len(hist) > cap:
        st.session_state[hist_key] = hist[-cap:]
        hist = st.session_state[hist_key]
    st.session_state[last_fp_key] = fp


def render_width_vol_history_panel(*, selected_expiry_str: str) -> None:
    """Compact session-local history display colocated with the width_vol strip."""
    hist_key = "implied_lab_width_vol_history_v0"
    last_fp_key = "implied_lab_width_vol_history_last_fp_v0"
    hist = st.session_state.get(hist_key)
    if not isinstance(hist, list) or not hist:
        return

    with st.expander("History (this session)", expanded=False):
        a, b = st.columns([1, 1])
        with a:
            st.caption(f"{len(hist)} event(s) · session-local only · width_vol only")
        with b:
            if st.button("Clear history", key=f"clear_wv_history_{selected_expiry_str}"):
                st.session_state[hist_key] = []
                st.session_state[last_fp_key] = ""
                st.rerun()

        st.caption("*History scope: width-only (v0). Directional-history slated for a future slice.*")

        # Newest first; single-line entries to avoid UI bloat.
        for e in reversed(hist[-20:]):
            if not isinstance(e, dict):
                continue
            as_of = str(e.get("as_of_utc") or "—")
            exp = str(e.get("expiry") or "—")
            wb = str(e.get("width_band") or "—")
            sg = str(e.get("shape_gap_strength") or "—")
            mr = str(e.get("market_reference_kind") or "—")
            st.caption(f"• as-of {as_of} · expiry {exp} · width {wb} · gap {sg} · ref {mr}")


def render_mvp1_primary_output_compact(v: dict) -> None:
    """Legacy compact digest below chart (post-MVP1 lab only). MVP1 mode uses friends-first above-fold."""
    mvp1 = v.get("mvp1_decision") if isinstance(v, dict) else None
    if not isinstance(mvp1, dict) or not mvp1.get("primary_output_state"):
        return
    _render_mvp1_decision_digest(mvp1, bordered=True, friends_first=False)


def render_implied_lab_verification(v: dict) -> None:
    """Structured display for outputs['verification'] (contract-driven summary + demoted detail)."""
    if not v:
        st.caption("Verification payload not available for this run.")
        return

    mvp1 = v.get("mvp1_decision")
    if isinstance(mvp1, dict) and mvp1.get("primary_output_state"):
        _render_mvp1_decision_digest(mvp1, bordered=False)

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
                "Target payoff → strikes on grid"
                if lm == "target_payoff"
                else ("Exact strikes (K1–K4)" if lm == "exact_strikes" else str(lm or "—")),
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


def render_decision_ready_review(
    verification: dict, *, mvp1_exclude_execution_ui: bool = False
) -> None:
    """Sprint 005: plain-language structure + payoff read + disagreement/ticket linkage."""
    payload = build_decision_ready_review_payload(
        verification, mvp1_exclude_execution_ui=mvp1_exclude_execution_ui
    )
    if not payload:
        return
    with st.container(border=True):
        st.markdown("##### Decision-ready review")
        if mvp1_exclude_execution_ui:
            st.caption(
                "Connects **Summary** to the glance digest below — descriptive only "
                "(MVP1 hides copy/paste trade-ticket export)."
            )
        else:
            st.caption("Connects **Summary** to the glance digest and **Trade ticket** next — descriptive only.")
        st.markdown(payload["structure_line"])
        st.markdown(payload["payoff_line"])
        st.markdown(payload["linkage_line"])
        for line in payload.get("bullets") or []:
            st.markdown(line)
        st.caption(payload.get("fit_caption") or "")


def implied_lab_trade_ticket_code_text(
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
    return ticket_text, (prem_k1, prem_k2, prem_k3, prem_k4), (
        side_put1,
        side_put2,
        side_call3,
        side_call4,
    )


def render_implied_lab_trade_ticket_panel(
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
    ticket_text, (prem_k1, prem_k2, prem_k3, prem_k4), (
        side_put1,
        side_put2,
        side_call3,
        side_call4,
    ) = implied_lab_trade_ticket_code_text(
        selected_expiry_str=selected_expiry_str,
        qty=qty,
        forward=forward,
        selected_strategy=selected_strategy,
        put_by_k=put_by_k,
        call_by_k=call_by_k,
        summary=summary,
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
            st.latex(r"\\text{Cost} = \\sum_{\\text{legs}} (\\pm \\text{premium})")
            lines = []
            if u1:
                lines.append(f"K1 put ({side_put1}): {sign1:+.0f} × {prem_k1:,.0f} = {c1:+,.0f} USD")
            if u2:
                lines.append(f"K2 put ({side_put2}): {sign2:+.0f} × {prem_k2:,.0f} = {c2:+,.0f} USD")
            if u3:
                lines.append(f"K3 call ({side_call3}): {sign3:+.0f} × {prem_k3:,.0f} = {c3:+,.0f} USD")
            if u4:
                lines.append(f"K4 call ({side_call4}): {sign4:+.0f} × {prem_k4:,.0f} = {c4:+,.0f} USD")
            st.code("\\n".join(lines), language="text")
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


def render_implied_lab_summary_card(
    outputs: dict, *, mvp1_lab_surfaces_hidden: bool = False
) -> None:
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
            "Reference strategy economics from the same engine as the hidden post-MVP UI (not a trade ticket)."
            if mvp1_lab_surfaces_hidden
            else "Payoff snapshot for the green line — same strikes and premiums as **Trade ticket (copy/paste)**."
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


