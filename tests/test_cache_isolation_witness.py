"""Parametrized cross-asset cache isolation witnesses (meta infra chapter 3)."""

from __future__ import annotations

import inspect
import os
from unittest.mock import patch

import pytest

from src.data import fetch_deribit, fetch_equity_options
from src.viz.display_payload_cache import clear_display_payload_cache, get_cached_display_payload


@pytest.mark.parametrize(
    ("asset_a", "asset_b"),
    [
        ("BTC", "ETH"),
        ("ETH", "BTC"),
    ],
)
def test_display_payload_cache_isolates_asset_pair(asset_a: str, asset_b: str) -> None:
    clear_display_payload_cache()
    calls: list[str] = []

    def builder_for(asset: str):
        def _builder() -> dict:
            calls.append(asset)
            return {"asset": {"id": asset}, "spot_usd": 1.0 if asset == "BTC" else 2.0}

        return _builder

    with patch.dict(os.environ, {"PPE_DISPLAY_CACHE_ENABLED": "1", "PPE_DISPLAY_CACHE_TTL_SECONDS": "120"}):
        first = get_cached_display_payload(asset_a, "full", builder_for(asset_a))
        second = get_cached_display_payload(asset_b, "full", builder_for(asset_b))
        first_again = get_cached_display_payload(asset_a, "full", builder_for(asset_a))

    assert first["asset"]["id"] == asset_a
    assert second["asset"]["id"] == asset_b
    assert first_again == first
    assert calls == [asset_a, asset_b]


def test_deribit_instruments_diagnostic_isolated_by_currency() -> None:
    fetch_deribit.clear_deribit_instruments_diagnostics()

    with patch.object(
        fetch_deribit,
        "_deribit_public_request",
        side_effect=[
            (None, "btc failure"),
            ([{"instrument_name": "ETH-1", "strike": 1.0, "expiration_timestamp": 1}], None),
        ],
    ):
        assert fetch_deribit.fetch_deribit_options_instruments("BTC") == []
        assert fetch_deribit.last_deribit_instruments_diagnostic("BTC") == "btc failure"
        assert fetch_deribit.fetch_deribit_options_instruments("ETH") != []
        assert fetch_deribit.last_deribit_instruments_diagnostic("ETH") is None
        assert fetch_deribit.last_deribit_instruments_diagnostic("BTC") == "btc failure"


@pytest.mark.parametrize(
    "func_name",
    [
        "fetch_equity_options_instruments",
        "fetch_equity_option_expiries",
        "fetch_equity_option_book_marks",
        "fetch_equity_spot",
        "fetch_equity_forward_and_iv_for_expiry",
        "fetch_equity_option_marks_by_expiry_full",
    ],
)
def test_equity_fetch_public_api_accepts_asset_id(func_name: str) -> None:
    fn = getattr(fetch_equity_options, func_name)
    assert "asset_id" in inspect.signature(fn).parameters


@pytest.mark.parametrize(
    "func_name",
    [
        "cached_lab_spot",
        "cached_option_expiries",
        "cached_option_instruments",
        "cached_option_book_marks",
        "cached_forward_iv",
        "cached_marks_full",
    ],
)
def test_app_cache_wrappers_keyed_by_asset_id(func_name: str) -> None:
    from src.viz import app_cache

    fn = getattr(app_cache, func_name)
    assert "asset_id" in inspect.signature(fn).parameters


def test_embed_only_lab_passes_asset_id_to_cached_partials() -> None:
    import ast
    from pathlib import Path

    source = Path("src/viz/embed_only_lab.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    fn = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "_load_export_rows"
    )
    joined = ast.unparse(fn)
    assert "partial(cached_forward_iv, asset_id=aid)" in joined
    assert "partial(cached_marks_full, asset_id=aid)" in joined
    assert "cached_option_expiries(asset_id=aid)" in joined
