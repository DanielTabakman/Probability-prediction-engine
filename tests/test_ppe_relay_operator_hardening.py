"""Relay/operator hardening — preflight ACTIVE_RUN, layer exempt paths, loop checkout."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_operator_git_sync import _loop_host_transient_branch
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
