"""Charter witness for MVP1 post-Phase3 steering + smoke (EVIDENCE-PLANE chapter)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest, validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/mvp1_post_phase3_steering_smoke_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MVP1_POST_PHASE3_STEERING_SMOKE.md"
SELECTION_OUTCOME = SOP / "POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "MVP1_POST_PHASE3_STEERING_SMOKE_EVIDENCE_STATUS.md"
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
    assert first["sliceId"] == "MVP1-PostPhase3-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_MVP1_POST_PHASE3_STEERING_SMOKE.md"


def test_active_manifest_after_post_phase3_closeout() -> None:
    manifest = load_manifest(REPO)
    assert manifest.get("phasePlanPath") in ("", PLAN_REL)
    assert manifest["status"] in ("COMPLETE", "READY", "RUNNING")
    sprint = manifest.get("sprintSpecPath") or ""
    assert sprint in (
        "docs/SOP/SPRINT_MVP1_POST_PHASE3_STEERING_SMOKE.md",
        "docs/SOP/SPRINT_MVP1_DEPLOY_WITNESS_REFRESH.md",
    )
    assert manifest.get("selectionRecord") in (
        "docs/SOP/POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION_OUTCOME.md",
        "docs/SOP/DEPLOY_WITNESS_REFRESH_SELECTION.md",
    )


def test_phase_queue_post_phase3_done_or_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert row["status"] in ("READY", "DONE")
    if row["status"] == "READY":
        assert "selectionPrep" in row


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"


def test_evidence_status_chapter_complete() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "MVP1-PostPhase3-Control-Slice001" in text
    assert "**CLOSED**" in text
    assert "**COMPLETE**" in text
    assert "POST_PHASE3_COMMERCIAL_WRAPPER_SELECTION" in text
