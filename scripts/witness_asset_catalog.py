"""Witness enabled assets: registry row + catalog entry + display boundary scaffold.

Usage:
  python scripts/witness_asset_catalog.py --asset BTC
  python scripts/witness_asset_catalog.py --all-enabled
  python scripts/witness_asset_catalog.py --all-enabled --live

CI uses mocked display-boundary checks by default; ``--live`` hits vendor fetch paths.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from src.data.assets_registry import (
    asset_venue,
    get_asset,
    is_asset_enabled,
    list_asset_ids_for_catalog_group,
    list_asset_ids_for_manifest_chapter,
    list_enabled_asset_ids,
)
from src.viz.embed_display_boundary import (
    CATALOG_PAYLOAD_KIND,
    build_asset_catalog_response,
    build_distribution_display_payload,
    validate_asset_catalog_payload,
    witness_display_boundary_for_asset,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Witness tradeable asset catalog + display boundary")
    ap.add_argument("--asset", help="Single asset id (e.g. BTC, ETH, NVDA)")
    ap.add_argument("--group", help="Witness all assets in catalog.group (e.g. crypto, equity_index)")
    ap.add_argument(
        "--manifest-slice",
        help="Witness assets declared in tier1 manifest chapter id",
    )
    ap.add_argument("--all-enabled", action="store_true", help="Witness every enabled registry asset")
    ap.add_argument("--live", action="store_true", help="Use live vendor fetch for display boundary")
    ap.add_argument("--json", action="store_true", help="Emit JSON report on stdout")
    return ap.parse_args(argv)


def witness_catalog_shape() -> tuple[bool, str, dict[str, Any]]:
    catalog = build_asset_catalog_response()
    ok, err = validate_asset_catalog_payload(catalog)
    return ok, err or "catalog shape ok", catalog


def run_witness(
    asset_ids: list[str],
    *,
    live: bool = False,
) -> dict[str, Any]:
    catalog_ok, catalog_msg, catalog = witness_catalog_shape()
    results: list[dict[str, Any]] = []
    all_ok = catalog_ok

    for aid in asset_ids:
        try:
            get_asset(aid)
        except KeyError:
            results.append({"asset_id": aid, "ok": False, "detail": "unknown asset_id"})
            all_ok = False
            continue

        if not is_asset_enabled(aid):
            results.append(
                {
                    "asset_id": aid,
                    "ok": True,
                    "skipped": True,
                    "detail": "disabled in registry",
                    "venue": asset_venue(aid),
                }
            )
            continue

        ok, detail = witness_display_boundary_for_asset(aid, live=live)
        results.append(
            {
                "asset_id": aid,
                "ok": ok,
                "detail": detail,
                "venue": asset_venue(aid),
                "live": live,
            }
        )
        all_ok = all_ok and ok

    return {
        "ok": all_ok and catalog_ok,
        "catalog_ok": catalog_ok,
        "catalog_detail": catalog_msg,
        "enabled_count": len(list_enabled_asset_ids()),
        "results": results,
        "catalog": catalog if catalog_ok else None,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.asset:
        asset_ids = [str(args.asset).strip().upper()]
    elif args.group:
        asset_ids = list_asset_ids_for_catalog_group(args.group, enabled_only=False)
    elif args.manifest_slice:
        asset_ids = list_asset_ids_for_manifest_chapter(args.manifest_slice)
    elif args.all_enabled:
        asset_ids = list_enabled_asset_ids()
    else:
        asset_ids = ["BTC", "ETH", "NVDA"]

    report = run_witness(asset_ids, live=bool(args.live))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"catalog: {'OK' if report['catalog_ok'] else 'FAIL'} — {report['catalog_detail']}")
        for row in report["results"]:
            label = row["asset_id"]
            if row.get("skipped"):
                print(f"  {label}: SKIP — {row['detail']}")
            elif row["ok"]:
                print(f"  {label}: OK — {row['detail']}")
            else:
                print(f"  {label}: FAIL — {row['detail']}")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
