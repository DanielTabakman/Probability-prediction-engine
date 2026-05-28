"""Charter witness for Phase 3 commercial wrapper (EVIDENCE-PLANE chapter)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest, validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/phase3_commercial_wrapper_relay.json"
SPRINT_SPEC = SOP / "SPRINT_PHASE3_COMMERCIAL_WRAPPER.md"
SELECTION_OUTCOME = SOP / "POST_MVP1_PRODUCT_SHELL_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "PHASE3_COMMERCIAL_WRAPPER_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
NEXT_SELECTION = SOP / "POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION.md"


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
    assert first["sliceId"] == "Phase3-CommercialWrapper-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_PHASE3_COMMERCIAL_WRAPPER.md"


def test_active_manifest_ready_for_relay() -> None:
    manifest = load_manifest(REPO)
    assert manifest.get("phasePlanPath") == PLAN_REL
    assert manifest["status"] in ("READY", "RUNNING")
    assert manifest["sprintSpecPath"] == "docs/SOP/SPRINT_PHASE3_COMMERCIAL_WRAPPER.md"


def test_phase_queue_phase3_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert row["status"] == "READY"
    assert "selectionPrep" in row


def test_evidence_status_control_slice_closed() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "Phase3-CommercialWrapper-Control-Slice001" in text
    assert "**CLOSED**" in text
    assert "POST_MVP1_PRODUCT_SHELL_SELECTION" in text
