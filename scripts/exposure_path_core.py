"""Exposure path menu orchestration — catalog load, market fetch, path activation (v0)."""

from __future__ import annotations

from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from src.data.assets_registry import (
    asset_class,
    asset_venue,
    deribit_currency,
    get_asset,
    is_usd_premium_options_venue,
)
from src.engine.exposure_paths import (
    EQUITY_OPTION_MULTIPLIER,
    EXPOSURE_PATH_KIND,
    FOOTER_COPY,
    RECOMMENDATION_STATUS,
    ExposurePath,
    ExposurePathTemplate,
    HorizonChip,
    build_strategy_lab_deep_link,
    bull_call_spread_strikes,
    count_live_paths,
    format_leg,
    mark_lookup,
    parse_path_template,
    premium_to_usd,
    resolve_trust_badge,
    select_expiry_ts,
    snap_strike,
    sort_exposure_paths,
    template_to_path_shell,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = _REPO_ROOT / "config" / "exposure_path_catalog.yaml"


def _normalize_asset_id(asset_id: str) -> str:
    return str(asset_id or "").strip().upper()


def _normalize_direction(direction: str) -> str:
    d = str(direction or "long").strip().lower()
    if d not in ("long", "short", "neutral"):
        return "long"
    return d


@lru_cache(maxsize=1)
def load_exposure_path_catalog(catalog_path: str | None = None) -> dict[str, Any]:
    path = Path(catalog_path) if catalog_path else DEFAULT_CATALOG_PATH
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError("exposure path catalog root must be a mapping")
    return data


def catalog_templates(catalog: dict[str, Any]) -> dict[str, ExposurePathTemplate]:
    raw = catalog.get("path_templates") or {}
    out: dict[str, ExposurePathTemplate] = {}
    if not isinstance(raw, dict):
        return out
    for path_id, row in raw.items():
        if isinstance(row, dict):
            out[str(path_id)] = parse_path_template(str(path_id), row)
    return out


def binding_key_for_asset(asset_id: str) -> str:
    return asset_class(asset_id)


def resolve_path_ids_for_asset(
    asset_id: str,
    direction: str,
    catalog: dict[str, Any],
) -> list[str]:
    aid = _normalize_asset_id(asset_id)
    bindings = catalog.get("asset_bindings") or {}
    key = binding_key_for_asset(aid)
    block = bindings.get(key) if isinstance(bindings, dict) else None
    if not isinstance(block, dict):
        return []
    dir_key = _normalize_direction(direction)
    ids = block.get(dir_key) or []
    if not isinstance(ids, list):
        return []
    return [str(x) for x in ids]


def _illustrative_size(catalog: dict[str, Any], *, venue: str) -> float:
    ill = catalog.get("illustrative_size") or {}
    if venue == "equity":
        try:
            return float(ill.get("equity_shares") or EQUITY_OPTION_MULTIPLIER)
        except (TypeError, ValueError):
            return float(EQUITY_OPTION_MULTIPLIER)
    try:
        return float(ill.get("crypto_notional_usd") or 10_000.0)
    except (TypeError, ValueError):
        return 10_000.0


def _fetch_spot(asset_id: str) -> float | None:
    aid = _normalize_asset_id(asset_id)
    venue = asset_venue(aid)
    if venue == "equity":
        from src.data.fetch_equity_options import fetch_equity_spot

        return fetch_equity_spot(asset_id=aid)
    if venue == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_spot

        return fetch_bybit_spot(asset_id=aid)
    from src.data.fetch_deribit import fetch_deribit_index

    return fetch_deribit_index(deribit_currency(aid))


def _fetch_option_expiries(asset_id: str) -> list[dict[str, Any]]:
    aid = _normalize_asset_id(asset_id)
    venue = asset_venue(aid)
    if venue == "equity":
        from src.data.fetch_equity_options import fetch_equity_option_expiries

        return fetch_equity_option_expiries(asset_id=aid)
    if venue == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_option_expiries

        return fetch_bybit_option_expiries(asset_id=aid)
    from src.data.fetch_deribit import fetch_deribit_option_expiries

    return fetch_deribit_option_expiries(deribit_currency(aid))


def _fetch_marks_for_expiry(asset_id: str, expiry_ts: int) -> dict[str, list[dict[str, Any]]]:
    aid = _normalize_asset_id(asset_id)
    venue = asset_venue(aid)
    if venue == "equity":
        from src.data.fetch_equity_options import fetch_equity_option_marks_by_expiry_full

        return fetch_equity_option_marks_by_expiry_full(expiry_ts, asset_id=aid)
    if venue == "bybit":
        from src.data.fetch_bybit_options import fetch_bybit_option_marks_by_expiry_full

        return fetch_bybit_option_marks_by_expiry_full(expiry_ts, asset_id=aid)
    from src.data.fetch_deribit import fetch_deribit_option_marks_by_expiry_full

    return fetch_deribit_option_marks_by_expiry_full(expiry_ts, currency=deribit_currency(aid))


def _expiry_date_str(expiries: list[dict[str, Any]], expiry_ts: int) -> str:
    for row in expiries:
        ts = row.get("expiration_timestamp") or row.get("expiry_ts")
        if ts is not None and int(ts) == int(expiry_ts):
            return str(row.get("expiry_date_str") or "")
    return ""


def _assess_chain_thin(asset_id: str, call_marks: list[dict[str, Any]]) -> bool:
    aid = _normalize_asset_id(asset_id)
    if asset_venue(aid) == "equity":
        from src.data.fetch_equity_options import assess_equity_chain_trust

        trust = assess_equity_chain_trust(call_marks)
        flags = trust.get("trust_flags") or []
        return "insufficient_marks" in flags or "thin_open_interest" in flags
    return len(call_marks) < 3


def _option_contract_multiplier(asset_id: str) -> float:
    aid = _normalize_asset_id(asset_id)
    if asset_venue(aid) == "equity":
        entry = get_asset(aid)
        try:
            return float(entry.get("contract_multiplier") or EQUITY_OPTION_MULTIPLIER)
        except (TypeError, ValueError):
            return float(EQUITY_OPTION_MULTIPLIER)
    return 1.0


def _activate_spot_path(
    path: ExposurePath,
    *,
    spot: float | None,
    illustrative_units: float,
    notional_usd_direct: bool,
) -> ExposurePath | None:
    if notional_usd_direct:
        path.cost_hint_usd = illustrative_units
        path.trust_badge = "Live"
        return path
    if spot is None or spot <= 0:
        return None
    path.cost_hint_usd = float(spot) * illustrative_units
    path.trust_badge = "Live"
    return path


def _activate_planned_path(path: ExposurePath) -> ExposurePath:
    path.trust_badge = "Planned"
    path.cost_hint_usd = None
    path.legs = []
    return path


def _activate_options_path(
    path: ExposurePath,
    template: ExposurePathTemplate,
    *,
    asset_id: str,
    spot: float,
    expiries: list[dict[str, Any]],
    horizon: HorizonChip,
    premium_in_usd: bool,
    contract_multiplier: float,
) -> ExposurePath | None:
    expiry_ts = select_expiry_ts(
        expiries,
        min_horizon_days=template.min_horizon_days,
        max_horizon_days=template.max_horizon_days,
        horizon=horizon,
    )
    if expiry_ts is None:
        return None

    marks = _fetch_marks_for_expiry(asset_id, expiry_ts)
    calls = marks.get("calls") or []
    puts = marks.get("puts") or []
    call_by_k = mark_lookup(calls)
    put_by_k = mark_lookup(puts)
    avail_calls = sorted(call_by_k)
    avail_puts = sorted(put_by_k)
    expiry_date = _expiry_date_str(expiries, expiry_ts)
    thin = _assess_chain_thin(asset_id, calls)
    path.trust_badge = resolve_trust_badge(planned=False, thin_chain=thin)
    path.deep_link = build_strategy_lab_deep_link(asset_id)

    structure = template.structure or ""
    legs: list[dict[str, str]] = []

    if structure in ("long_call", "long_call_otm"):
        if not avail_calls:
            return None
        target = spot * (1.10 if structure == "long_call_otm" else 1.0)
        strike = snap_strike(avail_calls, target)
        premium = call_by_k.get(strike)
        if premium is None:
            return None
        path.cost_hint_usd = premium_to_usd(
            premium,
            forward_usd=spot,
            premium_in_usd=premium_in_usd,
            contract_multiplier=contract_multiplier,
        )
        legs.append(
            format_leg(
                asset_id=asset_id,
                instrument="Call",
                side="BUY",
                strike=strike,
                expiry_date=expiry_date,
            )
        )
    elif structure == "bull_call_spread":
        spread = bull_call_spread_strikes(spot, avail_calls)
        if spread is None:
            return None
        long_k, short_k = spread
        long_mark = call_by_k.get(long_k)
        short_mark = call_by_k.get(short_k)
        if long_mark is None or short_mark is None:
            return None
        net = float(long_mark) - float(short_mark)
        path.cost_hint_usd = premium_to_usd(
            net,
            forward_usd=spot,
            premium_in_usd=premium_in_usd,
            contract_multiplier=contract_multiplier,
        )
        legs.extend(
            [
                format_leg(
                    asset_id=asset_id,
                    instrument="Call",
                    side="BUY",
                    strike=long_k,
                    expiry_date=expiry_date,
                ),
                format_leg(
                    asset_id=asset_id,
                    instrument="Call",
                    side="SELL",
                    strike=short_k,
                    expiry_date=expiry_date,
                ),
            ]
        )
    elif structure == "short_put":
        if not avail_puts:
            return None
        strike = snap_strike(avail_puts, spot * 0.95)
        premium = put_by_k.get(strike)
        if premium is None:
            return None
        credit = premium_to_usd(
            premium,
            forward_usd=spot,
            premium_in_usd=premium_in_usd,
            contract_multiplier=contract_multiplier,
        )
        path.cost_hint_usd = credit
        legs.append(
            format_leg(
                asset_id=asset_id,
                instrument="Put",
                side="SELL",
                strike=strike,
                expiry_date=expiry_date,
            )
        )
    else:
        return None

    path.legs = legs
    return path


def activate_path_template(
    template: ExposurePathTemplate,
    *,
    asset_id: str,
    catalog_order: int,
    spot: float | None,
    expiries: list[dict[str, Any]],
    horizon: HorizonChip,
    illustrative_units: float,
) -> ExposurePath | None:
    aid = _normalize_asset_id(asset_id)
    premium_in_usd = is_usd_premium_options_venue(aid)
    contract_multiplier = _option_contract_multiplier(aid)

    if template.status == "planned" or template.liquidity == "planned":
        shell = template_to_path_shell(
            template,
            catalog_order=catalog_order,
            trust_badge="Planned",
        )
        return _activate_planned_path(shell)

    shell = template_to_path_shell(
        template,
        catalog_order=catalog_order,
        trust_badge="Live",
    )

    if template.instrument_rail == "spot_equity":
        return _activate_spot_path(
            shell,
            spot=spot,
            illustrative_units=illustrative_units,
            notional_usd_direct=template.path_id == "crypto_spot",
        )

    if template.instrument_rail == "listed_options":
        if spot is None or spot <= 0:
            return None
        return _activate_options_path(
            shell,
            template,
            asset_id=aid,
            spot=float(spot),
            expiries=expiries,
            horizon=horizon,
            premium_in_usd=premium_in_usd,
            contract_multiplier=contract_multiplier,
        )

    return _activate_planned_path(shell)


def find_exposure_paths(
    asset_id: str,
    direction: str,
    *,
    horizon: HorizonChip = "any",
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build ranked ExposurePath cards for one asset + direction.
    Returns JSON-serializable envelope for CLI and boundary consumers.
    """
    aid = _normalize_asset_id(asset_id)
    dir_key = _normalize_direction(direction)
    cat = catalog if catalog is not None else load_exposure_path_catalog()
    templates = catalog_templates(cat)
    path_ids = resolve_path_ids_for_asset(aid, dir_key, cat)
    sort_order = [str(x) for x in (cat.get("sort_order") or [])]

    spot = _fetch_spot(aid)
    expiries = _fetch_option_expiries(aid) if path_ids else []
    venue = asset_venue(aid)
    illustrative = _illustrative_size(cat, venue=venue)

    activated: list[ExposurePath] = []
    for order, path_id in enumerate(path_ids):
        template = templates.get(path_id)
        if template is None:
            continue
        path = activate_path_template(
            template,
            asset_id=aid,
            catalog_order=order,
            spot=spot,
            expiries=expiries,
            horizon=horizon,
            illustrative_units=illustrative,
        )
        if path is not None:
            activated.append(path)

    ranked = sort_exposure_paths(activated, sort_order=sort_order)
    live_count = count_live_paths(ranked)
    options_live = sum(1 for p in ranked if p.instrument_rail == "listed_options" and p.trust_badge == "Live")
    spot_live = sum(1 for p in ranked if p.instrument_rail == "spot_equity" and p.trust_badge == "Live")

    status = "ok"
    if dir_key != "neutral" and (spot_live < 1 or options_live < 2):
        status = "insufficient_chain"

    return {
        "kind": EXPOSURE_PATH_KIND,
        "asset_id": aid,
        "direction": dir_key,
        "horizon": horizon,
        "status": status,
        "live_path_count": live_count,
        "paths": [p.to_dict() for p in ranked],
        "recommendation_status": RECOMMENDATION_STATUS,
        "footer_copy": FOOTER_COPY,
        "as_of_utc": datetime.now(tz=UTC).isoformat(),
        "spot_usd": round(float(spot), 4) if spot is not None else None,
        "proof_asset": aid in [str(x).upper() for x in (cat.get("proof_assets") or [])],
    }


# Re-export for tests and CLI slice
__all__ = [
    "DEFAULT_CATALOG_PATH",
    "activate_path_template",
    "binding_key_for_asset",
    "catalog_templates",
    "find_exposure_paths",
    "load_exposure_path_catalog",
    "resolve_path_ids_for_asset",
]
