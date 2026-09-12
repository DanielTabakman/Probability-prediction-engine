"""Minimal supported-asset registry for Options Market Read.

v1 enables BTC only. Add a row here to enable another asset without changing
the public endpoint or response schema.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketReadAsset:
    asset_id: str
    quote_currency: str
    enabled: bool = True


DEFAULT_ASSET_ID = "BTC"

_REGISTRY: dict[str, MarketReadAsset] = {
    "BTC": MarketReadAsset(asset_id="BTC", quote_currency="USD", enabled=True),
}


def resolve_market_read_asset(raw: str | None) -> MarketReadAsset:
    """Normalize case and resolve. Blank/omitted → default asset."""
    if raw is None or not str(raw).strip():
        return _REGISTRY[DEFAULT_ASSET_ID]
    key = str(raw).strip().upper()
    spec = _REGISTRY.get(key)
    if spec is None or not spec.enabled:
        raise KeyError(key)
    return spec
