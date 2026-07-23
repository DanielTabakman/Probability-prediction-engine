"""Fixture/live witness for Market Proposal + Hedge Capacity Preview v0."""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data.fetch_deribit import (
    fetch_deribit_btc_index,
    fetch_deribit_options_instruments,
    fetch_deribit_order_book,
)
from src.engine.market_proposal_hedge_capacity import (
    SETTLEMENT_PROVENANCE,
    adjacent_strikes,
    build_preview,
    build_preview_from_fixture,
    export_json,
    export_markdown,
    render_markdown,
    select_proposed_threshold,
    to_dict,
)

FIXTURE_PATH = ROOT / "fixtures" / "market_proposal_hedge_capacity" / "btc_terminal_v0.json"
ARTIFACT_DIR = ROOT / "artifacts" / "market_proposal_hedge_capacity"


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fixture", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = parser.parse_args()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = ARTIFACT_DIR / ("fixture_witness" if args.fixture else "live_witness") / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.fixture:
        preview = build_preview_from_fixture(FIXTURE_PATH)
        source_mode = "fixture"
    else:
        data = _live_data()
        (out_dir / "live_input.json").write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        preview = build_preview(data)
        source_mode = "live"

    json_path = export_json(preview, out_dir / "market_proposal_hedge_capacity_preview.json")
    md_path = export_markdown(preview, out_dir / "market_proposal_hedge_capacity_preview.md")
    summary = {
        "ok": preview.readiness_state in {"SHAREABLE_DESIGN", "REVIEW_ONLY"},
        "mode": source_mode,
        "readiness_state": preview.readiness_state,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "yes_policy_capacity_usd": preview.yes_hedge.policy_capacity_usd,
        "no_policy_capacity_usd": preview.no_hedge.policy_capacity_usd,
        "yes_flags": preview.yes_hedge.flags,
        "no_flags": preview.no_hedge.flags,
        "question": preview.proposed_contract.question,
    }
    (out_dir / "witness_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fixture:
        fixture_export = ARTIFACT_DIR / "exports" / "fixture_market_proposal_hedge_capacity_v0.md"
        fixture_export.parent.mkdir(parents=True, exist_ok=True)
        fixture_export.write_text(render_markdown(preview), encoding="utf-8")
    return 0 if summary["ok"] else 1


def _live_data() -> dict[str, Any]:
    instruments = fetch_deribit_options_instruments("BTC", expired=False)
    inverse = [
        _normalize_instrument(row)
        for row in instruments
        if row.get("base_currency") == "BTC"
        and row.get("settlement_currency") == "BTC"
        and row.get("quote_currency") == "BTC"
        and row.get("option_type") in {"call", "put"}
        and row.get("strike") is not None
        and row.get("instrument_name")
    ]
    if not inverse:
        raise RuntimeError("No live BTC inverse option instruments returned by Deribit public API")
    index = fetch_deribit_btc_index()
    if index is None:
        raise RuntimeError("No live BTC index returned by Deribit public API")
    expiry = _select_expiry(inverse, index)
    expiry_rows = [row for row in inverse if row["expiry_utc"] == expiry]
    proposed = select_proposed_threshold(expiry_rows, expiry, float(index))
    lower, upper = adjacent_strikes(expiry_rows, expiry, proposed)
    needed = [
        _find(expiry_rows, lower, "call"),
        _find(expiry_rows, upper, "call"),
        _find(expiry_rows, lower, "put"),
        _find(expiry_rows, upper, "put"),
    ]
    books = {}
    for row in needed:
        time.sleep(0.15)
        book = fetch_deribit_order_book(row["instrument_name"], depth=5)
        if not isinstance(book, dict):
            raise RuntimeError(f"No live order book for {row['instrument_name']}")
        books[row["instrument_name"]] = {
            "timestamp_utc": _timestamp_utc(book.get("timestamp")),
            "asks": book.get("asks") or [],
            "bids": book.get("bids") or [],
        }
    return {
        "as_of_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "data_mode": "live_public_deribit",
        "index_price_usd": float(index),
        "requested_event": {
            "underlying": "BTC",
            "comparator": "above",
            "requested_threshold_usd": float(index),
            "selected_expiry_utc": expiry,
            "requested_payout_usd": 10000.0,
            "max_depth_levels": 3,
            "max_slippage_bps": 500.0,
        },
        "reserve_policy": {
            "legging_reserve_bps": 15.0,
            "stale_sync_reserve_bps": 10.0,
            "settlement_currency_basis_reserve_bps": 25.0,
        },
        "settlement_metadata": {
            "settlement_source": "Deribit BTC Index",
            "settlement_method": (
                "Official delivery price is the 30-minute TWAP of the relevant Deribit Index "
                "from 07:30 to 08:00 UTC for instruments expiring at 08:00 UTC, sampled every 4 seconds."
            ),
            "provenance": SETTLEMENT_PROVENANCE,
        },
        "instruments": expiry_rows,
        "order_books": books,
    }


def _normalize_instrument(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    ts = row.get("expiration_timestamp")
    if ts is not None:
        out["expiry_utc"] = _timestamp_utc(ts)
    return out


def _select_expiry(instruments: list[dict[str, Any]], index: float) -> str:
    by_expiry: dict[str, list[dict[str, Any]]] = {}
    for row in instruments:
        by_expiry.setdefault(row["expiry_utc"], []).append(row)
    now = datetime.now(timezone.utc)
    for expiry in sorted(by_expiry):
        if datetime.fromisoformat(expiry.replace("Z", "+00:00")) <= now:
            continue
        rows = by_expiry[expiry]
        strikes = sorted({float(row["strike"]) for row in rows})
        if not any(strike <= index for strike in strikes) or not any(strike > index for strike in strikes):
            continue
        lower = max(strike for strike in strikes if strike <= index)
        upper = min(strike for strike in strikes if strike > lower)
        if all(_maybe_find(rows, strike, typ) for strike in (lower, upper) for typ in ("call", "put")):
            return expiry
    raise RuntimeError("No expiry with adjacent live call/put strikes around current BTC index")


def _find(rows: list[dict[str, Any]], strike: float, option_type: str) -> dict[str, Any]:
    found = _maybe_find(rows, strike, option_type)
    if found is None:
        raise RuntimeError(f"Missing live {option_type} at {strike}")
    return found


def _maybe_find(rows: list[dict[str, Any]], strike: float, option_type: str) -> dict[str, Any] | None:
    return next(
        (
            row
            for row in rows
            if float(row.get("strike") or -1) == strike and row.get("option_type") == option_type
        ),
        None,
    )


def _timestamp_utc(ts: Any) -> str:
    return datetime.fromtimestamp(float(ts) / 1000.0, tz=timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


if __name__ == "__main__":
    raise SystemExit(main())
