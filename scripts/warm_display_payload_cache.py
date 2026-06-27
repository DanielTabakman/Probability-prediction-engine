#!/usr/bin/env python3
"""Warm in-process display payload cache for all enabled registry assets.

Run after deploy or on a schedule so first user hits warm cache:

  python scripts/warm_display_payload_cache.py
  python scripts/warm_display_payload_cache.py --base-url http://127.0.0.1:8765
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import list_enabled_asset_ids  # noqa: E402
from src.viz.display_payload_cache import (  # noqa: E402
    clear_display_payload_cache,
    get_cached_display_payload,
)
from src.viz.embed_display_boundary import (  # noqa: E402
    DISPLAY_DEPTH_FULL,
    build_live_distribution_display_payload,
)
from src.viz.lab_asset_selection import LAB_ASSET_QUERY_PARAM  # noqa: E402


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Warm display.json cache for enabled assets")
    ap.add_argument(
        "--base-url",
        default="",
        help="HTTP base for ppe_display_api (default: in-process build)",
    )
    ap.add_argument(
        "--depth",
        default=DISPLAY_DEPTH_FULL,
        choices=("summary", "full"),
        help="Payload depth to warm (default: full)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def _warm_in_process(asset_ids: list[str], *, depth: str) -> dict:
    clear_display_payload_cache()
    results: list[dict] = []
    ok = True
    for aid in asset_ids:
        try:
            payload = get_cached_display_payload(
                aid,
                depth,
                lambda asset_id=aid: build_live_distribution_display_payload(
                    asset_id=asset_id,
                    display_depth=depth,
                ),
            )
            series_count = len(payload.get("series_by_expiry") or [])
            results.append(
                {
                    "asset_id": aid,
                    "ok": True,
                    "spot_usd": payload.get("spot_usd"),
                    "series_count": series_count,
                }
            )
        except Exception as exc:  # noqa: BLE001
            ok = False
            results.append({"asset_id": aid, "ok": False, "error": str(exc)})
    return {"ok": ok, "mode": "in_process", "depth": depth, "results": results}


def _warm_http(base_url: str, asset_ids: list[str], *, depth: str) -> dict:
    base = base_url.rstrip("/")
    results: list[dict] = []
    ok = True
    for aid in asset_ids:
        url = f"{base}/display.json?{LAB_ASSET_QUERY_PARAM}={aid}&depth={depth}"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "ppe-warm/1"},
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = resp.read()
            payload = json.loads(body.decode("utf-8"))
            if payload.get("kind") == "display_error":
                ok = False
                results.append({"asset_id": aid, "ok": False, "error": payload.get("error")})
                continue
            results.append(
                {
                    "asset_id": aid,
                    "ok": True,
                    "spot_usd": payload.get("spot_usd"),
                    "series_count": len(payload.get("series_by_expiry") or []),
                }
            )
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            ok = False
            results.append({"asset_id": aid, "ok": False, "error": str(exc)})
    return {"ok": ok, "mode": "http", "depth": depth, "base_url": base, "results": results}


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    asset_ids = list_enabled_asset_ids()
    if not asset_ids:
        print("warm_display_payload_cache: no enabled assets", file=sys.stderr)
        return 1

    if args.base_url:
        report = _warm_http(args.base_url, asset_ids, depth=args.depth)
    else:
        report = _warm_in_process(asset_ids, depth=args.depth)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for row in report["results"]:
            if row.get("ok"):
                print(
                    f"  {row['asset_id']}: OK spot={row.get('spot_usd')} "
                    f"series={row.get('series_count')}"
                )
            else:
                print(f"  {row['asset_id']}: FAIL — {row.get('error')}")
        print(f"warm: {'OK' if report['ok'] else 'FAIL'} ({report['mode']}, depth={report['depth']})")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
