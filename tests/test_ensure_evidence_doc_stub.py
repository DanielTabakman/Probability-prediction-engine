"""Tests for ensure_evidence_doc_stub."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.relay.ensure_evidence_doc_stub import ensure_evidence_doc_stub


def _write_plan(tmp_path: Path) -> str:
    plan = {
        "name": "test_chapter",
        "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
        "slices": [
            {"sliceId": "Test-Product-Slice002", "declaredPlane": "PRODUCT-PLANE"},
            {
                "sliceId": "Test-Closeout-Slice003",
                "closeout": {
                    "chapterId": "test_chapter",
                    "chapterTitle": "Test Chapter",
                    "evidenceDoc": "docs/SOP/TEST_CHAPTER_EVIDENCE_STATUS.md",
                    "sprintSpec": "docs/SOP/SPRINT_TEST.md",
                },
            },
        ],
    }
    rel = "docs/SOP/PHASE_PLANS/test_relay.json"
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan), encoding="utf-8")
    (tmp_path / "docs" / "SOP" / "SPRINT_TEST.md").write_text("# sprint\n", encoding="utf-8")
    return rel


def test_ensure_evidence_doc_stub_creates_pending(tmp_path: Path) -> None:
    rel = _write_plan(tmp_path)
    result = ensure_evidence_doc_stub(tmp_path, rel)
    assert result.get("created") is True
    evidence = tmp_path / "docs" / "SOP" / "TEST_CHAPTER_EVIDENCE_STATUS.md"
    assert evidence.is_file()
    text = evidence.read_text(encoding="utf-8")
    assert "**Status:** **PENDING**" in text
    assert "Test-Product-Slice002" in text


def test_ensure_evidence_doc_stub_idempotent(tmp_path: Path) -> None:
    rel = _write_plan(tmp_path)
    ensure_evidence_doc_stub(tmp_path, rel)
    result = ensure_evidence_doc_stub(tmp_path, rel)
    assert result.get("skipped") is True
    assert result.get("reason") == "exists"
