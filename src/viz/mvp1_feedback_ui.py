"""MVP1 feedback capture UI (§15F rubric; opt-in via PPE_ENABLE_FEEDBACK=1)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.viz.app_env import env_flag
from src.viz.mvp1_feedback_store import (
    CONFUSION_CATEGORIES,
    LIKERT_MAX,
    LIKERT_MIN,
    insert_feedback,
    open_store,
)


def feedback_panel_enabled() -> bool:
    """Public demo disables feedback by default (no shared server-side SQLite on open host)."""
    return env_flag("PPE_ENABLE_FEEDBACK", False)

_LIKERT_LABELS = {
    1: "1 — Strongly disagree",
    2: "2 — Disagree",
    3: "3 — Neutral",
    4: "4 — Agree",
    5: "5 — Strongly agree",
}


def _feedback_context_from_verification(verification: dict | None) -> dict[str, Any]:
    if not isinstance(verification, dict):
        return {}
    mvp1 = verification.get("mvp1_decision") if isinstance(verification.get("mvp1_decision"), dict) else {}
    vs = (
        verification.get("verification_summary")
        if isinstance(verification.get("verification_summary"), dict)
        else {}
    )
    return {
        "primary_output_state": mvp1.get("primary_output_state"),
        "data_quality": mvp1.get("data_quality"),
        "classification_label": mvp1.get("classification_label"),
        "disagreement_category_id": vs.get("disagreement_category_id"),
        "as_of_utc": vs.get("as_of_utc"),
    }


def render_mvp1_feedback_panel(*, verification: dict | None = None) -> None:
    """Discoverable Give feedback expander for MVP1 friends-first context."""
    if not feedback_panel_enabled():
        return
    with st.expander("Give feedback", expanded=False):
        st.caption(
            "Help us improve the cockpit. Responses are stored in this app's snapshot store "
            "(private full app only). No account or email required."
        )
        confusion = st.selectbox(
            "What best describes your experience?",
            options=list(CONFUSION_CATEGORIES),
            index=0,
            key="mvp1_feedback_confusion_category",
        )
        usefulness = st.select_slider(
            "How useful was this session for understanding the market read?",
            options=list(range(LIKERT_MIN, LIKERT_MAX + 1)),
            value=3,
            format_func=lambda v: _LIKERT_LABELS.get(int(v), str(v)),
            key="mvp1_feedback_usefulness",
        )
        repeat_intent = st.select_slider(
            "Would you want to use this again?",
            options=list(range(LIKERT_MIN, LIKERT_MAX + 1)),
            value=3,
            format_func=lambda v: _LIKERT_LABELS.get(int(v), str(v)),
            key="mvp1_feedback_repeat_intent",
        )
        objections = st.text_area(
            "Objections or free-text notes (optional)",
            placeholder="What felt wrong, missing, or hard to trust?",
            max_chars=4000,
            key="mvp1_feedback_objections",
        )
        session_note = st.text_input(
            "Session label (optional, this device only)",
            placeholder="e.g. first pass, after belief tweak",
            max_chars=500,
            key="mvp1_feedback_session_note",
        )
        if st.button("Submit feedback", key="mvp1_feedback_submit", type="primary"):
            try:
                conn = open_store()
                try:
                    rid = insert_feedback(
                        conn,
                        confusion_category=confusion,
                        usefulness=int(usefulness),
                        repeat_use_intent=int(repeat_intent),
                        objections_text=objections or None,
                        session_note=session_note or None,
                        context=_feedback_context_from_verification(verification),
                    )
                finally:
                    conn.close()
            except ValueError as exc:
                st.error(str(exc))
            else:
                st.success(f"Thanks — feedback saved locally (id `{rid[:8]}…`).")
