"""MSOS journey crawler — static manifest + optional live witness."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
MSOS_WEB = REPO_ROOT / "apps" / "msos-web"


def test_journey_crawler_module_exports_routes() -> None:
    from scripts.msos_journey_crawler import MSOS_JOURNEY_ROUTES, page_looks_like_404

    paths = {path for path, _ in MSOS_JOURNEY_ROUTES}
    assert "/monitor" in paths
    assert "/history" in paths
    assert page_looks_like_404("<title>404: This page could not be found</title>") is not None
    assert page_looks_like_404("<h1>Monitor</h1>") is None


def test_paper_trade_detail_redirects_when_missing() -> None:
    page = (MSOS_WEB / "src" / "app" / "monitor" / "paper" / "[id]" / "page.tsx").read_text(
        encoding="utf-8"
    )
    assert 'redirect("/monitor")' in page
    assert "notFound()" not in page


def test_delete_uses_hard_monitor_nav_from_detail() -> None:
    actions = (MSOS_WEB / "src" / "components" / "PaperTradeManageActions.tsx").read_text(
        encoding="utf-8"
    )
    nav = (MSOS_WEB / "src" / "lib" / "monitorNav.ts").read_text(encoding="utf-8")
    assert "goToMonitorAfterDelete" in actions
    assert "window.location.assign" in nav
    assert "/monitor/paper/" in nav


def test_not_found_page_offers_monitor_escape() -> None:
    not_found = (MSOS_WEB / "src" / "app" / "not-found.tsx").read_text(encoding="utf-8")
    assert "MSOS_ROUTES.monitor" in not_found
    assert "Command Center" in not_found


@pytest.mark.witness
@pytest.mark.slow
def test_journey_crawler_live_when_msos_base_url_set() -> None:
    base = os.environ.get("MSOS_BASE_URL", "").strip()
    if not base:
        pytest.skip("Set MSOS_BASE_URL to run live journey crawler (e.g. http://localhost:3000)")

    proc = subprocess.run(
        [
            sys.executable,
            "scripts/msos_journey_crawler.py",
            "--base-url",
            base,
            "--flows",
            "routes",
            "missing-paper",
            "delete-paper",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
