"""MVP1 friends-first above-fold helpers (trust-at-a-glance filtering)."""

from __future__ import annotations

from src.viz.app_panels import _primary_output_state_label, trust_strip_at_a_glance_lines


def test_primary_output_state_label_replaces_underscores():
    assert _primary_output_state_label({"primary_output_state": "watch_only"}) == "watch only"


def test_trust_at_a_glance_omits_duplicate_primary_output_line():
    verification = {
        "verification_summary": {
            "as_of_utc": "2026-05-20T12:00:00Z",
            "data_sources": ["deribit"],
            "overlay_basis": "listed marks",
        },
        "mvp1_decision": {
            "data_quality": "usable",
            "primary_output_state": "watch_only",
            "primary_output_reason": "Below materiality threshold.",
        },
    }
    lines = trust_strip_at_a_glance_lines(verification)
    text = "\n".join(lines)
    assert "MVP1 data quality" in text
    assert "MVP1 primary output" not in text
    assert "expand **Verification**" not in text
    assert len(lines) <= 4
