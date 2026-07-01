"""Tests for operator maintenance helpers (not relay)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch

from scripts.check_vm_host_health import host_health_is_fresh
from scripts.ppe_gh_auth_expiry import format_gh_expiry_line
from scripts.ppe_network_watchdog import run_network_watchdog
from scripts.ppe_worktree_janitor import assess_worktrees, remove_worktree


def test_host_health_is_fresh() -> None:
    fresh = {
        "as_of": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "alerts": [],
    }
    assert host_health_is_fresh(fresh) is True
    stale = {
        "as_of": "2020-01-01T00:00:00Z",
        "alerts": ["vm_disk_warn: 1GB free"],
    }
    assert host_health_is_fresh(stale) is False


def test_blind_spots_ignore_stale_host_health(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    stale_path = tmp_path / "artifacts/control_plane/VM_HOST_HEALTH.json"
    stale_path.parent.mkdir(parents=True)
    stale_path.write_text(
        json.dumps(
            {
                "as_of": "2020-01-01T00:00:00Z",
                "alerts": ["vm_ssh_unreachable: bogus"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with patch("scripts.ppe_operator_blind_spots._gh_auth_ok", return_value=(True, "")):
        with patch("scripts.ppe_operator_blind_spots._open_vm_mirror_prs", return_value=[]):
            from scripts.ppe_operator_blind_spots import assess_operator_blind_spots

            blind = assess_operator_blind_spots(tmp_path, {"verdict": "RUN_AUTO"})
    ids = {i["id"] for i in blind.get("issues") or []}
    assert "vm_host_resources" not in ids
    assert blind.get("health", {}).get("host_health_stale") is True


def test_network_watchdog_notifies_after_threshold(tmp_path, monkeypatch) -> None:
    state = tmp_path / "artifacts/control_plane/NETWORK_WATCHDOG_STATE.json"
    state.parent.mkdir(parents=True)
    state.write_text(json.dumps({"consecutive_failures": 2, "alert_sent": False}) + "\n", encoding="utf-8")
    with patch(
        "scripts.ppe_network_watchdog.probe_vm_ssh",
        return_value={"ok": False, "host": "ppe-vm", "detail": "timeout"},
    ):
        with patch("scripts.ppe_notify_push.send_ntfy_to_topic", return_value=True) as mock_ntfy:
            report = run_network_watchdog(tmp_path, fail_threshold=3, notify=True)
    assert report["consecutive_failures"] == 3
    assert report["notified"] is True
    mock_ntfy.assert_called_once()


def test_gh_auth_expiry_warn_line() -> None:
    line = format_gh_expiry_line({"ok": True, "warn_expiry": True, "days_left": 3})
    assert line and "3d" in line


def test_assess_worktrees(tmp_path, monkeypatch) -> None:
    def fake_git(repo, *args):
        if args[:2] == ("worktree", "list"):
            main = repo.resolve()
            out = f"worktree {main}\nHEAD abc\nbranch refs/heads/main\n\n"
            out += f"worktree {main / '_worktrees' / 'old'}\nHEAD def\nbranch refs/heads/product/x\n\n"
            return type("P", (), {"returncode": 0, "stdout": out, "stderr": ""})()
        if args[:2] == ("rev-parse", "--show-toplevel"):
            return type("P", (), {"returncode": 0, "stdout": str(repo.resolve()), "stderr": ""})()
        return type("P", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr("scripts.ppe_worktree_janitor._git", fake_git)
    payload = assess_worktrees(tmp_path)
    assert payload["ok"] is True
    assert payload["safe_count"] >= 1


def test_remove_worktree_blocks_outside_prefix(tmp_path) -> None:
    result = remove_worktree(tmp_path, "src/foo")
    assert result["ok"] is False
