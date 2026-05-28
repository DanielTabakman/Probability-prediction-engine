"""Closeout witness for Phase 3 commercial wrapper (EVIDENCE-PLANE chapter)."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVIDENCE_STATUS = REPO / "docs" / "SOP" / "PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md"


def test_evidence_status_chapter_complete() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "**Status:** **COMPLETE**" in text
    assert "Phase3-CommercialWrapper-Product-Slice002" in text
    assert "Phase3-CommercialWrapper-Smoke-Slice003" in text
    assert "Phase3-CommercialWrapper-Closeout-Slice004" in text
    for slice_id in (
        "Phase3-CommercialWrapper-Control-Slice001",
        "Phase3-CommercialWrapper-Product-Slice002",
        "Phase3-CommercialWrapper-Smoke-Slice003",
        "Phase3-CommercialWrapper-Closeout-Slice004",
    ):
        assert slice_id in text
        assert "**CLOSED**" in text
    assert "228" in text
    assert "20260527_232631" in text
    assert "20260527_232844" in text
    assert "20260527_234308" in text
    assert "b4b195b" in text
