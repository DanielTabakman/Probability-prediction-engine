"""TTL cache for live display payloads."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from src.viz.display_payload_cache import (
    clear_display_payload_cache,
    get_cached_display_payload,
)


def test_cache_returns_same_payload_within_ttl() -> None:
    clear_display_payload_cache()
    calls = {"n": 0}

    def builder() -> dict:
        calls["n"] += 1
        return {"kind": "distribution_display_boundary", "n": calls["n"]}

    with patch.dict(os.environ, {"PPE_DISPLAY_CACHE_ENABLED": "1", "PPE_DISPLAY_CACHE_TTL_SECONDS": "60"}):
        first = get_cached_display_payload("BTC", "full", builder)
        second = get_cached_display_payload("BTC", "full", builder)

    assert first == second == {"kind": "distribution_display_boundary", "n": 1}
    assert calls["n"] == 1


def test_cache_keys_by_asset_and_depth() -> None:
    clear_display_payload_cache()
    calls: list[tuple[str, str]] = []

    def builder(asset_id: str, depth: str):
        def _inner() -> dict:
            calls.append((asset_id, depth))
            return {"asset_id": asset_id, "depth": depth}

        return _inner

    with patch.dict(os.environ, {"PPE_DISPLAY_CACHE_ENABLED": "1", "PPE_DISPLAY_CACHE_TTL_SECONDS": "60"}):
        get_cached_display_payload("BTC", "full", builder("BTC", "full"))
        get_cached_display_payload("ETH", "full", builder("ETH", "full"))
        get_cached_display_payload("BTC", "summary", builder("BTC", "summary"))
        get_cached_display_payload("BTC", "full", builder("BTC", "full"))

    assert calls == [("BTC", "full"), ("ETH", "full"), ("BTC", "summary")]


def test_cache_disabled_rebuilds_each_time() -> None:
    clear_display_payload_cache()
    calls = {"n": 0}

    def builder() -> dict:
        calls["n"] += 1
        return {"n": calls["n"]}

    with patch.dict(os.environ, {"PPE_DISPLAY_CACHE_ENABLED": "0"}):
        get_cached_display_payload("BTC", "full", builder)
        get_cached_display_payload("BTC", "full", builder)

    assert calls["n"] == 2
