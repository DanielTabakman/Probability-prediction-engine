"""Tests for gh auth expiry parsing."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_gh_auth_expiry import assess_gh_auth_expiry


def test_gh_auth_ok() -> None:
    proc = type(
        "P",
        (),
        {"returncode": 0, "stdout": "github.com\n  ✓ Logged in\n", "stderr": ""},
    )()
    with patch("subprocess.run", return_value=proc):
        out = assess_gh_auth_expiry()
    assert out["ok"] is True


def test_gh_auth_needs_reauth() -> None:
    proc = type(
        "P",
        (),
        {"returncode": 1, "stdout": "", "stderr": "not logged in to github.com"},
    )()
    with patch("subprocess.run", return_value=proc):
        out = assess_gh_auth_expiry()
    assert out["needs_reauth"] is True
