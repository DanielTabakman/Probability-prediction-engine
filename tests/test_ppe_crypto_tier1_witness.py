"""Witness for ppe_deribit_crypto_tier1_v1 — SOL/BNB/XRP registry + Deribit listing gate."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.data.assets_registry import (
    deribit_currency,
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


def test_crypto_tier1_assets_merged_in_registry_disabled() -> None:
    load_assets_registry.cache_clear()
    assert set(TIER1_CRYPTO_IDS) <= set(list_asset_ids())
    for aid in TIER1_CRYPTO_IDS:
        entry = get_asset(aid)
        assert entry.get("venue") == "deribit"
        assert entry.get("enabled") is False
        assert is_asset_enabled(aid) is False
    assert set(TIER1_CRYPTO_IDS).isdisjoint(set(list_enabled_asset_ids()))


def test_crypto_tier1_manifest_chapter_matches_registry() -> None:
    load_assets_registry.cache_clear()
    manifest_ids = list_asset_ids_for_manifest_chapter("ppe_deribit_crypto_tier1_v1")
    assert manifest_ids == sorted(TIER1_CRYPTO_IDS)
    for aid in manifest_ids:
        assert aid in list_asset_ids()


def test_sol_spread_width_from_manifest() -> None:
    load_assets_registry.cache_clear()
    assert spread_width_for_asset("SOL") == 50.0
    assert deribit_currency("SOL") == "SOL"


def test_disabled_crypto_not_in_enabled_catalog_list() -> None:
    load_assets_registry.cache_clear()
    enabled = list_enabled_asset_ids()
    for aid in TIER1_CRYPTO_IDS:
        assert aid not in enabled


@pytest.mark.parametrize("asset_id", TIER1_CRYPTO_IDS)
def test_tier1_crypto_rows_document_deribit_delist(asset_id: str) -> None:
    load_assets_registry.cache_clear()
    notes = get_asset(asset_id).get("trust_notes") or []
    joined = " ".join(str(n) for n in notes).lower()
    assert "deribit" in joined
    assert "delisted" in joined or "0 live" in joined


def test_evidence_documents_deribit_skip() -> None:
    body = EVIDENCE.read_text(encoding="utf-8")
    assert "Deribit" in body
    assert "SOL" in body
    assert "skip" in body.lower() or "delisted" in body.lower()


def test_assets_yaml_tier1_crypto_enabled_false() -> None:
    data = yaml.safe_load(ASSETS_PATH.read_text(encoding="utf-8"))
    assets = data.get("assets") or {}
    for aid in TIER1_CRYPTO_IDS:
        assert assets[aid]["enabled"] is False
