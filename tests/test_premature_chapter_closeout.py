"""Guards against steering COMPLETE while slices/assets are still pending."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_manifest import load_manifest
from scripts.ppe_queue import load_queue
from scripts.ppe_queue_health import (
    heal_premature_chapter_closeout,
    validate_chapter_closeout_ready,
)
from scripts.relay.apply_control_closeout import CloseoutSpec, apply_control_closeout


def _write_plan(tmp_path: Path, rel: str, evidence_rel: str) -> str:
    plan = {
        "name": "test",
        "slices": [
            {"sliceId": "T-Control-001"},
            {"sliceId": "T-Core-002"},
            {
                "sliceId": "T-Closeout-003",
                "closeout": {
                    "chapterId": "test_ch",
                    "chapterTitle": "Test Chapter",
                    "chapterStatus": "COMPLETE",
                    "evidenceDoc": evidence_rel,
                    "sprintSpec": "docs/SOP/SPRINT_TEST.md",
                    "nextSelectionDoc": "docs/SOP/POST_TEST.md",
                },
            },
        ],
    }
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan), encoding="utf-8")
    return rel


def test_validate_closeout_ready_blocks_pending_evidence(tmp_path: Path) -> None:
    evidence_rel = "docs/SOP/TEST_EVIDENCE.md"
    plan_rel = _write_plan(tmp_path, "docs/SOP/PHASE_PLANS/test_relay.json", evidence_rel)
    ev = tmp_path / evidence_rel
    ev.parent.mkdir(parents=True, exist_ok=True)
    ev.write_text(
        "# evidence\n\n**Status:** **CHARTERED**\n\n| Slice | Status |\n|-------|--------|\n| T-Control-001 | PENDING |\n",
        encoding="utf-8",
    )
    ok, blockers = validate_chapter_closeout_ready(tmp_path, plan_rel)
    assert not ok
    assert any("PENDING" in b for b in blockers)


def test_apply_closeout_blocked_before_steering_patch(tmp_path: Path) -> None:
    evidence_rel = "docs/SOP/TEST_EVIDENCE.md"
    plan_rel = _write_plan(tmp_path, "docs/SOP/PHASE_PLANS/test_relay.json", evidence_rel)
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True, exist_ok=True)
    (sop / "HANDOFF.md").write_text("# HANDOFF\n\n```text\nold\n```\n", encoding="utf-8")
    (sop / "MVP1_FRONTIER.md").write_text("### Current execution focus (MVP1 framing)\nold\n\n### X\n", encoding="utf-8")
    (sop / "PPE_INTEGRATED_STATUS.md").write_text("**As-of:** 2026-01-01\n", encoding="utf-8")
    ev = sop / "TEST_EVIDENCE.md"
    ev.write_text(
        "# evidence\n\n**Status:** **CHARTERED**\n\n| Slice | Status |\n|-------|--------|\n| T-Core-002 | PENDING |\n",
        encoding="utf-8",
    )
    spec = CloseoutSpec(
        chapter_id="test_ch",
        chapter_title="Test Chapter",
        chapter_status="COMPLETE",
        closed_date="2026-06-29",
        evidence_doc=evidence_rel,
        sprint_spec="docs/SOP/SPRINT_TEST.md",
        next_selection_doc="docs/SOP/POST_TEST.md",
        slice_id="T-Closeout-003",
    )
    report = apply_control_closeout(tmp_path, closeout=spec, phase_plan_path=plan_rel)
    assert report.get("blocked") is True
    assert "PENDING" in " ".join(report.get("blockers") or [])
    assert "**COMPLETE**" not in ev.read_text(encoding="utf-8")
    assert "old" in (sop / "HANDOFF.md").read_text(encoding="utf-8")


def test_heal_reopens_only_first_premature_done_as_ready(tmp_path: Path) -> None:
    plans = []
    for n in ("a", "b"):
        evidence_rel = f"docs/SOP/EV_{n.upper()}.md"
        plan_rel = _write_plan(tmp_path, f"docs/SOP/PHASE_PLANS/plan_{n}_relay.json", evidence_rel)
        plans.append(plan_rel)
        ev = tmp_path / evidence_rel
        ev.parent.mkdir(parents=True, exist_ok=True)
        ev.write_text(
            f"# ev\n\n**Status:** **COMPLETE**\n\n| Slice | Status |\n|-------|--------|\n| X | PENDING |\n",
            encoding="utf-8",
        )
    queue_path = tmp_path / "docs" / "SOP" / "PHASE_QUEUE.json"
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    queue_path.write_text(
        json.dumps(
            {
                "items": [
                    {"planPath": plans[0], "status": "DONE"},
                    {"planPath": plans[1], "status": "DONE"},
                ]
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps({"phasePlanPath": "", "status": "COMPLETE"}),
        encoding="utf-8",
    )
    fixes, actions = heal_premature_chapter_closeout(tmp_path, apply=True)
    assert fixes
    queue = load_queue(tmp_path)
    by_plan = {str(i["planPath"]): str(i["status"]).upper() for i in queue["items"]}
    assert by_plan[plans[0]] == "READY"
    assert by_plan[plans[1]] == "PLANNED"
    assert load_manifest(tmp_path)["status"] == "READY"
    assert "IN PROGRESS" in (tmp_path / "docs" / "SOP" / "EV_A.md").read_text(encoding="utf-8")
