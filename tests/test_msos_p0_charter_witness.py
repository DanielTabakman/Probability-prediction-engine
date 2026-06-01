"""Charter witness for MSOS Website Program P0 (queue install)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

PLAN_REL = "docs/SOP/PHASE_PLANS/msos_website_program_p0_relay.json"
SPRINT_SPEC = SOP / "SPRINT_MSOS_WEBSITE_PROGRAM_P0.md"
SELECTION_OUTCOME = SOP / "POST_MSOS_WEBSITE_PROGRAM_P0_SELECTION.md"
EVIDENCE_STATUS = SOP / "MSOS_WEBSITE_PROGRAM_P0_EVIDENCE_STATUS.md"
MSOS_PROGRAM = SOP / "MSOS_WEBSITE_PROGRAM.md"
MSOS_FRONTIER = SOP / "MSOS_FRONTIER.md"
STORYBOARD_GATE = REPO / "docs" / "VISION" / "MSOS_STORYBOARD_GATE.md"
MASTER = REPO / "docs" / "VISION" / "PPE_MASTER_MVP1.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
BACKLOG = SOP / "PHASE_CHAPTER_BACKLOG.json"
P1_PLAN = SOP / "PHASE_PLANS" / "msos_p1_stack_routing_relay.json"


def test_charter_artifacts_exist() -> None:
    for path in (
        SPRINT_SPEC,
        Path(REPO / PLAN_REL),
        SELECTION_OUTCOME,
        EVIDENCE_STATUS,
        MSOS_PROGRAM,
        MSOS_FRONTIER,
        STORYBOARD_GATE,
        PHASE_QUEUE,
        BACKLOG,
        P1_PLAN,
    ):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_master_contains_waterfall_queue() -> None:
    text = MASTER.read_text(encoding="utf-8")
    assert "MSOS WEBSITE PROGRAM — SELECTED WATERFALL QUEUE — 2026-05-31" in text


def test_phase_plan_valid_and_first_slice_is_control() -> None:
    plan = json.loads((REPO / PLAN_REL).read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    first = plan["slices"][0]
    assert first["sliceId"] == "MSOS-P0-Control-Slice001"
    assert first["declaredPlane"] == "EVIDENCE-PLANE"
    assert plan["baselineBranch"] == "main"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "msos_website_program_p0"


def test_phase_queue_msos_p0_ready_or_done() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == PLAN_REL)
    assert row["status"] in ("READY", "DONE")
    if row["status"] == "READY":
        assert "selectionPrep" in row


def test_backlog_p1_queued_p2_blocked() -> None:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    by_id = {item["chapterId"]: item for item in backlog["items"]}
    assert by_id["msos_p1_stack_routing"]["status"] in ("queued", "chartered", "done")
    assert by_id["msos_p2_homepage"]["status"] == "blocked"
    assert by_id["msos_p8_tester_release"]["status"] == "blocked"


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"
