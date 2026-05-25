"""Tests for sync_msos_repo_truth_v1."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from scripts.msos.build_snapshot import MARKER_END, MARKER_START
from scripts.sync_msos_repo_truth import (
    _find_marker_indices,
    run_sync,
    write_sync_report,
)

SAMPLE_DOC = {
    "body": {
        "content": [
            {
                "paragraph": {
                    "elements": [
                        {
                            "startIndex": 1,
                            "textRun": {"content": f"Intro\n{MARKER_START}\nold body\n{MARKER_END}\n"},
                        }
                    ]
                }
            }
        ]
    }
}


def test_find_marker_indices():
    indices = _find_marker_indices(SAMPLE_DOC, MARKER_START, MARKER_END)
    assert indices is not None
    start, end = indices
    assert start < end


def test_run_sync_dry_run(tmp_path):
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "VISION").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(
        "### Current execution focus (MVP1 framing)\n- test\n\n### Other\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md").write_text(
        "| Contract element | Status | Notes |\n|---|---|---|\n| x | y | z |\n",
        encoding="utf-8",
    )
    rc = run_sync(tmp_path, dry_run=True)
    assert rc == 0
    report = json.loads(
        (tmp_path / "artifacts" / "control_plane" / "msos_sync_report.json").read_text(encoding="utf-8")
    )
    assert report["skipped"] is True
    assert report["reason"] == "dry_run"
    assert (tmp_path / "artifacts" / "msos_repo_truth_snapshot.md").is_file()


def test_run_sync_skips_without_env(tmp_path):
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "VISION").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(
        "### Current execution focus (MVP1 framing)\n- test\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md").write_text("", encoding="utf-8")
    rc = run_sync(tmp_path, dry_run=False)
    assert rc == 0
    report = json.loads(
        (tmp_path / "artifacts" / "control_plane" / "msos_sync_report.json").read_text(encoding="utf-8")
    )
    assert report["reason"] == "missing_env_or_token"


@patch("scripts.sync_msos_repo_truth.push_markdown_to_doc")
def test_run_sync_push_ok(mock_push, tmp_path):
    mock_push.return_value = {"document_id": "doc123", "chars_inserted": 100}
    (tmp_path / ".env.mcp").write_text(
        "GOOGLE_CLIENT_ID=id\nGOOGLE_CLIENT_SECRET=secret\nMSOS_REPO_TRUTH_DOC_ID=doc123\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "VISION").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "MVP1_FRONTIER.md").write_text(
        "### Current execution focus (MVP1 framing)\n- test\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "VISION" / "PPE_MASTER_MVP1.md").write_text("", encoding="utf-8")

    token_dir = tmp_path / ".config" / "google-docs-mcp"
    token_dir.mkdir(parents=True)
    token_dir.joinpath("token.json").write_text(
        json.dumps(
            {
                "token": "t",
                "refresh_token": "r",
                "token_uri": "https://oauth2.googleapis.com/token",
                "client_id": "id",
                "client_secret": "secret",
                "scopes": ["https://www.googleapis.com/auth/documents"],
            }
        ),
        encoding="utf-8",
    )

    with patch("scripts.sync_msos_repo_truth._token_path", return_value=token_dir / "token.json"):
        with patch("scripts.sync_msos_repo_truth._load_google_credentials", return_value=MagicMock()):
            rc = run_sync(tmp_path, dry_run=False)
    assert rc == 0
    mock_push.assert_called_once()
