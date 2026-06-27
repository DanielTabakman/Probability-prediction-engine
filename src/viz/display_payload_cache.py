"""In-process TTL cache for live display payloads (ppe_display_api WSGI).

Streamlit ``@st.cache_data`` does not survive across WSGI requests; this module
keys cache entries by asset id + depth so repeat MSOS loads stay fast.
"""

from __future__ import annotations

import os
import time
from threading import Lock
from typing import Any, Callable

_CACHE: dict[tuple[str, str], tuple[float, dict[str, Any]]] = {}
_LOCK = Lock()

DEFAULT_TTL_SECONDS = 120


def display_cache_ttl_seconds() -> int:
    raw = os.environ.get("PPE_DISPLAY_CACHE_TTL_SECONDS", "").strip()
    if not raw:
        return DEFAULT_TTL_SECONDS
    try:
        ttl = int(raw)
    except ValueError:
        return DEFAULT_TTL_SECONDS
    return max(0, ttl)


def cache_enabled() -> bool:
    flag = os.environ.get("PPE_DISPLAY_CACHE_ENABLED", "1").strip().lower()
    return flag not in ("0", "false", "no", "off")


def clear_display_payload_cache() -> None:
    with _LOCK:
        _CACHE.clear()


def get_cached_display_payload(
    asset_id: str,
    depth: str,
    builder: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Return cached payload or build and store when caching is enabled."""
    aid = str(asset_id or "").strip().upper() or "BTC"
    depth_key = str(depth or "full").strip().lower() or "full"
    ttl = display_cache_ttl_seconds()
    if not cache_enabled() or ttl <= 0:
        return builder()

    key = (aid, depth_key)
    now = time.monotonic()
    with _LOCK:
        hit = _CACHE.get(key)
        if hit is not None and now - hit[0] < ttl:
            return hit[1]

    payload = builder()
    with _LOCK:
        _CACHE[key] = (now, payload)
    return payload
