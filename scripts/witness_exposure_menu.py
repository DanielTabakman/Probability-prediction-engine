"""Witness exposure menu bindings and path activation for registry assets.

Usage:
  python -m scripts.witness_exposure_menu --group equity_index --live
  python -m scripts.witness_exposure_menu --asset SPY --asset QQQ --asset IWM
  python -m scripts.witness_exposure_menu --all-enabled
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.exposure_path_core import (  # noqa: E402
    find_exposure_paths,
    load_exposure_path_catalog,
    resolve_path_ids_for_asset,
)
from src.data.assets_registry import (  # noqa: E402
    asset_class,
    asset_venue,
    is_asset_enabled,
    list_asset_ids_for_catalog_group,
    list_enabled_asset_ids,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Witness exposure menu catalog bindings + paths")
    ap.add_argument("--asset", action="append", default=[], help="Asset id (repeatable)")
    ap.add_argument("--group", help="Catalog group (e.g. equity_index, crypto)")
    ap.add_argument("--all-enabled", action="store_true", help="Every enabled registry asset")
    ap.add_argument(
        "--direction",
        default="long",
        choices=("long", "short", "neutral"),
        help="Exposure direction to witness (default long)",
    )
    ap.add_argument(
        "--live",
        action="store_true",
        help="Hit live vendor fetch (default: mocked equity/crypto chain)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def _equity_mock_expiries() -> list[dict[str, Any]]:
    now = int(time.time() * 1000)
    return [
        {"expiration_timestamp": now + 90 * 86_400_000, "expiry_date_str": "2026-09-28"},
        {"expiration_timestamp": now + 300 * 86_400_000, "expiry_date_str": "2027-04-25"},
    ]


def _equity_mock_marks(spot: float) -> dict[str, list[dict[str, Any]]]:
    atm = round(spot, 0)
    otm = round(spot * 1.1, 0)
    return {
        "calls": [
            {"strike": float(atm), "mark_btc": max(1.0, spot * 0.05), "open_interest": 500},
            {"strike": float(otm), "mark_btc": max(0.5, spot * 0.02), "open_interest": 200},
            {"strike": float(otm + max(2.0, spot * 0.05)), "mark_btc": max(0.25, spot * 0.01), "open_interest": 150},
        ],
        "puts": [
            {"strike": float(atm * 0.95), "mark_btc": max(0.75, spot * 0.03), "open_interest": 400},
            {"strike": float(atm), "mark_btc": max(1.0, spot * 0.04), "open_interest": 350},
        ],
    }


def _default_spot(asset_id: str) -> float:
    defaults = {
        "NVDA": 180.0,
        "SPY": 580.0,
        "QQQ": 500.0,
        "IWM": 210.0,
        "BTC": 100_000.0,
        "ETH": 3_500.0,
        "SOL": 150.0,
    }
    return defaults.get(asset_id.upper(), 100.0)


def _resolve_asset_ids(args: argparse.Namespace) -> list[str]:
    if args.asset:
        return sorted({str(a).strip().upper() for a in args.asset if str(a).strip()})
    if args.group:
        return list_asset_ids_for_catalog_group(args.group, enabled_only=True)
    if args.all_enabled:
        return list_enabled_asset_ids()
    return ["SPY", "QQQ", "IWM"]


def _binding_ok(asset_id: str, direction: str, catalog: dict[str, Any]) -> tuple[bool, str, list[str]]:
    key = asset_class(asset_id)
    bindings = catalog.get("asset_bindings") or {}
    if key not in bindings:
        return False, f"missing asset_bindings for class {key!r}", []
    path_ids = resolve_path_ids_for_asset(asset_id, direction, catalog)
    if not path_ids and direction != "neutral":
        return False, f"no paths bound for direction {direction!r}", []
    return True, f"binding {key!r} ok ({len(path_ids)} template(s))", path_ids


def witness_one_asset(
    asset_id: str,
    *,
    direction: str,
    live: bool,
    catalog: dict[str, Any],
) -> dict[str, Any]:
    aid = asset_id.strip().upper()
    bind_ok, bind_detail, template_ids = _binding_ok(aid, direction, catalog)
    row: dict[str, Any] = {
        "asset_id": aid,
        "asset_class": asset_class(aid),
        "enabled": is_asset_enabled(aid),
        "binding_ok": bind_ok,
        "binding_detail": bind_detail,
        "template_ids": template_ids,
    }
    if not bind_ok:
        row["ok"] = False
        return row

    spot = _default_spot(aid)

    def _run() -> dict[str, Any]:
        return find_exposure_paths(aid, direction, catalog=catalog)

    try:
        if live:
            report = _run()
        else:
            marks = _equity_mock_marks(spot)
            with (
                patch("scripts.exposure_path_core._fetch_spot", return_value=spot),
                patch("scripts.exposure_path_core._fetch_option_expiries", return_value=_equity_mock_expiries()),
                patch("scripts.exposure_path_core._fetch_marks_for_expiry", return_value=marks),
            ):
                report = _run()
    except Exception as exc:  # noqa: BLE001
        row["ok"] = False
        row["error"] = str(exc)
        return row

    paths = report.get("paths") or []
    live_paths = [p for p in paths if isinstance(p, dict) and p.get("trust_badge") == "Live"]
    thin = [p for p in paths if isinstance(p, dict) and p.get("trust_badge") == "Thin chain"]
    sections = report.get("sections") or []

    row.update(
        {
            "ok": len(live_paths) >= 1 or direction == "neutral",
            "status": report.get("status"),
            "live_path_count": len(live_paths),
            "thin_chain_count": len(thin),
            "section_count": len(sections),
            "path_ids": [p.get("path_id") for p in paths if isinstance(p, dict)],
            "mode": "live" if live else "mocked",
        }
    )
    if direction != "neutral" and len(live_paths) < 2:
        row["warn"] = "fewer than 2 live paths — check chain or trust badges"
        row["ok"] = len(live_paths) >= 1
    return row


def run_witness(
    asset_ids: list[str],
    *,
    direction: str = "long",
    live: bool = False,
) -> dict[str, Any]:
    catalog = load_exposure_path_catalog()
    results = [witness_one_asset(aid, direction=direction, live=live, catalog=catalog) for aid in asset_ids]
    ok = all(r.get("ok") for r in results)
    return {
        "ok": ok,
        "direction": direction,
        "live": live,
        "asset_count": len(asset_ids),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    asset_ids = _resolve_asset_ids(args)
    report = run_witness(asset_ids, direction=str(args.direction), live=bool(args.live))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        mode = "live" if report["live"] else "mocked"
        print(f"exposure menu witness ({mode}, direction={report['direction']})")
        for row in report["results"]:
            label = row["asset_id"]
            if row.get("ok"):
                extra = (
                    f"live={row.get('live_path_count')} thin={row.get('thin_chain_count', 0)} "
                    f"sections={row.get('section_count')}"
                )
                if row.get("warn"):
                    extra += f" — WARN {row['warn']}"
                print(f"  {label}: OK — {extra}")
            else:
                print(f"  {label}: FAIL — {row.get('error') or row.get('binding_detail')}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
