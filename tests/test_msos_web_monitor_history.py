"""MSOS monitor & history live v1 — product slice witness."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_monitor_history_feed_lib_exists() -> None:
    lib = (MSOS_WEB / "src" / "lib" / "monitorHistoryFeed.ts").read_text(encoding="utf-8")
    assert "loadMonitorFeed" in lib
    assert "loadHistoryFeed" in lib
    assert "buildCalibrationStrip" in lib
    assert "buildReviewEvents" in lib
    assert "loadCommandCenterSummary" in lib
    assert "loadWorkflowSummary" in lib or "getCurrentThesis" in lib
    assert "Executed" not in lib or "live routing" in lib


def test_monitor_history_api_routes_require_identity() -> None:
    monitor_route = (MSOS_WEB / "src" / "app" / "api" / "monitor" / "feed" / "route.ts").read_text(
        encoding="utf-8"
    )
    history_route = (MSOS_WEB / "src" / "app" / "api" / "history" / "feed" / "route.ts").read_text(
        encoding="utf-8"
    )
    for route in (monitor_route, history_route):
        assert "requireProtectedIdentity" in route
        assert "identity.ok" in route


def test_monitor_page_uses_live_feed() -> None:
    page = (MSOS_WEB / "src" / "app" / "monitor" / "page.tsx").read_text(encoding="utf-8")
    content = (MSOS_WEB / "src" / "components" / "MonitorContent.tsx").read_text(encoding="utf-8")
    assert "loadMonitorFeed" in page
    assert "feed={feed}" in page
    assert "monitoringFixtures" not in content
    assert "feed.watchPanels" in content
    assert "no live order transmitted" in content


def test_history_page_uses_live_feed() -> None:
    page = (MSOS_WEB / "src" / "app" / "history" / "page.tsx").read_text(encoding="utf-8")
    content = (MSOS_WEB / "src" / "components" / "HistoryContent.tsx").read_text(encoding="utf-8")
    assert "loadHistoryFeed" in page
    assert "feed={feed}" in page
    assert "historyFixtures" not in content
    assert "feed.entries" in content
    assert "Executed" in content
    assert "no live positions connected" in content


def test_command_center_calibration_strip_from_live_summary() -> None:
    content = (MSOS_WEB / "src" / "components" / "CommandCenterContent.tsx").read_text(encoding="utf-8")
    assert "buildCalibrationStrip" in content
    assert "buildReviewEvents" in content
    assert "calibrationStrip.title" in content
    assert "reviewEvents.map" in content
    assert "commandCenterFixtures" not in content or "headlines" in content
