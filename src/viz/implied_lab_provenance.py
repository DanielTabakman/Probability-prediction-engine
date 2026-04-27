"""
Structured verification payload for the BTC implied options lab (Sprint: provenance first slice).

Builds a single dict consumed by app.py; no Streamlit dependency here.
"""

from __future__ import annotations

from typing import Any

from src.viz.belief_disagreement_hints import build_disagreement_scan_payload
from src.viz.disagreement_thresholds import (
    L1_SHAPE_GAP_LOW_BELOW,
    L1_SHAPE_GAP_MODERATE_BELOW,
)

# Display-only: trust strip pointer (Sprint 006). Kept static so we do not imply extra provenance.
TRUST_STRIP_VERIFICATION_POINTER = (
    "Full traces and numeric inputs: expand **Verification** below."
)

TRUST_STRIP_FALLBACK_LINE = (
    "Provenance summary unavailable for this run. "
    "Expand **Verification** below for traces and inputs when available."
)


def build_trust_strip_lines(verification: dict[str, Any] | None) -> list[str]:
    """
    Compact read-only lines for the always-visible trust strip (verification_summary + optional belief note).
    Does not invent as-of, sources, or overlay text when absent — uses honest placeholders.
    """
    if not verification or not isinstance(verification, dict):
        return [TRUST_STRIP_FALLBACK_LINE]
    vs = verification.get("verification_summary")
    if not isinstance(vs, dict) or not vs:
        return [TRUST_STRIP_FALLBACK_LINE]

    lines: list[str] = []
    as_of = vs.get("as_of_utc")
    if isinstance(as_of, str) and as_of.strip():
        lines.append(f"**As of (UTC):** {as_of.strip()}")
    else:
        lines.append("**As of (UTC):** not reported for this run.")

    ds = vs.get("data_sources")
    if isinstance(ds, list) and len(ds) > 0:
        lines.append("**Sources:** " + ", ".join(str(x) for x in ds))
    else:
        lines.append("**Sources:** not listed for this run.")

    ob = vs.get("overlay_basis")
    if isinstance(ob, str) and ob.strip():
        lines.append(f"**Overlay basis:** {ob.strip()}")
    else:
        lines.append("**Overlay basis:** not reported for this run.")

    sfs = vs.get("strategy_families_scope")
    if isinstance(sfs, str) and sfs.strip():
        lines.append(sfs.strip())

    belief = verification.get("belief")
    if isinstance(belief, dict) and belief.get("enabled") and not belief.get("invalid"):
        note = belief.get("note")
        if isinstance(note, str) and note.strip():
            lines.append(f"**Belief (teal):** {note.strip()}")

    lines.append(TRUST_STRIP_VERIFICATION_POINTER)
    return lines


def _build_trust_artifact_md(market_implied: dict[str, Any]) -> str:
    """Shared helper: trust/artifact note for candidate strip payloads."""
    if market_implied.get("breeden_litzenberger") == "skipped":
        sr = market_implied.get("skip_reason")
        return (
            "**Trust / artifact note:** Market-implied density (orange) was **skipped** by the same marks gate "
            "as the chart engine. "
            + (
                str(sr).strip()
                if isinstance(sr, str) and sr.strip()
                else "Market-implied curve not computed (marks gate); the orange curve may be absent."
            )
            + " Cross-check **Verification** → Distribution for call-mark count and skip reason."
        )
    call_n = market_implied.get("call_marks_count")
    call_n_txt = f"{int(call_n)}" if isinstance(call_n, int) else "the reported"
    return (
        "**Trust / artifact note:** Uses the current marks snapshot + Breeden–Litzenberger market-implied density "
        f"(orange; computed from {call_n_txt} call marks when available). "
        "Sparse strikes / wide bid–ask / stale quotes can shift the inferred peak and apparent width. "
        "Cross-check **Trust / provenance** and expand **Verification** for call-mark count, cache notes, and trace paths."
    )


