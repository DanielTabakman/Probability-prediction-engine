"""Tests for phone-friendly operator status copy."""

from __future__ import annotations

from scripts.ppe_phone_status import format_phone_status, phone_status_title, verdict_headline


def test_phone_status_title_healthy():
    assert phone_status_title({"verdict": "RUN_AUTO"}) == "PPE: All good"


def test_phone_status_title_ide_build():
    title = phone_status_title(
        {
            "verdict": "IDE_BUILD",
            "blocker": "Next product slice [MVP1-Slice004] needs IDE BUILD",
        }
    )
    assert "IDE BUILD" in title
    assert "MVP1-Slice004" in title


def test_format_phone_status_readable():
    body = format_phone_status(
        {
            "verdict": "RUN_LOCAL",
            "chapter_name": "MVP1 distribution quant v2",
            "blocker": "IDE product marker present — finish chapter with run_ppe_local",
            "commands": ["ppe_go.cmd → new Agent → Ctrl+V → Enter"],
        },
        stack={"loop_running": True, "watch_running": True, "ntfy_listen_running": True},
        repo=None,
    )
    assert "Running (finish step)" in body
    assert "MVP1 distribution quant v2" in body
    assert "Loop is running" in body
    assert "loop on" in body
    assert "VERDICT=" not in body


def test_verdict_headline():
    assert verdict_headline("IDE_BUILD") == "Needs you - IDE BUILD"
