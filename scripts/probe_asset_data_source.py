#!/usr/bin/env python3
"""Probe live data availability for a registry asset before enablement or BUILD.

For **new** assets or wrong venue, run discover_asset_data_source.py first (multi-venue scan).
Use this script to verify the **current** registry row after changes.

Examples:
  python scripts/discover_asset_data_source.py --asset SOL
  python scripts/probe_asset_data_source.py --asset SOL
  python scripts/probe_asset_data_source.py --asset NVDA --json
  python scripts/probe_asset_data_source.py --manifest-slice ppe_deribit_crypto_tier1_v1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import (  # noqa: E402
    asset_venue,
    bybit_base_coin,
    deribit_currency,
    equity_symbol,
    get_asset,
    list_asset_ids_for_catalog_group,
    list_asset_ids_for_manifest_chapter,
)
from scripts.asset_source_discovery_core import scan_bybit_crypto  # noqa: E402

VENUE_MAP_PATH = _REPO_ROOT / "config" / "asset_venue_source_map.yaml"
DERIBIT_BASE = "https://www.deribit.com/api/v2"


def _load_venue_map() -> dict[str, Any]:
    if not VENUE_MAP_PATH.is_file():
        return {}
    with VENUE_MAP_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _research_alternatives(asset_id: str) -> dict[str, Any] | None:
    research = _load_venue_map().get("research_alternatives") or {}
    row = research.get(asset_id.upper())
    return row if isinstance(row, dict) else None


def _deribit_get(method: str, params: dict[str, Any]) -> tuple[Any | None, str | None]:
    try:
        resp = requests.get(f"{DERIBIT_BASE}/public/{method}", params=params, timeout=20)
        resp.raise_for_status()
        body = resp.json()
    except Exception as exc:  # noqa: BLE001 — probe script surfaces vendor errors
        return None, str(exc)
    if isinstance(body, dict) and body.get("error"):
        err = body["error"]
        return None, str(err.get("message") or err)
    return body.get("result") if isinstance(body, dict) else body, None


def probe_deribit(asset_id: str) -> dict[str, Any]:
    currency = deribit_currency(asset_id)
    options, opt_err = _deribit_get(
        "get_instruments",
        {"currency": currency, "kind": "option", "expired": "false"},
    )
    index, idx_err = _deribit_get("get_index_price", {"index_name": f"{currency.lower()}_usd"})
    option_count = len(options) if isinstance(options, list) else 0
    index_price = None
    if isinstance(index, dict):
        index_price = index.get("index_price")
    return {
        "venue": "deribit",
        "currency": currency,
        "option_instruments": option_count,
        "index_price_usd": index_price,
        "options_available": option_count > 0,
        "errors": {"instruments": opt_err, "index": idx_err},
        "fetch_module": "src.data.fetch_deribit",
        "api_base": DERIBIT_BASE,
    }


def probe_equity(asset_id: str) -> dict[str, Any]:
    symbol = equity_symbol(asset_id)
    entry = get_asset(asset_id)
    data_source = str(entry.get("data_source") or "yfinance")
    expiry_count = 0
    err: str | None = None
    if data_source == "yfinance":
        try:
            import yfinance as yf

            opts = getattr(yf.Ticker(symbol), "options", None) or []
            expiry_count = len(list(opts))
        except Exception as exc:  # noqa: BLE001
            err = str(exc)
    else:
        err = f"unsupported data_source: {data_source}"
    return {
        "venue": "equity",
        "equity_symbol": symbol,
        "data_source": data_source,
        "option_expiries": expiry_count,
        "options_available": expiry_count > 0,
        "errors": {"yfinance": err},
        "fetch_module": "src.data.fetch_equity_options",
    }


def probe_bybit(asset_id: str) -> dict[str, Any]:
    entry = get_asset(asset_id)
    coin = str(entry.get("bybit_base_coin") or asset_id).strip().upper()
    row = scan_bybit_crypto(coin)
    return {
        "venue": "bybit",
        "base_coin": coin,
        "option_instruments": row.get("options_count", 0),
        "index_price_usd": row.get("index_price_usd"),
        "options_available": bool(row.get("options_available")),
        "errors": row.get("errors") or {},
        "fetch_module": row.get("fetch_module") or "src.data.fetch_bybit_options",
        "api_base": "https://api.bybit.com/v5",
    }


def probe_asset(asset_id: str) -> dict[str, Any]:
    aid = asset_id.strip().upper()
    try:
        entry = get_asset(aid)
    except KeyError:
        return {"asset_id": aid, "ok": False, "error": "unknown asset_id"}

    venue = asset_venue(aid)
    if venue == "deribit":
        vendor = probe_deribit(aid)
    elif venue == "bybit":
        vendor = probe_bybit(aid)
    elif venue == "equity":
        vendor = probe_equity(aid)
    else:
        return {
            "asset_id": aid,
            "ok": False,
            "venue": venue,
            "error": f"no probe for venue {venue!r} — extend probe_asset_data_source.py",
        }

    research = _research_alternatives(aid)
    options_ok = bool(vendor.get("options_available"))
    report: dict[str, Any] = {
        "asset_id": aid,
        "ok": options_ok,
        "venue": venue,
        "enabled_in_registry": entry.get("enabled"),
        "label": entry.get("label"),
        "asset_class": entry.get("asset_class"),
        "vendor_probe": vendor,
        "enable_recommendation": "enable" if options_ok else "block_until_source_available",
        "sop": "docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md",
    }
    if research:
        report["research_alternatives"] = research
    if not options_ok:
        report["blocker"] = (
            f"{aid}: {venue} probe found no live options chain — do not set enabled: true"
        )
    return report


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Probe live data source for registry asset(s)")
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--asset", action="append", default=[], help="Asset id (repeatable)")
    target.add_argument(
        "--manifest-slice",
        help="Probe all assets in tier1 manifest chapter (e.g. ppe_deribit_crypto_tier1_v1)",
    )
    target.add_argument("--group", help="Probe all assets in catalog.group (e.g. crypto, equity_index)")
    ap.add_argument("--json", action="store_true", help="Emit JSON on stdout")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.manifest_slice:
        asset_ids = list_asset_ids_for_manifest_chapter(args.manifest_slice)
    elif args.group:
        asset_ids = list_asset_ids_for_catalog_group(args.group, enabled_only=False)
    else:
        asset_ids = sorted({a.strip().upper() for a in args.asset if a.strip()})

    if not asset_ids:
        print("probe_asset_data_source: no assets", file=sys.stderr)
        return 1

    reports = [probe_asset(aid) for aid in asset_ids]
    summary = {
        "ok": all(r.get("ok") for r in reports),
        "asset_ids": asset_ids,
        "reports": reports,
        "venue_map": str(VENUE_MAP_PATH.relative_to(_REPO_ROOT)),
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        for r in reports:
            vp = r.get("vendor_probe") or {}
            status = "OK" if r.get("ok") else "BLOCKED"
            print(f"{r['asset_id']}: {status} — venue={r.get('venue')}")
            if r.get("venue") == "deribit":
                print(
                    f"  Deribit {vp.get('currency')}: "
                    f"{vp.get('option_instruments', 0)} options, "
                    f"index={vp.get('index_price_usd')}"
                )
            elif r.get("venue") == "bybit":
                print(
                    f"  Bybit {vp.get('base_coin')}: "
                    f"{vp.get('option_instruments', 0)} options, "
                    f"index={vp.get('index_price_usd')}"
                )
            elif r.get("venue") == "equity":
                print(
                    f"  {vp.get('data_source')} {vp.get('equity_symbol')}: "
                    f"{vp.get('option_expiries', 0)} expiries"
                )
            if r.get("blocker"):
                print(f"  blocker: {r['blocker']}")
            if r.get("research_alternatives"):
                print(f"  research: see config/asset_venue_source_map.yaml -> {r['asset_id']}")

    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
