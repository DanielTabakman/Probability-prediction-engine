"""Tests for scripts/ppe_manifest.py and resolve_active_phase."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.ppe_manifest import (
    load_manifest,
    maybe_mark_manifest_complete,
    resolve_summary,
    save_manifest,
    validate_manifest,
    validate_phase_plan,
)
from scripts.ppe_phase_plan_window import mark_slice_complete


def _write_plan(tmp_path: Path, name: str = "test_relay.json") -> Path:
    plan = {
        "name": "Test chapter",
        "baselineBranch": "main",
        "slices": [
            {"sliceId": "Test-Control-001", "declaredPlane": "CONTROL-PLANE"},
            {
                "sliceId": "Test-Closeout-002",
                "declaredPlane": "CONTROL-PLANE",
                "closeout": {"chapterId": "test", "chapterTitle": "T", "chapterStatus": "COMPLETE"},
            },
        ],
    }
    rel = f"docs/SOP/PHASE_PLANS/{name}"
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(plan), encoding="utf-8")
    return rel


def test_validate_phase_plan_requires_closeout():
    assert validate_phase_plan({"slices": [{"sliceId": "A"}]})
    assert not validate_phase_plan(
        {
            "slices": [
                {"sliceId": "A"},
                {"sliceId": "B", "closeout": {}},
            ]
        }
    )


def test_manifest_ready_requires_plan(tmp_path: Path):
    manifest = {
        "phasePlanPath": "",
        "status": "READY",
        "selectionRecord": "",
    }
    errs = validate_manifest(tmp_path, manifest)
    assert any("phasePlanPath" in e for e in errs)


def test_resolve_summary_ok(tmp_path: Path):
    plan_rel = _write_plan(tmp_path)
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(
            {
                "phasePlanPath": plan_rel,
                "sprintSpecPath": "",
                "selectionRecord": "",
                "status": "READY",
            }
        ),
        encoding="utf-8",
    )
    summary = resolve_summary(tmp_path)
    assert summary["errors"] == []
    assert summary["slice_count"] == 2
    assert summary["first_slice_id"] == "Test-Control-001"


def test_maybe_mark_manifest_complete(tmp_path: Path):
    plan_rel = _write_plan(tmp_path)
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"phasePlanPath": plan_rel, "status": "RUNNING"}),
        encoding="utf-8",
    )
    plan_abs = tmp_path / plan_rel
    assert not maybe_mark_manifest_complete(tmp_path, plan_abs, "Test-Closeout-002")
    mark_slice_complete(tmp_path, plan_rel, "Test-Control-001")
    assert maybe_mark_manifest_complete(tmp_path, plan_abs, "Test-Closeout-002")
    assert load_manifest(tmp_path)["status"] == "COMPLETE"
    assert not maybe_mark_manifest_complete(tmp_path, plan_abs, "Test-Control-001")


def test_save_manifest_roundtrip(tmp_path: Path):
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text('{"status":"READY","phasePlanPath":""}', encoding="utf-8")
    save_manifest(tmp_path, load_manifest(tmp_path) | {"status": "RUNNING"})
    assert load_manifest(tmp_path)["status"] == "RUNNING"
