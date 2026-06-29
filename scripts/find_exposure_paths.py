"""CLI — ranked exposure path menu for one asset + direction.

Usage:
  python scripts/find_exposure_paths.py --asset NVDA --direction long --json
  python scripts/find_exposure_paths.py --asset BTC --direction long --horizon 3m --json
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

from scripts.exposure_path_core import find_exposure_paths  # noqa: E402
from src.engine.exposure_paths import HorizonChip  # noqa: E402

_VALID_HORIZONS: tuple[HorizonChip, ...] = ("any", "3m", "12m")


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Find ranked exposure paths for an asset + direction")
    ap.add_argument("--asset", required=True, help="Asset id (e.g. NVDA, BTC)")
    ap.add_argument(
        "--direction",
        default="long",
        choices=["long", "short", "neutral"],
        help="Exposure direction (default: long)",
    )
    ap.add_argument(
        "--horizon",
        default="any",
        choices=list(_VALID_HORIZONS),
        help="Optional horizon chip filter (default: any)",
    )
    ap.add_argument("--catalog", help="Optional path to exposure_path_catalog.yaml")
    ap.add_argument("--json", action="store_true", help="Emit JSON envelope on stdout")
    return ap.parse_args(argv)


def run_find_exposure_paths(
    asset_id: str,
    direction: str,
    *,
    horizon: HorizonChip = "any",
    catalog_path: str | None = None,
) -> dict[str, Any]:
    from scripts.exposure_path_core import load_exposure_path_catalog

    catalog = load_exposure_path_catalog(catalog_path) if catalog_path else None
    return find_exposure_paths(
        asset_id,
        direction,
        horizon=horizon,
        catalog=catalog,
    )


def _print_human(report: dict[str, Any]) -> None:
    aid = report.get("asset_id", "")
    status = report.get("status", "")
    live = report.get("live_path_count", 0)
    print(f"{aid} {report.get('direction', '')} — status={status} live_paths={live}")
    for path in report.get("paths") or []:
        badge = path.get("trust_badge", "")
        label = path.get("label", path.get("path_id", ""))
        cost = path.get("cost_hint_usd")
        cost_s = f" ${cost:,.2f}" if cost is not None else ""
        print(f"  [{badge}] {label}{cost_s}")
    footer = report.get("footer_copy")
    if footer:
        print(f"\n{footer}")


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    asset = str(args.asset or "").strip()
    if not asset:
        print("error: --asset is required", file=sys.stderr)
        return 2

    try:
        report = run_find_exposure_paths(
            asset,
            args.direction,
            horizon=args.horizon,  # type: ignore[arg-type]
            catalog_path=args.catalog,
        )
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _print_human(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
