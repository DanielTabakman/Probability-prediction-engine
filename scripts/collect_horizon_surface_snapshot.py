"""
Daily collector for Options Horizon BTC options surface snapshots.

Writes JSON under artifacts/horizon_surface_archive/ by default.
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.fetch_deribit import (
    DEFAULT_OPTION_EXPIRIES_MAX,
    fetch_deribit_btc_index,
    fetch_deribit_btc_option_expiries,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_forward_and_iv_for_expiry,
)
from src.data.horizon_surface_archive import (
    build_surface_snapshot,
    default_archive_root,
    default_snapshot_path,
    serialize_surface_snapshot,
)


def collect_horizon_surface_snapshot(
    *,
    max_expiries: int = DEFAULT_OPTION_EXPIRIES_MAX,
    output: Path | None = None,
    archive_root: Path | None = None,
    spot_fn: Callable[[], float | None] | None = None,
    expiries_fn: Callable[[int], list[dict[str, Any]]] | None = None,
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None] | None = None,
    marks_full_fn: Callable[[int], dict[str, Any]] | None = None,
    now: datetime | None = None,
    asset_id: str = "BTC",
) -> Path:
    """Build surface snapshot JSON and write to archive; returns output path."""
    spot_loader = spot_fn or _default_spot
    expiries_loader = expiries_fn or fetch_deribit_btc_option_expiries
    fwd_iv_loader = forward_iv_fn or fetch_deribit_forward_and_iv_for_expiry
    marks_loader = marks_full_fn or fetch_deribit_btc_option_marks_by_expiry_full

    run_ts = now or datetime.now(tz=UTC)
    as_of_utc = run_ts.isoformat()
    now_ms = run_ts.timestamp() * 1000

    spot = spot_loader()
    if spot is None or float(spot) <= 0:
        raise RuntimeError("spot price unavailable from Deribit index")

    expiries = expiries_loader(max_expiries)
    if not expiries:
        raise RuntimeError("no option expiries returned from Deribit")

    snapshot = build_surface_snapshot(
        as_of_utc=as_of_utc,
        spot_usd=float(spot),
        expiries=expiries,
        forward_iv_fn=fwd_iv_loader,
        marks_full_fn=marks_loader,
        now_ms=now_ms,
        asset_id=asset_id,
    )
    if not snapshot.get("expiries"):
        raise RuntimeError("surface snapshot builder returned no expiries")

    root = archive_root or default_archive_root(ROOT)
    out = output or default_snapshot_path(as_of_utc=run_ts, root=root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize_surface_snapshot(snapshot), encoding="utf-8")
    return out


def _default_spot() -> float | None:
    return fetch_deribit_btc_index()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Collect Options Horizon surface JSON snapshot")
    ap.add_argument("--max-expiries", type=int, default=DEFAULT_OPTION_EXPIRIES_MAX)
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="JSON output path (default: artifacts/horizon_surface_archive/YYYY-MM-DD/...)",
    )
    ap.add_argument(
        "--archive-root",
        type=Path,
        default=None,
        help="Root directory for dated archive folders",
    )
    args = ap.parse_args(argv)

    try:
        out = collect_horizon_surface_snapshot(
            max_expiries=args.max_expiries,
            output=args.output,
            archive_root=args.archive_root,
        )
    except RuntimeError as exc:
        print(f"collect_horizon_surface_snapshot: {exc}", file=sys.stderr)
        return 1

    print(f"collect_horizon_surface_snapshot: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
