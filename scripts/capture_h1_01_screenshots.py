from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


APP_URL = "http://localhost:8501"
APP_URL_QA_ORANGE_OFF = "http://localhost:8501/?qa_orange_unavailable=1"


def _wait_for_anchor_heading(page, timeout_ms: int = 120_000) -> str:
    """
    Returns "available" or "unavailable" once one of the truth-state headings appears.
    """
    available_txt = "Market-implied pricing distribution (risk-neutral)"
    unavailable_txt = "Reference distribution (market-implied unavailable)"
    start = time.time()
    while (time.time() - start) * 1000 < timeout_ms:
        # Prefer the actual on-screen chart heading (markdown renders as h3).
        if page.locator("h3").filter(has_text=unavailable_txt).count() > 0:
            return "unavailable"
        if page.locator("h3").filter(has_text=available_txt).count() > 0:
            return "available"
        time.sleep(0.25)
    raise TimeoutError("Timed out waiting for anchor truth-state heading.")


def _open_expiry_dropdown(page) -> None:
    # Streamlit uses BaseWeb select. Prefer the select associated with the "Expiry" label.
    # In Streamlit, the label is typically a sibling within the same block container.
    block = page.locator('div:has-text("Expiry")').first
    sel = block.locator('div[data-baseweb="select"]').first
    sel.scroll_into_view_if_needed()
    sel.click()


def _select_expiry_by_index(page, idx: int) -> None:
    # Options render as role=option when the dropdown is open.
    opts = page.locator('div[role="option"]')
    # Wait briefly for options to mount.
    start = time.time()
    n = opts.count()
    while n == 0 and (time.time() - start) < 5.0:
        time.sleep(0.1)
        n = opts.count()
    if idx >= n:
        raise IndexError(f"expiry option index {idx} out of range (n={n})")
    opts.nth(idx).click()


def main() -> int:
    # Output path uses neutral naming; avoid legacy internal labels acting as steering.
    out_dir = Path("artifacts") / "first_screen_anchor"
    out_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(APP_URL, wait_until="domcontentloaded")

        # Give Streamlit time to mount and fetch enough to render the first-screen anchor state.
        # We specifically wait for the expiry selector to appear (implied lab mounted),
        # then for the anchor truth-state heading.
        page.get_by_text("Expiry", exact=True).wait_for(timeout=180_000)
        state = _wait_for_anchor_heading(page, timeout_ms=180_000)
        # Snapshot line is part of the first-screen contract when the chart mounts.
        page.get_by_text("Market snapshot (UTC):").wait_for(timeout=180_000)
        page.wait_for_timeout(750)
        page.screenshot(path=str(out_dir / f"first_screen_orange_{state}.png"), full_page=False)

        # Deterministic "orange unavailable" capture for anchor-state evidence.
        page.goto(APP_URL_QA_ORANGE_OFF, wait_until="domcontentloaded")
        state2 = _wait_for_anchor_heading(page)
        page.wait_for_timeout(750)
        # Always write the QA capture to the unavailable filename for closeout evidence.
        page.screenshot(path=str(out_dir / "first_screen_orange_unavailable.png"), full_page=False)

        browser.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

