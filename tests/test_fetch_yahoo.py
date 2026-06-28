"""Tests for Yahoo price fetch shaping."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd

from src.data.fetch_yahoo import fetch_yahoo_prices


def test_fetch_yahoo_prices_no_tickers_returns_empty_frame() -> None:
    out = fetch_yahoo_prices(symbols={"noop": []}, period="5d")
    assert out.empty


def test_fetch_yahoo_prices_single_ticker_multiindex() -> None:
    idx = pd.to_datetime(["2026-01-01", "2026-01-02"])
    raw = pd.DataFrame(
        {
            ("BTC-USD", "Open"): [100.0, 101.0],
            ("BTC-USD", "Close"): [100.5, 101.5],
            ("BTC-USD", "Volume"): [10, 11],
        },
        index=idx,
    )
    raw.columns = pd.MultiIndex.from_tuples(raw.columns)

    with patch("src.data.fetch_yahoo.yf.download", return_value=raw):
        out = fetch_yahoo_prices(symbols={"bitcoin": ["BTC-USD"]}, period="5d")

    assert not out.empty
    assert set(out["symbol"]) == {"BTC-USD"}
    assert set(out["asset"]) == {"bitcoin"}
    assert "close" in out.columns
    assert float(out["close"].iloc[-1]) == 101.5
