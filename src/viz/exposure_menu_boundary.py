"""Exposure menu display API — ranked path cards for MSOS / embed (read-only boundary)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from scripts.exposure_path_core import find_exposure_paths
from src.engine.exposure_paths import EXPOSURE_PATH_KIND, HorizonChip

EXPOSURE_MENU_KIND = EXPOSURE_PATH_KIND
EXPOSURE_MENU_HTTP_PATH = "/ppe-display-api/exposure-menu.json"
EXPOSURE_MENU_HTTP_PATH_ALT = "/exposure-menu.json"

_VALID_HORIZONS: frozenset[HorizonChip] = frozenset({"any", "3m", "12m"})
_VALID_DIRECTIONS = frozenset({"long", "short", "neutral"})

_FIXTURE_PATH = Path(__file__).resolve().parent / "exposure_menu_offline_fixture.json"


def _qs_str(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    text = str(raw[0]).strip()
    return text or None


def _normalize_horizon(value: str | None) -> HorizonChip:
    key = (value or "any").strip().lower()
    if key in _VALID_HORIZONS:
        return key  # type: ignore[return-value]
    return "any"


def _normalize_direction(value: str | None) -> str:
    key = (value or "long").strip().lower()
    if key in _VALID_DIRECTIONS:
        return key
    return "long"


def load_offline_fixture() -> dict[str, Any]:
    """Static NVDA long payload for embed/tests when live fetch is unavailable."""
    if not _FIXTURE_PATH.is_file():
        raise FileNotFoundError(f"offline fixture missing: {_FIXTURE_PATH}")
    data = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("exposure menu fixture root must be a mapping")
    return data


def build_exposure_menu_response(environ: dict[str, Any]) -> dict[str, Any]:
    asset = (_qs_str(environ, "asset") or "NVDA").strip().upper()
    direction = _normalize_direction(_qs_str(environ, "direction"))
    horizon = _normalize_horizon(_qs_str(environ, "horizon"))
    offline = (_qs_str(environ, "offline") or "").lower() in ("1", "true", "yes")
    if offline:
        fixture = load_offline_fixture()
        if fixture.get("asset_id") != asset or fixture.get("direction") != direction:
            return {
                "kind": "exposure_menu_error",
                "error": f"offline fixture only covers NVDA long (requested {asset} {direction})",
            }
        return fixture
    return find_exposure_paths(asset, direction, horizon=horizon)


def handle_exposure_menu_wsgi_path(
    path: str,
    environ: dict[str, Any],
) -> tuple[str, bytes] | None:
    normalized = path.rstrip("/") or "/"
    if normalized not in (EXPOSURE_MENU_HTTP_PATH, EXPOSURE_MENU_HTTP_PATH_ALT):
        return None
    try:
        payload = build_exposure_menu_response(environ)
    except Exception as exc:  # noqa: BLE001 — surface fetch failures as JSON
        payload = {"kind": "exposure_menu_error", "error": str(exc)}
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    kind = payload.get("kind")
    if kind == "exposure_menu_error":
        status = "400 Bad Request" if "offline fixture" in str(payload.get("error") or "") else "503 Service Unavailable"
    else:
        status = "200 OK"
    return status, body
