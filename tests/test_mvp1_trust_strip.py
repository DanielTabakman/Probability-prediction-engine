"""Trust strip lines include MVP1 decision disclosure when present."""

from __future__ import annotations

from src.viz.implied_lab_provenance import build_trust_strip_lines


def test_trust_strip_includes_mvp1_decision_fields():
    verification = {
        "verification_summary": {
            "as_of_utc": "2026-05-19T12:00:00Z",
            "data_sources": ["deribit"],
            "overlay_basis": "listed marks",
        },
        "mvp1_decision": {
            "data_quality": "usable",
            "primary_output_state": "watch_only",
            "primary_output_reason": "Materiality below threshold for candidate.",
        },
    }
    lines = build_trust_strip_lines(verification)
    text = "\n".join(lines)
    assert "MVP1 data quality" in text
    assert "`usable`" in text
    assert "MVP1 primary output" in text
    assert "watch only" in text
    assert "Materiality below" in text


def test_trust_strip_without_mvp1_decision_omits_mvp1_lines():
    verification = {
        "verification_summary": {
            "as_of_utc": "2026-05-19T12:00:00Z",
            "data_sources": ["deribit"],
        },
    }
    lines = build_trust_strip_lines(verification)
    text = "\n".join(lines)
    assert "MVP1 data quality" not in text
    assert "MVP1 primary output" not in text
