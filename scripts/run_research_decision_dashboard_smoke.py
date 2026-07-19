"""Smoke witness for the feature-flagged Research Decision Dashboard."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
APP_ENTRY = ROOT / "src" / "viz" / "app.py"
ARTIFACTS_DIR = ROOT / "artifacts" / "research_decision_dashboard_smoke"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.viz.research_decision_dashboard import load_default_research_decision_dashboard


def _pick_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_ready(url: str, timeout_s: float = 90.0) -> None:
    deadline = time.time() + timeout_s
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                return
            last_error = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last_error = f"{type(exc).__name__}: {exc}"
        time.sleep(1.0)
    raise RuntimeError(f"Streamlit did not become ready: {last_error}")


def _run_page_witness(url: str, screenshot_path: Path) -> dict[str, bool]:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1200})
        page.goto(url, wait_until="networkidle", timeout=90000)
        page.get_by_test_id("stMainBlockContainer").get_by_text("Research Review").wait_for(timeout=60000)
        page.get_by_text("Profitability:").wait_for(timeout=60000)
        page.wait_for_timeout(1500)
        page.screenshot(path=str(screenshot_path), full_page=True)
        text = page.locator("body").inner_text(timeout=30000)
        browser.close()
    return {
        "stop_polymarket_branch": "STOP_POLYMARKET_BRANCH" in text,
        "theory_plausible_not_tested": "general theory is not disproven" in text.lower()
        or "PLAUSIBLE_NOT_ECONOMICALLY_TESTED" in text,
        "profitability_not_tested": "Profitability:" in text and "NOT_TESTED" in text,
        "execution_not_authorized": "Execution:" in text and "NOT_AUTHORIZED" in text,
        "seven_frozen_candidates": "Frozen candidates:" in text and "7" in text,
        "zero_eligible_contracts": "eligible contracts:" in text and "0" in text,
    }


def main() -> int:
    dashboard = load_default_research_decision_dashboard()
    structured_checks = {
        "fixture_recommendation": dashboard.recommendation == "STOP_POLYMARKET_BRANCH",
        "fixture_theory_status": dashboard.theory_status == "PLAUSIBLE_NOT_ECONOMICALLY_TESTED",
        "fixture_profitability": dashboard.profitability_status == "NOT_TESTED",
        "fixture_execution": dashboard.execution_status == "NOT_AUTHORIZED",
        "fixture_candidates": len(dashboard.candidates) == 7,
        "fixture_zero_eligible": all(row.canonical_classification != "ELIGIBLE" for row in dashboard.candidates),
    }

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ARTIFACTS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = run_dir / "research_decision_dashboard.png"
    manifest_path = run_dir / "research_decision_dashboard_smoke.json"
    port = _pick_free_port()
    url = f"http://127.0.0.1:{port}/"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(APP_ENTRY),
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    env = os.environ.copy()
    env["PPE_RESEARCH_REVIEW_UI"] = "1"
    env["PPE_RESEARCH_REVIEW_DEFAULT"] = "1"
    env["PPE_ENABLE_SNAPSHOTS"] = "0"
    log_path = run_dir / "streamlit.log"
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=env,
        stdout=log_path.open("w", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        text=True,
    )
    page_checks: dict[str, bool] = {}
    try:
        _wait_ready(url)
        page_checks = _run_page_witness(url, screenshot_path)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)

    manifest = {
        "ok": all(structured_checks.values()) and all(page_checks.values()),
        "url": url,
        "screenshot_path": str(screenshot_path),
        "streamlit_log": str(log_path),
        "structured_checks": structured_checks,
        "page_checks": page_checks,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
