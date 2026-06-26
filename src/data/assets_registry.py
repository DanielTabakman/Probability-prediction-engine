"""Load tradeable asset registry from config/assets.yaml (Deribit crypto wedge v1)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_PATH = _REPO_ROOT / "config" / "assets.yaml"


def _normalize_asset_id(asset_id: str) -> str:
    return str(asset_id or "").strip().upper()


@lru_cache(maxsize=1)
def load_assets_registry() -> dict[str, Any]:
    with ASSETS_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("assets registry root must be a mapping")
    return data


def default_asset_id() -> str:
    reg = load_assets_registry()
    asset_id = _normalize_asset_id(str(reg.get("default_asset_id") or "BTC"))
    if not asset_id:
        return "BTC"
    return asset_id


def get_asset(asset_id: str | None = None) -> dict[str, Any]:
    reg = load_assets_registry()
    assets = reg.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("assets registry must define assets mapping")
    aid = _normalize_asset_id(asset_id or default_asset_id())
    entry = assets.get(aid)
    if not isinstance(entry, dict):
        raise KeyError(f"unknown asset_id: {aid}")
    return entry


def deribit_currency(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    currency = _normalize_asset_id(str(entry.get("deribit_currency") or asset_id or default_asset_id()))
    if not currency:
        raise ValueError(f"asset {asset_id!r} missing deribit_currency")
    return currency


def spread_width_for_asset(asset_id: str | None = None) -> float:
    entry = get_asset(asset_id)
    width = entry.get("spread_width")
    if width is None:
        return 5000.0 if deribit_currency(asset_id) == "BTC" else 500.0
    return float(width)
