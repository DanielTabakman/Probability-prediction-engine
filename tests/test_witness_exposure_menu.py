"""Tests for witness_exposure_menu.py."""

from __future__ import annotations

from scripts import witness_exposure_menu as witness_mod


def test_equity_index_witness_mocked_long() -> None:
    report = witness_mod.run_witness(["SPY", "QQQ", "IWM"], direction="long", live=False)
    assert report["ok"] is True
    assert len(report["results"]) == 3
    for row in report["results"]:
        assert row["binding_ok"] is True
        assert row["live_path_count"] >= 2
        assert row["section_count"] >= 3
        assert "sector_etf_proxy" not in row["path_ids"]


def test_nvda_short_witness_includes_put_path() -> None:
    report = witness_mod.run_witness(["NVDA"], direction="short", live=False)
    row = report["results"][0]
    assert row["ok"] is True
    assert "long_put_leaps" in row["path_ids"]
    assert "cash_secured_put" in row["path_ids"]
