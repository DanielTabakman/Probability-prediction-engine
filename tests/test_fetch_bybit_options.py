"""Tests for Bybit options fetch adapter (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.data import fetch_bybit_options as bybit
from src.data.assets_registry import load_assets_registry


def _sample_instrument() -> dict:
    return {
        "symbol": "SOL-31JUL26-82-C-USDT",
        "status": "Trading",
        "optionsType": "Call",
        "deliveryTime": "1785484800000",
    }


def _sample_ticker() -> dict:
    return {
        "symbol": "SOL-31JUL26-82-C-USDT",
        "markPrice": "2.5",
        "markIv": "0.55",
        "indexPrice": "70.5",
        "underlyingPrice": "70.7",
    }


def test_parse_symbol_strike_and_side() -> None:
    parsed = bybit._parse_symbol("SOL-31JUL26-82-P-USDT")
    assert parsed is not None
    assert parsed["strike"] == 82.0
    assert parsed["option_type"] == "put"


@patch.object(bybit, "_fetch_instruments_pages")
def test_fetch_bybit_options_instruments_shape(mock_pages: MagicMock) -> None:
    load_assets_registry.cache_clear()
    mock_pages.return_value = [_sample_instrument()]
    out = bybit.fetch_bybit_options_instruments(asset_id="SOL", max_expiries=5)
    assert len(out) == 1
    assert out[0]["instrument_name"] == "SOL-31JUL26-82-C-USDT"
    assert out[0]["strike"] == 82.0
    assert out[0]["option_type"] == "call"
    assert out[0]["expiration_timestamp"] == 1785484800000


@patch.object(bybit, "_ticker_map")
@patch.object(bybit, "fetch_bybit_options_instruments")
def test_fetch_bybit_option_marks_by_expiry_full(
    mock_inst: MagicMock,
    mock_tickers: MagicMock,
) -> None:
    load_assets_registry.cache_clear()
    mock_inst.return_value = [
        {
            "instrument_name": "SOL-31JUL26-82-C-USDT",
            "strike": 82.0,
            "expiration_timestamp": 1785484800000,
            "option_type": "call",
        }
    ]
    mock_tickers.return_value = {"SOL-31JUL26-82-C-USDT": _sample_ticker()}
    marks = bybit.fetch_bybit_option_marks_by_expiry_full(1785484800000, asset_id="SOL")
    assert len(marks["calls"]) == 1
    assert marks["calls"][0]["mark_btc"] == 2.5


@patch.object(bybit, "_ticker_map")
def test_fetch_bybit_spot_from_index(mock_tickers: MagicMock) -> None:
    load_assets_registry.cache_clear()
    mock_tickers.return_value = {"SOL-31JUL26-82-C-USDT": _sample_ticker()}
    assert bybit.fetch_bybit_spot(asset_id="SOL") == 70.5
