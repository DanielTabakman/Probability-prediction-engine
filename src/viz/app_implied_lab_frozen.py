"""
Frozen evaluation + strategy details panels extracted from app_implied_lab_view.

Behavior-neutral: preserves widget keys and session_state keys.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from src.viz import frozen_evaluation_store as _fz_store
from src.viz.app_panels import (
    render_belief_vs_market_glance as _render_belief_vs_market_glance,
    render_implied_lab_verification as _render_implied_lab_verification,
)
from src.viz.frozen_evaluation_record import build_frozen_evaluation_record
from src.viz.reviewed_class_summary import build_class_summary, serialize_rollup_csv


def render_implied_lab_frozen_and_strategy_sections(
    *,
    snapshots_enabled: bool,
    show_debug_ui: bool,
    post_mvp_implied_lab_ui: bool,
    selected_expiry_str: str,
    outputs: dict[str, Any],
    selected_strategy: dict[str, Any] | None,
    avail_strikes: list[float],
) -> None:
                    if "ppe_frozen_view_id" not in st.session_state:
                        st.session_state["ppe_frozen_view_id"] = None
                    with st.expander("Freeze & history (this device, SQLite)", expanded=False):
                        if not snapshots_enabled:
                            st.info(
                                "Snapshots are disabled on this host. "
                                "Use the private app hostname to freeze/reopen/review."
                            )
                        else:
                            st.caption(
                                "Explicit **freeze** writes the current **verification** witness to a local database "
                                f"(default `{_fz_store.default_db_path()}`; override with env **PPE_SNAPSHOT_DB_PATH**)."
                            )
                            _fz_note = st.text_input(
                                "Optional note (stored with snapshot)",
                                key=f"ppe_freeze_note_{selected_expiry_str}",
                            )
                            if st.button("Freeze this evaluation", key=f"ppe_freeze_btn_{selected_expiry_str}"):
                                _fv = outputs.get("verification")
                                if isinstance(_fv, dict) and _fv:
                                    _owner_email = _fz_store.resolve_snapshot_owner_email()
                                    _rec = build_frozen_evaluation_record(
                                        verification=_fv,
                                        expiry_str=selected_expiry_str,
                                        operator_note=_fz_note or None,
                                        owner_email=_owner_email,
                                    )
                                    _conn = _fz_store.open_store()
                                    try:
                                        _rid = _fz_store.insert_record(_conn, _rec)
                                        _owner_hint = f" (owner `{_owner_email}`)" if _owner_email else ""
                                        st.success(f"Saved frozen snapshot `{_rid}`{_owner_hint}")
                                    finally:
                                        _conn.close()
                                else:
                                    st.warning("No verification payload to freeze for this run.")
                            _owner_scope = _fz_store.resolve_snapshot_owner_email()
                            _conn2 = _fz_store.open_store()
                            try:
                                _fz_rows = _fz_store.list_recent(
                                    _conn2,
                                    limit=40,
                                    owner_email=_owner_scope,
                                )
                            finally:
                                _conn2.close()
                            if _fz_rows:
                                _labels = [f"{r['summary_line']}  (id {r['id'][:8]}…)" for r in _fz_rows]
                                _ix = st.selectbox(
                                    "Pick a frozen record",
                                    range(len(_fz_rows)),
                                    format_func=lambda i: _labels[i],
                                    key=f"ppe_freeze_pick_{selected_expiry_str}",
                                )
                                c1, c2 = st.columns(2)
                                with c1:
                                    if st.button(
                                        "Reopen read-only view",
                                        key=f"ppe_freeze_reopen_{selected_expiry_str}",
                                    ):
                                        st.session_state["ppe_frozen_view_id"] = _fz_rows[int(_ix)]["id"]
                                        st.rerun()
                                with c2:
                                    if st.button(
                                        "Clear read-only view",
                                        key=f"ppe_freeze_clear_{selected_expiry_str}",
                                    ):
                                        st.session_state["ppe_frozen_view_id"] = None
                                        st.rerun()
                            else:
                                st.caption("No frozen records on this device yet.")
                    if snapshots_enabled:
                        with st.expander("Pending snapshot reviews", expanded=False):
                            _conn_pd = _fz_store.open_store()
                            try:
                                _expiries = _fz_store.list_distinct_frozen_expiries(_conn_pd)
                            finally:
                                _conn_pd.close()
                            _exp_choice = st.selectbox(
                                "Filter by expiry (pending only)",
                                options=["(all)"] + _expiries,
                                index=0,
                                key=f"ppe_pending_expiry_filter_{selected_expiry_str}",
                            )
                            _pend_sort = st.selectbox(
                                "Sort pending",
                                options=list(_fz_store.PENDING_SORT_OPTIONS),
                                format_func=lambda s: {
                                    _fz_store.PENDING_SORT_NEWEST: "Newest frozen first",
                                    _fz_store.PENDING_SORT_EXPIRY: "Expiry (A→Z)",
                                    _fz_store.PENDING_SORT_HORIZON: "Review horizon ref",
                                }.get(s, s),
                                index=0,
                                key=f"ppe_pending_sort_{selected_expiry_str}",
                            )
                            _pend_exp = (
                                None if _exp_choice == "(all)" else str(_exp_choice).strip()
                            )
                            _conn_pd2 = _fz_store.open_store()
                            try:
                                _pend = _fz_store.list_snapshots_pending_review(
                                    _conn_pd2,
                                    limit=200,
                                    expiry=_pend_exp,
                                    sort=_pend_sort,
                                )
                            finally:
                                _conn_pd2.close()
                            if not _pend:
                                st.caption("No snapshots pending review.")
                            else:
                                for _pi, _pr in enumerate(_pend):
                                    _pc1, _pc2 = st.columns((4, 1))
                                    with _pc1:
                                        st.caption(
                                            f"{_pr['summary_line']}  (`{_pr['id'][:8]}…`)"
                                        )
                                    with _pc2:
                                        if st.button(
                                            "Open", key=f"ppe_pend_open_{_pr['id']}_{_pi}"
                                        ):
                                            st.session_state["ppe_frozen_view_id"] = _pr["id"]
                                            st.rerun()

                        with st.expander(
                            "Class summary — reviewed snapshots (Phase 6)", expanded=False
                        ):
                            st.caption(
                                "Rollup over snapshots with a **saved** review status other than **pending**. "
                                "Counts use disagreement category (direction proxy), shape-gap label, Breeden gate, "
                                "benchmark method, and classifier version from each frozen record."
                            )
                            _status_opts = [
                                "supportive",
                                "contradictory",
                                "contaminated",
                                "not_judgeable",
                            ]
                            _sel_statuses = st.multiselect(
                                "Filter by review status",
                                options=_status_opts,
                                default=_status_opts,
                                key=f"ppe_phase6_status_filter_{selected_expiry_str}",
                            )
                            _use_date = st.checkbox(
                                "Filter by reviewed date (local)",
                                value=False,
                                key=f"ppe_phase6_date_enable_{selected_expiry_str}",
                            )
                            _dr = None
                            if _use_date:
                                _dr = st.date_input(
                                    "Reviewed date range",
                                    key=f"ppe_phase6_date_filter_{selected_expiry_str}",
                                )
                            _after_utc = None
                            _before_utc = None
                            try:
                                if (
                                    isinstance(_dr, (tuple, list))
                                    and len(_dr) == 2
                                    and _dr[0]
                                    and _dr[1]
                                ):
                                    _after_utc = f"{_dr[0].isoformat()}T00:00:00Z"
                                    _before_utc = f"{_dr[1].isoformat()}T23:59:59Z"
                            except Exception:
                                _after_utc, _before_utc = None, None
                            _conn_ex = _fz_store.open_store()
                            try:
                                _expiries2 = _fz_store.list_distinct_frozen_expiries(_conn_ex)
                            finally:
                                _conn_ex.close()
                            _exp_choice2 = st.selectbox(
                                "Filter by expiry (reviewed only)",
                                options=["(all)"] + _expiries2,
                                index=0,
                                key=f"ppe_phase6_expiry_filter_{selected_expiry_str}",
                            )
                            _cls_exp = (
                                None
                                if _exp_choice2 == "(all)"
                                else str(_exp_choice2).strip()
                            )
                            _conn_cls = _fz_store.open_store()
                            try:
                                _completed = _fz_store.list_completed_review_snapshots(
                                    _conn_cls,
                                    limit=500,
                                    review_statuses=list(_sel_statuses)
                                    if _sel_statuses
                                    else [],
                                    expiry=_cls_exp,
                                    reviewed_after_utc=_after_utc,
                                    reviewed_before_utc=_before_utc,
                                )
                            finally:
                                _conn_cls.close()
                            _rollup = build_class_summary(_completed)
                            st.markdown(f"**{_rollup['operator_summary_line']}**")
                            st.metric(
                                "Reviewed snapshots (non-pending)",
                                int(_rollup["n_reviewed"]),
                            )
                            if _rollup["n_reviewed"]:
                                import json as _json

                                _rollup_json = _json.dumps(
                                    _rollup, indent=2, ensure_ascii=False
                                ).encode("utf-8")
                                st.download_button(
                                    "Download rollup (JSON)",
                                    data=_rollup_json,
                                    file_name="ppe_phase6_rollup.json",
                                    mime="application/json",
                                    key=f"ppe_rollup_dl_json_{selected_expiry_str}",
                                )
                                _rollup_csv = serialize_rollup_csv(_rollup).encode("utf-8")
                                st.download_button(
                                    "Download rollup (CSV)",
                                    data=_rollup_csv,
                                    file_name="ppe_phase6_rollup.csv",
                                    mime="text/csv",
                                    key=f"ppe_rollup_dl_csv_{selected_expiry_str}",
                                )
                                _ca, _cb = st.columns(2)
                                with _ca:
                                    st.subheader("Review outcomes")
                                    st.json(_rollup["by_review_status"])
                                    st.subheader("Disagreement category")
                                    st.json(_rollup["by_disagreement_category"])
                                    st.subheader("Shape gap strength")
                                    st.json(_rollup["by_shape_gap_strength"])
                                with _cb:
                                    st.subheader("Data quality (MVP1)")
                                    st.json(_rollup.get("by_data_quality", {}))
                                    st.subheader("Primary output state (MVP1)")
                                    st.json(_rollup.get("by_primary_output_state", {}))
                                    st.subheader("Breeden gate (legacy trust proxy)")
                                    st.json(_rollup["by_trust_breeden"])
                                    st.subheader("Benchmark method")
                                    st.json(_rollup["by_benchmark_method"])
                                    st.subheader("Classifier version")
                                    st.json(_rollup["by_classifier_version"])

                                st.subheader("Reviewed snapshots (filtered)")
                                _rows = []
                                for r in _completed[:50]:
                                    rec = (
                                        r.get("record")
                                        if isinstance(r.get("record"), dict)
                                        else {}
                                    )
                                    vdoc = (
                                        rec.get("verification")
                                        if isinstance(rec.get("verification"), dict)
                                        else {}
                                    )
                                    vs = (
                                        vdoc.get("verification_summary")
                                        if isinstance(
                                            vdoc.get("verification_summary"), dict
                                        )
                                        else {}
                                    )
                                    _rows.append(
                                        {
                                            "snapshot_id": str(
                                                r.get("snapshot_id") or ""
                                            )[:8]
                                            + "…",
                                            "reviewed_at_utc": (r.get("review") or {}).get(
                                                "reviewed_at_utc"
                                            ),
                                            "expiry": r.get("expiry"),
                                            "review_status": (r.get("review") or {}).get(
                                                "review_status"
                                            ),
                                            "disagreement_category_id": (vs or {}).get(
                                                "disagreement_category_id"
                                            ),
                                            "classifier_version": rec.get("classifier_version"),
                                            "outcome_notes": (
                                                (r.get("review") or {}).get("outcome_notes") or ""
                                            )[:120],
                                            "_snapshot_id_full": r.get("snapshot_id"),
                                        }
                                    )
                                if _rows:
                                    _df = pd.DataFrame(_rows)
                                    st.dataframe(
                                        _df.drop(columns=["_snapshot_id_full"]),
                                        use_container_width=True,
                                        hide_index=True,
                                    )
                                    try:
                                        _csv2 = _df.drop(
                                            columns=["_snapshot_id_full"]
                                        ).to_csv(index=False).encode("utf-8")
                                        st.download_button(
                                            "Download reviewed table (CSV)",
                                            data=_csv2,
                                            file_name="ppe_reviewed_table_filtered.csv",
                                            mime="text/csv",
                                            key=f"ppe_phase6_table_csv_{selected_expiry_str}",
                                        )
                                    except Exception:
                                        pass
                                    for _ri, _row in enumerate(_rows[:20]):
                                        if st.button(
                                            f"Open {_row['snapshot_id']}",
                                            key=f"ppe_phase6_open_{_row['_snapshot_id_full']}_{_ri}",
                                        ):
                                            st.session_state["ppe_frozen_view_id"] = _row[
                                                "_snapshot_id_full"
                                            ]
                                            st.rerun()

                            try:
                                _flat = [
                                    {
                                        "snapshot_id": r.get("snapshot_id"),
                                        "review_status": (r.get("review") or {}).get("review_status"),
                                        "reviewed_at_utc": (r.get("review") or {}).get("reviewed_at_utc"),
                                        "review_horizon_ref": (r.get("review") or {}).get("review_horizon_ref"),
                                        "paper_tag": (r.get("review") or {}).get("paper_tag"),
                                        "outcome_notes": (r.get("review") or {}).get("outcome_notes"),
                                    }
                                    for r in _completed
                                ]
                                _csv = pd.DataFrame(_flat).to_csv(index=False).encode("utf-8")
                                st.download_button(
                                    "Download reviewed rows (CSV)",
                                    data=_csv,
                                    file_name="ppe_reviewed_snapshots.csv",
                                    mime="text/csv",
                                    key=f"ppe_rollup_dl_csv_{selected_expiry_str}",
                                )
                            except Exception as _e:
                                st.caption(f"CSV export unavailable: {type(_e).__name__}")
                    _fvid = st.session_state.get("ppe_frozen_view_id")
                    if _fvid and snapshots_enabled:
                        _conn3 = _fz_store.open_store()
                        try:
                            _frozen = _fz_store.get_by_id(_conn3, str(_fvid))
                        finally:
                            _conn3.close()
                        if _frozen:
                            with st.expander("Read-only: frozen snapshot", expanded=True):
                                st.caption("Persisted record — **not** live Deribit marks.")
                                _fv_doc = (
                                    _frozen.get("verification")
                                    if isinstance(_frozen.get("verification"), dict)
                                    else {}
                                )
                                if _fv_doc:
                                    _render_implied_lab_verification(_fv_doc)
                                    _render_belief_vs_market_glance(_fv_doc)
                                else:
                                    st.caption("No `verification` field on this record.")
                                st.markdown("##### Review (Phase 5)")
                                _conn_rev = _fz_store.open_store()
                                try:
                                    _rev_existing = _fz_store.get_review_for_snapshot(_conn_rev, str(_fvid))
                                finally:
                                    _conn_rev.close()
                                _rev_opts = list(_fz_store.REVIEW_STATUSES)
                                _rev_ix = 0
                                if _rev_existing and _rev_existing.get("review_status") in _rev_opts:
                                    _rev_ix = _rev_opts.index(str(_rev_existing["review_status"]))
                                _sel_status = st.selectbox(
                                    "Review status",
                                    options=_rev_opts,
                                    index=_rev_ix,
                                    key=f"ppe_rev_status_{_fvid}",
                                )
                                _default_notes = (
                                    (_rev_existing.get("outcome_notes") or "")
                                    if _rev_existing
                                    else ""
                                )
                                _notes_val = st.text_area(
                                    "Outcome notes",
                                    value=_default_notes,
                                    key=f"ppe_rev_notes_{_fvid}",
                                )
                                _default_paper = (
                                    (_rev_existing.get("paper_tag") or "")
                                    if _rev_existing
                                    else ""
                                )
                                _paper_val = st.text_input(
                                    "Paper tag (optional, ≤120 chars)",
                                    value=_default_paper,
                                    max_chars=120,
                                    key=f"ppe_rev_paper_{_fvid}",
                                )
                                if _rev_existing and _rev_existing.get("review_horizon_ref"):
                                    st.caption(
                                        f"Review horizon ref: `{_rev_existing['review_horizon_ref']}`"
                                    )
                                if st.button("Save review", key=f"ppe_rev_save_{_fvid}"):
                                    _href = _fz_store.review_horizon_ref_from_frozen(_frozen)
                                    _cs = _fz_store.open_store()
                                    try:
                                        _fz_store.upsert_review(
                                            _cs,
                                            snapshot_id=str(_fvid),
                                            review_status=_sel_status,
                                            outcome_notes=_notes_val or None,
                                            review_horizon_ref=_href or None,
                                            paper_tag=_paper_val or None,
                                        )
                                    finally:
                                        _cs.close()
                                    st.toast("Review saved.")
                                    st.rerun()
                                if show_debug_ui:
                                    with st.expander("Debug: full frozen JSON", expanded=False):
                                        st.json(_frozen)
                        else:
                            st.warning("Frozen record not found (id may have been deleted).")
                            st.session_state["ppe_frozen_view_id"] = None
                    elif _fvid and not snapshots_enabled:
                        st.session_state["ppe_frozen_view_id"] = None

                    # Strategy details are useful, but not part of the top-of-screen story.
                    with st.expander("Strategy details (optional)", expanded=False):
                        if not post_mvp_implied_lab_ui:
                            st.caption(
                                "Strike-level strategy tables are hidden in MVP1 mode. "
                                "Set **PPE_POST_MVP1_LAB_UI=1** to open the full post-MVP lab."
                            )
                        elif not (selected_strategy and selected_strategy.get("k1") is not None):
                            if avail_strikes:
                                st.caption(
                                    "Set strikes in the **left column** (open **Adjust strategy shape**) "
                                    "to see payoff and name above."
                                )
                            else:
                                st.caption(
                                    "No strikes available for this expiry; use **Refresh priced inputs (Deribit)** "
                                    "or pick another expiry."
                                )
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
