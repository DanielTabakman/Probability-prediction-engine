"""Tests for autobuilder fast brief and desktop VM status helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scripts.ppe_autobuilder import ACTION_ENSURE, PHASE_STACK_DOWN, try_fast_stack_brief
from scripts.ppe_desktop_vm_status import _needs_ensure


def test_try_fast_stack_brief_when_loop_down(tmp_path: Path) -> None:
    with patch(
        "scripts.ppe_desktop_operator_stack.stack_status",
        return_value={"loop_running": False, "watch_running": False},
    ):
        out = try_fast_stack_brief(tmp_path)
    assert out is not None
    assert out["phase"] == PHASE_STACK_DOWN
    assert out["recommended_action"] == ACTION_ENSURE
    assert out.get("fast_path") is True


def test_try_fast_stack_brief_skips_when_stack_up(tmp_path: Path) -> None:
    with patch(
        "scripts.ppe_desktop_operator_stack.stack_status",
        return_value={"loop_running": True, "watch_running": True},
    ):
        out = try_fast_stack_brief(tmp_path)
    assert out is None


def test_needs_ensure_detects_stack_down() -> None:
    assert _needs_ensure("PHASE=STACK_DOWN VERDICT=RUN_AUTO stack_loop=False stack_watch=False")
    assert not _needs_ensure("PHASE=HEALTHY_IDLE VERDICT=RUN_AUTO stack_loop=True stack_watch=True")
