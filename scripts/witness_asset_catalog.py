"""Witness enabled assets: registry row + catalog entry + display boundary scaffold.

Usage:
  python -m scripts.witness_asset_catalog --asset BTC
  python -m scripts.witness_asset_catalog --all-enabled
  python -m scripts.witness_asset_catalog --group crypto --pre-enable

CI uses mocked display-boundary checks by default; ``--live`` hits vendor fetch paths.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import (  # noqa: E402
    asset_venue,
    get_asset,
    is_asset_enabled,
    is_exposure_only,
    list_asset_ids_for_catalog_group,
    list_asset_ids_for_manifest_chapter,
    list_enabled_asset_ids,
)
from src.viz.embed_display_boundary import (  # noqa: E402
    build_asset_catalog_response,
    validate_asset_catalog_payload,
    witness_display_boundary_for_asset,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Witness tradeable asset catalog + display boundary")
    ap.add_argument("--asset", action="append", default=[], help="Asset id (repeatable)")
    ap.add_argument("--group", help="Witness all assets in catalog.group (e.g. crypto, equity_index)")
    ap.add_argument(
        "--manifest-slice",
        help="Witness assets declared in tier1 manifest chapter id",
    )
    ap.add_argument("--all-enabled", action="store_true", help="Witness every enabled registry asset")
    ap.add_argument(
        "--pre-enable",
        action="store_true",
        help="Validate disabled registry rows (enablement gate; mocked display boundary)",
    )
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
    pre_enable: bool = False,
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

        if not is_asset_enabled(aid) and not pre_enable:
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

        if is_exposure_only(aid):
            if live:
                try:
                    from scripts.probe_hyperliquid_perp import probe_hyperliquid_perp

                    probe = probe_hyperliquid_perp(aid)
                    ok = probe.get("status") == "ok"
                    detail = "exposure-only perp probe ok" if ok else str(probe.get("status") or "probe failed")
                except Exception as exc:  # noqa: BLE001 - witness reports vendor/probe failure
                    ok = False
                    detail = str(exc)
            else:
                ok = True
                detail = "exposure-only asset catalog ok"
        else:
            ok, detail = witness_display_boundary_for_asset(aid, live=live, pre_enable=pre_enable)
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
        "pre_enable": pre_enable,
        "results": results,
        "catalog": catalog if catalog_ok else None,
    }


def resolve_asset_ids(args: argparse.Namespace) -> list[str]:
    if args.asset:
        return sorted({str(a).strip().upper() for a in args.asset if str(a).strip()})
    if args.group:
        return list_asset_ids_for_catalog_group(args.group, enabled_only=False)
    if args.manifest_slice:
        return list_asset_ids_for_manifest_chapter(args.manifest_slice)
    if args.all_enabled:
        return list_enabled_asset_ids()
    return ["BTC", "ETH", "NVDA"]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    asset_ids = resolve_asset_ids(args)
    report = run_witness(asset_ids, live=bool(args.live), pre_enable=bool(args.pre_enable))
    try:
        from scripts.ppe_tracking_hub import record_asset_witness

        record_asset_witness(_REPO_ROOT, report)
    except Exception:
        pass
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
