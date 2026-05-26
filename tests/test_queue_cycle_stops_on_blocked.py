"""Tests that queue cycle marks BLOCKED and stops on hard outcomes."""

from __future__ import annotations

import json
from pathlib import Path
from unittest import mock

import pytest

from scripts import queue_cycle as qc
from scripts import run_queue_cycle as runner


@pytest.fixture
def pending_queue(tmp_path: Path) -> Path:
    item = {
        "queueId": "Q-BLOCK-0001",
        "chapterId": "block_test",
        "chapterTitle": "Block test",
        "phasePlanName": "block_test_relay",
        "status": "PENDING",
        "createdAt": "2026-05-26T00:00:00Z",
        "updatedAt": "2026-05-26T00:00:00Z",
        "sprintSpecPath": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
        "selectionRecord": "docs/SOP/POST_VALIDATION_CHAPTER_SELECTION.md",
        "slices": [
            {
                "sliceId": "Block-Control-Slice001",
                "declaredPlane": "CONTROL-PLANE",
            },
            {
                "sliceId": "Block-Product-Slice002",
                "declaredPlane": "PRODUCT-PLANE",
                "touchSet": ["tests/"],
            },
            {
                "sliceId": "Block-Closeout-Slice003",
                "declaredPlane": "CONTROL-PLANE",
                "closeout": {
                    "chapterId": "block_test",
                    "chapterTitle": "Block test",
                    "chapterStatus": "COMPLETE",
                    "closedDate": "2026-05-26",
                    "evidenceDoc": "docs/SOP/VALIDATION_EVIDENCE_STATUS.md",
                    "sprintSpec": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
                    "nextSelectionDoc": "docs/SOP/MVP1_FRONTIER.md",
                },
            },
        ],
    }
    rel = "docs/SOP/SLICE_QUEUE_V1.json"
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(
            {
                "version": 1,
                "defaultBaselineBranch": "main",
                "defaultSprintSpecPath": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
                "items": [item],
            }
        ),
        encoding="utf-8",
    )
    repo = Path(__file__).resolve().parents[1]
    for doc in (
        "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
        "docs/SOP/POST_VALIDATION_CHAPTER_SELECTION.md",
        "docs/SOP/VALIDATION_EVIDENCE_STATUS.md",
        "docs/SOP/MVP1_FRONTIER.md",
    ):
        dst = tmp_path / doc
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text((repo / doc).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps({"phasePlanPath": "", "status": "COMPLETE"}),
        encoding="utf-8",
    )
    return p


def test_classify_blocked_on_stop_for_review(tmp_path: Path):
    orch = tmp_path / "artifacts/orchestrator"
    orch.mkdir(parents=True)
    report = {
        "wrapper_exit_code": 0,
        "status_bucket": "stop_for_review_or_procedural",
        "awaiting_user": True,
        "relay_result": {"decision": "STOP_FOR_REVIEW", "safe_to_continue": False},
    }
    (orch / "LAST_RUN_REPORT.json").write_text(json.dumps(report), encoding="utf-8")
    (tmp_path / "docs/SOP").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps(
            {
                "phasePlanPath": "docs/SOP/PHASE_PLANS/x.json",
                "status": "READY",
            }
        ),
        encoding="utf-8",
    )
    status, reason = qc.classify_chapter_outcome(
        tmp_path, wrapper_exit_code=0, plan_rel="docs/SOP/PHASE_PLANS/x.json"
    )
    assert status == "BLOCKED"
    assert "STOP_FOR_REVIEW" in reason or "awaiting" in reason.lower()


def test_classify_done_on_manifest_complete(tmp_path: Path):
    orch = tmp_path / "artifacts/orchestrator"
    orch.mkdir(parents=True)
    plan_rel = "docs/SOP/PHASE_PLANS/x.json"
    (orch / "LAST_RUN_REPORT.json").write_text(
        json.dumps(
            {
                "wrapper_exit_code": 0,
                "status_bucket": "continue",
                "relay_result": {"decision": "CONTINUE", "safe_to_continue": True},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs/SOP").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps({"phasePlanPath": plan_rel, "status": "COMPLETE"}),
        encoding="utf-8",
    )
    status, _ = qc.classify_chapter_outcome(
        tmp_path, wrapper_exit_code=0, plan_rel=plan_rel
    )
    assert status == "DONE"


def test_process_one_marks_blocked_on_nonzero_exit(pending_queue: Path, tmp_path: Path):
    with mock.patch.object(runner, "_run_ppe", return_value=20):
        code, should_continue = runner._process_one_chapter(
            tmp_path, queue_rel="docs/SOP/SLICE_QUEUE_V1.json", dry_run=False
        )
    assert code != 0
    assert should_continue is False
    data = qc.load_queue(tmp_path)
    item = qc.find_item_by_queue_id(data, "Q-BLOCK-0001")
    assert item is not None
    assert item["status"] == "BLOCKED"
