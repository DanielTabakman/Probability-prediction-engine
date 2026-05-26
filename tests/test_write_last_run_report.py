"""Tests for write_last_run_report context enrichment."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.write_last_run_report import _enrich_from_manifest, _render_md


def test_enrich_from_manifest_adds_context_ritual(tmp_path: Path):
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"status": "RUNNING", "sprintSpecPath": ""}),
        encoding="utf-8",
    )
    report: dict = {"next_action": "test"}
    _enrich_from_manifest(tmp_path, report)
    assert report.get("manifest_path")
    assert report.get("context_ritual")
    md = _render_md(report)
    assert "Cursor context ritual" in md
