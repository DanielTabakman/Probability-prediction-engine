"""Tests for apply_control_closeout_v1."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.relay.apply_control_closeout import (
    CloseoutSpec,
    apply_control_closeout,
    build_handoff_gate,
)
from scripts.relay.steering_alignment import check_steering_alignment


def _minimal_docs(tmp_path: Path) -> CloseoutSpec:
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    spec = CloseoutSpec(
        chapter_id="test_chapter",
        chapter_title="Test Chapter",
        chapter_status="COMPLETE",
        closed_date="2026-05-20",
        evidence_doc="docs/SOP/TEST_EVIDENCE.md",
        sprint_spec="docs/SOP/SPRINT_TEST.md",
        next_selection_doc="docs/SOP/POST_TEST_SELECTION.md",
        carry_docs=["docs/SOP/TEST_EVIDENCE.md"],
        dual_smoke_run_ids=["20260520_000001"],
        pytest_count=42,
        slice_id="Test-Closeout-Slice001",
    )
    (sop / "HANDOFF.md").write_text(
        "# HANDOFF\n\n## HANDOFF GATE\n\n```text\n"
        f"- Next pending execution step: **steward SELECTION** — `{spec.next_selection_doc}`\n"
        f"- Last closed chapter: **{spec.chapter_title}** — **{spec.chapter_status}** {spec.closed_date}\n"
        "```\n\n## Current priority\n\nold\n\n"
        "## Recommended next step\n\nold\n\n## Last updated\n\nold\n",
        encoding="utf-8",
    )
    (sop / "MVP1_FRONTIER.md").write_text(
        "### Current execution focus (MVP1 framing)\n"
        f"- **Active BUILD chapter:** **none** — [`POST_TEST_SELECTION.md`]({spec.next_selection_doc})\n"
        f"- **Last closed chapter:** **{spec.chapter_title}** — **{spec.chapter_status}** {spec.closed_date}\n\n"
        "### Other\n",
        encoding="utf-8",
    )
    (sop / "PPE_INTEGRATED_STATUS.md").write_text(
        "**As-of:** 2026-01-01\n\n## Archived chapters\n\n| Chapter | Status |\n"
        f"|---------|--------|\n| {spec.chapter_title} | **{spec.chapter_status}** {spec.closed_date} |\n\n"
        f"**Next chapter SELECTION:** [`POST_TEST_SELECTION.md`]({spec.next_selection_doc})\n\n"
        "## Engineering gates\n\n"
        "| Gate | Status | Notes |\n|------|--------|-------|\n"
        "| `python -m pytest -q` | **PASS** | old |\n"
        "| Dual smoke | **PASS** | old |\n\n"
        f"## Next BUILD (agent lane)\n\n[`POST_TEST_SELECTION.md`]({spec.next_selection_doc})\n",
        encoding="utf-8",
    )
    (sop / "TEST_EVIDENCE.md").write_text(
        "## Chapter status\n\n**Test Chapter:** **PENDING**.\n", encoding="utf-8"
    )
    return spec


def test_build_handoff_gate_includes_chapter() -> None:
    spec = CloseoutSpec(
        chapter_id="x",
        chapter_title="Test Chapter",
        chapter_status="COMPLETE",
        closed_date="2026-05-20",
        evidence_doc="docs/SOP/E.md",
        sprint_spec="docs/SOP/S.md",
        next_selection_doc="docs/SOP/POST_TEST_SELECTION.md",
    )
    gate = build_handoff_gate(spec)
    assert "test chapter" in gate.lower()
    assert "POST_TEST_SELECTION.md" in gate


def test_apply_closeout_idempotent(tmp_path: Path) -> None:
    spec = _minimal_docs(tmp_path)
    report1 = apply_control_closeout(tmp_path, closeout=spec)
    assert report1["passed"]
    report2 = apply_control_closeout(tmp_path, closeout=spec)
    assert report2["passed"]
    align = check_steering_alignment(
        tmp_path,
        expected_chapter_title=spec.chapter_title,
        expected_closed_date=spec.closed_date,
        expected_next_selection=spec.next_selection_doc,
        expected_evidence_doc=spec.evidence_doc,
    )
    assert align.passed
    brief = tmp_path / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md"
    assert brief.is_file()
    assert "Test Chapter" in brief.read_text(encoding="utf-8")


def test_relay_closeout_job_refusal_without_closeout_block(tmp_path: Path) -> None:
    import scripts.relay_runtime_v0 as relay

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps({"slices": [{"sliceId": "Other-Slice"}]}), encoding="utf-8")
    runtime = relay.Runtime(tmp_path)
    code, _msg = relay.dispatch_apply_control_closeout_v1(
        runtime,
        relay_run_dir=None,
        phase_plan_path=plan_path,
        slice_id="Other-Slice",
        force=True,
    )
    assert code == relay.EXIT_REFUSAL


def test_find_closeout_in_plan(tmp_path: Path) -> None:
    from scripts.relay.apply_control_closeout import find_closeout_for_slice, load_phase_plan

    plan_path = tmp_path / "plan.json"
    plan_path.write_text(
        json.dumps(
            {
                "slices": [
                    {
                        "sliceId": "A-Closeout-001",
                        "closeout": {"chapterId": "a", "chapterTitle": "A"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    plan = load_phase_plan(plan_path)
    assert find_closeout_for_slice(plan, "A-Closeout-001") is not None
    assert find_closeout_for_slice(plan, "other") is None
