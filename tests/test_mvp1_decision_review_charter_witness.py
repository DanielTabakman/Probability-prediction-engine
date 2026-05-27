"""Charter witness for MVP1 decision-ready review polish (PRODUCT chapter)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest, validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/mvp1_decision_ready_review_polish_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MVP1_DECISION_READY_REVIEW_POLISH.md"
SELECTION_OUTCOME = SOP / "POST_MVP1_SPRINT003_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "MVP1_DECISION_READY_REVIEW_POLISH_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"


def test_charter_artifacts_exist() -> None:
    for path in (
        SPRINT_SPEC,
        Path(REPO / PLAN_REL),
        SELECTION_OUTCOME,
        EVIDENCE_STATUS,
        PHASE_QUEUE,
    ):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_phase_plan_valid_and_first_slice_is_control_charter() -> None:
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    first = plan["slices"][0]
    assert first["sliceId"] == "MVP1-DecisionReview-Control-Slice001"
    assert first["declaredPlane"] == "CONTROL"
    assert plan["baselineBranch"] == "main"
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_DECISION_READY_REVIEW_POLISH.md"


def test_active_manifest_ready_for_relay() -> None:
    manifest = load_manifest(REPO)
    assert manifest.get("phasePlanPath") == PLAN_REL
    assert manifest["status"] == "READY"
    assert manifest["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_DECISION_READY_REVIEW_POLISH.md"


def test_phase_queue_decision_review_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert row["status"] == "READY"
    assert "selectionPrep" in row
