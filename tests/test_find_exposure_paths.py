"""Tests for find_exposure_paths CLI and mocked orchestration."""

from __future__ import annotations

import json
import time
from typing import Any
from unittest.mock import patch

import pytest

from scripts import exposure_path_core as core_mod
from scripts import find_exposure_paths as cli_mod


def _now_ms() -> int:
    return int(time.time() * 1000)


def _nvda_expiries() -> list[dict[str, Any]]:
    now = _now_ms()
    return [
        {"expiration_timestamp": now + 90 * 86_400_000, "expiry_date_str": "2026-09-28"},
        {"expiration_timestamp": now + 300 * 86_400_000, "expiry_date_str": "2027-04-25"},
    ]


def _nvda_marks() -> dict[str, list[dict[str, Any]]]:
    return {
        "calls": [
            {"strike": 180.0, "mark_btc": 12.5, "open_interest": 500},
            {"strike": 198.0, "mark_btc": 6.0, "open_interest": 300},
            {"strike": 200.0, "mark_btc": 5.25, "open_interest": 250},
            {"strike": 220.0, "mark_btc": 2.5, "open_interest": 200},
        ],
        "puts": [
            {"strike": 171.0, "mark_btc": 8.0, "open_interest": 400},
            {"strike": 180.0, "mark_btc": 8.0, "open_interest": 350},
        ],
    }


def _btc_expiries() -> list[dict[str, Any]]:
    now = _now_ms()
    return [
        {"expiration_timestamp": now + 120 * 86_400_000, "expiry_date_str": "2026-10-28"},
    ]


def _btc_marks() -> dict[str, list[dict[str, Any]]]:
    return {
        "calls": [
            {"strike": 100_000.0, "mark_btc": 0.045},
            {"strike": 110_000.0, "mark_btc": 0.025},
            {"strike": 112_000.0, "mark_btc": 0.020},
        ],
        "puts": [],
    }


def _sol_expiries() -> list[dict[str, Any]]:
    now = _now_ms()
    return [
        {"expiration_timestamp": now + 120 * 86_400_000, "expiry_date_str": "2026-10-28"},
    ]


def _sol_marks() -> dict[str, list[dict[str, Any]]]:
    return {
        "calls": [
            {"strike": 70.0, "mark_btc": 4.5},
            {"strike": 80.0, "mark_btc": 2.5},
            {"strike": 82.0, "mark_btc": 2.0},
        ],
        "puts": [],
    }


@pytest.fixture
def nvda_mocks():
    with (
        patch.object(core_mod, "_fetch_spot", return_value=180.0),
        patch.object(core_mod, "_fetch_option_expiries", return_value=_nvda_expiries()),
        patch.object(core_mod, "_fetch_marks_for_expiry", return_value=_nvda_marks()),
    ):
        yield


@pytest.fixture
def btc_mocks():
    with (
        patch.object(core_mod, "_fetch_spot", return_value=100_000.0),
        patch.object(core_mod, "_fetch_option_expiries", return_value=_btc_expiries()),
        patch.object(core_mod, "_fetch_marks_for_expiry", return_value=_btc_marks()),
    ):
        yield


@pytest.fixture
def sol_mocks():
    with (
        patch.object(core_mod, "_fetch_spot", return_value=70.5),
        patch.object(core_mod, "_fetch_option_expiries", return_value=_sol_expiries()),
        patch.object(core_mod, "_fetch_marks_for_expiry", return_value=_sol_marks()),
    ):
        yield


def test_nvda_long_returns_live_spot_and_options(nvda_mocks) -> None:
    report = cli_mod.run_find_exposure_paths("NVDA", "long")
    assert report["kind"] == "exposure_paths"
    assert report["asset_id"] == "NVDA"
    assert report["direction"] == "long"
    assert report["status"] == "ok"
    assert report["recommendation_status"] == "path_not_recommendation"
    assert "trade recommendations" in (report.get("footer_copy") or "").lower()

    paths = report["paths"]
    assert len(paths) >= 3
    live = [p for p in paths if p["trust_badge"] == "Live"]
    assert len(live) >= 3

    spot_live = [p for p in live if p["instrument_rail"] == "spot_equity"]
    options_live = [p for p in live if p["instrument_rail"] == "listed_options"]
    assert len(spot_live) >= 1
    assert len(options_live) >= 2

    for p in paths:
        assert p["recommendation_status"] == "path_not_recommendation"
    for p in options_live:
        assert p.get("deep_link") == "/strategy-lab?asset=NVDA"


def test_btc_long_returns_live_paths(btc_mocks) -> None:
    report = cli_mod.run_find_exposure_paths("BTC", "long")
    assert report["asset_id"] == "BTC"
    assert report["status"] == "ok"
    assert report["proof_asset"] is True
    live = [p for p in report["paths"] if p["trust_badge"] == "Live"]
    assert len(live) >= 3
    spot = next(p for p in live if p["path_id"] == "crypto_spot")
    assert spot["cost_hint_usd"] == 10_000.0


def test_sol_long_returns_live_paths(sol_mocks) -> None:
    report = cli_mod.run_find_exposure_paths("SOL", "long")
    assert report["asset_id"] == "SOL"
    assert report["status"] == "ok"
    assert report["proof_asset"] is True
    live = [p for p in report["paths"] if p["trust_badge"] == "Live"]
    assert len(live) >= 3
    for path in live:
        if path["instrument_rail"] == "listed_options":
            assert path.get("deep_link") == "/strategy-lab?asset=SOL"


def test_sort_spot_before_aggressive_options(nvda_mocks) -> None:
    report = cli_mod.run_find_exposure_paths("NVDA", "long")
    path_ids = [p["path_id"] for p in report["paths"]]
    assert path_ids.index("long_stock") < path_ids.index("long_otm_call")


def test_planned_rail_has_planned_badge(nvda_mocks) -> None:
    report = cli_mod.run_find_exposure_paths("NVDA", "long")
    planned = next(p for p in report["paths"] if p["path_id"] == "sector_etf_proxy")
    assert planned["trust_badge"] == "Planned"
    assert "cost_hint_usd" not in planned


def test_insufficient_chain_when_options_missing() -> None:
    with (
        patch.object(core_mod, "_fetch_spot", return_value=180.0),
        patch.object(core_mod, "_fetch_option_expiries", return_value=[]),
        patch.object(core_mod, "_fetch_marks_for_expiry", return_value={"calls": [], "puts": []}),
    ):
        report = cli_mod.run_find_exposure_paths("NVDA", "long")
    assert report["status"] == "insufficient_chain"
    live = [p for p in report["paths"] if p["trust_badge"] == "Live"]
    assert len(live) < 3


def test_main_json_stdout(capsys, nvda_mocks) -> None:
    code = cli_mod.main(["--asset", "NVDA", "--direction", "long", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["asset_id"] == "NVDA"
    assert data["kind"] == "exposure_paths"


def test_main_horizon_flag(capsys, nvda_mocks) -> None:
    code = cli_mod.main(["--asset", "NVDA", "--direction", "long", "--horizon", "3m", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["horizon"] == "3m"
