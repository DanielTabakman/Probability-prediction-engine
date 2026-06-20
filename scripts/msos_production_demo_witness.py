"""HTTP witness for MSOS production demo journey (marketstructureos.com).

Canon: docs/SOP/MSOS_E2E_PRODUCT_WITNESS_V1_EVIDENCE_STATUS.md

Usage:
  python scripts/msos_production_demo_witness.py
  python scripts/msos_production_demo_witness.py --write artifacts/health/msos_production_demo_witness.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_BASE = "https://marketstructureos.com"
APP_HOST = "https://app.marketstructureos.com"

JOURNEY_PATHS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("/", "homepage", ("Market Structure OS", "Explore the platform")),
    ("/strategy-lab", "strategy_lab", ("Strategy Lab", "PPE")),
    ("/strategy-lab/confirm", "thesis_confirm", ("Is this what you think is true",)),
    ("/strategy-lab/expression", "expression", ("expression",)),
    ("/command-center", "command_center", ("Command Center", "Current work")),
    ("/monitor", "monitor", ("Monitor", "Monitoring")),
    ("/history", "history", ("History", "Observed")),
    ("/learn", "learn", ("Learn loop", "comprehension")),
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _fetch(url: str, *, timeout: float = 30.0) -> tuple[int, str, str | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "ppe-msos-production-demo-witness/1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body, None
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        return int(exc.code), body, str(exc.reason)
    except Exception as exc:
        return 0, "", str(exc)


def _has_research_cta(html: str) -> bool:
    return bool(
        re.search(r"Request research beta access", html, re.IGNORECASE)
        or re.search(r"research beta", html, re.IGNORECASE)
    )


def run_witness(*, base_url: str = DEFAULT_BASE) -> dict[str, Any]:
    base = base_url.rstrip("/")
    checks: list[dict[str, Any]] = []

    for path, key, needles in JOURNEY_PATHS:
        url = f"{base}{path}"
        status, body, err = _fetch(url)
        missing = [n for n in needles if n not in body]
        ok = status == 200 and not missing and err is None
        checks.append(
            {
                "id": key,
                "url": url,
                "ok": ok,
                "status": status,
                "error": err,
                "missing_phrases": missing,
            }
        )

    home_status, home_body, home_err = _fetch(f"{base}/")
    cta_ok = home_status == 200 and _has_research_cta(home_body)
    checks.append(
        {
            "id": "research_beta_cta",
            "url": f"{base}/",
            "ok": cta_ok,
            "status": home_status,
            "error": None if cta_ok else (home_err or "CTA not in HTML — set PPE_RESEARCH_OFFER_URL on VPS and rebuild msos_web"),
            "missing_phrases": [] if cta_ok else ["Request research beta access"],
        }
    )

    app_status, app_body, app_err = _fetch(f"{APP_HOST}/")
    access_ok = app_status in (200, 401, 403) and (
        "Cloudflare Access" in app_body or "Log in" in app_body or app_status in (401, 403)
    )
    checks.append(
        {
            "id": "sign_in_access_gate",
            "url": f"{APP_HOST}/",
            "ok": access_ok,
            "status": app_status,
            "error": app_err,
            "missing_phrases": [] if access_ok else ["Cloudflare Access"],
        }
    )

    failed = [c for c in checks if not c.get("ok")]
    journey_failed = [c for c in failed if c["id"] not in ("research_beta_cta",)]
    return {
        "version": 1,
        "generated_at": _utc_now(),
        "base_url": base,
        "passed": len(failed) == 0,
        "journey_passed": len(journey_failed) == 0,
        "checks": checks,
        "summary": {
            "total": len(checks),
            "failed": len(failed),
            "journey_failed": len(journey_failed),
        },
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="MSOS production demo HTTP witness")
    ap.add_argument("--base-url", default=DEFAULT_BASE)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", type=Path, default=None, help="Write JSON report to path")
    args = ap.parse_args(argv)

    report = run_witness(base_url=args.base_url)
    text = json.dumps(report, indent=2) + "\n"

    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"msos_production_demo_witness: wrote {args.write}")

    if args.json or not args.write:
        print(text, end="")

    if report["journey_passed"]:
        print("msos_production_demo_witness: journey PASS", file=sys.stderr)
    else:
        print("msos_production_demo_witness: journey FAIL", file=sys.stderr)

    if not report["passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
