"""Tests for Options Horizon chart payload builder."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd

from src.viz.horizon_chart_payload import build_horizon_chart_payload


def test_build_horizon_chart_payload_shape() -> None:
    hist = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(["2026-06-01", "2026-06-02"], utc=True),
            "close": [100_000.0, 101_000.0],
            "volume": [1000.0, 1100.0],
            "symbol": ["BTC-USD", "BTC-USD"],
            "asset": ["bitcoin", "bitcoin"],
        }
    )

    with (
        patch("src.viz.horizon_chart_payload.fetch_deribit_btc_index", return_value=101_000.0),
        patch(
            "src.viz.horizon_chart_payload.fetch_deribit_btc_option_expiries",
            return_value=[{"expiry_ts": 1893456000000, "expiry_date_str": "2030-01-01"}],
        ),
        patch(
            "src.viz.horizon_chart_payload.fetch_deribit_btc_futures_forward_curve",
            return_value=[],
        ),
        patch(
            "src.viz.horizon_chart_payload.fetch_deribit_forward_and_iv_for_expiry",
            return_value={"forward": 101_000.0, "atm_iv": 0.5},
        ),
        patch(
            "src.viz.horizon_chart_payload.fetch_deribit_btc_option_marks_by_expiry_full",
            return_value={"calls": [], "puts": []},
        ),
        patch("src.viz.horizon_chart_payload.fetch_yahoo_prices", return_value=hist),
        patch("src.viz.horizon_chart_payload.archive_meta", return_value={"available_days": 0}),
    ):
        payload = build_horizon_chart_payload(expiry_ts=1893456000000)

    assert payload["kind"] == "horizon_chart"
    assert len(payload["historical"]["series"]) == 2
    assert payload["implied"] is not None
    assert payload["meta"]["simulation_only"] is True
