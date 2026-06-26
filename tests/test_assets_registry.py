"""Asset registry (config/assets.yaml) and Deribit currency helpers."""

from __future__ import annotations

import pytest

from src.data.assets_registry import (
    default_asset_id,
    deribit_currency,
    get_asset,
    load_assets_registry,
    spread_width_for_asset,
)


def test_assets_registry_schema() -> None:
    reg = load_assets_registry()
    assert reg.get("version") == 1
    assert default_asset_id() == "BTC"
    assets = reg.get("assets")
    assert isinstance(assets, dict)
    assert set(assets) >= {"BTC", "ETH"}
    for asset_id in ("BTC", "ETH"):
        entry = assets[asset_id]
        assert entry.get("venue") == "deribit"
        assert entry.get("deribit_currency") == asset_id
        assert entry.get("price_unit") == "USD"
        assert isinstance(entry.get("spread_width"), (int, float))
        assert entry.get("spread_width") > 0
        assert isinstance(entry.get("label"), str) and entry["label"]


def test_deribit_currency_from_registry() -> None:
    assert deribit_currency("BTC") == "BTC"
    assert deribit_currency("ETH") == "ETH"
    assert deribit_currency(None) == "BTC"


def test_spread_width_for_asset() -> None:
    assert spread_width_for_asset("BTC") == 5000.0
    assert spread_width_for_asset("ETH") == 500.0


def test_get_asset_unknown_raises() -> None:
    with pytest.raises(KeyError, match="unknown asset_id"):
        get_asset("DOGE")
