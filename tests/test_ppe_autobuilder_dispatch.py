"""Tests for centralized autobuilder dispatch."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_autobuilder_dispatch import (
    dispatch_build,
    maybe_dispatch_loop,
    should_dispatch_loop,
)


def test_should_dispatch_loop_requires_ide_build():
    assert should_dispatch_loop(__import__("pathlib").Path("."), {"verdict": "RUN_AUTO"}) is False
    assert should_dispatch_loop(__import__("pathlib").Path("."), {"verdict": "IDE_BUILD"}) is True


def test_maybe_dispatch_loop_delegates():
    repo = __import__("pathlib").Path(".")
    status = {"verdict": "IDE_BUILD"}
    with (
        patch("scripts.ppe_autobuilder_dispatch.should_dispatch_loop", return_value=True),
        patch(
            "scripts.ppe_autobuilder_dispatch.dispatch_build",
            return_value={"started": True, "mode": "ide_handoff"},
        ) as dispatch,
    ):
        out = maybe_dispatch_loop(repo, status)
    dispatch.assert_called_once()
    assert out and out.get("started")


def test_dispatch_build_calls_respond():
    repo = __import__("pathlib").Path(".")
    with patch(
        "scripts.ppe_ide_handoff.respond_to_ide_build",
        return_value={"started": True},
    ) as respond:
        dispatch_build(repo, source="test", note="hi", force_handoff=True)
    respond.assert_called_once()
