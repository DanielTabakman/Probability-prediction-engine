"""Tests for notify setup and mirror SSH cache hydration."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_notify_setup import init_notify_config
from scripts.ppe_operator_vm_mirror_refresh import hydrate_vm_mirror_from_ssh_cache


def test_init_notify_config_creates_local_file(tmp_path) -> None:
    example = tmp_path / "ppe_operator_notify.local.cmd.example"
    example.write_text(
        'set "PPE_NTFY_TOPIC=ppe-your-secret-topic-here"\n'
        'set "PPE_NTFY_CMD_SECRET=your-long-random-secret-here"\n',
        encoding="utf-8",
    )
    out = init_notify_config(tmp_path)
    assert out.get("ok") is True
    dest = tmp_path / "ppe_operator_notify.local.cmd"
    assert dest.is_file()
    text = dest.read_text(encoding="utf-8")
    assert "ppe-your-secret-topic-here" not in text
    assert "PPE_NTFY_TOPIC=ppe-" in text


def test_hydrate_vm_mirror_from_ssh_cache(tmp_path) -> None:
    cache_dir = tmp_path / "artifacts/orchestrator"
    cache_dir.mkdir(parents=True)
    cache = {
        "as_of": "2026-07-01T00:00:00Z",
        "ok": True,
        "stdout": "PHASE=FINISH_IN_FLIGHT VERDICT=RUN_LOCAL slice=Test-Slice001",
        "parsed": {"phase": "FINISH_IN_FLIGHT", "verdict": "RUN_LOCAL", "slice": "Test-Slice001"},
    }
    (cache_dir / "VM_STATUS_CACHE.json").write_text(json.dumps(cache), encoding="utf-8")
    mirror = tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json"
    mirror.parent.mkdir(parents=True)
    mirror.write_text(json.dumps({"phase": None}) + "\n", encoding="utf-8")

    with patch("scripts.ppe_operator_vm_ssh.cache_is_fresh", return_value=True):
        out = hydrate_vm_mirror_from_ssh_cache(tmp_path)
    assert out.get("ok") is True
    data = json.loads(mirror.read_text(encoding="utf-8"))
    assert data["phase"] == "FINISH_IN_FLIGHT"
    assert data["source"] == "ssh_cache"
