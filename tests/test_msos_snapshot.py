"""Tests for MSOS snapshot builder."""

from __future__ import annotations

from pathlib import Path

from scripts.msos.build_snapshot import (
    MSOS_DOC_DISPLAY_NAME,
    build_snapshot_markdown,
    compose_google_doc_markdown,
    extract_execution_focus,
    extract_section15a_table,
    write_snapshot_artifact,
    SnapshotMeta,
)

REPO = Path(__file__).resolve().parents[1]

SAMPLE_FRONTIER = """## MVP1_FRONTIER

### Current execution focus (MVP1 framing)
- **Active BUILD chapter:** **none** — await steward **SELECTION**
- **Last closed chapter:** **Test Chapter** — **COMPLETE** 2026-05-20

### Phase 2
"""

SAMPLE_CANON_TABLE = """
15A. MVP1 IMPLEMENTATION STATUS (REPO-TRUTH)

Purpose
Maps contract.

| Contract element | Status | Notes |
|------------------|--------|--------|
| Freeze explicit | **shipped (v0)** | notes |
"""


def test_extract_execution_focus():
    block = extract_execution_focus(SAMPLE_FRONTIER)
    assert "Active BUILD chapter" in block
    assert "Test Chapter" in block


def test_extract_section15a_table():
    table_md, rows = extract_section15a_table(SAMPLE_CANON_TABLE)
    assert "| Contract element |" in table_md
    assert len(rows) == 1
    assert rows[0]["Status"] == "**shipped (v0)**"


def test_build_snapshot_against_real_repo():
    md, meta = build_snapshot_markdown(REPO)
    assert f"# {MSOS_DOC_DISPLAY_NAME}" in md
    assert "§0 — INDEX" in md
    assert "WHAT_THIS_DOCUMENT_IS" in md
    assert "CHATGPT_DOC_MAP" in md
    assert "MVP1_FRONTIER" in md
    assert "| Chapter |" in md or "Archived chapters" in md
    assert meta.generated_at.endswith("Z")


def test_write_snapshot_artifact(tmp_path):
    md = "# test\n"
    meta = SnapshotMeta(
        generated_at="2026-05-25T00:00:00Z",
        head_sha="abc",
        slice_id=None,
        pytest_count=None,
        dual_smoke_run_ids=[],
        section15a_drift_warnings=[],
    )
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "VISION").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(SAMPLE_FRONTIER, encoding="utf-8")
    (tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md").write_text(SAMPLE_CANON_TABLE, encoding="utf-8")
    out = write_snapshot_artifact(tmp_path, md, meta)
    assert out.is_file()
    assert (tmp_path / "artifacts" / "control_plane" / "msos_snapshot_meta.json").is_file()


def test_compose_google_doc_markdown_uses_display_name():
    wrapped = compose_google_doc_markdown(f"# {MSOS_DOC_DISPLAY_NAME} (auto-generated)\n\nbody")
    assert wrapped.startswith(f"# {MSOS_DOC_DISPLAY_NAME}\n")
    assert "MSOS_REPO_TRUTH_AUTO_START" in wrapped
