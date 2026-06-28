"""Tests for witness_asset_catalog.py CLI scaffold."""

from __future__ import annotations

import json

from scripts import witness_asset_catalog as witness_mod


def test_run_witness_all_enabled_mocked() -> None:
    report = witness_mod.run_witness(["BTC", "ETH", "NVDA", "SOL"], live=False)
    assert report["catalog_ok"] is True
    assert report["ok"] is True
    by_id = {r["asset_id"]: r for r in report["results"]}
    assert by_id["BTC"]["ok"] is True
    assert by_id["ETH"]["ok"] is True
    assert by_id["NVDA"]["ok"] is True
    assert by_id["NVDA"].get("skipped") is not True


def test_main_json_stdout(capsys) -> None:
    code = witness_mod.main(["--asset", "BTC", "--json"])
    assert code == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["ok"] is True
    assert data["catalog_ok"] is True


def test_main_unknown_asset_fails() -> None:
    code = witness_mod.main(["--asset", "DOGE", "--json"])
    assert code == 1
