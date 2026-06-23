"""Tests for ensure_production_deploy helpers."""

from __future__ import annotations

from scripts.ensure_production_deploy import find_run_for_sha


def test_find_run_for_sha_matches_head() -> None:
    runs = [
        {"databaseId": "1", "headSha": "abc", "conclusion": "failure"},
        {"databaseId": "2", "headSha": "def", "conclusion": "success"},
    ]
    match = find_run_for_sha(runs, "def")
    assert match is not None
    assert match["databaseId"] == "2"


def test_find_run_for_sha_missing() -> None:
    assert find_run_for_sha([], "abc") is None
