#!/usr/bin/env python3
"""Auto-discover the best live options source for an asset (multi-venue scan).

Agents MUST run this FIRST when the operator asks to add, enable, or hook up any asset.
Do not ask which exchange — scan wired venues and execute next_action.

Examples:
  python scripts/discover_asset_data_source.py --asset SOL
  python scripts/discover_asset_data_source.py --asset BNB --kind crypto --json
  python scripts/discover_asset_data_source.py --asset SPY --kind equity
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.asset_source_discovery import discover_asset_source  # noqa: E402
from src.data.assets_registry import get_asset, load_assets_registry  # noqa: E402


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Discover live options source for an asset")
    ap.add_argument("--asset", required=True, help="Asset id (e.g. SOL, SPY, NVDA)")
    ap.add_argument(
        "--kind",
        default="auto",
        choices=("auto", "crypto", "equity"),
        help="Asset class hint for venue scan order (default: auto)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    aid = str(args.asset).strip().upper()
    load_assets_registry.cache_clear()
    registry_entry: dict | None = None
    in_registry = False
    try:
        registry_entry = get_asset(aid)
        in_registry = True
    except KeyError:
        registry_entry = None

    report = discover_asset_source(
        aid,
        asset_kind=args.kind,
        registry_entry=registry_entry,
        in_registry=in_registry,
    )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        status = "OK" if report.get("ok") else "BLOCKED"
        print(f"{aid}: {status} — kind={report.get('asset_kind')}")
        for row in report.get("scan_results") or []:
            live = "live" if row.get("options_available") else "empty"
            wired = "wired" if row.get("wired") else "needs-adapter"
            print(
                f"  {row.get('venue')}: {row.get('options_count', 0)} options ({live}, {wired})"
            )
        if report.get("recommended_venue"):
            print(f"  -> recommend: {report['recommended_venue']} ({report.get('options_count')} options)")
        print(f"  next_action: {report.get('next_action')}")
        for step in report.get("agent_steps") or []:
            print(f"    - {step}")

    actionable = report.get("next_action") not in ("blocked_no_live_options", "already_enabled")
    return 0 if (report.get("ok") and actionable) or report.get("next_action") == "already_enabled" else 1


if __name__ == "__main__":
    raise SystemExit(main())
