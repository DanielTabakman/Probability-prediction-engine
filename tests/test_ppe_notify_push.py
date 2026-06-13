"""Tests for mobile ntfy push helper."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import scripts.ppe_notify_push as push


def test_send_ntfy_skips_when_topic_unset(monkeypatch):
    monkeypatch.delenv("PPE_NTFY_TOPIC", raising=False)
    monkeypatch.setenv("PPE_NOTIFY", "1")
    assert push.send_ntfy("t", "b") is False


def test_send_ntfy_skips_when_notify_disabled(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "secret-topic")
    monkeypatch.setenv("PPE_NOTIFY", "0")
    assert push.send_ntfy("t", "b") is False


def test_send_ntfy_respects_daily_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_DAILY_CAP", "1")
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    push.record_ntfy_send("first", tags=["ppe"], priority="default", repo=tmp_path)

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        assert push.send_ntfy("second", "body", tags=["ppe"]) is False
    assert urlopen.call_count == 1
    assert "budget" in urlopen.call_args[0][0].headers["Title"].lower()


def test_send_ntfy_urgent_bypasses_daily_cap(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_DAILY_CAP", "1")
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    push.record_ntfy_send("first", tags=["ppe"], priority="default", repo=tmp_path)

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        assert push.send_ntfy("PPE loop stopped", "down", tags=["ppe"], priority="urgent") is True
    urlopen.assert_called_once()


def test_quota_exceeded_updates_status_file(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_DAILY_CAP", "1")
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    push.record_ntfy_send("first", tags=["ppe"], priority="default", repo=tmp_path)

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response):
        assert push.send_ntfy("blocked", "body", tags=["ppe"]) is False

    snap = json.loads((tmp_path / push.QUOTA_STATUS_REL).read_text(encoding="utf-8"))
    assert snap["at_cap"] is True
    assert snap["skipped_last"] == "blocked"


def test_format_quota_brief(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    push.record_ntfy_send("PPE OK - RUN_LOCAL", tags=["ppe", "ok"], priority="low", repo=tmp_path)
    text = push.format_quota_brief(tmp_path)
    assert "1/40" in text
    assert "heartbeat" in text


def test_send_ntfy_posts_to_topic(monkeypatch, tmp_path):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "ppe-test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_SERVER", "https://ntfy.example")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        ok = push.send_ntfy("PPE operator: IDE_BUILD", "blocker text", tags=["ppe"], priority="high")

    assert ok is True
    request = urlopen.call_args[0][0]
    assert request.full_url == "https://ntfy.example/ppe-test-topic"


def test_send_from_payload(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    payload = tmp_path / "notify.json"
    payload.write_text(
        json.dumps({"title": "PPE operator: ERROR", "body": "boom", "verdict": "ERROR"}) + "\n",
        encoding="utf-8",
    )

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", {"PPE_NTFY_TOPIC": "t", "PPE_NOTIFY": "1"}, clear=False):
        with patch("urllib.request.urlopen", return_value=response):
            assert push.send_from_payload(payload) is True


def test_priority_for_verdict():
    assert push._priority_for_verdict("IDE_BUILD") == "high"
    assert push._priority_for_verdict("ERROR") == "urgent"


def test_send_weekly_digest_from_payload(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    payload = tmp_path / "WEEKLY_DIGEST_NOTIFY.json"
    payload.write_text(json.dumps({"week_monday": "2026-06-01", "phone_body": "digest"}) + "\n", encoding="utf-8")

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", {"PPE_NTFY_TOPIC": "t", "PPE_NOTIFY": "1"}, clear=False):
        with patch("urllib.request.urlopen", return_value=response):
            assert push.send_weekly_digest_from_payload(payload) is True


def test_quiet_hours_mute_routine(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_QUIET_HOURS", "1")
    monkeypatch.setenv("PPE_NTFY_QUIET_START", "01:00")
    monkeypatch.setenv("PPE_NTFY_QUIET_END", "08:00")
    with patch("scripts.ppe_notify_push.is_ntfy_quiet_hours", return_value=True):
        assert push.is_routine_notify_muted(title="PPE operator: IDE_BUILD") is True
        assert push.is_routine_notify_muted(title="PPE: still stuck - foo") is False
        assert push.is_routine_notify_muted(tags=["ppe", "cmd"]) is False


def test_quiet_stuck_only_once_per_night(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_QUIET_HOURS", "1")
    with patch("scripts.ppe_notify_push.is_ntfy_quiet_hours", return_value=True):
        assert push.quiet_stuck_allowed(tmp_path) is True
        push.mark_quiet_stuck_sent(tmp_path)
        assert push.quiet_stuck_allowed(tmp_path) is False
    with patch("scripts.ppe_notify_push.is_ntfy_quiet_hours", return_value=False):
        push.reset_quiet_stuck_if_awake(tmp_path)
        with patch("scripts.ppe_notify_push.is_ntfy_quiet_hours", return_value=True):
            assert push.quiet_stuck_allowed(tmp_path) is True


def test_stuck_reminder_not_muted_by_quiet_hours(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    with patch("scripts.ppe_notify_push.is_ntfy_quiet_hours", return_value=True):
        assert push.is_routine_notify_muted(title="PPE: still stuck - IDE BUILD") is False
