"""Tests for probe_asset_data_source.py (mocked vendor calls)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from scripts import probe_asset_data_source as probe_mod


def test_probe_deribit_reports_option_count() -> None:
    with patch.object(probe_mod, "_deribit_get") as mock_get:
        mock_get.side_effect = [
            ([{"instrument_name": "BNB-1JAN26-700-C"}], None),
            ({"index_price": 700.0}, None),
        ]
        out = probe_mod.probe_deribit("BNB")
    assert out["option_instruments"] == 1
    assert out["options_available"] is True
    assert out["index_price_usd"] == 700.0


def test_probe_deribit_zero_options_blocked() -> None:
    with patch.object(probe_mod, "_deribit_get") as mock_get:
        mock_get.side_effect = [
            ([], None),
            ({"index_price": 700.0}, None),
        ]
        out = probe_mod.probe_asset("BNB")
    assert out["ok"] is False
    assert out["enable_recommendation"] == "block_until_source_available"
    assert "research_alternatives" in out


def test_probe_equity_uses_yfinance_expiries() -> None:
    mock_ticker = MagicMock()
    mock_ticker.options = ("2026-07-18", "2026-08-15")
    with patch.object(probe_mod, "get_asset", return_value={"data_source": "yfinance"}):
        with patch.object(probe_mod, "equity_symbol", return_value="NVDA"):
            with patch("yfinance.Ticker", return_value=mock_ticker):
                out = probe_mod.probe_equity("NVDA")
    assert out["option_expiries"] == 2
    assert out["options_available"] is True


def test_main_json_exit_code_blocked_batch() -> None:
    with patch.object(probe_mod, "probe_asset", return_value={"ok": False, "asset_id": "SOL"}):
        code = probe_mod.main(["--asset", "SOL", "--json"])
    assert code == 1
