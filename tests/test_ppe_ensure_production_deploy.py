"""Tests for ensure_production_deploy helpers."""

from __future__ import annotations

import scripts.ensure_production_deploy as deploy


def test_find_run_for_sha_matches_head() -> None:
    runs = [
        {"databaseId": "1", "headSha": "abc", "conclusion": "failure"},
        {"databaseId": "2", "headSha": "def", "conclusion": "success"},
    ]
    match = deploy.find_run_for_sha(runs, "def")
    assert match is not None
    assert match["databaseId"] == "2"


def test_find_run_for_sha_missing() -> None:
    assert deploy.find_run_for_sha([], "abc") is None


def test_check_ship_verify_delegates(monkeypatch) -> None:
    monkeypatch.setattr(deploy, "verify_msos_web_ship", lambda **_: (True, None))
    ok, detail = deploy.check_ship_verify(base_url="https://example.com")
    assert ok is True
    assert detail is None
