"""Lab asset selection for Streamlit implied lab and embed display API."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.data.assets_registry import (
    asset_venue,
    default_asset_id,
    get_asset,
    load_assets_registry,
)

LAB_ASSET_QUERY_PARAM = "asset"
_DERIBIT_LAB_ASSETS = ("BTC", "ETH")


def list_selectable_lab_asset_ids() -> list[str]:
    """BTC/ETH plus equity registry entries (e.g. NVDA)."""
    ids: list[str] = list(_DERIBIT_LAB_ASSETS)
    reg = load_assets_registry()
    assets = reg.get("assets")
    if not isinstance(assets, dict):
        return ids
    for aid, entry in sorted(assets.items()):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("venue") or "").strip().lower() != "equity":
            continue
        upper = str(aid).strip().upper()
        if upper and upper not in ids:
            ids.append(upper)
    return ids


def display_asset_meta(asset_id: str) -> dict[str, str]:
    aid = str(asset_id or default_asset_id()).strip().upper()
    entry = get_asset(aid)
    label = str(entry.get("label") or f"{aid} options")
    price_axis = f"{aid} price at expiry"
    return {
        "id": aid,
        "label": label,
        "price_axis_label": price_axis,
        "instrument_label": label,
    }


def normalize_lab_asset_id(value: str | None) -> str:
    raw = str(value or "").strip().upper()
    if not raw:
        return default_asset_id()
    allowed = set(list_selectable_lab_asset_ids())
    return raw if raw in allowed else default_asset_id()


def lab_asset_id_from_environ(environ: dict[str, Any]) -> str:
    from urllib.parse import parse_qs

    qs = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False)
    raw = (qs.get(LAB_ASSET_QUERY_PARAM) or [""])[0]
    return normalize_lab_asset_id(raw)


def lab_asset_id_from_streamlit() -> str:
    raw = st.query_params.get(LAB_ASSET_QUERY_PARAM)
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    return normalize_lab_asset_id(raw if isinstance(raw, str) else str(raw or ""))


def render_lab_asset_selector(*, key: str = "implied_lab_asset_id") -> str:
    """Streamlit selectbox; syncs session state with ``?asset=`` when present."""
    options = list_selectable_lab_asset_ids()
    labels = {aid: display_asset_meta(aid)["label"] for aid in options}
    qp_id = lab_asset_id_from_streamlit()
    if key not in st.session_state or st.session_state[key] not in options:
        st.session_state[key] = qp_id if qp_id in options else default_asset_id()
    index = options.index(st.session_state[key])
    selected = st.selectbox(
        "Asset",
        options,
        index=index,
        format_func=lambda aid: labels.get(aid, aid),
        key=key,
    )
    default = default_asset_id()
    if selected != default:
        st.query_params[LAB_ASSET_QUERY_PARAM] = selected
    elif LAB_ASSET_QUERY_PARAM in st.query_params:
        del st.query_params[LAB_ASSET_QUERY_PARAM]
    return str(selected)
