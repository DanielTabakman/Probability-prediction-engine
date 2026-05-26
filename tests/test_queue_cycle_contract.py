"""Tests for chapter queue contract and plan/manifest generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import queue_cycle as qc


@pytest.fixture
def sample_item() -> dict:
    return {
        "queueId": "Q-TEST-0001",
        "chapterId": "test_chapter",
        "chapterTitle": "Test chapter",
        "phasePlanName": "test_chapter_relay",
        "baselineBranch": "main",
        "sprintSpecPath": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
        "selectionRecord": "docs/SOP/POST_VALIDATION_CHAPTER_SELECTION.md",
        "status": "PENDING",
        "createdAt": "2026-05-26T00:00:00Z",
        "updatedAt": "2026-05-26T00:00:00Z",
        "slices": [
            {
                "sliceId": "Test-Control-Slice001",
                "declaredPlane": "CONTROL-PLANE",
                "susMinutes": 15,
                "hardMinutes": 30,
                "maxAttempts": 1,
            },
            {
                "sliceId": "Test-Product-Slice002",
                "declaredPlane": "PRODUCT-PLANE",
                "touchSet": ["src/viz/", "tests/"],
                "forbiddenTouch": ["src/viz/app.py"],
                "susMinutes": 15,
                "hardMinutes": 30,
                "maxAttempts": 2,
            },
            {
                "sliceId": "Test-Closeout-Slice003",
                "declaredPlane": "CONTROL-PLANE",
                "susMinutes": 15,
                "hardMinutes": 30,
                "maxAttempts": 1,
                "closeout": {
                    "chapterId": "test_chapter",
                    "chapterTitle": "Test chapter",
                    "chapterStatus": "COMPLETE",
                    "closedDate": "2026-05-26",
                    "evidenceDoc": "docs/SOP/VALIDATION_EVIDENCE_STATUS.md",
                    "sprintSpec": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
                    "nextSelectionDoc": "docs/SOP/MVP1_FRONTIER.md",
                },
            },
        ],
    }


@pytest.fixture
def queue_file(tmp_path: Path, sample_item: dict) -> Path:
    data = {
        "version": 1,
        "defaultBaselineBranch": "main",
        "defaultSprintSpecPath": "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
        "items": [sample_item],
    }
    rel = "docs/SOP/SLICE_QUEUE_V1.json"
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    # Copy referenced docs from repo
    repo = Path(__file__).resolve().parents[1]
    for doc in (
        "docs/SOP/SPRINT_VALIDATION_CHAPTER.md",
        "docs/SOP/POST_VALIDATION_CHAPTER_SELECTION.md",
        "docs/SOP/VALIDATION_EVIDENCE_STATUS.md",
        "docs/SOP/MVP1_FRONTIER.md",
    ):
        src = repo / doc
        dst = tmp_path / doc
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    manifest = {
        "phasePlanPath": "",
        "sprintSpecPath": "",
        "status": "COMPLETE",
        "notes": "test",
    }
    mp = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    mp.write_text(json.dumps(manifest), encoding="utf-8")
    return p


def test_validate_queue_item_ok(tmp_path: Path, queue_file: Path, sample_item: dict):
    errors = qc.validate_queue_item(sample_item, repo_root=tmp_path)
    assert errors == []


def test_build_and_write_phase_plan(tmp_path: Path, queue_file: Path, sample_item: dict):
    _, plan_rel = qc.write_generated_phase_plan(tmp_path, sample_item)
    plan_path = tmp_path / plan_rel
    assert plan_path.is_file()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert plan["name"] == "test_chapter_relay"
    assert len(plan["slices"]) == 3
    assert plan["sprintSpecPath"] == "docs/SOP/SPRINT_VALIDATION_CHAPTER.md"


def test_write_manifest_for_item(tmp_path: Path, queue_file: Path, sample_item: dict):
    _, plan_rel = qc.write_generated_phase_plan(tmp_path, sample_item)
    qc.write_manifest_for_item(tmp_path, sample_item, plan_rel)
    manifest = qc.load_manifest(tmp_path)
    assert manifest["status"] == "READY"
    assert manifest["phasePlanPath"] == plan_rel.replace("\\", "/")
    assert "Q-TEST-0001" in manifest.get("notes", "")


def test_pick_next_pending_skips_done(tmp_path: Path, queue_file: Path):
    data = qc.load_queue(tmp_path)
    data["items"].append(
        {
            **data["items"][0],
            "queueId": "Q-TEST-0002",
            "status": "DONE",
        }
    )
    data["items"][0]["status"] = "PENDING"
    pending = qc.pick_next_pending(data)
    assert pending is not None
    assert pending["queueId"] == "Q-TEST-0001"


def test_repo_seed_queue_validates():
    repo = Path(__file__).resolve().parents[1]
    data = qc.load_queue(repo)
    for item in data.get("items") or []:
        if not isinstance(item, dict):
            continue
        errors = qc.validate_queue_item(item, repo_root=repo)
        assert errors == [], f"{item.get('queueId')}: {errors}"
