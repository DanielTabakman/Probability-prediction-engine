"""Relay/operator hardening — preflight ACTIVE_RUN, layer exempt paths, loop checkout."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_active_run import (
    clear_active_run,
    heal_stale_running_manifest,
    load_active_run,
    write_active_run,
)
from scripts.ppe_manifest import load_manifest, save_manifest
from scripts.ppe_operator_git_sync import _loop_host_transient_branch
from scripts.ppe_operator_loop_pass import EXIT_PASS_HANDLED, run_loop_pass
from scripts.ppe_operator_status import VERDICT_RUN_LOCAL, VERDICT_STALE_STATE, collect_operator_status
from scripts.ppe_preflight import maybe_clear_stale_active_run
from scripts.repo_layer_paths import is_preflight_dirty_exempt


def test_preflight_dirty_exempt_automation_paths() -> None:
    assert is_preflight_dirty_exempt(".cursor/IDE_BUILD_TRIGGER.json")
    assert is_preflight_dirty_exempt("artifacts/orchestrator/OPERATOR_STATUS.md")
    assert not is_preflight_dirty_exempt("scripts/ppe_notify_push.py")


def test_clear_stale_active_run_when_manifest_ready(tmp_path: Path) -> None:
    orch = tmp_path / "artifacts" / "orchestrator"
    orch.mkdir(parents=True)
    active = orch / "ACTIVE_RUN.json"
    active.write_text(json.dumps({"slice_id": "Old-Slice"}), encoding="utf-8")
    manifest = {"status": "READY", "phasePlanPath": "docs/SOP/PHASE_PLANS/x.json"}
    reason = maybe_clear_stale_active_run(tmp_path, manifest)
    assert reason is not None
    assert not active.is_file()


def test_loop_host_transient_branch_prefixes() -> None:
    assert _loop_host_transient_branch("charter/foo", "main")
    assert _loop_host_transient_branch("build/auto/x", "main")
    assert not _loop_host_transient_branch("main", "main")
    assert not _loop_host_transient_branch("feature/user-work", "main")


def test_audit_git_dirty_preflight_skips_exempt_paths(tmp_path: Path) -> None:
    from scripts.repo_layer_paths import LayerScope, audit_git_dirty_preflight

    trigger = tmp_path / ".cursor" / "IDE_BUILD_TRIGGER.json"
    trigger.parent.mkdir(parents=True)
    trigger.write_text("{}", encoding="utf-8")
    script = tmp_path / "scripts" / "ppe_notify_push.py"
    script.parent.mkdir(parents=True)
    script.write_text("# dirty\n", encoding="utf-8")

    scope = LayerScope(
        layer="ppe-core",
        layer_preset="PPE_CORE",
        allowed_paths=("src/engine/",),
        forbidden_paths=(),
        touch_set=(),
    )
    with patch("scripts.repo_layer_paths.git_dirty_paths") as mock_dirty:
        mock_dirty.return_value = [
            ".cursor/IDE_BUILD_TRIGGER.json",
            "scripts/ppe_notify_push.py",
        ]
        violations = audit_git_dirty_preflight(tmp_path, scope)
    assert len(violations) == 1
    assert "ppe_notify_push" in violations[0]


def test_local_relay_writes_and_clears_active_run(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "docs" / "SOP"
    manifest_dir.mkdir(parents=True)
    plan_dir = tmp_path / "docs" / "SOP" / "PHASE_PLANS"
    plan_dir.mkdir(parents=True)
    plan_path = plan_dir / "test_relay.json"
    plan_path.write_text(
        json.dumps(
            {
                "name": "test",
                "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                "slices": [
                    {
                        "sliceId": "Test-Closeout",
                        "closeout": {"chapterId": "test"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    save_manifest(
        tmp_path,
        {
            "phasePlanPath": "docs/SOP/PHASE_PLANS/test_relay.json",
            "status": "READY",
        },
    )
    (tmp_path / "docs" / "SOP" / "SPRINT_TEST.md").write_text("# test\n", encoding="utf-8")

    write_active_run(tmp_path, kind="phase", plan_path="docs/SOP/PHASE_PLANS/test_relay.json")
    assert load_active_run(tmp_path) is not None
    clear_active_run(tmp_path)
    assert load_active_run(tmp_path) is None


def test_heal_stale_running_manifest_without_active_run(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "docs" / "SOP"
    manifest_dir.mkdir(parents=True)
    save_manifest(
        tmp_path,
        {
            "phasePlanPath": "docs/SOP/PHASE_PLANS/x.json",
            "status": "RUNNING",
        },
    )
    assert heal_stale_running_manifest(tmp_path) is True
    assert load_manifest(tmp_path)["status"] == "READY"


def test_collect_operator_status_heals_stale_running(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "docs" / "SOP"
    manifest_dir.mkdir(parents=True)
    plan_dir = tmp_path / "docs" / "SOP" / "PHASE_PLANS"
    plan_dir.mkdir(parents=True)
    (plan_dir / "x.json").write_text(
        json.dumps(
            {
                "name": "x",
                "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                "slices": [{"sliceId": "X-Closeout", "closeout": {"chapterId": "x"}}],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP" / "SPRINT_TEST.md").write_text("# x\n", encoding="utf-8")
    save_manifest(
        tmp_path,
        {
            "phasePlanPath": "docs/SOP/PHASE_PLANS/x.json",
            "status": "RUNNING",
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "selectionRecord": "",
        },
    )
    (tmp_path / "docs" / "SOP" / "PHASE_QUEUE.json").write_text(
        json.dumps({"items": []}),
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text(
        json.dumps({"items": []}),
        encoding="utf-8",
    )

    with patch("scripts.ppe_operator_status.evaluate_continuous_guards") as mock_guard:
        from scripts.ppe_operator_guards import GuardResult

        mock_guard.return_value = GuardResult(exit_code=0, plan_path="docs/SOP/PHASE_PLANS/x.json")
        status = collect_operator_status(tmp_path)

    assert status["verdict"] != VERDICT_STALE_STATE
    assert load_manifest(tmp_path)["status"] == "READY"


def test_loop_pass_run_local_starts_finish(tmp_path: Path, monkeypatch) -> None:
    manifest_dir = tmp_path / "docs" / "SOP"
    manifest_dir.mkdir(parents=True)
    save_manifest(
        tmp_path,
        {
            "phasePlanPath": "docs/SOP/PHASE_PLANS/x.json",
            "status": "READY",
        },
    )

    def fake_collect(_repo: Path) -> dict:
        return {"verdict": VERDICT_RUN_LOCAL, "exit_code": 0}

    def fake_run_local(_repo: Path) -> dict:
        return {"started": True, "mode": "run_local"}

    monkeypatch.setattr("scripts.ppe_operator_loop_pass.collect_operator_status", fake_collect)
    monkeypatch.setattr("scripts.ppe_autobuilder.action_run_local", fake_run_local)

    assert run_loop_pass(tmp_path) == EXIT_PASS_HANDLED
