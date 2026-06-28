"""Enablement pipeline + group witness tests."""

from __future__ import annotations

import json

from scripts import enable_asset_batch as enable_mod
from scripts import witness_asset_catalog as witness_mod


def test_witness_group_resolves_crypto_assets() -> None:
    ids = witness_mod.list_asset_ids_for_catalog_group("crypto", enabled_only=False)
    assert "BTC" in ids
    assert "ETH" in ids


def test_enable_asset_batch_dry_run_skips_enabled(monkeypatch) -> None:
    def fake_witness(_args, asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", lambda: (True, {"ok": True}))
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0


def test_enable_asset_batch_witnesses_to_enable_list(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_witness(_args, asset_ids, *, live=False):
        seen.append(list(asset_ids))
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", lambda: (True, {"ok": True}))
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0
    assert len(seen) == 1
    assert set(seen[0]) == {"BNB", "SOL", "XRP"}


def test_witness_pre_enable_disabled_staging_asset() -> None:
    report = witness_mod.run_witness(["SOL"], live=False, pre_enable=True)
    assert report["ok"] is True
    row = report["results"][0]
    assert row["asset_id"] == "SOL"
    assert row["ok"] is True
    assert not row.get("skipped")


def test_enable_dry_run_witnesses_disabled_crypto_batch() -> None:
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--skip-isolation", "--json"]) == 0


def test_enable_asset_batch_manifest_slice_witness(monkeypatch) -> None:
    def fake_witness(_args, asset_ids, *, live=False):
        assert asset_ids == ["SPY"]
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    args = enable_mod._parse_args(
        ["--manifest-slice", "ppe_equity_universe_tier1a_v1", "--dry-run"]
    )
    ok, _ = enable_mod._run_witness(args, ["SPY"], live=False)
    assert ok is True


def test_enable_asset_batch_runs_cache_isolation_pytest(monkeypatch) -> None:
    isolation_calls: list[str] = []

    def fake_witness(_args, asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    def fake_isolation():
        isolation_calls.append("run")
        return True, {"ok": True}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", fake_isolation)
    monkeypatch.setattr(
        enable_mod,
        "_plan_enablement",
        lambda asset_ids: [{"asset_id": "SOL", "action": "enable", "detail": "would set enabled: true"}],
    )
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0
    assert isolation_calls == ["run"]


def test_enable_asset_batch_skip_isolation(monkeypatch) -> None:
    def fake_witness(_args, asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    def fail_isolation():
        raise AssertionError("isolation should be skipped")

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", fail_isolation)
    monkeypatch.setattr(
        enable_mod,
        "_plan_enablement",
        lambda asset_ids: [{"asset_id": "SOL", "action": "enable", "detail": "would set enabled: true"}],
    )
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--skip-isolation", "--json"]) == 0


def test_witness_group_cli_json(capsys) -> None:
    code = witness_mod.main(["--group", "crypto", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["catalog_ok"] is True
    asset_ids = {row["asset_id"] for row in data["results"]}
    assert "BTC" in asset_ids
    assert "ETH" in asset_ids


def test_witness_group_pre_enable_cli_json(capsys) -> None:
    code = witness_mod.main(["--group", "crypto", "--pre-enable", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    by_id = {row["asset_id"]: row for row in data["results"]}
    assert by_id["SOL"]["ok"] is True
    assert not by_id["SOL"].get("skipped")


def test_witness_manifest_slice_tier1a() -> None:
    ids = witness_mod.list_asset_ids_for_manifest_chapter("ppe_equity_universe_tier1a_v1")
    assert ids == ["IWM", "QQQ", "SPY"]
