from __future__ import annotations

from typing import Any

from src.data.fetch_deribit import (
    fetch_deribit_btc_futures_forward_curve as _fetch_deribit_btc_futures_forward_curve,
    fetch_deribit_btc_index as _fetch_deribit_btc_index,
    fetch_deribit_btc_option_book_marks as _fetch_deribit_btc_option_book_marks,
    fetch_deribit_btc_option_expiries as _fetch_deribit_btc_option_expiries,
    fetch_deribit_btc_option_marks_by_expiry_full as _fetch_deribit_btc_option_marks_by_expiry_full,
    fetch_deribit_btc_options_instruments as _fetch_deribit_btc_options_instruments,
    fetch_deribit_btc_options_for_chart as _fetch_deribit_btc_options_for_chart,
    fetch_deribit_btc_options_summary as _fetch_deribit_btc_options_summary,
    fetch_deribit_btc_tight_bull_spreads as _fetch_deribit_btc_tight_bull_spreads,
    fetch_deribit_forward_and_iv_for_expiry as _fetch_deribit_forward_and_iv_for_expiry,
    last_deribit_instruments_diagnostic as _last_deribit_instruments_diagnostic,
)
from src.probability_engine.services.market_data import snapshot_deribit_option_book_marks


def get_deribit_btc_index() -> float | None:
    return _fetch_deribit_btc_index()


def get_deribit_btc_futures_forward_curve(*, max_contracts: int) -> Any:
    return _fetch_deribit_btc_futures_forward_curve(max_contracts=max_contracts)


def get_deribit_btc_options_instruments(*, expired: bool) -> Any:
    return _fetch_deribit_btc_options_instruments(expired=expired)


def get_deribit_btc_option_book_marks(*, snapshot: bool = True) -> dict[str, float] | None:
    marks = _fetch_deribit_btc_option_book_marks()
    if snapshot:
        snapshot_deribit_option_book_marks(marks)
    return marks


def get_deribit_btc_tight_bull_spreads(
    *,
    spot_price: float,
    spread_width: float,
    max_expiries: int,
    instruments: Any,
    option_book_marks: dict[str, float] | None,
) -> Any:
    return _fetch_deribit_btc_tight_bull_spreads(
        spot_price=spot_price,
        spread_width=spread_width,
        max_expiries=max_expiries,
        instruments=instruments,
        option_book_marks=option_book_marks,
    )


def get_deribit_btc_options_for_chart(*, instruments: Any) -> Any:
    return _fetch_deribit_btc_options_for_chart(instruments=instruments)


def get_deribit_btc_option_expiries(*, max_expiries: int) -> tuple[list[dict[str, Any]], Any]:
    rows = _fetch_deribit_btc_option_expiries(max_expiries=max_expiries)
    return rows, _last_deribit_instruments_diagnostic()


def get_deribit_forward_and_iv_for_expiry(*, expiry_ts: float, spot: float) -> dict[str, Any] | None:
    return _fetch_deribit_forward_and_iv_for_expiry(expiry_ts, spot)


def get_deribit_btc_option_marks_by_expiry_full(*, expiry_ts: float) -> dict[str, Any] | None:
    return _fetch_deribit_btc_option_marks_by_expiry_full(expiry_ts)


def get_deribit_btc_options_summary(*, max_tickers: int) -> Any:
    return _fetch_deribit_btc_options_summary(max_tickers=max_tickers)

