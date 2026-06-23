"""HTTP witness for MSOS production demo journey (marketstructureos.com).

Canon: docs/SOP/MSOS_E2E_PRODUCT_WITNESS_V1_EVIDENCE_STATUS.md

Usage:
  python scripts/msos_production_demo_witness.py
  python scripts/msos_production_demo_witness.py --write artifacts/health/msos_production_demo_witness.json

Integration checks (PPE display API + Strategy Lab embed) fail the witness when broken —
catches obvious production regressions before operator walkthrough.
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
DISPLAY_PAYLOAD_KIND = "distribution_display_boundary"

# Known storyboard fixture copy — warn until live-metrics slice wires display API into UI.
FIXTURE_PREVIEW_SPOT = "$104,320"
FIXTURE_SAMPLE_SPOT = "Sample only"

JOURNEY_PATHS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("/", "homepage", ("Market Structure OS", "Explore the platform")),
    ("/strategy-lab", "strategy_lab", ("Strategy Lab", "Deribit")),
    ("/strategy-lab/confirm", "thesis_confirm", ("Is this what you actually believe?",)),
    ("/strategy-lab/expression", "expression", ("expression",)),
    ("/command-center", "command_center", ("Command Center", "Monitor")),
    ("/monitor", "monitor", ("Monitor", "Command Center")),
    ("/history", "history", ("History", "Live trades")),
    ("/learn", "learn", ("Reflect", "What did you take away?")),
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


def validate_display_api_response(
    status: int,
    body: str,
) -> tuple[bool, str | None, dict[str, Any] | None]:
    """True when display.json returns live distribution payload (not 500 / display_error)."""
    if status != 200:
        snippet = (body or "")[:200].strip()
        return False, f"HTTP {status}" + (f": {snippet}" if snippet else ""), None
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return False, "invalid JSON", None
    if not isinstance(data, dict):
        return False, "payload not an object", None
    if data.get("kind") == "display_error":
        return False, str(data.get("error") or "display_error"), data
    if data.get("kind") != DISPLAY_PAYLOAD_KIND:
        return False, f"unexpected kind {data.get('kind')!r}", data
    spot = data.get("spot_usd")
    if not isinstance(spot, (int, float)) or float(spot) <= 0:
        return False, "spot_usd missing or non-positive", data
    series = data.get("series_by_expiry")
    if not isinstance(series, list) or not series:
        return False, "series_by_expiry empty", data
    return True, None, data


def validate_belief_overlay_api_response(
    status: int,
    body: str,
) -> tuple[bool, str | None]:
    if status != 200:
        snippet = (body or "")[:200].strip()
        return False, f"HTTP {status}" + (f": {snippet}" if snippet else "")
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return False, "invalid JSON"
    if not isinstance(data, dict):
        return False, "payload not an object"
    if data.get("kind") != "belief_overlay":
        return False, f"unexpected kind {data.get('kind')!r}"
    pdf = data.get("pdf_pct")
    if not isinstance(pdf, list) or len(pdf) < 2:
        return False, "pdf_pct missing or too short"
    return True, None


def validate_strategy_suggestion_api_response(
    status: int,
    body: str,
) -> tuple[bool, str | None]:
    if status != 200:
        snippet = (body or "")[:200].strip()
        return False, f"HTTP {status}" + (f": {snippet}" if snippet else "")
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return False, "invalid JSON"
    if not isinstance(data, dict):
        return False, "payload not an object"
    if data.get("kind") != "strategy_suggestion_boundary":
        return False, f"unexpected kind {data.get('kind')!r}"
    suggested = data.get("suggested")
    if not isinstance(suggested, dict):
        return False, "suggested block missing"
    legs = suggested.get("legs")
    if not isinstance(legs, list) or not legs:
        return False, "suggested.legs empty"
    market = data.get("market")
    if not isinstance(market, dict):
        return False, "market block missing"
    pdf = market.get("pdf_pct")
    if not isinstance(pdf, list) or len(pdf) < 2:
        return False, "market.pdf_pct missing or too short"
    overlay = suggested.get("overlay")
    if not isinstance(overlay, dict):
        return False, "suggested.overlay missing"
    payoff = overlay.get("payoff_pct")
    if not isinstance(payoff, list) or len(payoff) < 2:
        return False, "suggested.overlay.payoff_pct missing or too short"
    return True, None


def validate_strategy_lab_html(html: str) -> tuple[bool, str | None]:
    """Strategy Lab must expose a live PPE surface, not degraded embed placeholder."""
    if "Sample mode — not live market data" in html:
        return False, "Strategy Lab rendered sample fixtures — live display API not loaded"
    if "Placeholder chart" in html and "ppe-chart-region" not in html:
        return False, "PPE chart in sample placeholder state"
    if "Embed pending" in html or "ppe-embed-degraded" in html:
        if "Placeholder chart" in html:
            return False, "PPE embed in sample/degraded state"
    if "ppe-chart-region" in html:
        return True, None
    if "Live via PPE" in html and "Native chart" in html:
        return True, None
    if "Traceback (most recent call last)" in html or "AttributeError" in html:
        return False, "Python error in page HTML"
    return False, "no PPE chart/embed region in Strategy Lab HTML"


def _collect_fixture_warnings(html: str) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    if FIXTURE_PREVIEW_SPOT in html or FIXTURE_SAMPLE_SPOT in html:
        warnings.append(
            {
                "id": "fixture_preview_metrics",
                "detail": "Hardcoded sample spot still in Strategy Lab UI — live display API may not be wired",
            }
        )
    if "Illustrative product storyboard" in html:
        warnings.append(
            {
                "id": "fixture_footer",
                "detail": "Storyboard disclaimer footer still visible",
            }
        )
    if "Preview data healthy" in html:
        warnings.append(
            {
                "id": "fixture_preview_pill",
                "detail": "Preview data pill — metrics not wired to live PPE yet",
            }
        )
    return warnings


def run_witness(*, base_url: str = DEFAULT_BASE) -> dict[str, Any]:
    base = base_url.rstrip("/")
    checks: list[dict[str, Any]] = []
    warnings: list[dict[str, str]] = []

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

    display_url = f"{base}/ppe-display-api/display.json"
    d_status, d_body, d_err = _fetch(display_url)
    d_ok, d_msg, d_data = validate_display_api_response(d_status, d_body)
    checks.append(
        {
            "id": "ppe_display_api",
            "url": display_url,
            "ok": d_ok,
            "status": d_status,
            "error": d_msg or d_err,
            "spot_usd": (d_data or {}).get("spot_usd"),
        }
    )

    overlay_ok = False
    overlay_msg: str | None = "display API unavailable for overlay probe"
    overlay_url = f"{base}/ppe-display-api/belief-overlay.json"
    if d_ok and d_data:
        series = d_data.get("series_by_expiry") or []
        expiry = series[0].get("expiry_date") if series else None
        if expiry:
            overlay_url = (
                f"{overlay_url}?expiry={expiry}&forward_mult=1.06&vol_mult=1.0"
            )
            o_status, o_body, o_err = _fetch(overlay_url)
            overlay_ok, overlay_msg = validate_belief_overlay_api_response(o_status, o_body)
            if o_err and not overlay_ok:
                overlay_msg = o_err
    checks.append(
        {
            "id": "ppe_belief_overlay_api",
            "url": overlay_url,
            "ok": overlay_ok,
            "status": 200 if overlay_ok else 0,
            "error": overlay_msg,
        }
    )

    suggestion_ok = False
    suggestion_msg: str | None = "display API unavailable for strategy suggestion probe"
    suggestion_url = f"{base}/ppe-display-api/strategy-suggestion.json"
    if d_ok and d_data:
        series = d_data.get("series_by_expiry") or []
        expiry = series[0].get("expiry_date") if series else None
        if expiry:
            suggestion_url = (
                f"{suggestion_url}?expiry={expiry}&forward_mult=1.0&vol_mult=0.7"
            )
            s_status, s_body, s_err = _fetch(suggestion_url)
            suggestion_ok, suggestion_msg = validate_strategy_suggestion_api_response(
                s_status, s_body
            )
            if s_err and not suggestion_ok:
                suggestion_msg = s_err
    checks.append(
        {
            "id": "ppe_strategy_suggestion_api",
            "url": suggestion_url,
            "ok": suggestion_ok,
            "status": 200 if suggestion_ok else 0,
            "error": suggestion_msg,
        }
    )

    lab_url = f"{base}/strategy-lab"
    lab_status, lab_body, lab_err = _fetch(lab_url)
    lab_ok, lab_msg = validate_strategy_lab_html(lab_body) if lab_status == 200 else (False, lab_err)
    checks.append(
        {
            "id": "strategy_lab_ppe_surface",
            "url": lab_url,
            "ok": lab_ok and lab_status == 200,
            "status": lab_status,
            "error": lab_msg or lab_err,
            "missing_phrases": [],
        }
    )
    if lab_status == 200:
        warnings.extend(_collect_fixture_warnings(lab_body))

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
    optional_ids = frozenset({"research_beta_cta"})
    integration_ids = frozenset({"ppe_display_api", "ppe_belief_overlay_api", "strategy_lab_ppe_surface"})
    journey_failed = [c for c in failed if c["id"] not in optional_ids]
    integration_failed = [c for c in failed if c["id"] in integration_ids]
    return {
        "version": 2,
        "generated_at": _utc_now(),
        "base_url": base,
        "passed": len(failed) == 0,
        "journey_passed": len(journey_failed) == 0,
        "integration_passed": len(integration_failed) == 0,
        "checks": checks,
        "warnings": warnings,
        "summary": {
            "total": len(checks),
            "failed": len(failed),
            "journey_failed": len(journey_failed),
            "integration_failed": len(integration_failed),
            "warnings": len(warnings),
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

    if not report.get("integration_passed", True):
        print("msos_production_demo_witness: integration FAIL (PPE display API or Strategy Lab embed)", file=sys.stderr)

    for w in report.get("warnings") or []:
        print(f"  warning: {w['id']}: {w['detail']}", file=sys.stderr)

    if not report["journey_passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
