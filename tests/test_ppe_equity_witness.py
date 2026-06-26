"""Witness slice PPE-Equity-Witness-Slice007 — NVDA equity path pytest + yfinance flake."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.msos_production_demo_witness import MULTI_ASSET_DISPLAY_PROBE_IDS
from src.data import fetch_equity_options

REPO = Path(__file__).resolve().parents[1]
SOP = REPO / "docs" / "SOP"
EVIDENCE = SOP / "PPE_EQUITY_OPTIONS_V1_EVIDENCE_STATUS.md"


CLOSED_SLICES = (
    "PPE-Equity-Control-Slice001",
    "PPE-Equity-Core-Slice002",
    "PPE-Equity-Core-Slice003",
    "PPE-Equity-UI-Slice004",
    "PPE-Equity-Product-Slice005",
    "PPE-Equity-Platform-Slice006",
)


def test_equity_witness_evidence_doc_lists_closed_product_slices() -> None:
    body = EVIDENCE.read_text(encoding="utf-8")
    for slice_id in CLOSED_SLICES:
        row = body.split(slice_id, 1)[1].split("\n", 1)[0]
        assert "**CLOSED**" in row, f"{slice_id} not marked CLOSED in evidence doc"


def test_equity_witness_slice007_closed_in_evidence_doc() -> None:
    body = EVIDENCE.read_text(encoding="utf-8")
    row = body.split("PPE-Equity-Witness-Slice007", 1)[1].split("\n", 1)[0]
    assert "**CLOSED**" in row


def test_production_demo_witness_probes_nvda() -> None:
    assert "NVDA" in MULTI_ASSET_DISPLAY_PROBE_IDS


def test_equity_product_test_modules_importable() -> None:
    pytest.importorskip("yfinance")
    import tests.test_fetch_equity_options  # noqa: F401
    import tests.test_equity_distribution_export  # noqa: F401
    import tests.test_msos_production_demo_witness  # noqa: F401
    import tests.test_msos_web_strategy_lab  # noqa: F401


@patch.object(fetch_equity_options.yf, "Ticker")
def test_yfinance_empty_options_returns_empty_instruments(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = []
    mock_ticker.return_value = tk
    assert fetch_equity_options.fetch_equity_options_instruments("NVDA") == []
    assert fetch_equity_options.fetch_equity_option_expiries("NVDA") == []
    assert fetch_equity_options.fetch_equity_option_book_marks("NVDA") == {}


@patch.object(fetch_equity_options.yf, "Ticker")
def test_yfinance_option_chain_failure_returns_empty_marks(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.options = ["2026-07-18"]
    tk.option_chain.side_effect = RuntimeError("yfinance flake")
    mock_ticker.return_value = tk
    expiry_ts = fetch_equity_options._expiry_str_to_ms("2026-07-18")
    assert fetch_equity_options.fetch_equity_option_marks_by_expiry(expiry_ts, "NVDA") == []
    assert fetch_equity_options.fetch_equity_forward_and_iv_for_expiry(expiry_ts, 180.0, symbol="NVDA") is None


@patch.object(fetch_equity_options.yf, "Ticker")
def test_yfinance_spot_failure_returns_none(mock_ticker: MagicMock) -> None:
    tk = MagicMock()
    tk.fast_info = {}
    tk.history.side_effect = RuntimeError("network flake")
    mock_ticker.return_value = tk
    assert fetch_equity_options.fetch_equity_spot("NVDA") is None


def test_equity_phase_plan_closeout_points_at_tradeable_universe() -> None:
    plan = json.loads((SOP / "PHASE_PLANS" / "ppe_equity_options_v1_relay.json").read_text(encoding="utf-8"))
    closeout = plan["slices"][-1].get("closeout") or {}
    assert closeout.get("nextSelectionDoc") == "docs/SOP/POST_PPE_TRADEABLE_UNIVERSE_V1_SELECTION.md"
