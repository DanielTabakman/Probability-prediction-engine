"""Charter witness for MSOS P4 Strategy Lab (SELECTION after P3 COMPLETE)."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import validate_phase_plan
from scripts.ppe_queue_health import audit_queue

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"

P4_PLAN_REL = "docs/SOP/PHASE_PLANS/msos_p4_strategy_lab_relay.json"
P4_PLAN = SOP / "PHASE_PLANS" / "msos_p4_strategy_lab_relay.json"
P4_SPRINT = SOP / "SPRINT_MSOS_P4_STRATEGY_LAB.md"
P4_SELECTION = SOP / "POST_MSOS_P4_STRATEGY_LAB_SELECTION.md"
P4_EVIDENCE = SOP / "MSOS_P4_STRATEGY_LAB_EVIDENCE_STATUS.md"
PHASE_QUEUE = SOP / "PHASE_QUEUE.json"
BACKLOG = SOP / "PHASE_CHAPTER_BACKLOG.json"
MANIFEST = SOP / "ACTIVE_PHASE_MANIFEST.json"


def test_p4_charter_artifacts_exist() -> None:
    for path in (P4_PLAN, P4_SPRINT, P4_SELECTION, P4_EVIDENCE):
        assert path.is_file(), f"missing charter artifact: {path.relative_to(REPO)}"


def test_p4_phase_plan_valid() -> None:
    plan = json.loads(P4_PLAN.read_text(encoding="utf-8"))
    assert not validate_phase_plan(plan)
    assert plan["slices"][0]["sliceId"] == "MSOS-P4-Control-Slice001"
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("chapterId") == "msos_p4_strategy_lab"


def test_phase_queue_msos_p4_ready() -> None:
    queue = json.loads(PHASE_QUEUE.read_text(encoding="utf-8"))
    row = next(item for item in queue["items"] if item["planPath"] == P4_PLAN_REL)
    assert row["status"] == "READY"
    assert row["selectionPrep"] == "docs/SOP/POST_MSOS_P4_STRATEGY_LAB_SELECTION.md"


def test_backlog_p4_chartered_with_plan() -> None:
    backlog = json.loads(BACKLOG.read_text(encoding="utf-8"))
    by_id = {item["chapterId"]: item for item in backlog["items"]}
    p4 = by_id["msos_p4_strategy_lab"]
    assert p4["status"] in ("queued", "chartered")
    assert p4["planPath"] == P4_PLAN_REL


def test_manifest_points_at_p4() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["phasePlanPath"] == P4_PLAN_REL
    assert manifest["status"] in ("READY", "RUNNING")


def test_queue_health_no_issues_on_live_queue() -> None:
    issues, _ = audit_queue(REPO)
    assert issues == [], f"queue health issues: {issues}"
