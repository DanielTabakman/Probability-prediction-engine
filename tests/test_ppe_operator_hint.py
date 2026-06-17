"""Tests for shared ppe_go operator hint copy."""

from __future__ import annotations

from scripts.ppe_operator_hint import DESKTOP_BUILD_CMD, PPE_GO_CMD, PPE_GO_HINT, append_ppe_go_hint


def test_append_ppe_go_hint_ide_build():
    body = append_ppe_go_hint("PRODUCT_BLOCKED", "IDE_BUILD")
    assert DESKTOP_BUILD_CMD in body or "DO THE THING" in body


def test_append_ppe_go_hint_skips_duplicate():
    text = f"Already: {PPE_GO_HINT}"
    assert append_ppe_go_hint(text, "IDE_BUILD") == text


def test_append_ppe_go_hint_run_auto_unchanged():
    assert append_ppe_go_hint("loop ok", "RUN_AUTO") == "loop ok"
