"""Charter witness for MSOS P3 Command Center (SELECTION 2026-06-03)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

P3_PLAN_REL = "docs/SOP/PHASE_PLANS/msos_p3_command_center_relay.json"
P3_PLAN = SOP / "PHASE_PLANS" / "msos_p3_command_center_relay.json"
P3_SPRINT = SOP / "SPRINT_MSOS_P3_COMMAND_CENTER.md"
P3_SELECTION = SOP / "POST_MSOS_P3_COMMAND_CENTER_SELECTION.md"
P3_EVIDENCE = SOP / "MSOS_P3_COMMAND_CENTER_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
BACKLOG = SOP / "PHASE_CHAPTER_BACKLOG.json"
MANIFEST = SOP / "ACTIVE_PHASE_MANIFEST.json"


def test_p3_charter_artifacts_exist() -> None:
    for path in (P3_PLAN, P3_SPRINT, P3_SELECTION, P3_EVIDENCE):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_p3_phase_plan_valid() -> None:
    plan = json.loads(P3_PLAN.read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "MSOS-P3-Control-Slice001"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "msos_p3_command_center"


def test_phase_queue_msos_p3_done() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == P3_PLAN_REL)
    assert row["status"] in ("DONE", "READY")
    assert row["selectionPrep"] == "docs/SOP/POST_MSOS_P3_COMMAND_CENTER_SELECTION.md"


def test_backlog_p3_done_with_plan() -> None:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    by_id = {item["chapterId"]: item for item in backlog["items"]}
    p3 = by_id["msos_p3_command_center"]
    assert p3["status"] == "done"
    assert p3["planPath"] == P3_PLAN_REL


def test_manifest_not_active_on_p3_after_complete() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phasePlanPath"] != P3_PLAN_REL


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"
