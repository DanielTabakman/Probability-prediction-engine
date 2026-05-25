"""Tests for google_docs_refresh_v1."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.google_docs_refresh import (
    _master_import_gap,
    _scan_naming_drift,
    run_google_docs_refresh,
)


def test_scan_naming_drift_flags_shorthand(tmp_path: Path):
    doc = tmp_path / "docs" / "SOP" / "example.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("See MSOS live mirror for status.\n", encoding="utf-8")
    findings = _scan_naming_drift(tmp_path)
    assert any(f["pattern"] == "MSOS live mirror" for f in findings)


def test_master_import_gap_when_protocol_missing(tmp_path: Path):
    canon = tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md"
    canon.parent.mkdir(parents=True)
    canon.write_text("# canon\n", encoding="utf-8")
    assert _master_import_gap(tmp_path) is True


@patch("scripts.sync_msos_repo_truth.run_sync", return_value=0)
@patch("scripts.google_docs_refresh._run_control_validation")
@patch("scripts.google_docs_refresh._witness")
@patch("scripts.google_docs_refresh._git_state")
def test_run_refresh_writes_report(
    mock_git,
    mock_witness,
    mock_validation,
    mock_sync,
    tmp_path: Path,
):
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "VISION").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(
        "### Current execution focus (MVP1 framing)\n- focus\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md").write_text(
        "GOOGLE_DOCS_REFRESH\n| Contract element | Status | Notes |\n|---|---|---|\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md").write_text(
        "| Chapter | MVP1 test |\n| Next SELECTION | [POST.md](POST.md) |\n",
        encoding="utf-8",
    )
    mock_git.return_value = {
        "branch": "main",
        "head": "abc123",
        "working_tree_clean": True,
        "upstream": None,
        "ahead": None,
        "behind": None,
    }
    mock_witness.return_value = {"http_skipped": True}
    mock_validation.return_value = {"skipped": True}

    report, code = run_google_docs_refresh(
        tmp_path,
        trigger="manual",
        skip_msos_push=True,
        skip_validation=True,
        skip_witness_http=True,
    )
    assert code == 0
    assert report["trigger"] == "manual"
    out = tmp_path / "artifacts" / "control_plane" / "google_docs_refresh_report.json"
    assert out.is_file()
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["job"] == "google_docs_refresh_v1"
