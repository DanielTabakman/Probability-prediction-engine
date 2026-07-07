"""Tests for msos_product_usage_telemetry_witness.py."""

from __future__ import annotations

import json
from unittest import mock

from scripts.msos_product_usage_telemetry_witness import probe_usage_api


def test_probe_usage_api_ok() -> None:
    payload = json.dumps({"ok": True}).encode("utf-8")

    class FakeResp:
        status = 200

        def read(self) -> bytes:
            return payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    with mock.patch("urllib.request.urlopen", return_value=FakeResp()) as urlopen:
        result = probe_usage_api("https://example.com")
    assert result["ok"] is True
    assert result["status"] == 200
    req = urlopen.call_args.args[0]
    assert req.headers["User-agent"].startswith("Mozilla/5.0")
    assert req.headers["Origin"] == "https://example.com"
    assert req.headers["Referer"] == "https://example.com/"


def test_probe_usage_api_http_error() -> None:
    import urllib.error

    err = urllib.error.HTTPError("https://example.com/api/usage/event", 503, "fail", {}, None)
    err.fp = mock.Mock(read=mock.Mock(return_value=b"unavailable"))

    with mock.patch("urllib.request.urlopen", side_effect=err):
        result = probe_usage_api("https://example.com")
    assert result["ok"] is False
    assert result["status"] == 503
