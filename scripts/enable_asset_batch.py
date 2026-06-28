#!/usr/bin/env python3
"""Enable a batch of registry assets after witness gate (meta infra enablement pipeline).

Examples:
  python scripts/enable_asset_batch.py --group equity_index --dry-run
  python scripts/enable_asset_batch.py --manifest-slice ppe_equity_universe_tier1a_v1 --dry-run
  python scripts/enable_asset_batch.py --group crypto --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import (  # noqa: E402
    ASSETS_PATH,
    get_asset,
    is_asset_enabled,
    list_asset_ids_for_catalog_group,
    list_asset_ids_for_manifest_chapter,
)

import yaml  # noqa: E402


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Enable asset batch in config/assets.yaml")
    target = ap.add_mutually_exclusive_group(required=True)
    target.add_argument("--group", help="catalog.group id (crypto, equity_index, …)")
    target.add_argument(
        "--manifest-slice",
        help="tier1 manifest chapter id (e.g. ppe_equity_universe_tier1a_v1)",
    )
    ap.add_argument("--asset", action="append", default=[], help="Explicit asset id (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="Print plan only; do not write YAML")
    ap.add_argument("--apply", action="store_true", help="Write enabled: true after witness pass")
    ap.add_argument("--skip-witness", action="store_true", help="Skip witness subprocess (not for prod)")
    ap.add_argument("--live-witness", action="store_true", help="Run witness with --live vendor fetch")
    ap.add_argument("--json", action="store_true", help="Emit JSON report")
    return ap.parse_args(argv)


def resolve_batch_asset_ids(args: argparse.Namespace) -> list[str]:
    if args.asset:
        return sorted({str(a).strip().upper() for a in args.asset if str(a).strip()})
    if args.group:
        return list_asset_ids_for_catalog_group(args.group, enabled_only=False)
    return list_asset_ids_for_manifest_chapter(args.manifest_slice)


def _load_assets_yaml() -> dict:
    with ASSETS_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("assets.yaml root must be a mapping")
    return data


def _plan_enablement(asset_ids: list[str]) -> list[dict]:
    rows: list[dict] = []
    for aid in asset_ids:
        try:
            entry = get_asset(aid)
        except KeyError:
            rows.append({"asset_id": aid, "action": "error", "detail": "unknown asset_id"})
            continue
        if is_asset_enabled(aid):
            rows.append({"asset_id": aid, "action": "skip", "detail": "already enabled"})
            continue
        rows.append({"asset_id": aid, "action": "enable", "detail": "would set enabled: true"})
    return rows


def _apply_enablement(asset_ids: list[str]) -> list[dict]:
    data = _load_assets_yaml()
    assets = data.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("assets.yaml missing assets mapping")

    applied: list[dict] = []
    for aid in asset_ids:
        if aid not in assets or not isinstance(assets[aid], dict):
            applied.append({"asset_id": aid, "action": "error", "detail": "missing registry row"})
            continue
        if assets[aid].get("enabled") is True:
            applied.append({"asset_id": aid, "action": "skip", "detail": "already enabled"})
            continue
        assets[aid]["enabled"] = True
        applied.append({"asset_id": aid, "action": "enabled", "detail": "enabled: true"})

    with ASSETS_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return applied


def _run_witness(
    args: argparse.Namespace,
    asset_ids: list[str],
    *,
    live: bool,
) -> tuple[bool, dict]:
    """Pre-enable witness on assets slated for enablement."""
    del args
    if not asset_ids:
        return True, {"ok": True, "results": []}

    from scripts import witness_asset_catalog as witness_mod

    report = witness_mod.run_witness(asset_ids, live=live, pre_enable=True)
    return bool(report.get("ok")), report


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.apply and args.dry_run:
        print("enable_asset_batch: use --dry-run or --apply, not both", file=sys.stderr)
        return 2

    asset_ids = resolve_batch_asset_ids(args)
    if not asset_ids:
        print("enable_asset_batch: no assets in batch", file=sys.stderr)
        return 1

    plan = _plan_enablement(asset_ids)
    to_enable = [row["asset_id"] for row in plan if row["action"] == "enable"]

    witness_ok = True
    witness_report: dict | None = None
    if to_enable and not args.skip_witness and (args.apply or args.dry_run):
        witness_ok, witness_report = _run_witness(args, to_enable, live=bool(args.live_witness))

    applied: list[dict] = []
    if args.apply and witness_ok and to_enable:
        applied = _apply_enablement(to_enable)

    report = {
        "ok": witness_ok and all(r["action"] != "error" for r in plan),
        "mode": "apply" if args.apply else "dry-run",
        "asset_ids": asset_ids,
        "plan": plan,
        "witness_ok": witness_ok,
        "witness": witness_report,
        "applied": applied,
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"enable_asset_batch ({report['mode']}): {len(asset_ids)} asset(s)")
        for row in plan:
            print(f"  {row['asset_id']}: {row['action'].upper()} — {row['detail']}")
        if to_enable:
            print(f"witness: {'OK' if witness_ok else 'FAIL'}")
        if applied:
            for row in applied:
                print(f"  applied {row['asset_id']}: {row['detail']}")

    if not witness_ok:
        return 1
    if args.apply and to_enable and not applied:
        return 1
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
