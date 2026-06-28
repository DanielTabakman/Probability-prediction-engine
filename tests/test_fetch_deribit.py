"""Unit tests for Deribit fetch helpers (beyond currency wiring)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.data import fetch_deribit


def test_ticker_price_prefers_mark_price() -> None:
    assert fetch_deribit._ticker_price({"mark_price": 100_000.0}) == 100_000.0


def test_ticker_price_mid_from_bid_ask() -> None:
    assert fetch_deribit._ticker_price({"best_bid_price": 99_000.0, "best_ask_price": 101_000.0}) == 100_000.0


def test_mark_prices_by_instrument_from_book_summary() -> None:
    rows = [
        {"instrument_name": "BTC-1JAN26-90000-C", "mark_price": 0.05},
        {"instrumentName": "BTC-1JAN26-100000-C", "markPrice": 0.02},
        {"instrument_name": "bad", "mark_price": "n/a"},
    ]
    out = fetch_deribit._mark_prices_by_instrument_from_book_summary(rows)
    assert out["BTC-1JAN26-90000-C"] == 0.05
    assert out["BTC-1JAN26-100000-C"] == 0.02
    assert len(out) == 2


def test_fetch_deribit_index_uses_index_price() -> None:
    with patch.object(
        fetch_deribit,
        "fetch_deribit_ticker",
        return_value={"index_price": 42_000.0},
    ):
        assert fetch_deribit.fetch_deribit_index("BTC") == 42_000.0


def test_deribit_public_request_parses_result() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"result": [{"instrument_name": "X"}]}
    mock_resp.raise_for_status = MagicMock()
    with patch.object(fetch_deribit.requests, "get", return_value=mock_resp):
        result, err = fetch_deribit._deribit_public_request("get_instruments", {"currency": "BTC"})
    assert err is None
    assert result == [{"instrument_name": "X"}]


def test_deribit_public_request_returns_error_payload() -> None:
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"error": {"code": 123, "message": "bad params"}}
    mock_resp.raise_for_status = MagicMock()
    with patch.object(fetch_deribit.requests, "get", return_value=mock_resp):
        result, err = fetch_deribit._deribit_public_request("get_instruments", {})
    assert result is None
    assert err is not None
    assert "123" in err


def test_fetch_deribit_option_expiries_dedupes_and_sorts() -> None:
    instruments = [
        {"expiration_timestamp": 2000, "option_type": "call", "strike": 90000},
        {"expiration_timestamp": 2000, "option_type": "put", "strike": 90000},
        {"expiration_timestamp": 1000, "option_type": "call", "strike": 80000},
    ]
    with patch.object(fetch_deribit, "fetch_deribit_options_instruments", return_value=instruments):
        expiries = fetch_deribit.fetch_deribit_option_expiries(max_expiries=5, currency="BTC")
    assert len(expiries) == 2
    assert expiries[0]["expiry_ts"] == 1000
    assert expiries[1]["expiry_ts"] == 2000
    assert expiries[0]["expiry_date_str"]
