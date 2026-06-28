"""Witness for ppe_deribit_crypto_tier1_v1 — SOL/BNB/XRP registry + venue routing."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.data.assets_registry import (
    asset_venue,
    bybit_base_coin,
    get_asset,
    is_asset_enabled,
    list_asset_ids,
    list_asset_ids_for_manifest_chapter,
    list_enabled_asset_ids,
    load_assets_registry,
    spread_width_for_asset,
)

REPO = Path(__file__).resolve().parents[1]
ASSETS_PATH = REPO / "config" / "assets.yaml"
EVIDENCE = REPO / "docs" / "SOP" / "PPE_DERIBIT_CRYPTO_TIER1_V1_EVIDENCE_STATUS.md"

TIER1_CRYPTO_IDS = ("SOL", "BNB", "XRP")


def test_crypto_tier1_assets_merged_in_registry() -> None:
    load_assets_registry.cache_clear()
    assert set(TIER1_CRYPTO_IDS) <= set(list_asset_ids())


def test_sol_enabled_on_bybit_venue() -> None:
    load_assets_registry.cache_clear()
    sol = get_asset("SOL")
    assert sol.get("venue") == "bybit"
    assert sol.get("enabled") is True
    assert is_asset_enabled("SOL") is True
    assert bybit_base_coin("SOL") == "SOL"


def test_bnb_xrp_still_disabled_deribit() -> None:
    load_assets_registry.cache_clear()
    for aid in ("BNB", "XRP"):
        entry = get_asset(aid)
        assert entry.get("venue") == "deribit"
        assert entry.get("enabled") is False
        assert is_asset_enabled(aid) is False


def test_crypto_tier1_manifest_chapter_matches_registry() -> None:
    load_assets_registry.cache_clear()
    manifest_ids = list_asset_ids_for_manifest_chapter("ppe_deribit_crypto_tier1_v1")
    assert manifest_ids == sorted(TIER1_CRYPTO_IDS)
    for aid in manifest_ids:
        assert aid in list_asset_ids()


def test_sol_spread_width_from_manifest() -> None:
    load_assets_registry.cache_clear()
    assert spread_width_for_asset("SOL") == 50.0


def test_sol_in_enabled_catalog_list() -> None:
    load_assets_registry.cache_clear()
    assert "SOL" in list_enabled_asset_ids()


def test_evidence_documents_sol_status() -> None:
    body = EVIDENCE.read_text(encoding="utf-8")
    assert "SOL" in body
    assert "Bybit" in body or "bybit" in body


def test_assets_yaml_sol_bybit_enabled() -> None:
    data = yaml.safe_load(ASSETS_PATH.read_text(encoding="utf-8"))
    sol = (data.get("assets") or {}).get("SOL") or {}
    assert sol.get("venue") == "bybit"
    assert sol.get("enabled") is True


def test_deribit_currency_rejects_bybit_asset() -> None:
    from src.data.assets_registry import deribit_currency

    load_assets_registry.cache_clear()
    with pytest.raises(ValueError, match="bybit venue"):
        deribit_currency("SOL")
