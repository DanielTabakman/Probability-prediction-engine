"""Multi-venue asset data source discovery — scan wired vendors and recommend routing.

Used by scripts/discover_asset_data_source.py (agents run before enabling new assets).
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

import requests
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
VENUE_MAP_PATH = _REPO_ROOT / "config" / "asset_venue_source_map.yaml"
DERIBIT_BASE = "https://www.deribit.com/api/v2"
BYBIT_BASE = "https://api.bybit.com/v5"

# Registry keys agents should set per venue when merging a new row
REGISTRY_FIELDS_BY_VENUE: dict[str, list[str]] = {
    "deribit": ["deribit_currency"],
    "bybit": ["bybit_base_coin"],
    "equity": ["equity_symbol", "data_source"],
}

FETCH_MODULE_BY_VENUE: dict[str, str] = {
    "deribit": "src.data.fetch_deribit",
    "bybit": "src.data.fetch_bybit_options",
    "equity": "src.data.fetch_equity_options",
}


def _normalize_id(asset_id: str) -> str:
    return str(asset_id or "").strip().upper()


def load_venue_map() -> dict[str, Any]:
    if not VENUE_MAP_PATH.is_file():
        return {}
    with VENUE_MAP_PATH.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def discovery_scan_order(asset_kind: str) -> list[str]:
    cfg = load_venue_map().get("discovery") or {}
    if asset_kind == "equity":
        order = cfg.get("equity_scan_order") or ["equity"]
    else:
        order = cfg.get("crypto_scan_order") or ["deribit", "bybit"]
    return [str(v).strip().lower() for v in order if str(v).strip()]


def infer_asset_kind(
    asset_id: str,
    *,
    registry_entry: dict[str, Any] | None = None,
    explicit: str | None = None,
) -> str:
    if explicit and explicit != "auto":
        return explicit.strip().lower()
    if registry_entry:
        ac = str(registry_entry.get("asset_class") or "").lower()
        if ac.startswith("equity") or ac == "commodity_proxy":
            return "equity"
        if registry_entry.get("equity_symbol"):
            return "equity"
        return "crypto"
    aid = _normalize_id(asset_id)
    if len(aid) <= 5 and aid.isalpha() and aid not in ("BTC", "ETH"):
        # Heuristic: short tickers without manifest context default crypto-first scan
        manifest = _load_tier1_template(aid)
        if manifest and str(manifest.get("asset_class", "")).startswith("equity"):
            return "equity"
    return "crypto"


def _load_tier1_template(asset_id: str) -> dict[str, Any] | None:
    path = _REPO_ROOT / "config" / "assets_tier1_manifest.yaml"
    if not path.is_file():
        return None
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    templates = (data or {}).get("asset_templates") or {}
    row = templates.get(_normalize_id(asset_id))
    return row if isinstance(row, dict) else None


def is_adapter_wired(venue: str) -> bool:
    module = FETCH_MODULE_BY_VENUE.get(venue.strip().lower())
    if not module:
        return False
    try:
        importlib.import_module(module)
        return True
    except ImportError:
        return False


def _deribit_get(method: str, params: dict[str, Any]) -> tuple[Any | None, str | None]:
    try:
        resp = requests.get(f"{DERIBIT_BASE}/public/{method}", params=params, timeout=20)
        resp.raise_for_status()
        body = resp.json()
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)
    if isinstance(body, dict) and body.get("error"):
        err = body["error"]
        return None, str(err.get("message") if isinstance(err, dict) else err)
    return body.get("result") if isinstance(body, dict) else body, None


def scan_deribit_crypto(currency: str) -> dict[str, Any]:
    cur = _normalize_id(currency)
    options, opt_err = _deribit_get(
        "get_instruments",
        {"currency": cur, "kind": "option", "expired": "false"},
    )
    index, idx_err = _deribit_get("get_index_price", {"index_name": f"{cur.lower()}_usd"})
    count = len(options) if isinstance(options, list) else 0
    index_price = index.get("index_price") if isinstance(index, dict) else None
    return {
        "venue": "deribit",
        "options_count": count,
        "options_available": count > 0,
        "index_price_usd": index_price,
        "wired": is_adapter_wired("deribit"),
        "fetch_module": FETCH_MODULE_BY_VENUE["deribit"],
        "registry_fields": {"deribit_currency": cur},
        "errors": {"instruments": opt_err, "index": idx_err},
    }


def scan_bybit_crypto(base_coin: str) -> dict[str, Any]:
    coin = _normalize_id(base_coin)
    count = 0
    index_price = None
    err: str | None = None
    try:
        resp = requests.get(
            f"{BYBIT_BASE}/market/tickers",
            params={"category": "option", "baseCoin": coin},
            timeout=20,
        )
        resp.raise_for_status()
        body = resp.json()
        if int(body.get("retCode") or 0) != 0:
            err = str(body.get("retMsg"))
        else:
            lst = (body.get("result") or {}).get("list") or []
            count = len(lst)
            if lst:
                index_price = lst[0].get("indexPrice") or lst[0].get("underlyingPrice")
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    return {
        "venue": "bybit",
        "options_count": count,
        "options_available": count > 0,
        "index_price_usd": float(index_price) if index_price is not None else None,
        "wired": is_adapter_wired("bybit"),
        "fetch_module": FETCH_MODULE_BY_VENUE.get("bybit"),
        "registry_fields": {"bybit_base_coin": coin},
        "errors": {"tickers": err},
    }


def scan_yfinance_equity(symbol: str) -> dict[str, Any]:
    sym = _normalize_id(symbol)
    expiry_count = 0
    err: str | None = None
    try:
        import yfinance as yf

        opts = getattr(yf.Ticker(sym), "options", None) or []
        expiry_count = len(list(opts))
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    return {
        "venue": "equity",
        "options_count": expiry_count,
        "options_available": expiry_count > 0,
        "index_price_usd": None,
        "wired": is_adapter_wired("equity"),
        "fetch_module": FETCH_MODULE_BY_VENUE["equity"],
        "registry_fields": {"equity_symbol": sym, "data_source": "yfinance"},
        "errors": {"yfinance": err},
    }


def scan_venue(venue: str, asset_id: str, asset_kind: str) -> dict[str, Any]:
    aid = _normalize_id(asset_id)
    v = venue.strip().lower()
    if v == "deribit":
        return scan_deribit_crypto(aid)
    if v == "bybit":
        return scan_bybit_crypto(aid)
    if v == "equity":
        return scan_yfinance_equity(aid)
    return {
        "venue": v,
        "options_count": 0,
        "options_available": False,
        "wired": is_adapter_wired(v),
        "errors": {"probe": f"unknown venue {v!r}"},
    }


def pick_best_venue(scan_results: list[dict[str, Any]]) -> dict[str, Any] | None:
    live = [r for r in scan_results if r.get("options_available")]
    if not live:
        return None
    wired_live = [r for r in live if r.get("wired")]
    pool = wired_live or live
    return max(pool, key=lambda r: int(r.get("options_count") or 0))


def resolve_next_action(
    *,
    asset_id: str,
    asset_kind: str,
    best: dict[str, Any] | None,
    registry_entry: dict[str, Any] | None,
    in_registry: bool,
) -> tuple[str, list[str]]:
    aid = _normalize_id(asset_id)
    if best is None:
        return "blocked_no_live_options", [
            f"No live options chain found for {aid} on scanned venues.",
            "Document skip in evidence; do not enable.",
        ]

    venue = str(best.get("venue"))
    wired = bool(best.get("wired"))

    if not wired:
        return "build_adapter", [
            f"Live options on {venue} ({best.get('options_count')} instruments) but fetch adapter not wired.",
            f"Implement {best.get('fetch_module') or venue} adapter (copy bybit/equity pattern), update venue map.",
            "Merge registry row, route app_cache + distribution_export, witness, enable.",
        ]

    if not in_registry:
        return "merge_registry_and_enable", [
            f"Merge {aid} into config/assets.yaml from assets_tier1_manifest.yaml template.",
            f"Set venue: {venue} and registry fields {best.get('registry_fields')}.",
            "enabled: true after witness; gate + commit + PR.",
        ]

    reg_venue = str((registry_entry or {}).get("venue") or "").lower()
    enabled = (registry_entry or {}).get("enabled") is True

    if reg_venue == venue and enabled:
        return "already_enabled", [f"{aid} already enabled on {venue}."]

    if reg_venue == venue and not enabled:
        return "enable_existing_row", [
            f"Registry row exists (venue={venue}, disabled).",
            f"python scripts/witness_asset_catalog.py --asset {aid} --live",
            f"python scripts/enable_asset_batch.py --asset {aid} --apply --live-witness",
        ]

    return "switch_venue_and_enable", [
        f"Registry has venue={reg_venue or '?'} but live chain is on {venue}.",
        f"Update config/assets.yaml: venue -> {venue}, set {best.get('registry_fields')}.",
        "Remove stale deribit-only fields if switching off Deribit.",
        f"Witness + enable {aid}; gate + commit + PR.",
    ]


def discover_asset_source(
    asset_id: str,
    *,
    asset_kind: str = "auto",
    registry_entry: dict[str, Any] | None = None,
    in_registry: bool = False,
) -> dict[str, Any]:
    aid = _normalize_id(asset_id)
    kind = infer_asset_kind(aid, registry_entry=registry_entry, explicit=asset_kind)
    order = discovery_scan_order(kind)
    scans = [scan_venue(v, aid, kind) for v in order]
    best = pick_best_venue(scans)
    next_action, agent_steps = resolve_next_action(
        asset_id=aid,
        asset_kind=kind,
        best=best,
        registry_entry=registry_entry,
        in_registry=in_registry,
    )

    return {
        "asset_id": aid,
        "asset_kind": kind,
        "ok": best is not None and bool(best.get("options_available")),
        "recommended_venue": best.get("venue") if best else None,
        "options_count": best.get("options_count") if best else 0,
        "wired": bool(best.get("wired")) if best else False,
        "next_action": next_action,
        "agent_steps": agent_steps,
        "scan_results": scans,
        "scan_order": order,
        "registry": {
            "in_registry": in_registry,
            "venue": (registry_entry or {}).get("venue"),
            "enabled": (registry_entry or {}).get("enabled"),
        },
        "sop": "docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md",
    }
