"""Tests for registry-driven Streamlit lab asset selection."""

from __future__ import annotations

from src.data.assets_registry import load_assets_registry
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
    assert ids == ["BTC", "ETH", "SOL", "NVDA"]
    assert "NVDA" in ids


def test_normalize_lab_asset_id_rejects_disabled_and_unknown() -> None:
    load_assets_registry.cache_clear()
    assert normalize_lab_asset_id("ETH") == "ETH"
    assert normalize_lab_asset_id("NVDA") == "NVDA"
    assert normalize_lab_asset_id("SOL") == "SOL"
    assert normalize_lab_asset_id("DOGE") == "BTC"
    assert normalize_lab_asset_id(None) == "BTC"


def test_lab_asset_id_from_environ_query_param() -> None:
    load_assets_registry.cache_clear()
    environ = {"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=ETH"}
    assert lab_asset_id_from_environ(environ) == "ETH"
    assert lab_asset_id_from_environ({"QUERY_STRING": f"{LAB_ASSET_QUERY_PARAM}=NVDA"}) == "NVDA"


def test_display_asset_meta_labels() -> None:
    load_assets_registry.cache_clear()
    meta = display_asset_meta("BTC")
    assert meta["id"] == "BTC"
    assert meta["label"] == "BTC options"
    assert meta["price_axis_label"] == "BTC price at expiry"
