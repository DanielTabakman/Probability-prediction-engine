"""Charter witness for MVP1 product shell clarity chapter."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/mvp1_product_shell_clarity_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MVP1_PRODUCT_SHELL_CLARITY.md"
SELECTION_OUTCOME = SOP / "POST_MVP1_DECISION_REVIEW_SELECTION_OUTCOME.md"
EVIDENCE_STATUS = SOP / "MVP1_PRODUCT_SHELL_CLARITY_EVIDENCE_STATUS.md"
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


def test_phase_plan_valid_and_first_slice_is_evidence_charter() -> None:
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    first = plan["slices"][0]
    assert first["sliceId"] == "MVP1-ProductShell-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"


def test_active_manifest_chapter_complete() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert "**COMPLETE**" in text
    assert "MVP1-ProductShell-Closeout-Slice004" in text


def test_phase_queue_product_shell_done() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert row["status"] == "DONE"
