"""Enablement pipeline + group witness tests."""

from __future__ import annotations

from scripts import enable_asset_batch as enable_mod
from scripts import witness_asset_catalog as witness_mod


def test_witness_group_resolves_crypto_assets() -> None:
    ids = witness_mod.list_asset_ids_for_catalog_group("crypto", enabled_only=False)
    assert "BTC" in ids
    assert "ETH" in ids


def test_enable_asset_batch_dry_run_skips_enabled(monkeypatch) -> None:
    def fake_witness(args, asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0


def test_enable_asset_batch_witness_uses_group_subprocess(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_subprocess(cmd):
        calls.append(cmd)
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness_subprocess", fake_subprocess)
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0
    assert len(calls) == 1
    assert "--group" in calls[0]
    assert "crypto" in calls[0]


def test_enable_asset_batch_witness_uses_manifest_slice(monkeypatch) -> None:
    calls: list[list[str]] = []

    def fake_subprocess(cmd):
        calls.append(cmd)
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness_subprocess", fake_subprocess)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", lambda: (True, {"ok": True}))
    args = enable_mod._parse_args(
        ["--manifest-slice", "ppe_equity_universe_tier1a_v1", "--dry-run"]
    )
    ok, _ = enable_mod._run_witness(args, ["SPY"], live=False)
    assert ok is True
    assert len(calls) == 1
    assert "--manifest-slice" in calls[0]
    assert "ppe_equity_universe_tier1a_v1" in calls[0]


def test_enable_asset_batch_runs_cache_isolation_pytest(monkeypatch) -> None:
    isolation_calls: list[str] = []

    def fake_subprocess(cmd):
        return True, {"ok": True, "results": []}

    def fake_isolation():
        isolation_calls.append("run")
        return True, {"ok": True}

    monkeypatch.setattr(enable_mod, "_run_witness_subprocess", fake_subprocess)
    monkeypatch.setattr(enable_mod, "_run_cache_isolation_pytest", fake_isolation)
    monkeypatch.setattr(
        enable_mod,
        "_plan_enablement",
        lambda asset_ids: [{"asset_id": "SOL", "action": "enable", "detail": "would set enabled: true"}],
    )
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0
    assert isolation_calls == ["run"]


def test_enable_asset_batch_skip_isolation(monkeypatch) -> None:
    def fake_subprocess(cmd):
        return True, {"ok": True, "results": []}

    def fail_isolation():
        raise AssertionError("isolation should be skipped")

    monkeypatch.setattr(enable_mod, "_run_witness_subprocess", fake_subprocess)
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
    import json

    data = json.loads(capsys.readouterr().out)
    assert data["ok"] is True
    assert data["catalog_ok"] is True
    asset_ids = {row["asset_id"] for row in data["results"]}
    assert "BTC" in asset_ids
    assert "ETH" in asset_ids


def test_witness_manifest_slice_tier1a() -> None:
    ids = witness_mod.list_asset_ids_for_manifest_chapter("ppe_equity_universe_tier1a_v1")
    assert ids == ["IWM", "QQQ", "SPY"]
