"""Tests that VM runtime state never creates Git publications."""

from __future__ import annotations

from scripts.ppe_vm_phase_mirror import (
    IN_FLIGHT_PHASES,
    MIRROR_HEARTBEAT_PUBLISH_SECONDS,
    _heartbeat_publish_due,
    maybe_commit_publish_vm_mirror,
)


def test_heartbeat_never_requests_git_publication_after_budget() -> None:
    payload = {"phase": "BUILD_IN_FLIGHT", "as_of": "2026-07-11T19:43:23Z"}
    prior = {
        "fingerprint": "BUILD_IN_FLIGHT|IDE_BUILD|ch|",
        "last_publish_at": "2020-01-01T00:00:00Z",
        "last_publish_ok": True,
    }
    assert _heartbeat_publish_due(payload, prior, fingerprint=prior["fingerprint"]) is False


def test_failed_legacy_publish_does_not_trigger_retry() -> None:
    payload = {"phase": "FINISH_IN_FLIGHT", "as_of": "2026-07-11T19:43:23Z"}
    prior = {
        "fingerprint": "FINISH_IN_FLIGHT|RUN_LOCAL|ch|",
        "last_publish_at": "2026-07-11T19:43:23Z",
        "last_publish_ok": False,
    }
    assert _heartbeat_publish_due(payload, prior, fingerprint=prior["fingerprint"]) is False


def test_maybe_commit_publish_is_permanent_noop(tmp_path) -> None:
    result = maybe_commit_publish_vm_mirror(
        tmp_path,
        {
            "phase": "BUILD_IN_FLIGHT",
            "verdict": "IDE_BUILD",
            "chapter_name": "ch",
            "as_of": "2026-07-11T19:43:23Z",
        },
    )
    assert result == {"skipped": True, "reason": "runtime_state_not_publishable"}
    assert not (tmp_path / "artifacts/control_plane/VM_MIRROR_PUBLISH_STATE.json").exists()


def test_in_flight_phases_remain_runtime_health_states() -> None:
    assert "BUILD_IN_FLIGHT" in IN_FLIGHT_PHASES
    assert "FINISH_IN_FLIGHT" in IN_FLIGHT_PHASES
    assert MIRROR_HEARTBEAT_PUBLISH_SECONDS >= 300
