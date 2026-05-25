"""Tests for scripts/ppe_preflight.py."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_preflight import run_preflight


def test_preflight_fails_without_plan(tmp_path: Path):
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"phasePlanPath": "", "status": "READY"}),
        encoding="utf-8",
    )
    result = run_preflight(tmp_path, check_orchestrator=False)
    assert result["ok"] is False
    assert any("phasePlanPath" in e for e in result["errors"])


def test_preflight_fails_complete_status(tmp_path: Path):
    plan_rel = "docs/SOP/PHASE_PLANS/t.json"
    plan_path = tmp_path / plan_rel
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(
        json.dumps(
            {
                "name": "x",
                "slices": [{"sliceId": "C", "closeout": {}}],
            }
        ),
        encoding="utf-8",
    )
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"phasePlanPath": plan_rel, "status": "COMPLETE"}),
        encoding="utf-8",
    )
    result = run_preflight(tmp_path, check_orchestrator=False)
    assert result["ok"] is False
    assert any("COMPLETE" in e for e in result["errors"])