def _build_expression_families_md(strategy_families: list[Any]) -> str:
    """Shared helper: expression families line for candidate strip payloads."""
    labels: list[str] = []
    for fam in strategy_families[:3]:
        if isinstance(fam, dict):
            lab = str(fam.get("label") or "").strip()
            if lab:
                labels.append(lab)
    return "**Expression families (fit-scope only):** " + (
        " · ".join(labels) if labels else "Illustrative_pattern rows live under **Review & disagreement digest**."
    )


def build_width_vol_candidate_strip_payload(
    verification: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Sprint 004 — compact, hypothesis-oriented strip fields for **width_vol** only.

    Gated on verification_summary.disagreement_category_id (same truth as the Verification row).
    """
    if not verification or not isinstance(verification, dict):
        return None
    vs = verification.get("verification_summary")
    if not isinstance(vs, dict) or not vs:
        return None
    if vs.get("disagreement_category_id") != "width_vol":
        return None
    bd = verification.get("belief_disagreement")
    if not isinstance(bd, dict) or not bd:
        return None

    trace = bd.get("classification_trace")
    trace_d = trace if isinstance(trace, dict) else {}
    sl = bd.get("summary_lines") or []
    anomaly_md = str(sl[0]).strip() if sl else "**Disagreement type:** Width / volatility disagreement"
    why_body = str(sl[2]).strip() if len(sl) > 2 else (
        "Peak aligned with the market reference while σ_user differs from ATM-implied σ at this horizon."
    )
    why_md = f"**Why flagged:** {why_body}"

    shape_gap = bd.get("shape_gap_strength") or trace_d.get("shape_gap_strength") or "—"
    confidence_md = (
        f"**Confidence (exploratory):** Shape-gap label **{shape_gap}** (L₁ distance label on the sampled grid). "
        "This is a *descriptor* of visual/shape difference — **not a probability**, not calibrated, and not used "
        "to choose the **width_vol** category (that comes from peak alignment × width band in the trace)."
    )

    mi = (verification.get("density") or {}).get("market_implied") or {}
    trust_md = _build_trust_artifact_md(mi)

    fams = bd.get("strategy_families") or []
    expr_md = _build_expression_families_md(fams)

    falsification_md = (
        "**Falsification (what would weaken or remove this candidate):** On a rerun with refreshed marks/forward, "
        "if the trace no longer shows **peak_aligned**, or the trace width band becomes **similar**, the category "
        "should move out of **width_vol** under the *same* rules. Audit via **Verification** → "
        "`belief_disagreement.classification_trace` (peak_aligned, width_band, category_id)."
    )

    return {
        "anomaly_md": anomaly_md,
        "why_md": why_md,
        "confidence_md": confidence_md,
        "trust_artifact_md": trust_md,
        "expression_families_md": expr_md,
        "falsification_md": falsification_md,
    }


def build_directional_candidate_strip_payload(
    verification: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Sprint 004 — compact, hypothesis-oriented strip fields for **directional** and **mixed**.

    Gated on verification_summary.disagreement_category_id in ("directional", "mixed").
    Mixed shares the location-shaped peak disagreement component.

    Design note: separate builder from build_width_vol_candidate_strip_payload (symmetric
    functions sharing _build_trust_artifact_md / _build_expression_families_md helpers)
    rather than a single dispatch function — each category has distinct gate logic and copy;
    the shared helpers eliminate the only true code duplication.
    """
    if not verification or not isinstance(verification, dict):
        return None
    vs = verification.get("verification_summary")
    if not isinstance(vs, dict) or not vs:
        return None
    if vs.get("disagreement_category_id") not in ("directional", "mixed"):
        return None
    bd = verification.get("belief_disagreement")
    if not isinstance(bd, dict) or not bd:
        return None

    trace = bd.get("classification_trace")
    trace_d = trace if isinstance(trace, dict) else {}
    sl = bd.get("summary_lines") or []
    anomaly_md = str(sl[0]).strip() if sl else "**Disagreement type:** Location-shaped tension — hypothesis to inspect"
    why_body = str(sl[2]).strip() if len(sl) > 2 else (
        "Peak does not align with the market reference modal while σ_user is within "
        "the width band at this horizon."
    )
    why_md = f"**Why flagged:** {why_body}"

    shape_gap = bd.get("shape_gap_strength") or trace_d.get("shape_gap_strength") or "—"
    confidence_md = (
        f"**Confidence (exploratory):** Shape-gap label **{shape_gap}** (L₁ distance label on the sampled grid). "
        "This is a *descriptor* of visual/shape difference — **not a probability**, not calibrated, and not the "
        "primary signal for the **directional** / **mixed** category (that comes from peak alignment × width band "
        "in the trace). Audit: `belief_disagreement.classification_trace.delta_peak_usd` vs `peak_tolerance_usd`."
    )

    mi = (verification.get("density") or {}).get("market_implied") or {}
    trust_md = _build_trust_artifact_md(mi)

    fams = bd.get("strategy_families") or []
    expr_md = _build_expression_families_md(fams)

    falsification_md = (
        "**Falsification (what would weaken or remove this candidate):** On a rerun with refreshed marks/forward, "
        "if the trace shows **peak_aligned = True**, the category moves out of **directional** / **mixed** "
        "under the *same* rules. Audit via **Verification** → "
        "`belief_disagreement.classification_trace` (peak_aligned, width_band, category_id)."
    )

    return {
        "anomaly_md": anomaly_md,
        "why_md": why_md,
        "confidence_md": confidence_md,
        "trust_artifact_md": trust_md,
        "expression_families_md": expr_md,
        "falsification_md": falsification_md,
    }


def _overlay_basis_one_line(lab_mode: str | None) -> str:
    """Same semantics as verification_summary.overlay_basis; compact for the glance card."""
    if lab_mode == "target_payoff":
        return (
            "Green overlay: strikes from target-payoff matching on the listed strike grid "
            "(not a continuous strike optimizer)."
        )
    if lab_mode == "exact_strikes":
        return "Green overlay: strikes from exact K1–K4 using listed option marks."
    return "Green overlay: mode not reported for this run."


def _width_relation_label(width_band: str | None) -> str:
    """Human-readable width band (aligned with classification_trace wording)."""
    if width_band == "narrower":
        return "Narrower than market (σ_user below width threshold vs ATM-implied σ at horizon)."
    if width_band == "wider":
        return "Wider than market (σ_user above width threshold vs ATM-implied σ at horizon)."
    if width_band == "similar":
        return "Similar width to market (σ_user near ATM-implied σ at horizon)."
    if not width_band:
        return "—"
    return str(width_band)


def _belief_vs_market_glance_block(
    *,
    belief_disagreement: dict[str, Any] | None,
    belief_verification: dict[str, Any] | None,
    market_data: dict[str, Any],
    belief_largest_gap_price_usd: float | None,
    as_of_utc: str,
    lab_mode: str | None,
) -> dict[str, Any] | None:
    """
    Compact, trace-oriented summary for UI — derived only from contract + market_data + gap price.
    No recommendation language; strategy families are fit-scope only.
    """
    if not belief_verification or not belief_verification.get("enabled"):
        return None
    if belief_verification.get("invalid"):
        return None
    bd = belief_disagreement if isinstance(belief_disagreement, dict) else None
    if not bd:
        return None
    trace = bd.get("classification_trace") if isinstance(bd.get("classification_trace"), dict) else None
    if not trace:
        return None

    lines = bd.get("summary_lines") or []
    type_line = lines[0] if lines else None
    wb = trace.get("width_band") or bd.get("width_band")

    gap_txt = "—"
    if belief_largest_gap_price_usd is not None and isinstance(
        belief_largest_gap_price_usd, (int, float)
    ):
        gap_txt = f"~${float(belief_largest_gap_price_usd):,.0f}"

    forward = float(market_data.get("forward") or 0.0)
    glance: dict[str, Any] = {
        "forward_usd": forward,
        "market_modal_usd": float(trace.get("market_peak_usd", 0.0)),
        "belief_peak_usd": float(trace.get("center_usd", 0.0)),
        "width_band": wb,
        "width_relation_label": _width_relation_label(str(wb) if wb is not None else None),
        "disagreement_type_line": type_line,
        "disagreement_category_id": bd.get("category_id") or trace.get("category_id"),
        "largest_gap_price_usd": belief_largest_gap_price_usd,
        "largest_gap_display": gap_txt,
        "shape_gap_strength": str(trace.get("shape_gap_strength", "—")),
        "market_reference_kind": str(trace.get("market_reference_kind", "—")),
        "as_of_utc": as_of_utc,
        "classification_trace_path": "verification.belief_disagreement.classification_trace",
        "overlay_basis_line": _overlay_basis_one_line(lab_mode),
        "formula_caption": (
            "Peaks & width category: belief_disagreement.classification_trace; "
            "L₁ shape label: ∫|f_user − f_ref|dx on area-normalized grid (see Verification)."
        ),
        "strategy_families_heading": "Strategy families that fit this disagreement",
        "fit_note": "Fit is not recommendation.",
        "illustrative_scope_note": (
            "Illustrative_pattern examples only — not optimized strikes; see Verification for formulas."
        ),
    }
    scan = build_disagreement_scan_payload(bd)
    if scan:
        glance.update(scan)
    return glance


def _verification_summary_block(
    *,
    belief_disagreement: dict[str, Any] | None,
    as_of_utc: str,
    data_sources: list[str],
    lab_mode: str | None,
) -> dict[str, Any]:
    """Compact, contract-anchored fields for the Verification panel summary row."""
    bd = belief_disagreement if isinstance(belief_disagreement, dict) else {}
    trace = bd.get("classification_trace") if isinstance(bd.get("classification_trace"), dict) else {}
    cat = bd.get("category_id") or trace.get("category_id")
    lines = bd.get("summary_lines") or []
    type_line = lines[0] if lines else None
    width_band = bd.get("width_band")
    shape_gap = bd.get("shape_gap_strength")
    parts = [f"category={cat}"]
    if width_band:
        parts.append(f"width_band={width_band}")
    if shape_gap:
        parts.append(f"shape_gap={shape_gap}")
    classification_dimensions = ", ".join(parts)

    overlay_note = _overlay_basis_one_line(lab_mode)

    return {
        "contract_schema_version": bd.get("contract_schema_version") or "—",
        "as_of_utc": as_of_utc,
        "data_sources": list(data_sources),
        "classification_trace_reference": "belief_disagreement.classification_trace",
        "disagreement_category_id": cat,
        "disagreement_type_line": type_line,
        "classification_dimensions": classification_dimensions,
        "derivation_paths": {
            "reference_density": (
                "Lognormal on chart grid from forward + ATM IV + T (risk-neutral reference, purple)."
            ),
            "market_implied_density": (
                "Breeden–Litzenberger from call marks when ≥3 strikes (orange curve)."
            ),
            "disagreement_category": (
                "Peak alignment × width-band thresholds → category_id; "
                "L₁ PDF gap labels the strength of shape difference, not the category."
            ),
            "cost_and_payoff": (
                "USD leg value = mark_btc × forward; grid P&L matches the green payoff line."
            ),
        },
        "lab_mode": lab_mode,
        "overlay_basis": overlay_note,
        "strategy_families_scope": (
            "Strategy families in the belief panel are illustrative_pattern fit classes only — "
            "not optimized tickets."
        ),
    }


def build_belief_disagreement_verification_trace(
    belief_disagreement: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Human-readable + raw classification trace for Verification panel.
    Primary display is markdown-style lines; raw is for debugging.
    """
    if not belief_disagreement or not isinstance(belief_disagreement, dict):
        return None
    trace = belief_disagreement.get("classification_trace")
    if not trace or not isinstance(trace, dict):
        return None

    th = trace.get("thresholds") or {}
    lines = [
        "### Belief vs market — disagreement classification",
        "",
        "**Peak alignment (location vs market-implied modal price on the chart grid)**",
        "- Rule: *aligned* if |belief center − market peak| is strictly less than peak tolerance.",
        (
            f"- Peak tolerance = max({th.get('peak_align_abs_min_usd', 1.0):g} USD, "
            f"{th.get('peak_align_rel_to_market_peak', 0.002):g} × market peak USD)."
        ),
        (
            f"- Values: center = **{trace.get('center_usd', 0):,.2f}** USD, "
            f"market peak = **{trace.get('market_peak_usd', 0):,.2f}** USD, "
            f"Δ = **{trace.get('delta_peak_usd', 0):,.2f}** USD, "
            f"tolerance = **{trace.get('peak_tolerance_usd', 0):,.2f}** USD → "
            f"**{'aligned' if trace.get('peak_aligned') else 'not aligned'}**."
        ),
        "",
        "**Width band (σ of ln price vs ATM-implied σ at this horizon)**",
        (
            f"- Rule: *narrower* if σ_user is less than σ_mkt × **{th.get('width_narrower_ratio', 0.92):g}**; "
            f"*wider* if σ_user is greater than σ_mkt × **{th.get('width_wider_ratio', 1.08):g}**; else *similar*."
        ),
        (
            f"- Values: σ_user = **{trace.get('sigma_user', 0):.6f}**, "
            f"σ_mkt (horizon) = **{trace.get('sigma_mkt', 0):.6f}** → "
            f"width band = **{trace.get('width_band', '—')}**."
        ),
        "",
        "**Category (from peak alignment × width band)**",
        "- If peak not aligned and width not similar → **mixed**.",
        "- If peak not aligned and width similar → **directional**.",
        "- If peak aligned and width not similar → **width_vol**.",
        "- If peak aligned and width similar → **aligned**.",
        f"- **Result:** **{trace.get('category_id', '—')}**.",
        "",
        "**Shape gap strength (L₁ PDF distance — summary label only)**",
        (
            f"- Not used to pick the category above; labels Low / Moderate / High from "
            f"∫|f_user − f_ref| dx using thresholds **{L1_SHAPE_GAP_LOW_BELOW:g}** and "
            f"**{L1_SHAPE_GAP_MODERATE_BELOW:g}** (see belief summary)."
        ),
        f"- **Value:** **{trace.get('shape_gap_strength', '—')}**.",
        "",
        f"**Market reference for peak:** **{trace.get('market_reference_kind', '—')}**.",
    ]
    human_readable = "\n".join(lines)
    return {
        "human_readable": human_readable,
        "raw": {"classification_trace": trace, "contract_schema_version": belief_disagreement.get("contract_schema_version")},
    }


def build_verification_payload(
    *,
    market_data: dict[str, Any],
    summary: dict[str, Any],
    strategy: dict[str, Any] | None,
    overlay: dict[str, Any],
    market_pdf_raw: list[float],
    call_marks: list[Any],
    belief_verification: dict[str, Any] | None,
    belief_disagreement: dict[str, Any] | None = None,
    solve_error: str | None = None,
    lab_mode: str | None = None,
    belief_largest_gap_price_usd: float | None = None,
) -> dict[str, Any]:
    """
    Normalize verification fields for the current derive_lab_outputs run.

    Breeden–Litzenberger gate must match implied_lab_derive: len(call_marks) >= 3
    before calling market_implied_density_breeden_litzenberger.
    """
    dist = market_data.get("dist") or {}
    prices: list[float] = dist.get("prices") or []
    grid_n = len(prices)
    price_min = float(market_data.get("price_min") or (prices[0] if prices else 0.0))
    price_max = float(market_data.get("price_max") or (prices[-1] if prices else 0.0))

    forward = float(market_data.get("forward") or 0.0)
    vol = float(market_data.get("vol") or 0.0)
    T_years = float(market_data.get("T_years") or 0.0)

    data_sources = list(market_data.get("data_sources") or ["Deribit"])
    as_of_utc = str(market_data.get("as_of_utc") or "")
    cache_ttl = market_data.get("quote_cache_ttl_s")
    cache_ttl_s = int(cache_ttl) if cache_ttl is not None else None

    call_n = len(call_marks)
    breeden_gate = call_n >= 3
    breeden_status = "computed" if breeden_gate else "skipped"
    skip_reason: str | None = None
    if not breeden_gate:
        skip_reason = (
            "Fewer than 3 call option marks at this expiry — Breeden–Litzenberger "
            "is not run (same gate as the chart engine)."
        )

    summary_err = summary.get("error")
    err = solve_error or (summary_err if isinstance(summary_err, str) else None)
    has_strategy = strategy is not None and strategy.get("k1") is not None
    payoff_usd = overlay.get("payoff_usd") or []
    applicable = bool(has_strategy and payoff_usd)

    belief_disagreement_provenance: dict[str, Any] | None = None
    if belief_disagreement and isinstance(belief_disagreement, dict):
        belief_disagreement_provenance = {
            "schema_version": belief_disagreement.get("contract_schema_version"),
            "as_of_utc": as_of_utc,
            "classification_trace_reference": "belief_disagreement.classification_trace",
        }

    verification_summary = _verification_summary_block(
        belief_disagreement=belief_disagreement,
        as_of_utc=as_of_utc,
        data_sources=data_sources,
        lab_mode=lab_mode,
    )

    belief_vs_market_glance = _belief_vs_market_glance_block(
        belief_disagreement=belief_disagreement,
        belief_verification=belief_verification,
        market_data=market_data,
        belief_largest_gap_price_usd=belief_largest_gap_price_usd,
        as_of_utc=as_of_utc,
        lab_mode=lab_mode,
    )

    return {
        "data_sources": data_sources,
        "as_of_utc": as_of_utc,
        "lab_mode": lab_mode,
        "verification_summary": verification_summary,
        "belief_vs_market_glance": belief_vs_market_glance,
        "snapshot_note": (
            "As-of is the run snapshot / valuation time used for this calculation "
            "(time to expiry, grid, and marks passed into the engine). "
            "It is not the native exchange timestamp on each individual quote packet."
        ),
        "quote_cache_ttl_s": cache_ttl_s,
        "cache_note": (
            f"Streamlit may cache Deribit REST responses for up to {cache_ttl_s} seconds — "
            "quotes can be slightly older than the as-of clock above."
            if cache_ttl_s is not None
            else "Cache TTL for quotes is not set on this run."
        ),
        "density": {
            "reference_risk_neutral": {
                "label": "Risk-neutral distribution (reference)",
                "description": (
                    "Lognormal density on the chart grid from forward and ATM implied volatility — "
                    "the purple reference curve."
                ),
                "method": "Black–Scholes lognormal terminal density on the discrete price grid",
                "forward_usd": forward,
                "atm_iv_annual": vol,
                "T_years": T_years,
                "grid_price_min_usd": price_min,
                "grid_price_max_usd": price_max,
                "grid_points": grid_n,
            },
            "market_implied": {
                "label": "Market-implied pricing distribution",
                "description": (
                    "Risk-neutral density from listed call prices via Breeden–Litzenberger "
                    "(orange curve when available)."
                ),
                "call_marks_count": call_n,
                "breeden_litzenberger": breeden_status,
                "skip_reason": skip_reason,
                "method_when_computed": "Breeden–Litzenberger (second derivative of call price w.r.t. strike)",
            },
        },
        "belief": belief_verification,
        "belief_disagreement": belief_disagreement,
        "belief_disagreement_provenance": belief_disagreement_provenance,
        "belief_disagreement_verification": build_belief_disagreement_verification_trace(
            belief_disagreement
        ),
        "strategy_summary": {
            "applicable": applicable,
            "error": err,
            "values": {
                "name": summary.get("name"),
                "net_cost_usd": summary.get("cost_usd"),
                "debit_credit": summary.get("debit_credit"),
                "max_gain_usd": summary.get("max_gain"),
                "max_loss_usd": summary.get("max_loss"),
                "breakevens_usd": summary.get("breakevens"),
                "qty": strategy.get("qty") if strategy else None,
            },
            "calculation_notes": {
                "net_cost": (
                    "Net USD = Σ over legs: (long=+1 / short=−1) × put/call mark_btc(strike) × forward. "
                    "Positive = debit (pay), negative = credit (receive)."
                ),
                "max_gain_loss": (
                    "Max gain = max(qty × payoff on each grid point); max loss = min(qty × payoff). "
                    "Payoff at expiry uses the same piecewise definition as the green line."
                ),
                "breakevens": (
                    "Breakevens: points on the price grid where net P&L crosses zero — "
                    "found by linear interpolation between adjacent samples."
                ),
            },
        },
    }

