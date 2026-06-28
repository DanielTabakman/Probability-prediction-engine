"""Asset registry (config/assets.yaml) and Deribit currency helpers."""

from __future__ import annotations

import pytest

from src.data.assets_registry import (
    asset_class,
    asset_tier,
    asset_venue,
    catalog_entry_for_asset,
    catalog_group,
    catalog_group_order,
    default_asset_id,
    deribit_currency,
    get_asset,
    is_asset_enabled,
    list_asset_ids,
    list_catalog_entries,
    list_enabled_asset_ids,
    load_assets_registry,
    registry_version,
    spread_width_for_asset,
)


def test_assets_registry_schema_v2() -> None:
    load_assets_registry.cache_clear()
    reg = load_assets_registry()
    assert registry_version() == 2
    assert reg.get("version") == 2
    assert default_asset_id() == "BTC"
    assets = reg.get("assets")
    assert isinstance(assets, dict)
    assert set(assets) >= {"BTC", "ETH", "NVDA", "SOL", "BNB", "XRP"}
    for asset_id in ("BTC", "ETH"):
        entry = assets[asset_id]
        assert entry.get("venue") == "deribit"
        assert entry.get("asset_class") == "crypto"
        assert entry.get("tier") == "core"
        assert entry.get("catalog", {}).get("group") == "crypto"
        assert entry.get("deribit_currency") == asset_id
        assert entry.get("price_unit") == "USD"
        assert isinstance(entry.get("spread_width"), (int, float))
        assert entry.get("spread_width") > 0
        assert isinstance(entry.get("label"), str) and entry["label"]
    nvda = assets["NVDA"]
    assert nvda.get("venue") == "equity"
    assert nvda.get("asset_class") == "equity_mega"
    assert nvda.get("enabled") is True
    assert nvda.get("catalog", {}).get("group") == "equity_mega"
    sol = assets["SOL"]
    assert sol.get("venue") == "bybit"
    assert sol.get("enabled") is True


def test_list_enabled_asset_ids() -> None:
    load_assets_registry.cache_clear()
    assert list_enabled_asset_ids() == ["BTC", "ETH", "NVDA", "SOL"]
    assert set(list_asset_ids()) >= {"BTC", "ETH", "NVDA", "SOL", "BNB", "XRP"}


def test_catalog_entry_shape() -> None:
    load_assets_registry.cache_clear()
    btc = catalog_entry_for_asset("BTC")
    assert btc["id"] == "BTC"
    assert btc["venue"] == "deribit"
    assert btc["asset_class"] == "crypto"
    assert btc["catalog_group"] == "crypto"
    assert btc["tier"] == "core"
    assert "label" in btc
    assert isinstance(btc["trust_notes"], list)


def test_list_catalog_entries_enabled_only() -> None:
    load_assets_registry.cache_clear()
    entries = list_catalog_entries()
    assert [e["id"] for e in entries] == ["BTC", "ETH", "NVDA", "SOL"]
    assert all(e["venue"] == "deribit" for e in entries if e["id"] in ("BTC", "ETH"))
    nvda = next(e for e in entries if e["id"] == "NVDA")
    assert nvda["venue"] == "equity"
    sol = next(e for e in entries if e["id"] == "SOL")
    assert sol["venue"] == "bybit"


def test_catalog_group_order_from_tier1_manifest() -> None:
    order = catalog_group_order()
    assert order
    assert order[0]["id"] == "crypto"
    assert any(row["id"] == "equity_mega" for row in order)


def test_deribit_currency_from_registry() -> None:
    assert deribit_currency("BTC") == "BTC"
    assert deribit_currency("ETH") == "ETH"
    assert deribit_currency(None) == "BTC"


def test_spread_width_for_asset() -> None:
    assert spread_width_for_asset("BTC") == 5000.0
    assert spread_width_for_asset("ETH") == 500.0
    load_assets_registry.cache_clear()
    assert spread_width_for_asset("SOL") == 50.0


def test_disabled_crypto_tier1_staging_rows() -> None:
    load_assets_registry.cache_clear()
    for aid in ("BNB", "XRP"):
        assert is_asset_enabled(aid) is False
        assert get_asset(aid).get("enabled") is False


def test_get_asset_unknown_raises() -> None:
    with pytest.raises(KeyError, match="unknown asset_id"):
        get_asset("DOGE")


def test_deribit_currency_rejects_equity_asset() -> None:
    load_assets_registry.cache_clear()
    with pytest.raises(ValueError, match="equity venue"):
        deribit_currency("NVDA")


def test_deribit_currency_rejects_bybit_asset() -> None:
    load_assets_registry.cache_clear()
    with pytest.raises(ValueError, match="bybit venue"):
        deribit_currency("SOL")


def test_spread_width_for_equity_registry() -> None:
    load_assets_registry.cache_clear()
    assert spread_width_for_asset("NVDA") == 25.0


def test_asset_class_and_group_helpers() -> None:
    load_assets_registry.cache_clear()
    assert asset_class("BTC") == "crypto"
    assert asset_class("NVDA") == "equity_mega"
    assert catalog_group("ETH") == "crypto"
    assert asset_tier("BTC") == "core"
    assert asset_venue("NVDA") == "equity"
    assert is_asset_enabled("BTC") is True
    assert is_asset_enabled("NVDA") is True
