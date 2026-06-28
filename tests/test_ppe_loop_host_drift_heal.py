"""Loop-host control-plane drift detection and recovery."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_manifest import load_manifest, maybe_mark_manifest_complete
from scripts.ppe_operator_git_sync import reset_runtime_sop_drift_from_origin
from scripts.ppe_phase_plan_window import mark_slice_complete
from scripts.ppe_queue_health import heal_premature_chapter_closeout
from scripts.ppe_vm_bootstrap import heal_premature_chapter_closeout_step


def _write_enable_pipe_plan(tmp_path: Path) -> str:
    rel = "docs/SOP/PHASE_PLANS/ppe_asset_enablement_pipeline_v1_relay.json"
    plan = {
        "name": "enable pipe",
        "slices": [
            {"sliceId": "PPE-EnablePipe-Control-Slice001"},
            {"sliceId": "PPE-EnablePipe-Core-Slice002"},
            {
                "sliceId": "PPE-EnablePipe-Closeout-Slice004",
                "closeout": {
                    "chapterId": "ppe_asset_enablement_pipeline_v1",
                    "evidenceDoc": "docs/SOP/PPE_ASSET_ENABLEMENT_PIPELINE_V1_EVIDENCE_STATUS.md",
                },
            },
        ],
    }
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan), encoding="utf-8")
    return rel


def test_maybe_mark_manifest_complete_blocks_on_pending_evidence(tmp_path: Path) -> None:
    plan_rel = _write_enable_pipe_plan(tmp_path)
    evidence = tmp_path / "docs/SOP/PPE_ASSET_ENABLEMENT_PIPELINE_V1_EVIDENCE_STATUS.md"
    evidence.write_text(
        "# evidence\n\n| Slice | Status |\n|-------|--------|\n| PPE-EnablePipe-Control-Slice001 | PENDING |\n",
        encoding="utf-8",
    )
    manifest_path = tmp_path / "docs/SOP/ACTIVE_PHASE_MANIFEST.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({"phasePlanPath": plan_rel, "status": "RUNNING"}), encoding="utf-8")
    mark_slice_complete(tmp_path, plan_rel, "PPE-EnablePipe-Control-Slice001")
    mark_slice_complete(tmp_path, plan_rel, "PPE-EnablePipe-Core-Slice002")
    plan_abs = tmp_path / plan_rel
    assert not maybe_mark_manifest_complete(tmp_path, plan_abs, "PPE-EnablePipe-Closeout-Slice004")
    assert load_manifest(tmp_path)["status"] == "RUNNING"


def test_heal_premature_chapter_closeout_reopens_queue_and_manifest(tmp_path: Path) -> None:
    plan_rel = _write_enable_pipe_plan(tmp_path)
    evidence = tmp_path / "docs/SOP/PPE_ASSET_ENABLEMENT_PIPELINE_V1_EVIDENCE_STATUS.md"
    evidence.write_text(
        "# evidence\n\n**Status:** **CHARTERED**\n\n| Slice | Status |\n|-------|--------|\n| X | PENDING |\n",
        encoding="utf-8",
    )
    sop = tmp_path / "docs/SOP"
    sop.mkdir(parents=True, exist_ok=True)
    (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps({"phasePlanPath": "", "status": "COMPLETE", "notes": "premature closeout"}),
        encoding="utf-8",
    )
    (sop / "PHASE_QUEUE.json").write_text(
        json.dumps(
            {
                "items": [
                    {
                        "planPath": plan_rel,
                        "status": "DONE",
                        "doneReason": "Chapter closeout",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (sop / "PHASE_SELECTION_ROADMAP.json").write_text(
        json.dumps({"items": [{"planPath": plan_rel, "status": "done"}]}),
        encoding="utf-8",
    )

    fixes, actions = heal_premature_chapter_closeout(tmp_path, apply=True)
    assert fixes
    manifest = json.loads((sop / "ACTIVE_PHASE_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "READY"
    assert manifest["phasePlanPath"] == plan_rel
    queue = json.loads((sop / "PHASE_QUEUE.json").read_text(encoding="utf-8"))
    assert queue["items"][0]["status"] == "READY"
    assert actions


def test_reset_runtime_sop_drift_from_origin_on_build_branch(tmp_path: Path) -> None:
    sop = tmp_path / "docs/SOP"
    sop.mkdir(parents=True, exist_ok=True)
    manifest = sop / "ACTIVE_PHASE_MANIFEST.json"
    manifest.write_text('{"status":"COMPLETE"}', encoding="utf-8")
    calls: list[list[str]] = []

    def fake_git(_repo: Path, *args: str):
        calls.append(list(args))
        if args[:2] == ("fetch", "origin"):
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("checkout", "origin/main"):
            manifest.write_text('{"status":"READY","phasePlanPath":"docs/SOP/PHASE_PLANS/x.json"}', encoding="utf-8")
            return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()
        if args[:2] == ("status", "--porcelain"):
            return type(
                "P",
                (),
                {"returncode": 0, "stdout": " M docs/SOP/ACTIVE_PHASE_MANIFEST.json\n", "stderr": ""},
            )()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    with patch("scripts.ppe_operator_git_sync._git_sync_cfg", return_value={"pullBranch": "main"}):
        with patch("scripts.ppe_operator_git_sync._current_branch", return_value="build/auto/Test-Slice001"):
            with patch("scripts.ppe_operator_git_sync._git", side_effect=fake_git):
                out = reset_runtime_sop_drift_from_origin(tmp_path)
    assert out.get("ok") is True
    assert out.get("changes")
    assert any(args[:3] == ["checkout", "origin/main", "--"] for args in calls)


def test_bootstrap_step_wraps_heal(tmp_path: Path) -> None:
    sop = tmp_path / "docs/SOP"
    sop.mkdir(parents=True, exist_ok=True)
    (sop / "ACTIVE_PHASE_MANIFEST.json").write_text('{"status":"COMPLETE","phasePlanPath":""}', encoding="utf-8")
    (sop / "PHASE_QUEUE.json").write_text(json.dumps({"items": []}), encoding="utf-8")
    out = heal_premature_chapter_closeout_step(tmp_path)
    assert out["action"] == "heal_premature_closeout"
