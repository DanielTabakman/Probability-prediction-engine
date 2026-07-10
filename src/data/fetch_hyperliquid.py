"""Hyperliquid public info API helpers for exposure-only perp rails."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import requests

HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"
REQUEST_TIMEOUT_SECONDS = 10


def _normalize_coin(coin: str) -> str:
    return str(coin or "").strip().upper()


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fetch_hyperliquid_perp_context(coin: str) -> dict[str, Any]:
    """Return mark/funding context for one Hyperliquid perp coin."""
    target = _normalize_coin(coin)
    if not target:
        raise ValueError("coin is required")

    resp = requests.post(
        HYPERLIQUID_INFO_URL,
        json={"type": "metaAndAssetCtxs"},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    resp.raise_for_status()
    payload = resp.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise ValueError("unexpected Hyperliquid metaAndAssetCtxs response")
    meta, ctxs = payload[0], payload[1]
    universe = meta.get("universe") if isinstance(meta, dict) else None
    if not isinstance(universe, list) or not isinstance(ctxs, list):
        raise ValueError("unexpected Hyperliquid universe response")

    for idx, row in enumerate(universe):
        if not isinstance(row, dict):
            continue
        name = _normalize_coin(str(row.get("name") or ""))
        if name != target:
            continue
        ctx = ctxs[idx] if idx < len(ctxs) and isinstance(ctxs[idx], dict) else {}
        mark = _as_float(ctx.get("markPx"))
        funding = _as_float(ctx.get("funding"))
        if mark is None or funding is None:
            raise ValueError(f"Hyperliquid {target} missing mark/funding")
        return {
            "coin": target,
            "mark_px": mark,
            "funding": funding,
            "open_interest": _as_float(ctx.get("openInterest")),
            "as_of_utc": datetime.now(tz=UTC).isoformat(),
            "source": "hyperliquid",
        }

    raise KeyError(f"Hyperliquid coin not found: {target}")


def fetch_hyperliquid_mark(coin: str) -> float:
    return float(fetch_hyperliquid_perp_context(coin)["mark_px"])


__all__ = [
    "HYPERLIQUID_INFO_URL",
    "fetch_hyperliquid_mark",
    "fetch_hyperliquid_perp_context",
]
