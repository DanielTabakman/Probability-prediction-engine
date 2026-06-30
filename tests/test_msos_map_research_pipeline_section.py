"""Gate: research pipeline section inject is idempotent."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MAP = REPO / "docs" / "SOP" / "assets" / "msos_module_map.html"


def test_research_pipeline_inject_idempotent() -> None:
    from scripts.msos_map_research_pipeline_section import inject

    before = MAP.read_text(encoding="utf-8")
    after = inject(before)
    again = inject(after)
    assert after == again
    assert 'id="research-pipeline"' in after


def test_research_pipeline_doc_exists() -> None:
    doc = REPO / "docs" / "SOP" / "RESEARCH_PIPELINE_V1.md"
    text = doc.read_text(encoding="utf-8")
    assert "cross_venue_event_gap" in text
    assert "Strategy layer (deferred)" in text
