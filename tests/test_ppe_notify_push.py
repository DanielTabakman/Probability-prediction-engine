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


def test_send_ntfy_posts_to_topic(monkeypatch):
    monkeypatch.setenv("PPE_NTFY_TOPIC", "ppe-test-topic")
    monkeypatch.setenv("PPE_NOTIFY", "1")
    monkeypatch.setenv("PPE_NTFY_SERVER", "https://ntfy.example")

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


def test_send_from_payload(tmp_path: Path):
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
