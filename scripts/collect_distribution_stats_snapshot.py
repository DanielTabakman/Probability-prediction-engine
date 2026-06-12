"""
Daily MVP collector for BTC implied distribution stats CSV snapshots.

Fetches live Deribit expiries/marks (same path as implied lab export) and writes
one timestamped CSV under artifacts/distribution_snapshots/ by default.
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
    fetch_deribit_btc_index,
    fetch_deribit_btc_option_expiries,
    fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_forward_and_iv_for_expiry,
)
from src.viz.distribution_export import (
    build_distribution_export_rows,
    serialize_distribution_export_csv,
)

DEFAULT_SNAPSHOT_ROOT = ROOT / "artifacts" / "distribution_snapshots"


def default_snapshot_path(
    *,
    as_of_utc: datetime,
    root: Path = DEFAULT_SNAPSHOT_ROOT,
) -> Path:
    day = as_of_utc.astimezone(UTC).strftime("%Y-%m-%d")
    stamp = as_of_utc.astimezone(UTC).strftime("%H%M%S")
    return root / day / f"ppe_btc_distribution_stats_{stamp}Z.csv"


def collect_distribution_stats_snapshot(
    *,
    max_expiries: int = 10,
    output: Path | None = None,
    snapshot_root: Path = DEFAULT_SNAPSHOT_ROOT,
    spot_fn: Callable[[], float | None] | None = None,
    expiries_fn: Callable[[int], list[dict[str, Any]]] | None = None,
    forward_iv_fn: Callable[[int, float], dict[str, Any] | None] | None = None,
    marks_full_fn: Callable[[int], dict[str, Any]] | None = None,
    now: datetime | None = None,
) -> Path:
    """Build export rows and write CSV; returns output path."""
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

    rows = build_distribution_export_rows(
        as_of_utc=as_of_utc,
        spot_usd=float(spot),
        expiries=expiries,
        forward_iv_fn=fwd_iv_loader,
        marks_full_fn=marks_loader,
        now_ms=now_ms,
    )
    if not rows:
        raise RuntimeError("export row builder returned no rows")

    out = output or default_snapshot_path(as_of_utc=run_ts, root=snapshot_root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(serialize_distribution_export_csv(rows), encoding="utf-8")
    return out


def _default_spot() -> float | None:
    return fetch_deribit_btc_index()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Collect BTC distribution stats CSV snapshot")
    ap.add_argument("--max-expiries", type=int, default=10)
    ap.add_argument(
        "--output",
        type=Path,
        default=None,
        help="CSV output path (default: artifacts/distribution_snapshots/YYYY-MM-DD/...)",
    )
    ap.add_argument(
        "--snapshot-root",
        type=Path,
        default=DEFAULT_SNAPSHOT_ROOT,
        help="Root directory for dated snapshot folders",
    )
    args = ap.parse_args(argv)

    try:
        out = collect_distribution_stats_snapshot(
            max_expiries=args.max_expiries,
            output=args.output,
            snapshot_root=args.snapshot_root,
        )
    except RuntimeError as exc:
        print(f"collect_distribution_stats_snapshot: {exc}", file=sys.stderr)
        return 1

    print(f"collect_distribution_stats_snapshot: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
