"""Enablement pipeline + group witness tests."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import enable_asset_batch as enable_mod
from scripts import gate_asset_enablement_diff as gate_mod
from scripts import witness_asset_catalog as witness_mod

REPO = Path(__file__).resolve().parents[1]


def test_witness_group_resolves_crypto_assets() -> None:
    ids = witness_mod.list_asset_ids_for_catalog_group("crypto", enabled_only=False)
    assert "BTC" in ids
    assert "ETH" in ids


def test_enable_asset_batch_dry_run_skips_enabled(monkeypatch) -> None:
    def fake_witness(_args, asset_ids, *, live=False):
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0


def test_enable_asset_batch_witnesses_to_enable_list(monkeypatch) -> None:
    seen: list[list[str]] = []

    def fake_witness(_args, asset_ids, *, live=False):
        seen.append(list(asset_ids))
        return True, {"ok": True, "results": []}

    monkeypatch.setattr(enable_mod, "_run_witness", fake_witness)
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
    assert enable_mod.main(["--group", "crypto", "--dry-run", "--json"]) == 0


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


def test_newly_enabled_asset_ids_detects_flip() -> None:
    assert gate_mod.newly_enabled_asset_ids({"SOL": False}, {"SOL": True}) == ["SOL"]


def test_gate_skips_when_assets_yaml_not_changed() -> None:
    assert gate_mod.main(["--changed-file", "docs/SOP/HANDOFF.md"]) == 0


def test_gate_passes_no_new_enablements(monkeypatch) -> None:
    yaml_text = "version: 2\nassets:\n  BTC:\n    enabled: true\n"
    monkeypatch.setattr(gate_mod, "_git_show", lambda repo, ref, rel: yaml_text)
    result = gate_mod.evaluate_enablement_diff(REPO, base_ref="origin/main", head_ref="HEAD")
    assert result["ok"] is True


def test_gate_passes_with_witness_artifact(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts" / "enablement"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "batch.json").write_text(
        json.dumps({"witness_ok": True, "asset_ids": ["SPY"]}),
        encoding="utf-8",
    )
    assert gate_mod._witness_artifact_ok(
        tmp_path, ["artifacts/enablement/batch.json"], ["SPY"]
    )


def test_pre_enable_witness_validates_disabled_sol() -> None:
    report = witness_mod.run_witness(["SOL"], live=False, pre_enable=True)
    assert report["ok"] is True
    assert report["results"][0]["asset_id"] == "SOL"
    assert not report["results"][0].get("skipped")
