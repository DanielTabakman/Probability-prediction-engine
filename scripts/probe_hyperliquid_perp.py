"""Probe Hyperliquid perp mark/funding for an exposure-only asset."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.data.assets_registry import asset_venue, hyperliquid_coin, is_asset_enabled  # noqa: E402
from src.data.fetch_hyperliquid import fetch_hyperliquid_perp_context  # noqa: E402


def probe_hyperliquid_perp(asset_id: str) -> dict[str, object]:
    aid = str(asset_id or "").strip().upper()
    if not aid:
        raise ValueError("asset is required")
    if asset_venue(aid) != "hyperliquid":
        raise ValueError(f"asset {aid!r} is not a Hyperliquid asset")
    ctx = fetch_hyperliquid_perp_context(hyperliquid_coin(aid))
    return {
        "asset_id": aid,
        "venue": "hyperliquid",
        "enabled": is_asset_enabled(aid),
        "status": "ok" if ctx.get("mark_px") and ctx.get("funding") is not None else "missing_market",
        **ctx,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Probe Hyperliquid perp mark/funding")
    ap.add_argument("--asset", default="HYPE", help="Asset id from config/assets.yaml")
    ap.add_argument("--json", action="store_true", help="Emit JSON")
    args = ap.parse_args(argv)

    try:
        report = probe_hyperliquid_perp(args.asset)
    except (KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"{report['asset_id']} Hyperliquid perp status={report['status']} "
            f"mark={report['mark_px']} funding={report['funding']}"
        )
    return 0 if report.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
