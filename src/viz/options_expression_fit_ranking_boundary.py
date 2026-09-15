"""Read-only options expression fit ranking boundary for MSOS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

from src.engine.options_expression_fit_ranking import (
    EXPRESSION_FIT_RANKING_KIND,
    ExpressionFitPreferences,
    PayoffPreference,
    rank_expression_candidates,
)

OPTIONS_EXPRESSION_FIT_RANKING_HTTP_PATH = "/ppe-display-api/options-expression-fit-ranking.json"
_VALID_PAYOFFS: frozenset[PayoffPreference] = frozenset(
    {"defined_risk", "capital_light", "upside_leverage", "income_style", "watch_only"}
)


def build_exposure_menu_response(environ: dict[str, Any]) -> dict[str, Any]:
    offline = (_qs_str(environ, "offline") or "").lower() in ("1", "true", "yes")
    if offline:
        fixture_path = Path(__file__).resolve().parent / "exposure_menu_offline_fixture.json"
        data = json.loads(fixture_path.read_text(encoding="utf-8"))
        asset = (_qs_str(environ, "asset") or data.get("asset_id") or "NVDA").strip().upper()
        direction = (_qs_str(environ, "direction") or data.get("direction") or "long").strip().lower()
        if data.get("asset_id") == asset and data.get("direction") == direction:
            return data
        return {
            "kind": "exposure_menu_error",
            "asset_id": asset,
            "paths": [],
            "error": f"offline fixture only covers {data.get('asset_id')} {data.get('direction')}",
        }
    from src.viz.exposure_menu_boundary import build_exposure_menu_response as _build

    return _build(environ)


def build_strategy_suggestion_response(**kwargs: Any) -> dict[str, Any]:
    from src.viz.strategy_suggestion_boundary import build_strategy_suggestion_response as _build

    return _build(**kwargs)


def _qs_str(environ: dict[str, Any], key: str) -> str | None:
    raw = parse_qs(environ.get("QUERY_STRING") or "", keep_blank_values=False).get(key)
    if not raw:
        return None
    text = str(raw[0]).strip()
    return text or None


def _qs_float(environ: dict[str, Any], key: str) -> float | None:
    value = _qs_str(environ, key)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _qs_int(environ: dict[str, Any], key: str) -> int | None:
    value = _qs_str(environ, key)
    if value is None:
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def _payoff_preference(value: str | None) -> PayoffPreference:
    key = str(value or "defined_risk").strip().lower()
    if key in _VALID_PAYOFFS:
        return key  # type: ignore[return-value]
    return "defined_risk"


def _candidate_from_strategy(payload: dict[str, Any], *, source_order: int) -> dict[str, Any] | None:
    suggested = payload.get("suggested")
    if not isinstance(suggested, dict):
        return None
    summary = suggested.get("summary") if isinstance(suggested.get("summary"), dict) else {}
    preset_id = str(suggested.get("preset_id") or "strategy_suggestion")
    expression_family = str(suggested.get("expression_family") or "")
    return {
        "candidate_id": f"strategy:{preset_id}",
        "label": str(suggested.get("name") or suggested.get("preset_label") or "Strategy Lab structure"),
        "source": "strategy_suggestion",
        "source_order": source_order,
        "direction": "neutral" if expression_family == "range" or preset_id == "short_iron_fly" else None,
        "leverage": "defined",
        "time_bound": "dated",
        "horizon_days": _qs_int({"QUERY_STRING": ""}, "unused"),
        "trust_badge": "Live",
        "fit_lenses": ["defined_risk", "capital_light"],
        "max_loss_usd": summary.get("max_loss_usd"),
        "summary": summary,
        "legs": suggested.get("legs") if isinstance(suggested.get("legs"), list) else [],
        "review": suggested.get("review") if isinstance(suggested.get("review"), dict) else {},
        "belief_vs_market_glance": suggested.get("belief_vs_market_glance"),
    }


def build_options_expression_fit_ranking_response(environ: dict[str, Any]) -> dict[str, Any]:
    direction = (_qs_str(environ, "direction") or "long").lower()
    horizon = (_qs_str(environ, "horizon") or "any").lower()
    expiry = _qs_str(environ, "expiry")
    target_horizon_days = _qs_int(environ, "target_horizon_days")
    max_loss_usd = _qs_float(environ, "max_loss_usd")
    payoff = _payoff_preference(_qs_str(environ, "payoff_preference"))

    exposure_payload = build_exposure_menu_response(environ)
    candidates = [
        {**path, "candidate_id": f"exposure:{path.get('path_id')}", "source": "exposure_menu", "source_order": i}
        for i, path in enumerate(exposure_payload.get("paths") or [])
        if isinstance(path, dict)
    ]
    strategy_payload: dict[str, Any] | None = None
    if expiry:
        strategy_payload = build_strategy_suggestion_response(
            expiry_date=expiry,
            forward_mult=_qs_float(environ, "forward_mult") or 1.0,
            vol_mult=_qs_float(environ, "vol_mult") or 1.0,
        )
        strategy_candidate = _candidate_from_strategy(strategy_payload, source_order=len(candidates))
        if strategy_candidate is not None:
            strategy_candidate["horizon_days"] = target_horizon_days
            candidates.append(strategy_candidate)

    prefs = ExpressionFitPreferences(
        direction=direction if direction in ("long", "short", "neutral") else "long",  # type: ignore[arg-type]
        belief=_qs_str(environ, "belief") or "",
        target_horizon_days=target_horizon_days,
        max_loss_usd=max_loss_usd,
        payoff_preference=payoff,
    )
    ranked = rank_expression_candidates(candidates, prefs)
    return {
        **ranked,
        "kind": EXPRESSION_FIT_RANKING_KIND,
        "asset_id": exposure_payload.get("asset_id"),
        "horizon": horizon,
        "source_kinds": {
            "exposure_menu": exposure_payload.get("kind"),
            "strategy_suggestion": strategy_payload.get("kind") if strategy_payload else None,
        },
    }


def handle_options_expression_fit_ranking_wsgi_path(
    path: str,
    environ: dict[str, Any],
) -> tuple[str, bytes] | None:
    if (path.rstrip("/") or "/") != OPTIONS_EXPRESSION_FIT_RANKING_HTTP_PATH:
        return None
    try:
        payload = build_options_expression_fit_ranking_response(environ)
        status = "200 OK"
    except Exception as exc:  # noqa: BLE001 - boundary returns JSON errors
        payload = {"kind": "options_expression_fit_ranking_error", "error": str(exc)}
        status = "503 Service Unavailable"
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return status, body
