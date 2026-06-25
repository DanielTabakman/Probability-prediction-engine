#!/usr/bin/env python3
"""Verify production MSOS web shipped the expected client bundles (no Playwright).

Fails when strategy-lab page JS still contains pre-labeled-axis copy or is missing
axis strings — catches stale msos_web images after a green Deploy VPS run.

Usage:
  python scripts/verify_msos_web_ship.py
  python scripts/verify_msos_web_ship.py --base-url https://marketstructureos.com
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.error
import urllib.request

DEFAULT_BASE = "https://marketstructureos.com"
USER_AGENT = "ppe-msos-web-ship-verify/1"

# Stale Strategy Lab bundle markers (pre #320 / LabeledDistributionChart).
STALE_STRATEGY_LAB_MARKERS = ("Reference curve", "Options market")

# Required in strategy-lab page chunk when labeled axes ship.
REQUIRED_STRATEGY_LAB_MARKERS = ("BTC price at expiry",)


def fetch_url(url: str, *, timeout: float = 30.0) -> tuple[int, str, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace") if exc.fp else ""
        return exc.code, body, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return 0, "", str(exc.reason)


def verify_strategy_lab_client_bundle(html: str, *, base_url: str) -> tuple[bool, str | None]:
    """Strategy Lab page JS must ship labeled chart axes."""
    chunks = sorted(set(re.findall(r"/_next/static/chunks/app/strategy-lab/page-[^\"']+\.js", html)))
    if not chunks:
        return False, "strategy-lab page bundle missing from HTML"
    base = base_url.rstrip("/")
    for rel in chunks:
        status, body, err = fetch_url(f"{base}{rel}")
        if status != 200 or err:
            return False, err or f"strategy-lab bundle HTTP {status}"
        stale = [m for m in STALE_STRATEGY_LAB_MARKERS if m in body]
        if stale:
            return False, (
                "strategy-lab bundle still ships stale legend copy "
                f"({', '.join(stale)}) — rebuild msos_web with --no-cache"
            )
        missing = [m for m in REQUIRED_STRATEGY_LAB_MARKERS if m not in body]
        if missing:
            return False, (
                "strategy-lab bundle missing labeled axis copy "
                f"({', '.join(missing)}) — msos_web deploy did not ship"
            )
    return True, None


def verify_msos_web_ship(*, base_url: str = DEFAULT_BASE) -> tuple[bool, str | None]:
    """HTTP ship gate for MSOS Next.js client bundles."""
    base = base_url.rstrip("/")
    status, body, err = fetch_url(f"{base}/strategy-lab")
    if status != 200 or err:
        return False, err or f"strategy-lab HTTP {status}"
    if "Traceback (most recent call last)" in body or "ModuleNotFoundError" in body:
        return False, "strategy-lab HTML contains server error"
    return verify_strategy_lab_client_bundle(body, base_url=base)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify MSOS web client bundles on production")
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    args = parser.parse_args(argv)

    ok, detail = verify_msos_web_ship(base_url=args.base_url)
    if ok:
        print(f"msos_web ship verify OK ({args.base_url.rstrip('/')})")
        return 0
    print(f"msos_web ship verify FAILED: {detail}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
