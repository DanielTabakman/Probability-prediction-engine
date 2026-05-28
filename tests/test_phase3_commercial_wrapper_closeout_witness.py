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
    assert "214" in text
    assert "20260528_092349" in text
    assert "20260528_092617" in text
    assert "20260528_093947" in text
    assert "49e856e" in text
    assert "daecb6c" in text
