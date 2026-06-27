"""Enablement pipeline + group witness tests."""

from __future__ import annotations

from scripts import enable_asset_batch as enable_mod
from scripts import witness_asset_catalog as witness_mod


def test_witness_group_resolves_crypto_assets() -> None:
    ids = witness_mod.list_asset_ids_for_catalog_group("crypto", enabled_only=False)
    assert "BTC" in ids
    assert "ETH" in ids


def test_enable_asset_batch_dry_run_skips_enabled(monkeypatch) -> None:
    def fake_witness(asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0


def test_witness_manifest_slice_tier1a() -> None:
    ids = witness_mod.list_asset_ids_for_manifest_chapter("ppe_equity_universe_tier1a_v1")
    assert ids == ["IWM", "QQQ", "SPY"]
