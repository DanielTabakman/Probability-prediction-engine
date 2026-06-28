#!/usr/bin/env python3
"""Auto-discover the best live options source for an asset (multi-venue scan).

Agents MUST run this FIRST when the operator asks to add, enable, or hook up any asset
or batch (group, manifest chapter, full registry). Do not ask which exchange.

Examples:
  python scripts/discover_asset_data_source.py --asset SOL
  python scripts/discover_asset_data_source.py --group crypto --json
  python scripts/discover_asset_data_source.py --manifest-slice ppe_deribit_crypto_tier1_v1
  python scripts/discover_asset_data_source.py --all-registry
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.asset_source_discovery_core import discover_asset_source  # noqa: E402
from src.data.assets_registry import (  # noqa: E402
    get_asset,
    list_asset_ids,
    list_asset_ids_for_catalog_group,
    list_asset_ids_for_manifest_chapter,
    load_assets_registry,
)


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Discover live options source for asset(s)")
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--asset", action="append", default=[], help="Asset id (repeatable)")
    target.add_argument("--group", help="catalog.group id (crypto, equity_index, …)")
    target.add_argument(
        "--manifest-slice",
        help="tier1 manifest chapter id (e.g. ppe_deribit_crypto_tier1_v1)",
    )
    target.add_argument(
        "--all-registry",
        action="store_true",
        help="Every asset id in config/assets.yaml",
    )
    ap.add_argument(
        "--kind",
        default="auto",
        choices=("auto", "crypto", "equity"),
        help="Asset class hint when not inferrable from registry (default: auto)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def resolve_batch_asset_ids(args: argparse.Namespace) -> list[str]:
    if args.asset:
        return sorted({str(a).strip().upper() for a in args.asset if str(a).strip()})
    if args.group:
        return list_asset_ids_for_catalog_group(args.group, enabled_only=False)
    if args.manifest_slice:
        return list_asset_ids_for_manifest_chapter(args.manifest_slice)
    if args.all_registry:
        return list_asset_ids()
    return []


def _registry_context(asset_id: str) -> tuple[dict | None, bool]:
    try:
        return get_asset(asset_id), True
    except KeyError:
        return None, False


def discover_one(asset_id: str, *, asset_kind: str) -> dict:
    entry, in_registry = _registry_context(asset_id)
    return discover_asset_source(
        asset_id,
        asset_kind=asset_kind,
        registry_entry=entry,
        in_registry=in_registry,
    )


def discover_batch(asset_ids: list[str], *, asset_kind: str) -> dict:
    reports = [discover_one(aid, asset_kind=asset_kind) for aid in asset_ids]
    by_action = Counter(str(r.get("next_action") or "unknown") for r in reports)
    actionable = sum(
        1
        for r in reports
        if r.get("next_action")
        not in ("blocked_no_live_options", "already_enabled")
        and r.get("ok")
    )
    blocked = sum(1 for r in reports if r.get("next_action") == "blocked_no_live_options")
    already = sum(1 for r in reports if r.get("next_action") == "already_enabled")
    return {
        "ok": actionable > 0 or (bool(reports) and blocked == 0 and already == len(reports)),
        "asset_ids": asset_ids,
        "count": len(reports),
        "actionable_count": actionable,
        "blocked_count": blocked,
        "already_enabled_count": already,
        "next_action_rollup": dict(sorted(by_action.items())),
        "reports": reports,
        "sop": "docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md",
    }


def _exit_code_for_report(report: dict) -> int:
    if "reports" in report:
        if report.get("actionable_count", 0) > 0:
            return 0
        if report.get("count", 0) > 0 and report.get("blocked_count", 0) == 0:
            return 0
        return 1
    action = report.get("next_action")
    actionable = action not in ("blocked_no_live_options", "already_enabled")
    if (report.get("ok") and actionable) or action == "already_enabled":
        return 0
    return 1


def _print_single(report: dict) -> None:
    aid = report.get("asset_id", "?")
    status = "OK" if report.get("ok") else "BLOCKED"
    print(f"{aid}: {status} — kind={report.get('asset_kind')}")
    for row in report.get("scan_results") or []:
        live = "live" if row.get("options_available") else "empty"
        wired = "wired" if row.get("wired") else "needs-adapter"
        print(
            f"  {row.get('venue')}: {row.get('options_count', 0)} options ({live}, {wired})"
        )
    if report.get("recommended_venue"):
        print(
            f"  -> recommend: {report['recommended_venue']} "
            f"({report.get('options_count')} options)"
        )
    print(f"  next_action: {report.get('next_action')}")
    for step in report.get("agent_steps") or []:
        print(f"    - {step}")


def _print_batch(summary: dict) -> None:
    print(
        f"batch: {summary.get('count')} assets — "
        f"{summary.get('actionable_count')} actionable, "
        f"{summary.get('already_enabled_count')} already enabled, "
        f"{summary.get('blocked_count')} blocked"
    )
    rollup = summary.get("next_action_rollup") or {}
    if rollup:
        parts = [f"{k}={v}" for k, v in rollup.items()]
        print(f"  rollup: {', '.join(parts)}")
    for report in summary.get("reports") or []:
        aid = report.get("asset_id", "?")
        venue = report.get("recommended_venue") or "-"
        action = report.get("next_action")
        opts = report.get("options_count", 0)
        print(f"  {aid}: {action} ({venue}, {opts} options)")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_assets_registry.cache_clear()
    asset_ids = resolve_batch_asset_ids(args)
    if not asset_ids:
        print("discover_asset_data_source: no assets", file=sys.stderr)
        return 1

    if len(asset_ids) == 1:
        report = discover_one(asset_ids[0], asset_kind=args.kind)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            _print_single(report)
        return _exit_code_for_report(report)

    summary = discover_batch(asset_ids, asset_kind=args.kind)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        _print_batch(summary)
    return _exit_code_for_report(summary)


if __name__ == "__main__":
    raise SystemExit(main())
