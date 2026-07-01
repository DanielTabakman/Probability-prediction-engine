"""Tests for ppe_operator_vm_ssh and VM phase trust resolution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.ppe_operator_vm_ssh import (
    cache_is_fresh,
    parse_autobuilder_brief,
    resolve_vm_trust,
    ssh_vm,
    write_vm_status_cache,
)
from scripts.ppe_vm_phase_mirror import load_vm_phase_mirror, write_vm_phase_mirror


def test_parse_autobuilder_brief() -> None:
    raw = "PHASE=FINISH_IN_FLIGHT VERDICT=RUN_LOCAL slice=- stack_loop=True stack_watch=True next=status"
    parsed = parse_autobuilder_brief(raw)
    assert parsed["phase"] == "FINISH_IN_FLIGHT"
    assert parsed["verdict"] == "RUN_LOCAL"
    assert parsed["slice"] == "-"


def test_resolve_vm_trust_wait_in_flight() -> None:
    trust = resolve_vm_trust(
        local_verdict="RUN_LOCAL",
        vm_brief=None,
        vm_mirror={"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL"},
    )
    assert trust["wait_for_vm"] is True
    assert trust["recommended_action"] == "wait"
    assert "do not spawn" in trust["agent_note"].lower()


def test_resolve_vm_trust_prefers_live_ssh_over_stale_mirror() -> None:
    trust = resolve_vm_trust(
        local_verdict="RUN_LOCAL",
        vm_brief={
            "ok": True,
            "source": "ssh",
            "parsed": {"phase": "BUILD_IN_FLIGHT", "verdict": "IDE_BUILD"},
        },
        vm_mirror={"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL"},
        mirror_stale=True,
    )
    assert trust["wait_for_vm"] is True
    assert trust["vm_phase"] == "BUILD_IN_FLIGHT"
    assert trust["vm_verdict"] == "IDE_BUILD"
    assert trust["source"] == "ssh"


def test_resolve_vm_trust_desktop_continue() -> None:
    trust = resolve_vm_trust(
        local_verdict="RUN_LOCAL",
        vm_brief={"parsed": {"phase": "RUN_LOCAL_PENDING", "verdict": "RUN_LOCAL"}},
        vm_mirror=None,
    )
    assert trust["wait_for_vm"] is False
    assert trust["recommended_action"] == "desktop_continue"


def test_cache_is_fresh() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    assert cache_is_fresh({"as_of": now}) is True
    assert cache_is_fresh({"as_of": "2020-01-01T00:00:00Z"}) is False


def test_ssh_vm_uses_timeout_and_opts(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        class R:
            returncode = 0
            stdout = "PHASE=HEALTHY_IDLE VERDICT=RUN_AUTO slice=-"
            stderr = ""

        return R()

    monkeypatch.setattr("scripts.ppe_operator_vm_ssh.subprocess.run", fake_run)
    out = ssh_vm("echo test", timeout=30)
    assert out["ok"] is True
    assert "-o" in calls[0]
    assert "BatchMode=yes" in calls[0]
    assert calls[0][-1] == "echo test"


def test_write_vm_phase_mirror_loop_host_only(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    (tmp_path / "ppe_operator_loop_host.local.cmd").write_text("@echo off\n", encoding="utf-8")
    status = {
        "as_of": "2026-07-01T00:00:00Z",
        "phase": "FINISH_IN_FLIGHT",
        "verdict": "RUN_LOCAL",
        "operator": {"chapter_name": "test chapter", "phase_plan_path": "docs/SOP/PHASE_PLANS/x.json"},
        "recommended_action": "status",
    }
    with patch("scripts.ppe_loop_host_guard.loop_host_start_allowed", return_value=(True, "ok")):
        path = write_vm_phase_mirror(tmp_path, status)
    assert path is not None
    assert path.is_file()
    loaded = load_vm_phase_mirror(tmp_path)
    assert loaded is not None
    assert loaded["phase"] == "FINISH_IN_FLIGHT"


def test_write_vm_status_cache_roundtrip(tmp_path) -> None:
    payload = {"as_of": "2026-07-01T00:00:00Z", "ok": True, "parsed": {"phase": "X"}}
    write_vm_status_cache(tmp_path, payload)
    cache_path = tmp_path / "artifacts/orchestrator/VM_STATUS_CACHE.json"
    assert cache_path.is_file()
    loaded = json.loads(cache_path.read_text(encoding="utf-8"))
    assert loaded["parsed"]["phase"] == "X"
