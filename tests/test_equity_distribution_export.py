"""Tests for equity forward/IV, trust flags, and distribution export rows."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd

from src.data import fetch_equity_options
from src.data.assets_registry import contract_multiplier, load_assets_registry
from src.data.equity_distribution_export import build_equity_distribution_export_rows


def _mock_chain_with_iv() -> MagicMock:
    calls = pd.DataFrame(
        [
            {
                "contractSymbol": "NVDA260718C00180000",
                "strike": 180.0,
                "lastPrice": 12.5,
                "impliedVolatility": 0.42,
                "openInterest": 500,
            },
            {
                "contractSymbol": "NVDA260718C00200000",
                "strike": 200.0,
                "lastPrice": 5.25,
                "impliedVolatility": 0.38,
                "openInterest": 80,
            },
        ]
    )
    puts = pd.DataFrame(
        [{"contractSymbol": "NVDA260718P00180000", "strike": 180.0, "lastPrice": 8.0, "openInterest": 10}]
    )
    chain = MagicMock()
    chain.calls = calls
    chain.puts = puts
    return chain


@patch.object(fetch_equity_options.yf, "Ticker")
def test_fetch_equity_forward_and_iv_uses_spot_and_atm_iv(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.return_value = _mock_chain_with_iv()
    mock_ticker.return_value = tk

    expiry_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")
    out = fetch_equity_options.fetch_equity_forward_and_iv_for_expiry(expiry_ts, 185.0, symbol="NVDA")
    assert out is not None
    assert out["forward"] == 185.0
    assert out["atm_iv"] == 0.42


@patch.object(fetch_equity_options.yf, "Ticker")
def test_fetch_equity_option_marks_by_expiry_full(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.return_value = _mock_chain_with_iv()
    mock_ticker.return_value = tk

    expiry_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")
    full = fetch_equity_options.fetch_equity_option_marks_by_expiry_full(expiry_ts, "NVDA")
    assert len(full["calls"]) == 2
    assert full["calls"][0]["open_interest"] == 500
    assert len(full["puts"]) == 1


def test_assess_equity_chain_trust_flags() -> None:
    thin = fetch_equity_options.assess_equity_chain_trust([{"open_interest": 1}, {"open_interest": 2}])
    assert "insufficient_marks" in thin["trust_flags"]
    assert "dividend_caveat_unmodeled" in thin["trust_flags"]
    assert thin["trust_ok"] is False

    ok = fetch_equity_options.assess_equity_chain_trust(
        [{"open_interest": 200}, {"open_interest": 300}, {"open_interest": 400}]
    )
    assert ok["trust_ok"] is True
    assert "thin_open_interest" not in ok["trust_flags"]


def test_contract_multiplier_nvda() -> None:
    load_assets_registry.cache_clear()
    assert contract_multiplier("NVDA") == 100.0


def test_build_equity_distribution_export_rows_skipped_bl() -> None:
    exp_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 185.0, "atm_iv": 0.4}

    def _marks(_exp: int) -> dict:
        return {"calls": []}

    rows = build_equity_distribution_export_rows(
        as_of_utc="2026-06-26T12:00:00+00:00",
        spot_usd=185.0,
        expiries=[{"expiry_date_str": "2026-07-18", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
        asset_id="NVDA",
    )
    assert len(rows) == 2
    assert rows[0]["asset"] == "NVDA"
    assert rows[0]["distribution"] == "lognormal_reference"
    assert "dividend_caveat_unmodeled" in rows[0]["bl_status"]
    assert rows[1]["bl_status"].startswith("skipped:insufficient_marks")


def test_build_equity_distribution_export_rows_computed_bl() -> None:
    exp_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")

    def _fwd_iv(_exp: int, _spot: float) -> dict:
        return {"forward": 185.0, "atm_iv": 0.4}

    def _marks(_exp: int) -> dict:
        return {
            "calls": [
                {"strike": 170.0, "mark_btc": 20.0, "open_interest": 500},
                {"strike": 185.0, "mark_btc": 12.0, "open_interest": 800},
                {"strike": 200.0, "mark_btc": 6.0, "open_interest": 600},
            ]
        }

    rows = build_equity_distribution_export_rows(
        as_of_utc="2026-06-26T12:00:00+00:00",
        spot_usd=185.0,
        expiries=[{"expiry_date_str": "2026-07-18", "expiry_ts": exp_ts}],
        forward_iv_fn=_fwd_iv,
        marks_full_fn=_marks,
        now_ms=exp_ts - 86400000 * 30,
        asset_id="NVDA",
    )
    bl_row = rows[1]
    assert bl_row["distribution"] == "market_implied_bl"
    assert bl_row["bl_status"].startswith("computed")
    assert bl_row["mean_usd"]
