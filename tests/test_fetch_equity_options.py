"""Tests for equity options fetch adapter (Yahoo → Deribit-shaped payloads)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from src.data import fetch_equity_options
from src.data.assets_registry import (
    asset_venue,
    equity_symbol,
    is_asset_enabled,
    load_assets_registry,
)


def _mock_chain() -> MagicMock:
    calls = pd.DataFrame(
        [
            {
                "contractSymbol": "NVDA260718C00180000",
                "strike": 180.0,
                "lastPrice": 12.5,
                "bid": 12.0,
                "ask": 13.0,
            },
            {
                "contractSymbol": "NVDA260718C00200000",
                "strike": 200.0,
                "lastPrice": 5.25,
                "bid": 5.0,
                "ask": 5.5,
            },
        ]
    )
    puts = pd.DataFrame(
        [
            {
                "contractSymbol": "NVDA260718P00180000",
                "strike": 180.0,
                "lastPrice": 8.0,
                "bid": 7.8,
                "ask": 8.2,
            }
        ]
    )
    chain = MagicMock()
    chain.calls = calls
    chain.puts = puts
    return chain


@patch.object(fetch_equity_options.yf, "Ticker")
def test_fetch_equity_options_instruments_deribit_shape(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.return_value = _mock_chain()
    mock_ticker.return_value = tk

    out = fetch_equity_options.fetch_equity_options_instruments("NVDA", max_expiries=1)
    assert len(out) == 3
    call = next(i for i in out if i["option_type"] == "call" and i["strike"] == 180.0)
    assert call["instrument_name"] == "NVDA260718C00180000"
    assert call["expiration_timestamp"] > 0
    assert call["equity_symbol"] == "NVDA"


@patch.object(fetch_equity_options.yf, "Ticker")
def test_fetch_equity_option_marks_by_expiry_calls_only(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.return_value = _mock_chain()
    mock_ticker.return_value = tk

    expiry_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")
    marks = fetch_equity_options.fetch_equity_option_marks_by_expiry(expiry_ts, "NVDA", max_expiries=1)
    assert len(marks) == 2
    assert marks[0]["strike"] == 180.0
    assert marks[0]["mark_btc"] == 12.5
    assert marks[1]["strike"] == 200.0


@patch.object(fetch_equity_options.yf, "Ticker")
def test_fetch_equity_option_book_marks(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.return_value = _mock_chain()
    mock_ticker.return_value = tk

    marks = fetch_equity_options.fetch_equity_option_book_marks("NVDA", max_expiries=1)
    assert marks["NVDA260718C00180000"] == 12.5
    assert marks["NVDA260718P00180000"] == 8.0


def test_nvda_registry_equity_venue_enabled() -> None:
    load_assets_registry.cache_clear()
    assert asset_venue("NVDA") == "equity"
    assert equity_symbol("NVDA") == "NVDA"
    assert is_asset_enabled("NVDA") is True
    assert is_asset_enabled("BTC") is True
