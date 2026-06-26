"""MSOS journey crawler — route walk + interaction flows that must never land on 404.

Catches soft-navigation races (e.g. delete paper trade → stale detail route) and missing
route regressions before operators hit them.

Usage:
  python scripts/msos_journey_crawler.py --base-url https://marketstructureos.com
  python scripts/msos_journey_crawler.py --base-url http://localhost:3000 --flows routes missing-paper delete-paper

Requires: pip install playwright && python -m playwright install chromium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.msos_playwright_session import prepare_msos_browser_context
from scripts.msos_production_demo_witness import DEFAULT_BASE

DEFAULT_OUT = Path("artifacts/health/msos_journey_crawler")

MSOS_JOURNEY_ROUTES: tuple[tuple[str, str], ...] = (
    ("/", "homepage"),
    ("/strategy-lab", "strategy_lab"),
    ("/strategy-lab/confirm", "thesis_confirm"),
    ("/strategy-lab/expression", "expression_plan"),
    ("/command-center", "command_center"),
    ("/monitor", "monitor"),
    ("/history", "history"),
    ("/learn", "learn"),
)

# Positive content per route key — bundled JS includes not-found.tsx strings on every page,
# so HTML substring checks false-positive. Prefer visible DOM + expected copy.
ROUTE_EXPECTED_CONTENT: dict[str, str] = {
    "homepage": "Turn your market thesis into a trade",
    "strategy_lab": "Strategy Lab",
    "thesis_confirm": "Confirm your view",
    "expression_plan": "Paper trade planner",
    "command_center": "Command Center",
    "monitor": "Watching now",
    "history": "History",
    "learn": "Reflect",
}

MONITOR_EXPECTED = ROUTE_EXPECTED_CONTENT["monitor"]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ensure_playwright() -> None:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium\n"
        ) from exc


def route_expected_content(route_key: str) -> str | None:
    return ROUTE_EXPECTED_CONTENT.get(route_key)


def page_looks_like_404(
    html: str,
    title: str = "",
    *,
    expected_content: str | None = None,
) -> str | None:
    """Static HTML heuristic for unit tests — production crawl uses page_looks_like_404_live."""
    if expected_content and expected_content in html:
        return None
    combined = f"{title}\n{html}"
    if re.search(r"<title[^>]*>\s*404\b", combined, re.I):
        return "document title is 404"
    if title.strip().startswith("404"):
        return f"document title suggests 404: {title!r}"
    return None


def page_looks_like_404_live(page: Any, *, expected_content: str | None = None) -> str | None:
    """Detect a rendered 404 without matching not-found strings bundled in client JS."""
    if expected_content:
        locator = page.get_by_text(expected_content, exact=False).first
        try:
            if locator.is_visible(timeout=2_000):
                return None
        except Exception:
            pass
    try:
        if page.locator("main.not-found-shell").is_visible():
            return "not-found shell is visible"
    except Exception:
        pass
    title = page.title()
    if re.search(r"\b404\b", title):
        return f"document title suggests 404: {title!r}"
    if expected_content:
        return f"expected content missing: {expected_content!r}"
    return None


def crawl_static_routes(page: Any, *, base: str) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for path, key in MSOS_JOURNEY_ROUTES:
        url = f"{base}{path}"
        response = page.goto(url, wait_until="domcontentloaded", timeout=90_000)
        page.wait_for_timeout(300)
        status = response.status if response else 0
        expected = route_expected_content(key)
        not_found_err = page_looks_like_404_live(page, expected_content=expected)
        checks.append(
            {
                "flow": "routes",
                "id": key,
                "url": url,
                "ok": status == 200 and not_found_err is None,
                "status": status,
                "error": not_found_err
                if not_found_err
                else (None if status == 200 else f"HTTP {status}"),
            }
        )
    return checks


def flow_missing_paper_trade(page: Any, *, base: str) -> dict[str, Any]:
    url = f"{base}/monitor/paper/__crawler_missing_trade__"
    response = page.goto(url, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(500)
    final_url = page.url
    status = response.status if response else 0
    not_found_err = page_looks_like_404_live(page, expected_content=MONITOR_EXPECTED)
    still_on_detail = "/monitor/paper/" in final_url
    ok = not still_on_detail and not_found_err is None and status == 200
    error = None
    if still_on_detail:
        error = f"expected redirect off paper detail, got {final_url}"
    elif not_found_err:
        error = not_found_err
    elif status != 200:
        error = f"HTTP {status}"
    return {
        "flow": "missing-paper",
        "id": "missing_paper_trade_redirect",
        "url": url,
        "final_url": final_url,
        "ok": ok,
        "status": status,
        "error": error,
    }


def _seed_paper_trade(context: Any, *, base: str) -> dict[str, Any] | None:
    now = _utc_now()
    thesis = {
        "instrument": "BTC",
        "horizonDays": 30,
        "marketRangePct": 12,
        "thesisRangePct": 8,
        "referenceLabel": "30d realized",
        "trustLabel": "Demo",
        "lifecycle": "confirmed",
        "updatedAt": now,
    }
    expression = {
        "familyId": "range",
        "planHeadline": f"Crawler delete test {uuid4().hex[:8]}",
        "planSummary": "Journey crawler seeded paper trade",
        "legs": [
            {
                "side": "BUY",
                "instrument": "BTC-PERP",
                "strike": "ATM",
                "tenor": "30d",
            }
        ],
        "lifecycle": "simulated",
        "updatedAt": now,
        "paperTradeStatus": "open",
        "savedAt": now,
        "expiryDate": "2026-12-31",
        "instrument": "BTC options",
    }
    thesis_resp = context.request.put(
        f"{base}/api/theses",
        data=json.dumps({"thesis": thesis}),
        headers={"Content-Type": "application/json"},
        timeout=30_000,
    )
    if thesis_resp.status not in (200, 201):
        return None
    trade_resp = context.request.post(
        f"{base}/api/theses/paper-trades",
        data=json.dumps({"expression": expression}),
        headers={"Content-Type": "application/json"},
        timeout=30_000,
    )
    if trade_resp.status not in (200, 201):
        return None
    body = trade_resp.json()
    trade = body.get("expression") if isinstance(body, dict) else None
    if not trade or not isinstance(trade, dict) or not trade.get("id"):
        return None
    return trade


def flow_delete_paper_trade(page: Any, context: Any, *, base: str) -> dict[str, Any]:
    trade = _seed_paper_trade(context, base=base)
    if not trade:
        return {
            "flow": "delete-paper",
            "id": "delete_paper_trade_redirect",
            "url": f"{base}/monitor",
            "ok": False,
            "status": 0,
            "error": "could not seed paper trade via API (thesis + POST paper-trades)",
        }

    trade_id = str(trade["id"])
    title = str(trade.get("planHeadline") or "Paper trade")
    detail_url = f"{base}/monitor/paper/{trade_id}"
    page.goto(detail_url, wait_until="domcontentloaded", timeout=90_000)

    delete_btn = page.get_by_role("button", name=re.compile(r"^Delete$", re.I))
    if delete_btn.count() == 0:
        return {
            "flow": "delete-paper",
            "id": "delete_paper_trade_redirect",
            "url": detail_url,
            "ok": False,
            "status": 0,
            "error": "Delete button not found on paper trade detail",
        }

    delete_btn.first.click()
    page.wait_for_url(re.compile(r"/monitor(\?|$)"), timeout=30_000)
    page.wait_for_timeout(400)

    final_url = page.url
    not_found_err = page_looks_like_404_live(page, expected_content=MONITOR_EXPECTED)
    on_monitor = "/monitor" in final_url and "/monitor/paper/" not in final_url
    ok = on_monitor and not_found_err is None
    error = None
    if not on_monitor:
        error = f"expected /monitor after delete, got {final_url}"
    elif not_found_err:
        error = not_found_err
    return {
        "flow": "delete-paper",
        "id": "delete_paper_trade_redirect",
        "url": detail_url,
        "final_url": final_url,
        "trade_id": trade_id,
        "trade_title": title,
        "ok": ok,
        "status": 200 if ok else 0,
        "error": error,
    }


def run_journey_crawler(
    *,
    base_url: str = DEFAULT_BASE,
    flows: tuple[str, ...] = ("routes", "missing-paper"),
    out_dir: Path | None = None,
) -> dict[str, Any]:
    _ensure_playwright()
    from playwright.sync_api import sync_playwright

    base = base_url.rstrip("/")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    shot_dir = (out_dir or DEFAULT_OUT) / run_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = prepare_msos_browser_context(browser)
        page = context.new_page()

        if "routes" in flows:
            checks.extend(crawl_static_routes(page, base=base))

        if "missing-paper" in flows:
            checks.append(flow_missing_paper_trade(page, base=base))
            page.screenshot(path=str(shot_dir / "missing_paper_trade.png"), full_page=True)

        if "delete-paper" in flows:
            result = flow_delete_paper_trade(page, context, base=base)
            checks.append(result)
            page.screenshot(path=str(shot_dir / "delete_paper_trade.png"), full_page=True)

        browser.close()

    failed = [c for c in checks if not c.get("ok")]
    return {
        "version": 1,
        "kind": "msos_journey_crawler",
        "generated_at": _utc_now(),
        "base_url": base,
        "run_id": run_id,
        "flows": list(flows),
        "screenshot_dir": str(shot_dir.as_posix()),
        "passed": len(failed) == 0,
        "checks": checks,
        "summary": {"total": len(checks), "failed": len(failed)},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MSOS journey crawler (anti-404 witness)")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument(
        "--flows",
        nargs="+",
        default=["routes", "missing-paper"],
        choices=["routes", "missing-paper", "delete-paper"],
        help="Crawler flows to run (default: routes + missing-paper)",
    )
    ap.add_argument("--write-dir", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    report = run_journey_crawler(
        base_url=args.base_url,
        flows=tuple(args.flows),
        out_dir=args.write_dir,
    )
    out_dir = args.write_dir or DEFAULT_OUT
    manifest_path = out_dir / f"{report['run_id']}_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))

    print(f"msos_journey_crawler: wrote {manifest_path}", file=sys.stderr)
    if report["passed"]:
        print("msos_journey_crawler: PASS", file=sys.stderr)
        return 0
    print("msos_journey_crawler: FAIL", file=sys.stderr)
    for item in report["checks"]:
        if not item.get("ok"):
            print(f"  FAIL {item.get('flow')}:{item.get('id')}: {item.get('error')}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
