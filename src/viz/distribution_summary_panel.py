"""On-screen Distribution summary table (display-only; reuses export rows)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.viz.implied_lab_legibility import (
    BL_STATUS_COMPUTED,
    BL_STATUS_SKIPPED_DEGENERATE,
    BL_STATUS_SKIPPED_INSUFFICIENT,
    DIST_COL_BL_LN_GAP,
    DIST_COL_EXPIRY,
    DIST_COL_MEAN,
    DIST_COL_METHOD,
    DIST_COL_Q25,
    DIST_COL_Q50,
    DIST_COL_Q75,
    DIST_COL_RANGE,
    DIST_COL_STATUS,
    DIST_HOW_TO_READ_MARKDOWN,
    DIST_METHOD_BL,
    DIST_METHOD_LOGNORMAL,
    DIST_SUMMARY_ANCHOR_ID,
    DIST_SUMMARY_TITLE,
)


def _parse_usd(value: str) -> float | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _fmt_usd_display(value: str) -> str:
    parsed = _parse_usd(value)
    if parsed is None:
        return "—"
    return f"${parsed:,.0f}"


def _range_width_usd(q25: str, q75: str) -> str:
    lo = _parse_usd(q25)
    hi = _parse_usd(q75)
    if lo is None or hi is None or hi <= lo:
        return "—"
    return f"${hi - lo:,.0f}"


def _signed_gap_display(value: str) -> str:
    parsed = _parse_usd(value)
    if parsed is None:
        return "—"
    sign = "+" if parsed > 0 else ""
    return f"{sign}${parsed:,.0f}"


def distribution_method_label(distribution: str) -> str:
    if distribution == "market_implied_bl":
        return DIST_METHOD_BL
    return DIST_METHOD_LOGNORMAL


def bl_status_display(bl_status: str, *, distribution: str) -> str:
    if distribution != "market_implied_bl":
        return ""
    status = (bl_status or "").strip().lower()
    if status == "computed":
        return BL_STATUS_COMPUTED
    if status == "skipped:insufficient_marks":
        return BL_STATUS_SKIPPED_INSUFFICIENT
    if status == "skipped:degenerate_density":
        return BL_STATUS_SKIPPED_DEGENERATE
    if status.startswith("skipped"):
        return f"Skipped: {bl_status.split(':', 1)[-1].replace('_', ' ')}"
    return status or ""


def build_distribution_summary_table_rows(
    export_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """User-facing table rows from CSV-shaped export rows."""
    display: list[dict[str, str]] = []
    for row in export_rows:
        distribution = str(row.get("distribution") or "")
        bl_status = str(row.get("bl_status") or "")
        skipped = distribution == "market_implied_bl" and bl_status.startswith("skipped")
        iqr_value = str(row.get("iqr_usd") or "")
        gap_value = str(row.get("bl_ln_mean_gap_usd") or "")
        display.append(
            {
                DIST_COL_EXPIRY: str(row.get("expiry_date") or ""),
                DIST_COL_METHOD: distribution_method_label(distribution),
                DIST_COL_MEAN: "—" if skipped else _fmt_usd_display(str(row.get("mean_usd") or "")),
                DIST_COL_Q25: "—" if skipped else _fmt_usd_display(str(row.get("q25_usd") or "")),
                DIST_COL_Q50: "—" if skipped else _fmt_usd_display(str(row.get("q50_usd") or "")),
                DIST_COL_Q75: "—" if skipped else _fmt_usd_display(str(row.get("q75_usd") or "")),
                DIST_COL_RANGE: "—" if skipped else _range_width_usd(
                    str(row.get("q25_usd") or ""),
                    str(row.get("q75_usd") or ""),
                )
                if not iqr_value
                else _fmt_usd_display(iqr_value),
                DIST_COL_BL_LN_GAP: "—"
                if distribution != "market_implied_bl" or skipped
                else _signed_gap_display(gap_value),
                DIST_COL_STATUS: bl_status_display(bl_status, distribution=distribution),
            }
        )
    return display


def render_distribution_summary_panel(export_rows: list[dict[str, str]]) -> None:
    """Render labeled summary table + how-to-read expander (anchor id for embed)."""
    if not export_rows:
        return
    st.markdown(f'<div id="{DIST_SUMMARY_ANCHOR_ID}"></div>', unsafe_allow_html=True)
    st.markdown(f"##### {DIST_SUMMARY_TITLE}")
    with st.expander("How to read this table", expanded=False):
        st.markdown(DIST_HOW_TO_READ_MARKDOWN)
    table_rows = build_distribution_summary_table_rows(export_rows)
    st.dataframe(
        table_rows,
        use_container_width=True,
        hide_index=True,
    )


def trust_state_from_export_row(row: dict[str, str]) -> str:
    """Map one export row to canonical trust_state (ok | thin_chain | degraded)."""
    existing = str(row.get("trust_state") or "").strip().lower()
    if existing in ("ok", "thin_chain", "degraded", "error", "fail"):
        if existing in ("error", "fail"):
            return "degraded"
        return existing

    if str(row.get("distribution") or "") != "market_implied_bl":
        return "ok"

    bl_status = str(row.get("bl_status") or "").strip().lower()
    base = bl_status.split("|")[0].strip()

    if base.startswith("skipped:insufficient_marks"):
        try:
            mark_count = int(str(row.get("call_marks_count") or "0"))
        except ValueError:
            mark_count = 0
        return "thin_chain" if mark_count > 0 else "degraded"

    if base.startswith("skipped:"):
        return "degraded"

    if "thin_open_interest" in bl_status or base.startswith("computed_caution"):
        return "thin_chain"

    if "insufficient_marks" in bl_status:
        return "degraded"

    return "ok"


def annotate_export_rows_trust(
    export_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    """Return export rows with per-row trust_state populated."""
    annotated: list[dict[str, str]] = []
    for row in export_rows:
        copy = dict(row)
        copy["trust_state"] = trust_state_from_export_row(copy)
        annotated.append(copy)
    return annotated


def aggregate_trust_state(export_rows: list[dict[str, str]]) -> str:
    """Roll up per-row trust_state for display.json (thin_chain wins, then degraded)."""
    trust_states = {
        str(row.get("trust_state") or "ok").strip().lower()
        for row in export_rows
        if row.get("trust_state")
    }
    if "thin_chain" in trust_states:
        return "thin_chain"
    if trust_states & {"error", "fail", "degraded"}:
        return "degraded"
    return "ok"


def summary_panel_contract(export_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Test helper: anchor + title + row count without Streamlit."""
    return {
        "anchor_id": DIST_SUMMARY_ANCHOR_ID,
        "title": DIST_SUMMARY_TITLE,
        "row_count": len(build_distribution_summary_table_rows(export_rows)),
        "table_rows": build_distribution_summary_table_rows(export_rows),
    }
