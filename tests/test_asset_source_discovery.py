"""Tests for asset_source_discovery (mocked vendor scans)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.data import asset_source_discovery as disc


def test_pick_best_venue_prefers_wired_with_more_options() -> None:
    scans = [
        {"venue": "deribit", "options_available": True, "options_count": 0, "wired": True},
        {"venue": "bybit", "options_available": True, "options_count": 318, "wired": True},
    ]
    best = disc.pick_best_venue(scans)
    assert best is not None
    assert best["venue"] == "bybit"


def test_pick_best_venue_unwired_live_when_no_wired() -> None:
    scans = [
        {"venue": "deribit", "options_available": False, "options_count": 0, "wired": True},
        {"venue": "bybit", "options_available": True, "options_count": 100, "wired": False},
    ]
    best = disc.pick_best_venue(scans)
    assert best is not None
    assert best["venue"] == "bybit"


def test_resolve_next_action_build_adapter_when_unwired() -> None:
    best = {
        "venue": "bybit",
        "options_count": 318,
        "wired": False,
        "fetch_module": "src.data.fetch_bybit_options",
    }
    action, steps = disc.resolve_next_action(
        asset_id="SOL",
        asset_kind="crypto",
        best=best,
        registry_entry={"venue": "deribit", "enabled": False},
        in_registry=True,
    )
    assert action == "build_adapter"
    assert "fetch_bybit_options" in steps[1]


def test_resolve_next_action_switch_venue() -> None:
    best = {
        "venue": "bybit",
        "options_count": 318,
        "wired": True,
        "registry_fields": {"bybit_base_coin": "SOL"},
    }
    action, _ = disc.resolve_next_action(
        asset_id="SOL",
        asset_kind="crypto",
        best=best,
        registry_entry={"venue": "deribit", "enabled": False},
        in_registry=True,
    )
    assert action == "switch_venue_and_enable"


def test_resolve_next_action_enable_existing_row() -> None:
    best = {"venue": "deribit", "options_count": 50, "wired": True}
    action, _ = disc.resolve_next_action(
        asset_id="BTC",
        asset_kind="crypto",
        best=best,
        registry_entry={"venue": "deribit", "enabled": False},
        in_registry=True,
    )
    assert action == "enable_existing_row"


def test_discover_asset_source_scans_deribit_then_bybit() -> None:
    with patch.object(disc, "scan_deribit_crypto") as mock_d:
        with patch.object(disc, "scan_bybit_crypto") as mock_b:
            mock_d.return_value = {
                "venue": "deribit",
                "options_count": 0,
                "options_available": False,
                "wired": True,
            }
            mock_b.return_value = {
                "venue": "bybit",
                "options_count": 318,
                "options_available": True,
                "wired": True,
                "fetch_module": "src.data.fetch_bybit_options",
                "registry_fields": {"bybit_base_coin": "SOL"},
            }
            report = disc.discover_asset_source(
                "SOL",
                registry_entry={"venue": "deribit", "enabled": False},
                in_registry=True,
            )
    assert report["ok"] is True
    assert report["recommended_venue"] == "bybit"
    assert report["next_action"] == "switch_venue_and_enable"
    mock_d.assert_called_once_with("SOL")
    mock_b.assert_called_once_with("SOL")


def test_discover_main_json_exit_enable_path() -> None:
    from scripts import discover_asset_data_source as cli

    fake_report = {
        "ok": True,
        "next_action": "enable_existing_row",
        "scan_results": [],
    }
    with patch.object(cli, "discover_asset_source", return_value=fake_report):
        code = cli.main(["--asset", "BTC", "--json"])
    assert code == 0
