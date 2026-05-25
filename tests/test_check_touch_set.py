"""Tests for scripts/check_touch_set.py."""

from __future__ import annotations

from scripts.check_touch_set import check_touch_set


def test_path_allowed_by_prefix():
    ok, errors = check_touch_set(
        ("src/viz/app_panels.py", "tests/test_trust_strip.py"),
        ("src/viz/app_panels.py", "tests/"),
    )
    assert ok
    assert errors == []


def test_path_outside_touch_set_fails():
    ok, errors = check_touch_set(
        ("src/viz/app.py",),
        ("src/viz/app_panels.py",),
    )
    assert not ok
    assert any("outside touch set" in e for e in errors)


def test_forbidden_prefix_fails():
    ok, errors = check_touch_set(
        ("src/viz/app.py",),
        ("src/viz/",),
        forbidden_prefixes=("src/viz/app.py",),
    )
    assert not ok
    assert any("forbidden" in e for e in errors)
