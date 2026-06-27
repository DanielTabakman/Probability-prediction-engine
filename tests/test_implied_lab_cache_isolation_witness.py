"""Cross-asset cache isolation witnesses (meta infra)."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.viz.display_payload_cache import clear_display_payload_cache, get_cached_display_payload


def test_display_payload_cache_isolates_assets() -> None:
    clear_display_payload_cache()
    calls: list[str] = []

    def builder_btc() -> dict:
        calls.append("BTC")
        return {"asset": {"id": "BTC"}, "spot_usd": 100_000.0}

    def builder_eth() -> dict:
        calls.append("ETH")
        return {"asset": {"id": "ETH"}, "spot_usd": 3_500.0}

    with patch.dict(os.environ, {"PPE_DISPLAY_CACHE_ENABLED": "1", "PPE_DISPLAY_CACHE_TTL_SECONDS": "120"}):
        btc = get_cached_display_payload("BTC", "full", builder_btc)
        eth = get_cached_display_payload("ETH", "full", builder_eth)
        btc_again = get_cached_display_payload("BTC", "full", builder_btc)

    assert btc["asset"]["id"] == "BTC"
    assert eth["asset"]["id"] == "ETH"
    assert btc_again == btc
    assert calls == ["BTC", "ETH"]


def test_cached_option_expiries_cache_key_includes_asset_id(monkeypatch: pytest.MonkeyPatch) -> None:
    """Streamlit cache functions must accept asset_id (regression guard)."""
    import inspect

    from src.viz import app_cache

    sig = inspect.signature(app_cache.cached_option_expiries)
    assert "asset_id" in sig.parameters
    sig_inst = inspect.signature(app_cache.cached_option_instruments)
    assert "asset_id" in sig_inst.parameters
    sig_marks = inspect.signature(app_cache.cached_option_book_marks)
    assert "asset_id" in sig_marks.parameters
