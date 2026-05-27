"""Charter witness for MVP1-Sprint003 (EVIDENCE-PLANE chapter)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest, validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/mvp1_sprint003_evidence_plane_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
SELECTION_OUTCOME = SOP / "POST_MVP1_FEEDBACK_BETA_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
NEXT_SELECTION = SOP / "POST_MVP1_SPRINT003_SELECTION.md"


def test_charter_artifacts_exist() -> None:
    for path in (
        SPRINT_SPEC,
        Path(REPO / PLAN_REL),
        SELECTION_OUTCOME,
        EVIDENCE_STATUS,
        PHASE_QUEUE,
        NEXT_SELECTION,
    ):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_phase_plan_valid_and_first_slice_is_control_charter() -> None:
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    first = plan["slices"][0]
    assert first["sliceId"] == "MVP1-Sprint003-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"


def test_active_manifest_chapter_complete() -> None:
    manifest = load_manifest(REPO)
    assert manifest.get("phasePlanPath") == ""
    assert manifest["status"] == "COMPLETE"
    assert manifest["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert plan["slices"][0]["sliceId"] == "MVP1-Sprint003-Control-Slice001"


def test_phase_queue_sprint003_done() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    sprint003 = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert sprint003["status"] == "DONE"
    assert "selectionPrep" in sprint003


def test_evidence_status_records_chapter_complete() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "MVP1-Sprint003-Control-Slice001" in text
    assert "**COMPLETE**" in text
    assert "POST_MVP1_SPRINT003_SELECTION" in text
