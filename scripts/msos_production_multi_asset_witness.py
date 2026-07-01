"""Production witness: display.json and exposure-menu.json healthy for every enabled asset."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import asset_venue, list_enabled_asset_ids  # noqa: E402
from src.viz.lab_asset_selection import LAB_ASSET_QUERY_PARAM  # noqa: E402

DEFAULT_BASE = "https://marketstructureos.com/ppe-display-api"

EXPOSURE_DIRECTION = "long"
EXPOSURE_HORIZON = "any"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Production multi-asset display witness")
    ap.add_argument("--base-url", default=DEFAULT_BASE, help="Display API base URL")
    ap.add_argument("--write", help="Write JSON report to path")
    ap.add_argument("--json", action="store_true", help="Print JSON report")
    return ap.parse_args(argv)


def _timeout_for(asset_id: str) -> float:
    return 180.0 if asset_venue(asset_id) == "equity" else 60.0


def _probe_display(base: str, asset_id: str) -> dict[str, Any]:
    url = f"{base.rstrip('/')}/display.json?{LAB_ASSET_QUERY_PARAM}={asset_id}"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "ppe-multi-asset-witness/1"})
    timeout = _timeout_for(asset_id)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
        payload = json.loads(body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"asset_id": asset_id, "ok": False, "surface": "display", "error": str(exc)}

    if payload.get("kind") == "display_error":
        return {"asset_id": asset_id, "ok": False, "surface": "display", "error": payload.get("error")}
    payload_asset = str((payload.get("asset") or {}).get("id") or "").upper()
    if payload_asset != asset_id.upper():
        return {
            "asset_id": asset_id,
            "ok": False,
            "surface": "display",
            "error": f"payload asset mismatch: {payload_asset}",
        }
    return {
        "asset_id": asset_id,
        "ok": True,
        "surface": "display",
        "spot_usd": payload.get("spot_usd"),
        "series_count": len(payload.get("series_by_expiry") or []),
        "trust_state": payload.get("trust_state") or payload.get("meta", {}).get("trust_state"),
    }


def _probe_exposure_menu(base: str, asset_id: str) -> dict[str, Any]:
    params = (
        f"asset={asset_id.upper()}&direction={EXPOSURE_DIRECTION}&horizon={EXPOSURE_HORIZON}"
    )
    url = f"{base.rstrip('/')}/exposure-menu.json?{params}"
    req = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "ppe-multi-asset-witness/1"},
    )
    timeout = _timeout_for(asset_id)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
        payload = json.loads(body)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"asset_id": asset_id, "ok": False, "surface": "exposure_menu", "error": str(exc)}

    if payload.get("kind") == "exposure_menu_error":
        return {
            "asset_id": asset_id,
            "ok": False,
            "surface": "exposure_menu",
            "error": payload.get("error"),
        }
    if payload.get("kind") != "exposure_paths":
        return {
            "asset_id": asset_id,
            "ok": False,
            "surface": "exposure_menu",
            "error": f"unexpected kind: {payload.get('kind')!r}",
        }
    if str(payload.get("asset_id") or "").upper() != asset_id.upper():
        return {
            "asset_id": asset_id,
            "ok": False,
            "surface": "exposure_menu",
            "error": "asset_id mismatch in exposure payload",
        }
    paths = payload.get("paths") or []
    live = [p for p in paths if isinstance(p, dict) and p.get("trust_badge") == "Live"]
    return {
        "asset_id": asset_id,
        "ok": True,
        "surface": "exposure_menu",
        "live_path_count": len(live),
        "status": payload.get("status"),
    }


def run_witness(*, base_url: str) -> dict[str, Any]:
    asset_ids = list_enabled_asset_ids()
    results: list[dict[str, Any]] = []
    for aid in asset_ids:
        results.append(_probe_display(base_url, aid))
        results.append(_probe_exposure_menu(base_url, aid))
    ok = all(row.get("ok") for row in results) if results else False
    return {"ok": ok, "base_url": base_url, "asset_count": len(asset_ids), "results": results}


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    report = run_witness(base_url=args.base_url)
    if args.write:
        out = Path(args.write)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json or not args.write:
        print(json.dumps(report, indent=2, sort_keys=True))
    elif not args.json:
        for row in report["results"]:
            status = "OK" if row.get("ok") else "FAIL"
            print(f"  {row['asset_id']}: {status}" + (f" — {row.get('error')}" if row.get("error") else ""))
        print(f"multi-asset witness: {'OK' if report['ok'] else 'FAIL'}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
