"""Closeout witness for MVP1-Sprint003-Closeout-Slice004 (EVIDENCE-PLANE)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

SPRINT_SPEC = SOP / "SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
EVIDENCE_STATUS = SOP / "MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md"


def test_sprint_spec_all_slices_closed_and_chapter_complete() -> None:
    text = SPRINT_SPEC.read_text(encoding="utf-8")
    for slice_id in (
        "MVP1-Sprint003-Evidence-Slice002",
        "MVP1-Sprint003-Witness-Slice003",
        "MVP1-Sprint003-Closeout-Slice004",
    ):
        assert slice_id in text
        assert f"{slice_id}" in text and "**CLOSED**" in text
    assert "## Sprint status" in text
    assert "**COMPLETE**" in text


def test_evidence_status_chapter_close_witness() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "**COMPLETE**" in text
    assert "MVP1-Sprint003-Closeout-Slice004" in text
    assert "**PASS**" in text
    assert "run_pushable_gate.py" in text
    assert "Chapter close (witness)" in text
