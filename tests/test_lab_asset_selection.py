"""Tests for registry-driven Streamlit lab asset selection."""

from __future__ import annotations

from src.data.assets_registry import default_asset_id, load_assets_registry
from src.viz.lab_asset_selection import (
    LAB_ASSET_QUERY_PARAM,
    display_asset_meta,
    lab_asset_id_from_environ,
    list_selectable_lab_asset_ids,
    normalize_lab_asset_id,
)


def test_list_selectable_lab_asset_ids_uses_enabled_registry_only() -> None:
    load_assets_registry.cache_clear()
    ids = list_selectable_lab_asset_ids()
    assert ids == [
        "BTC",
        "ETH",
        "SOL",
        "IWM",
        "QQQ",
        "SPY",
        "AAPL",
        "AMZN",
        "GOOGL",
        "META",
        "MSFT",
        "NVDA",
        "USO",
    ]
    assert "NVDA" in ids
    assert all(asset_id in ids for asset_id in ("AAPL", "MSFT", "AMZN", "GOOGL", "META"))


def test_normalize_lab_asset_id_rejects_disabled_and_unknown() -> None:
    load_assets_registry.cache_clear()
    assert normalize_lab_asset_id("ETH") == "ETH"
    assert normalize_lab_asset_id("NVDA") == "NVDA"
    assert normalize_lab_asset_id("AAPL") == "AAPL"
    assert normalize_lab_asset_id("MSFT") == "MSFT"
    assert normalize_lab_asset_id("AMZN") == "AMZN"
    assert normalize_lab_asset_id("GOOGL") == "GOOGL"
    assert normalize_lab_asset_id("META") == "META"
    assert normalize_lab_asset_id("SOL") == "SOL"
    assert normalize_lab_asset_id("USO") == "USO"
    default = default_asset_id()
    assert normalize_lab_asset_id("DOGE") == default
    assert normalize_lab_asset_id(None) == default


def test_lab_asset_id_from_environ_query_param() -> None:
    load_assets_registry.cache_clear()
    environ = {"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=ETH"}
    assert lab_asset_id_from_environ(environ) == "ETH"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=NVDA"}) == "NVDA"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=AAPL"}) == "AAPL"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=MSFT"}) == "MSFT"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=AMZN"}) == "AMZN"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=GOOGL"}) == "GOOGL"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=META"}) == "META"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=USO"}) == "USO"


def test_display_asset_meta_labels() -> None:
    load_assets_registry.cache_clear()
    meta = display_asset_meta("BTC")
    assert meta["id"] == "BTC"
    assert meta["label"] == "BTC options"
    assert meta["price_axis_label"] == "BTC price at expiry"
