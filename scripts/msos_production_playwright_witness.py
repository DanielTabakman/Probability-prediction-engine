"""Headless browser witness for MSOS production (screenshots + light interaction).

Complements HTTP witness (`msos_production_demo_witness.py`) with rendered-page checks
that catch broken PPE embeds, obvious layout regressions, and journey navigation.

Usage:
  python scripts/msos_production_playwright_witness.py
  python scripts/msos_production_playwright_witness.py --write-dir artifacts/health/msos_production_playwright
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.msos_playwright_session import (
    dismiss_platform_tutorial_if_visible,
    prepare_msos_browser_context,
)
from scripts.msos_production_demo_witness import (
    DEFAULT_BASE,
    LAB_ASSET_QUERY_PARAM,
    MULTI_ASSET_DISPLAY_PROBE_IDS,
    _utc_now,
    validate_display_api_response,
    validate_strategy_lab_html,
)
from scripts.msos_public_copy_gate import scan_html

DEFAULT_OUT = Path("artifacts/health/msos_production_playwright")

JOURNEY: tuple[tuple[str, str], ...] = (
    ("/", "homepage"),
    ("/strategy-lab", "strategy_lab"),
    ("/strategy-lab/confirm", "thesis_confirm"),
    ("/command-center", "command_center"),
)

# Non-BTC catalog spot checks — NVDA (equity) + one crypto (ETH).
REQUIRED_LIVE_PILL_SPOTS: tuple[tuple[str, str], ...] = (
    ("NVDA", "Live · equity options chain"),
    ("ETH", "Live · Deribit options"),
)

LIVE_PILL_EXPECTED: dict[str, str] = dict(REQUIRED_LIVE_PILL_SPOTS)

LIVE_PILL_SPOT_ASSETS: tuple[str, ...] = tuple(
    aid for aid in MULTI_ASSET_DISPLAY_PROBE_IDS if aid in LIVE_PILL_EXPECTED
)

LIVE_PILL_WAIT_MS = 120_000


def _missing_live_pill_spot_assets() -> list[str]:
    return [aid for aid, _ in REQUIRED_LIVE_PILL_SPOTS if aid not in LIVE_PILL_SPOT_ASSETS]


def validate_strategy_lab_live_pill_html(
    html: str,
    *,
    asset_id: str,
    expected_pill: str,
) -> tuple[bool, str | None]:
    """True when Strategy Lab shows the live data pill for the requested asset."""
    if "Sample mode — not live market data" in html:
        return False, "Strategy Lab rendered sample fixtures — live display API not loaded"
    if "Sample data · not live" in html:
        return False, "Live pill shows sample/demo mode"
    if expected_pill not in html:
        return False, f"expected live pill {expected_pill!r} not in page HTML"
    if 'class="pill live"' not in html and "pill live" not in html:
        return False, "live pill CSS class not present (may still be loading or demo)"
    aid = asset_id.strip().upper()
    if aid not in html:
        return False, f"{aid} not present in Strategy Lab HTML"
    return True, None


def _wait_for_live_pill_html(
    page: Any,
    *,
    asset_id: str,
    expected_pill: str,
    timeout_ms: int = LIVE_PILL_WAIT_MS,
) -> tuple[str, bool, str | None]:
    deadline = time.monotonic() + timeout_ms / 1000
    last_html = ""
    last_err: str | None = "live pill did not appear within timeout"
    while time.monotonic() < deadline:
        last_html = page.content()
        if "Sample data · not live" in last_html or "Sample mode — not live market data" in last_html:
            return last_html, False, "Strategy Lab in sample/demo mode"
        ok, err = validate_strategy_lab_live_pill_html(
            last_html,
            asset_id=asset_id,
            expected_pill=expected_pill,
        )
        if ok:
            return last_html, True, None
        if "Loading live data" not in last_html:
            last_err = err
        page.wait_for_timeout(750)
    return last_html, False, last_err


def _spot_check_strategy_lab_live_pill(
    page: Any,
    *,
    base: str,
    asset_id: str,
    expected_pill: str,
    shot_dir: Path,
) -> dict[str, Any]:
    url = f"{base}/strategy-lab?{LAB_ASSET_QUERY_PARAM}={asset_id}"
    page.goto(url, wait_until="networkidle", timeout=90_000)
    dismiss_platform_tutorial_if_visible(page)
    _, ok, err = _wait_for_live_pill_html(
        page,
        asset_id=asset_id,
        expected_pill=expected_pill,
    )
    key = f"strategy_lab_live_pill_{asset_id.lower()}"
    shot_path = shot_dir / f"{key}.png"
    page.screenshot(path=str(shot_path), full_page=True)
    return {
        "id": key,
        "url": url,
        "ok": ok,
        "status": 200,
        "error": err,
        "asset_id": asset_id,
        "expected_pill": expected_pill,
        "screenshot": str(shot_path.as_posix()),
    }


def _ensure_playwright() -> None:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "playwright is not installed. Run:\n"
            "  pip install playwright\n"
            "  python -m playwright install chromium\n"
        ) from exc


def run_playwright_witness(
    *,
    base_url: str = DEFAULT_BASE,
    out_dir: Path,
) -> dict[str, Any]:
    _ensure_playwright()
    from playwright.sync_api import sync_playwright

    base = base_url.rstrip("/")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    shot_dir = out_dir / run_id
    shot_dir.mkdir(parents=True, exist_ok=True)

    checks: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = prepare_msos_browser_context(browser)
        page = context.new_page()

        api_resp = context.request.get(f"{base}/ppe-display-api/display.json", timeout=60_000)
        api_body = api_resp.text()
        api_ok, api_err, api_data = validate_display_api_response(api_resp.status, api_body)
        checks.append(
            {
                "id": "ppe_display_api",
                "url": f"{base}/ppe-display-api/display.json",
                "ok": api_ok,
                "status": api_resp.status,
                "error": api_err,
                "spot_usd": (api_data or {}).get("spot_usd"),
            }
        )

        for path, key in JOURNEY:
            url = f"{base}{path}"
            page.goto(url, wait_until="networkidle", timeout=90_000)
            screenshot = shot_dir / f"{key}.png"
            page.screenshot(path=str(screenshot), full_page=True)
            html = page.content()
            copy_errors, copy_warns = scan_html(html, page_id=key)
            for warn in copy_warns:
                warnings.append({"id": f"public_copy_{key}_{warn.label}", "detail": warn.detail})
            entry: dict[str, Any] = {
                "id": key,
                "url": url,
                "screenshot": str(screenshot.as_posix()),
                "ok": len(copy_errors) == 0,
                "status": 200,
                "error": copy_errors[0].detail if copy_errors else None,
            }
            if path == "/strategy-lab":
                embed_ok, embed_err = validate_strategy_lab_html(html)
                entry["ok"] = embed_ok and entry["ok"]
                entry["error"] = embed_err or entry["error"]
                if "$104,320" in html:
                    warnings.append(
                        {
                            "id": "fixture_preview_metrics",
                            "detail": "Hardcoded storyboard spot $104,320 still in Strategy Lab UI",
                        }
                    )
                if "Illustrative product storyboard" in html:
                    warnings.append(
                        {
                            "id": "fixture_footer",
                            "detail": "Storyboard disclaimer footer still visible",
                        }
                    )
            checks.append(entry)

        lab_url = f"{base}/strategy-lab"
        page.goto(lab_url, wait_until="networkidle", timeout=90_000)
        dismiss_platform_tutorial_if_visible(page)
        higher = page.get_by_role("button", name="Higher", exact=True)
        belief_ok = higher.count() > 0
        belief_curve_ok = False
        if belief_ok:
            higher.first.click()
            page.wait_for_timeout(1500)
            html = page.content()
            belief_curve_ok = "strokeDasharray" in html or "#2dd4bf" in html
            page.screenshot(path=str(shot_dir / "strategy_lab_after_belief.png"), full_page=True)
        checks.append(
            {
                "id": "click_belief_higher",
                "url": lab_url,
                "ok": belief_ok and "Your view" in page.content() and belief_curve_ok,
                "status": 200 if belief_ok else 0,
                "error": None
                if belief_ok and "Your view" in page.content() and belief_curve_ok
                else "Belief preset click failed or belief curve did not render",
                "screenshot": str((shot_dir / "strategy_lab_after_belief.png").as_posix())
                if belief_ok
                else None,
            }
        )

        confirm = page.get_by_role("link", name=re.compile(r"Confirm view", re.I))
        dismiss_platform_tutorial_if_visible(page)
        confirm_ok = confirm.count() > 0
        if confirm_ok:
            confirm.first.click()
            page.wait_for_url(re.compile(r"/strategy-lab/confirm"), timeout=30_000)
            shot = shot_dir / "thesis_confirm_after_click.png"
            page.screenshot(path=str(shot), full_page=True)
        checks.append(
            {
                "id": "click_confirm_thesis",
                "url": lab_url,
                "ok": confirm_ok,
                "status": 200 if confirm_ok else 0,
                "error": None if confirm_ok else "Confirm view link not found",
                "screenshot": str((shot_dir / "thesis_confirm_after_click.png").as_posix())
                if confirm_ok
                else None,
            }
        )

        for asset_id in _missing_live_pill_spot_assets():
            checks.append(
                {
                    "id": f"strategy_lab_live_pill_{asset_id.lower()}",
                    "url": None,
                    "ok": False,
                    "status": 0,
                    "error": f"{asset_id} missing from multi-asset display probe catalog",
                    "asset_id": asset_id,
                    "expected_pill": LIVE_PILL_EXPECTED[asset_id],
                    "screenshot": None,
                }
            )

        for asset_id in LIVE_PILL_SPOT_ASSETS:
            expected_pill = LIVE_PILL_EXPECTED[asset_id]
            checks.append(
                _spot_check_strategy_lab_live_pill(
                    page,
                    base=base,
                    asset_id=asset_id,
                    expected_pill=expected_pill,
                    shot_dir=shot_dir,
                )
            )

        browser.close()

    failed = [c for c in checks if not c.get("ok")]
    return {
        "version": 1,
        "kind": "msos_production_playwright_witness",
        "generated_at": _utc_now(),
        "base_url": base,
        "run_id": run_id,
        "screenshot_dir": str(shot_dir.as_posix()),
        "passed": len(failed) == 0,
        "checks": checks,
        "warnings": warnings,
        "summary": {"total": len(checks), "failed": len(failed), "warnings": len(warnings)},
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MSOS production Playwright witness")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--write-dir", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    out_dir = args.write_dir or DEFAULT_OUT
    report = run_playwright_witness(base_url=args.base_url, out_dir=out_dir)
    manifest_path = out_dir / f"{report['run_id']}_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))

    print(f"msos_production_playwright_witness: wrote {manifest_path}", file=sys.stderr)
    if report["warnings"]:
        for w in report["warnings"]:
            print(f"  warning: {w['id']}: {w['detail']}", file=sys.stderr)

    if report["passed"]:
        print("msos_production_playwright_witness: PASS", file=sys.stderr)
        return 0
    print("msos_production_playwright_witness: FAIL", file=sys.stderr)
    for item in report["checks"]:
        if not item.get("ok"):
            print(f"  FAIL {item['id']}: {item.get('error')}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
