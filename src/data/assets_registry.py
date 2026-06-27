"""Load tradeable asset registry from config/assets.yaml (registry v2)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
ASSETS_PATH = _REPO_ROOT / "config" / "assets.yaml"
TIER1_MANIFEST_PATH = _REPO_ROOT / "config" / "assets_tier1_manifest.yaml"


def _normalize_asset_id(asset_id: str) -> str:
    return str(asset_id or "").strip().upper()


@lru_cache(maxsize=1)
def load_assets_registry() -> dict[str, Any]:
    with ASSETS_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("assets registry root must be a mapping")
    return data


@lru_cache(maxsize=1)
def load_tier1_manifest() -> dict[str, Any]:
    if not TIER1_MANIFEST_PATH.is_file():
        return {}
    with TIER1_MANIFEST_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def registry_version() -> int:
    reg = load_assets_registry()
    try:
        return int(reg.get("version") or 1)
    except (TypeError, ValueError):
        return 1


def default_asset_id() -> str:
    reg = load_assets_registry()
    asset_id = _normalize_asset_id(str(reg.get("default_asset_id") or "BTC"))
    if not asset_id:
        return "BTC"
    return asset_id


def _assets_mapping() -> dict[str, Any]:
    reg = load_assets_registry()
    assets = reg.get("assets")
    if not isinstance(assets, dict):
        raise ValueError("assets registry must define assets mapping")
    return assets


def list_asset_ids() -> list[str]:
    return sorted(_normalize_asset_id(aid) for aid in _assets_mapping())


def get_asset(asset_id: str | None = None) -> dict[str, Any]:
    aid = _normalize_asset_id(asset_id or default_asset_id())
    entry = _assets_mapping().get(aid)
    if not isinstance(entry, dict):
        raise KeyError(f"unknown asset_id: {aid}")
    return entry


def asset_venue(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    return str(entry.get("venue") or "deribit").strip().lower()


def is_asset_enabled(asset_id: str | None = None) -> bool:
    entry = get_asset(asset_id)
    if "enabled" in entry:
        return entry.get("enabled") is True
    if asset_venue(asset_id) == "equity":
        return False
    return True


def list_enabled_asset_ids() -> list[str]:
    return [aid for aid in list_asset_ids() if is_asset_enabled(aid)]


def asset_class(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    raw = entry.get("asset_class")
    if raw:
        return str(raw).strip().lower()
    if asset_venue(asset_id) == "equity":
        return "equity_mega"
    return "crypto"


def asset_tier(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    return str(entry.get("tier") or "core").strip().lower()


def catalog_group(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    catalog = entry.get("catalog")
    if isinstance(catalog, dict) and catalog.get("group"):
        return str(catalog["group"]).strip().lower()
    legacy = entry.get("catalog_group")
    if legacy:
        return str(legacy).strip().lower()
    return asset_class(asset_id)


def catalog_group_order() -> list[dict[str, str]]:
    manifest = load_tier1_manifest()
    catalog = manifest.get("catalog")
    if not isinstance(catalog, dict):
        return []
    order = catalog.get("group_order")
    if not isinstance(order, list):
        return []
    out: list[dict[str, str]] = []
    for row in order:
        if not isinstance(row, dict):
            continue
        gid = str(row.get("id") or "").strip()
        label = str(row.get("label") or gid).strip()
        if gid:
            out.append({"id": gid, "label": label})
    return out


def catalog_entry_for_asset(asset_id: str) -> dict[str, Any]:
    aid = _normalize_asset_id(asset_id)
    entry = get_asset(aid)
    trust = entry.get("trust_notes")
    notes = [str(n) for n in trust] if isinstance(trust, list) else []
    return {
        "id": aid,
        "label": str(entry.get("label") or f"{aid} options"),
        "asset_class": asset_class(aid),
        "venue": asset_venue(aid),
        "tier": asset_tier(aid),
        "catalog_group": catalog_group(aid),
        "price_unit": str(entry.get("price_unit") or "USD"),
        "trust_notes": notes,
    }


def list_catalog_entries(*, enabled_only: bool = True) -> list[dict[str, Any]]:
    """Enabled assets with catalog picker metadata (no prices or curves)."""
    ids = list_enabled_asset_ids() if enabled_only else list_asset_ids()
    return [catalog_entry_for_asset(aid) for aid in ids]


def list_asset_ids_for_catalog_group(group_id: str, *, enabled_only: bool = False) -> list[str]:
    """Asset ids whose catalog.group matches (e.g. crypto, equity_index)."""
    gid = str(group_id or "").strip().lower()
    if not gid:
        return []
    ids = list_enabled_asset_ids() if enabled_only else list_asset_ids()
    return sorted(aid for aid in ids if catalog_group(aid) == gid)


def list_asset_ids_for_manifest_chapter(chapter_id: str) -> list[str]:
    """Asset ids declared for a tier-1 manifest chapter (may be disabled in registry)."""
    cid = str(chapter_id or "").strip()
    if not cid:
        return []
    manifest = load_tier1_manifest()
    chapters = manifest.get("chapters")
    if not isinstance(chapters, dict):
        return []
    chapter = chapters.get(cid)
    if not isinstance(chapter, dict):
        return []
    assets = chapter.get("assets")
    if not isinstance(assets, list):
        return []
    return sorted(_normalize_asset_id(str(aid)) for aid in assets if str(aid).strip())


def equity_symbol(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    sym = entry.get("equity_symbol") or asset_id or default_asset_id()
    return _normalize_asset_id(str(sym))


def deribit_currency(asset_id: str | None = None) -> str:
    entry = get_asset(asset_id)
    if asset_venue(asset_id) == "equity":
        raise ValueError(f"asset {asset_id!r} is equity venue, not deribit")
    currency = _normalize_asset_id(str(entry.get("deribit_currency") or asset_id or default_asset_id()))
    if not currency:
        raise ValueError(f"asset {asset_id!r} missing deribit_currency")
    return currency


def spread_width_for_asset(asset_id: str | None = None) -> float:
    entry = get_asset(asset_id)
    width = entry.get("spread_width")
    if width is not None:
        return float(width)
    if asset_venue(asset_id) == "equity":
        return 25.0
    return 5000.0 if deribit_currency(asset_id) == "BTC" else 500.0


def contract_multiplier(asset_id: str | None = None) -> float:
    entry = get_asset(asset_id)
    mult = entry.get("contract_multiplier")
    if mult is not None:
        return float(mult)
    if asset_venue(asset_id) == "equity":
        return 100.0
    return 1.0
