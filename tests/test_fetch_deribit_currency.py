"""Deribit fetch passes currency to public API (multi-asset wedge)."""

from __future__ import annotations

from unittest.mock import patch

from src.data import fetch_deribit


def test_fetch_deribit_options_instruments_passes_eth_currency() -> None:
    captured: list[dict] = []

    def _fake_request(method: str, params: dict | None = None):
        if method == "get_instruments" and params:
            captured.append(dict(params))
        return [{"instrument_name": "ETH-1JAN26-3000-C"}], None

    with patch.object(fetch_deribit, "_deribit_public_request", side_effect=_fake_request):
        out = fetch_deribit.fetch_deribit_options_instruments("ETH", expired=False)

    assert len(out) == 1
    assert captured == [{"currency": "ETH", "kind": "option", "expired": "false"}]


def test_fetch_deribit_btc_wrapper_still_uses_btc() -> None:
    captured: list[dict] = []

    def _fake_request(method: str, params: dict | None = None):
        if method == "get_instruments" and params:
            captured.append(dict(params))
        return [], None

    with patch.object(fetch_deribit, "_deribit_public_request", side_effect=_fake_request):
        fetch_deribit.fetch_deribit_btc_options_instruments(expired=False)

    assert captured[0]["currency"] == "BTC"
