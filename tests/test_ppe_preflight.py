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


def test_preflight_repairs_backlog_evidence_complete(tmp_path: Path) -> None:
    sop = tmp_path / "docs" / "SOP"
    plans = sop / "PHASE_PLANS"
    plans.mkdir(parents=True)
    (sop / "PHASE_QUEUE.json").write_text(
        json.dumps({"version": 1, "items": []}),
        encoding="utf-8",
    )
    (sop / "CHAPTER_DONE_EVIDENCE.md").write_text(
        "# Evidence\n\n**Status:** **COMPLETE** 2026-06-05\n",
        encoding="utf-8",
    )
    plan = {
        "name": "done",
        "slices": [
            {
                "sliceId": "X-Closeout",
                "closeout": {"evidenceDoc": "docs/SOP/CHAPTER_DONE_EVIDENCE.md"},
            }
        ],
    }
    (plans / "done.json").write_text(json.dumps(plan), encoding="utf-8")
    (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
        json.dumps(
            {
                "version": 1,
                "items": [
                    {
                        "chapterId": "done",
                        "status": "blocked",
                        "planPath": "docs/SOP/PHASE_PLANS/done.json",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    manifest_path = sop / "ACTIVE_PHASE_MANIFEST.json"
    manifest_path.write_text(
        json.dumps({"phasePlanPath": "", "status": "COMPLETE"}),
        encoding="utf-8",
    )
    result = run_preflight(tmp_path, check_orchestrator=False, allow_complete=True)
    assert result["ok"] is True
    backlog = json.loads((sop / "PHASE_CHAPTER_BACKLOG.json").read_text(encoding="utf-8"))
    assert backlog["items"][0]["status"] == "done"
