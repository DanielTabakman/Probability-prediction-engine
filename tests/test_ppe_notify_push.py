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
    urlopen.assert_not_called()


def test_send_ntfy_dedupes_repeated_title(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_DAILY_CAP", "40")
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    push.record_ntfy_send("PPE OK - RUN_LOCAL", tags=["ppe", "ok"], priority="low", repo=tmp_path)

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        assert push.send_ntfy("PPE OK - RUN_LOCAL", "again", tags=["ppe", "ok"], priority="low") is False
    urlopen.assert_not_called()


def test_send_ntfy_posts_to_topic(monkeypatch, tmp_path):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "ppe-test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_SERVER", "https://ntfy.example")
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=response) as urlopen:
        ok = push.send_ntfy("PPE operator: IDE_BUILD", "blocker text", tags=["ppe"], priority="high")

    assert ok is True
    request = urlopen.call_args[0][0]
    assert request.full_url == "https://ntfy.example/ppe-test-topic"
    assert request.headers["Title"] == "PPE operator: IDE_BUILD"
    assert request.headers["Priority"] == "high"


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
    assert push._priority_for_verdict("SUPPLY_LOW") == "low"


def test_send_weekly_digest_from_payload(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_REPO_ROOT", str(tmp_path))
    monkeypatch.setenv("PPE_NTFY_MIN_INTERVAL_SEC", "0")
    payload = tmp_path / "WEEKLY_DIGEST_NOTIFY.json"
    payload.write_text(
        json.dumps(
            {
                "week_monday": "2026-06-01",
                "phone_title": "This week in PPE - Jun 1-7",
                "phone_body": "What's different for you\n- MSOS now has a public homepage you can share",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    response = MagicMock()
    response.status = 200
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)

    with patch.dict("os.environ", {"PPE_NTFY_TOPIC": "t", "PPE_NOTIFY": "1"}, clear=False):
        with patch("urllib.request.urlopen", return_value=response) as urlopen:
            assert push.send_weekly_digest_from_payload(payload) is True

    request = urlopen.call_args[0][0]
    assert request.headers["Title"] == "This week in PPE - Jun 1-7"
    assert "public homepage" in request.data.decode("utf-8")
