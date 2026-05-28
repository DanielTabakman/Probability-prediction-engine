"""Charter witness for MVP1-Sprint003-Control-Slice001 (EVIDENCE-PLANE)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest, resolve_summary, validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/mvp1_sprint003_evidence_plane_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
SELECTION_OUTCOME = SOP / "POST_MVP1_FEEDBACK_BETA_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"


def test_charter_artifacts_exist() -> None:
    for path in (SPRINT_SPEC, Path(REPO / PLAN_REL), SELECTION_OUTCOME, EVIDENCE_STATUS, PHASE_QUEUE):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_phase_plan_valid_and_first_slice_is_control_charter() -> None:
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    first = plan["slices"][0]
    assert first["sliceId"] == "MVP1-Sprint003-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"


def test_active_manifest_after_sprint003_closeout() -> None:
    manifest = load_manifest(REPO)
    assert manifest.get("phasePlanPath") in ("", PLAN_REL)
    assert manifest["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_SPRINT003_EVIDENCE_PLANE.md"
    assert manifest["status"] in ("COMPLETE", "RUNNING", "READY")
    if manifest["status"] == "RUNNING":
        summary = resolve_summary(REPO)
        assert summary["errors"] == []
        assert summary["first_slice_id"] == "MVP1-Sprint003-Control-Slice001"


def test_phase_queue_sprint003_done_or_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    sprint003 = next(
        item for item in queue["items"] if item["planPath"] == PLAN_REL
    )
    assert sprint003["status"] in ("READY", "DONE")
    if sprint003["status"] == "READY":
        assert "selectionPrep" in sprint003


def test_evidence_status_stub_records_control_slice_closed() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "MVP1-Sprint003-Control-Slice001" in text
    assert "**CLOSED**" in text
