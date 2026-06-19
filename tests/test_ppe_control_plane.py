"""Tests for unified control plane reconcile and request routing."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_control_plane import (
    CONTROL_PLANE_STATUS_REL,
    ACTION_ALREADY_QUEUED,
    ACTION_NOW,
    ACTION_QUEUE,
    ACTION_WAIT,
    collect_alignment_findings,
    reconcile_control_plane,
    route_build_request,
    write_control_plane_status,
)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    sop = repo / "docs" / "SOP"
    plans = sop / "PHASE_PLANS"
    plans.mkdir(parents=True)
    orch = repo / "artifacts" / "orchestrator"
    orch.mkdir(parents=True)

    active_plan = "docs/SOP/PHASE_PLANS/msos_e2e_product_witness_v1_relay.json"
    blocked_plan = "docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json"

    plan = {
        "name": "E2E witness",
        "slices": [{"sliceId": "MSOS-E2EWitV1-Control-Slice001", "closeout": {}}],
    }
    _write_json(plans / "msos_e2e_product_witness_v1_relay.json", plan)
    _write_json(plans / "msos_billing_stripe_v1_relay.json", {"name": "Stripe", "slices": [{"sliceId": "X", "closeout": {}}]})

    _write_json(
        sop / "ACTIVE_PHASE_MANIFEST.json",
        {
            "phasePlanPath": active_plan,
            "sprintSpecPath": "docs/SOP/SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md",
            "selectionRecord": "docs/SOP/POST_MSOS_E2E_PRODUCT_WITNESS_V1_SELECTION.md",
            "status": "READY",
        },
    )
    (sop / "SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md").write_text("# sprint\n", encoding="utf-8")
    (sop / "POST_MSOS_E2E_PRODUCT_WITNESS_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")

    _write_json(
        sop / "PHASE_QUEUE.json",
        {
            "version": 1,
            "items": [
                {"planPath": active_plan, "status": "READY", "reason": "active"},
                {"planPath": blocked_plan, "status": "PLANNED", "reason": "after e2e"},
            ],
        },
    )
    _write_json(
        sop / "PHASE_CHAPTER_BACKLOG.json",
        {
            "version": 1,
            "items": [
                {
                    "chapterId": "msos_e2e_product_witness_v1",
                    "status": "chartered",
                    "planPath": active_plan,
                    "priority": "medium",
                },
                {
                    "chapterId": "msos_billing_stripe_v1",
                    "status": "blocked",
                    "planPath": blocked_plan,
                    "priority": "medium",
                },
            ],
        },
    )
    (sop / "PHASE_SELECTION_ROADMAP.json").write_text('{"version":1,"items":[]}\n', encoding="utf-8")
    return repo


def _mock_runtime(verdict: str = "RUN_AUTO", chapter: str = "E2E witness") -> dict:
    return {
        "verdict": verdict,
        "phase": "HEALTHY_IDLE",
        "recommended_action": "status",
        "operator": {
            "chapter_name": chapter,
            "manifest_status": "READY",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/msos_e2e_product_witness_v1_relay.json",
        },
        "commands": {},
    }


def test_route_active_chapter_now(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    with patch("scripts.ppe_autobuilder.collect_autobuilder_status", return_value=_mock_runtime()):
        route = route_build_request(
            repo,
            chapter_id="msos_e2e_product_witness_v1",
            reason="finish witness slice",
        )
    assert route["action"] == ACTION_NOW


def test_route_different_chapter_queues(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    with patch("scripts.ppe_autobuilder.collect_autobuilder_status", return_value=_mock_runtime()):
        route = route_build_request(
            repo,
            chapter_id="msos_billing_stripe_v1",
            reason="start stripe",
            apply=True,
        )
    assert route["action"] == ACTION_QUEUE
    backlog = json.loads((repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json").read_text(encoding="utf-8"))
    stripe = next(i for i in backlog["items"] if i["chapterId"] == "msos_billing_stripe_v1")
    assert "start stripe" in stripe["reason"]


def test_route_running_pipeline_wait(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    manifest = json.loads((repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["status"] = "RUNNING"
    _write_json(repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json", manifest)

    with patch("scripts.ppe_autobuilder.collect_autobuilder_status", return_value=_mock_runtime()):
        route = route_build_request(
            repo,
            chapter_id="msos_billing_stripe_v1",
            reason="stripe now",
            apply=True,
        )
    assert route["action"] == ACTION_QUEUE
    assert "queued behind" in route["reason"].lower() or route["action"] == ACTION_QUEUE


def test_route_already_chartered(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    manifest = json.loads((repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["phasePlanPath"] = "docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json"
    _write_json(repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json", manifest)
    with patch("scripts.ppe_autobuilder.collect_autobuilder_status", return_value=_mock_runtime()):
        route = route_build_request(
            repo,
            chapter_id="msos_e2e_product_witness_v1",
            reason="duplicate",
        )
    assert route["action"] == ACTION_ALREADY_QUEUED


def test_alignment_manifest_matches_queue(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    findings = collect_alignment_findings(repo)
    assert not any(f["code"] == "manifest_queue_mismatch" for f in findings)


def test_alignment_detects_mismatch(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    manifest = json.loads((repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json").read_text(encoding="utf-8"))
    manifest["phasePlanPath"] = "docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json"
    _write_json(repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json", manifest)
    findings = collect_alignment_findings(repo)
    assert any(f["code"] == "manifest_queue_mismatch" for f in findings)


def test_reconcile_writes_control_plane_status(tmp_path: Path) -> None:
    repo = _minimal_repo(tmp_path)
    with patch("scripts.ppe_autobuilder.collect_autobuilder_status", return_value=_mock_runtime()):
        with patch("scripts.ppe_operator_status.collect_operator_status", return_value={"verdict": "RUN_AUTO", "as_of": "t"}):
            snapshot = reconcile_control_plane(repo, apply=False)
    path = write_control_plane_status(repo, snapshot)
    assert path.name == Path(CONTROL_PLANE_STATUS_REL).name
    assert snapshot["verdict"] == "RUN_AUTO"
    assert snapshot["source_of_truth"]["human_read"] == CONTROL_PLANE_STATUS_REL
