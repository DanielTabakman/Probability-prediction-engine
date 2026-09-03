"""Deterministic educational fit ranking for options expression candidates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

ExpressionDirection = Literal["long", "short", "neutral"]
PayoffPreference = Literal["defined_risk", "capital_light", "upside_leverage", "income_style", "watch_only"]
TrustBadge = Literal["Live", "Thin chain", "Planned"]

EXPRESSION_FIT_RANKING_KIND = "options_expression_fit_ranking"
RECOMMENDATION_STATUS = "educational_fit_not_recommendation"
LIMITATION_TEXT = (
    "Educational fit ranking only. It compares paper candidates against stated constraints; "
    "it is not financial advice, a recommendation, expected-profit optimization, or an order ticket."
)

SCORE_WEIGHTS: dict[str, int] = {
    "direction_fit": 30,
    "horizon_fit": 20,
    "max_loss_fit": 20,
    "payoff_fit": 15,
    "trust_fit": 15,
}

_DIRECTION_ALIASES = {
    "bullish": "long",
    "up": "long",
    "bearish": "short",
    "down": "short",
    "range": "neutral",
    "calm": "neutral",
    "neutral": "neutral",
    "long": "long",
    "short": "short",
}

_PAYOFF_LENSES: dict[PayoffPreference, tuple[str, ...]] = {
    "defined_risk": ("defined_risk",),
    "capital_light": ("capital_light",),
    "upside_leverage": ("upside_leverage",),
    "income_style": ("income_style",),
    "watch_only": ("simplest", "liquid"),
}


@dataclass(frozen=True)
class ExpressionFitPreferences:
    direction: ExpressionDirection = "long"
    belief: str = ""
    target_horizon_days: int | None = None
    max_loss_usd: float | None = None
    payoff_preference: PayoffPreference = "defined_risk"


def _normalize_direction(value: Any) -> ExpressionDirection:
    key = str(value or "long").strip().lower()
    return _DIRECTION_ALIASES.get(key, "long")  # type: ignore[return-value]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _candidate_text(candidate: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("label", "headline", "capital_shape", "structure", "sort_group", "expression_family"):
        value = candidate.get(key)
        if value:
            parts.append(str(value))
    for key in ("pros", "cons", "fit_lenses"):
        values = candidate.get(key)
        if isinstance(values, list):
            parts.extend(str(v) for v in values)
    return " ".join(parts).lower()


def infer_candidate_direction(candidate: dict[str, Any]) -> ExpressionDirection:
    raw = candidate.get("direction")
    if raw:
        return _normalize_direction(raw)
    text = _candidate_text(candidate)
    if any(token in text for token in ("range", "iron fly", "short vol", "calmer", "neutral")):
        return "neutral"
    if any(token in text for token in ("put", "bear", "downside")):
        return "short"
    return "long"


def _direction_component(candidate: dict[str, Any], prefs: ExpressionFitPreferences) -> tuple[float, str]:
    candidate_direction = infer_candidate_direction(candidate)
    if candidate_direction == prefs.direction:
        return 1.0, f"direction matches {prefs.direction}"
    if prefs.direction == "neutral" and candidate.get("leverage") == "defined":
        return 0.65, "defined-risk structure can express a range view, but direction is imperfect"
    if candidate_direction == "neutral":
        return 0.45, f"neutral payoff only partly matches a {prefs.direction} view"
    return 0.0, f"direction is {candidate_direction}, not {prefs.direction}"


def _horizon_days(candidate: dict[str, Any]) -> int | None:
    for key in ("horizon_days", "target_horizon_days"):
        value = candidate.get(key)
        if value is not None:
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return None
    min_h = candidate.get("min_horizon_days")
    max_h = candidate.get("max_horizon_days")
    try:
        if min_h is not None and max_h is not None:
            return int((float(min_h) + float(max_h)) / 2)
        if min_h is not None:
            return int(float(min_h))
        if max_h is not None:
            return int(float(max_h))
    except (TypeError, ValueError):
        return None
    return None


def _horizon_component(candidate: dict[str, Any], prefs: ExpressionFitPreferences) -> tuple[float, str]:
    target = prefs.target_horizon_days
    if target is None:
        return 1.0, "no target horizon constraint supplied"
    if candidate.get("time_bound") == "none":
        return (0.85, "no-expiry exposure can be held across the target horizon")
    days = _horizon_days(candidate)
    if days is None:
        return (0.5, "dated candidate has no precise horizon metadata")
    diff = abs(days - target)
    if diff <= 14:
        return (1.0, f"horizon is within 14 days of {target}d")
    if diff <= 45:
        return (0.75, f"horizon is close to {target}d")
    if diff <= 120:
        return (0.45, f"horizon is meaningfully away from {target}d")
    return (0.15, f"horizon is far from {target}d")


def _loss_value(candidate: dict[str, Any]) -> float | None:
    summary = candidate.get("summary")
    if isinstance(summary, dict) and summary.get("max_loss_usd") is not None:
        try:
            return abs(float(summary["max_loss_usd"]))
        except (TypeError, ValueError):
            return None
    for key in ("max_loss_usd", "cost_hint_usd"):
        value = candidate.get(key)
        if value is not None:
            try:
                return abs(float(value))
            except (TypeError, ValueError):
                return None
    return None


def _max_loss_component(candidate: dict[str, Any], prefs: ExpressionFitPreferences) -> tuple[float, str]:
    if candidate.get("trust_badge") == "Planned":
        return (0.2, "planned rail lacks live max-loss evidence")
    if candidate.get("leverage") == "high" and _loss_value(candidate) is None:
        return (0.1, "high-leverage candidate lacks a defined max-loss value")
    if prefs.max_loss_usd is None:
        return (1.0 if candidate.get("leverage") == "defined" else 0.65, "no max-loss cap supplied")
    loss = _loss_value(candidate)
    if loss is None:
        if candidate.get("leverage") == "none":
            return (0.55, "uncapped spot-style exposure has no premium max-loss estimate")
        return (0.25, "candidate lacks a comparable max-loss estimate")
    cap = max(0.0, float(prefs.max_loss_usd))
    if loss <= cap:
        return (1.0, f"max loss ${loss:,.0f} is inside the ${cap:,.0f} cap")
    if cap > 0 and loss <= cap * 1.25:
        return (0.55, f"max loss ${loss:,.0f} is slightly above the ${cap:,.0f} cap")
    return (0.0, f"max loss ${loss:,.0f} exceeds the ${cap:,.0f} cap")


def _payoff_component(candidate: dict[str, Any], prefs: ExpressionFitPreferences) -> tuple[float, str]:
    lenses = {str(x) for x in candidate.get("fit_lenses") or []}
    desired = set(_PAYOFF_LENSES[prefs.payoff_preference])
    if lenses & desired:
        return (1.0, f"payoff preference matches {prefs.payoff_preference}")
    text = _candidate_text(candidate)
    if prefs.payoff_preference == "defined_risk" and ("defined" in text or "capped" in text):
        return (0.8, "copy indicates defined or capped risk")
    if prefs.payoff_preference == "capital_light" and candidate.get("cost_hint_usd") is not None:
        return (0.65, "has an illustrative capital estimate")
    return (0.25, f"payoff preference is a weak match for {prefs.payoff_preference}")


def _trust_component(candidate: dict[str, Any]) -> tuple[float, str]:
    badge = str(candidate.get("trust_badge") or "Live")
    if badge == "Live":
        return (1.0, "live data available")
    if badge == "Thin chain":
        return (0.55, "thin-chain data lowers confidence")
    return (0.15, "planned rail is context only")


def _stable_tiebreak(candidate: dict[str, Any]) -> tuple[int, str]:
    badge_rank = {"Live": 0, "Thin chain": 1, "Planned": 2}.get(str(candidate.get("trust_badge") or ""), 3)
    order = int(candidate.get("catalog_order") or candidate.get("source_order") or 0)
    return (badge_rank * 10_000 + order, str(candidate.get("candidate_id") or candidate.get("path_id") or ""))


def score_expression_candidate(
    candidate: dict[str, Any],
    prefs: ExpressionFitPreferences,
) -> dict[str, Any]:
    components = {
        "direction_fit": _direction_component(candidate, prefs),
        "horizon_fit": _horizon_component(candidate, prefs),
        "max_loss_fit": _max_loss_component(candidate, prefs),
        "payoff_fit": _payoff_component(candidate, prefs),
        "trust_fit": _trust_component(candidate),
    }
    scored_components = {
        key: {
            "score": round(_bounded(raw) * SCORE_WEIGHTS[key], 4),
            "weight": SCORE_WEIGHTS[key],
            "reason": reason,
        }
        for key, (raw, reason) in components.items()
    }
    total = round(sum(row["score"] for row in scored_components.values()), 4)
    candidate_id = str(candidate.get("candidate_id") or candidate.get("path_id") or candidate.get("preset_id") or "")
    label = str(candidate.get("label") or candidate.get("name") or candidate_id)
    misses = [
        row["reason"]
        for row in scored_components.values()
        if float(row["score"]) < float(row["weight"]) * 0.8
    ]
    return {
        "candidate_id": candidate_id,
        "label": label,
        "score": total,
        "components": scored_components,
        "why": f"{label} scores {total:.1f}/100 because " + "; ".join(
            row["reason"] for row in scored_components.values() if float(row["score"]) >= float(row["weight"]) * 0.8
        ),
        "why_lower": misses[:3],
        "candidate": candidate,
    }


def rank_expression_candidates(
    candidates: list[dict[str, Any]],
    prefs: ExpressionFitPreferences,
) -> dict[str, Any]:
    scored = [score_expression_candidate(candidate, prefs) for candidate in candidates]
    scored.sort(
        key=lambda row: (
            -float(row["score"]),
            _stable_tiebreak(row["candidate"])[0],
            _stable_tiebreak(row["candidate"])[1],
        )
    )
    for rank, row in enumerate(scored, start=1):
        row["rank"] = rank
    top = scored[0] if scored else None
    return {
        "kind": EXPRESSION_FIT_RANKING_KIND,
        "recommendation_status": RECOMMENDATION_STATUS,
        "weights": dict(SCORE_WEIGHTS),
        "preferences": {
            "direction": prefs.direction,
            "belief": prefs.belief,
            "target_horizon_days": prefs.target_horizon_days,
            "max_loss_usd": prefs.max_loss_usd,
            "payoff_preference": prefs.payoff_preference,
        },
        "ranked": scored,
        "top_fit": top,
        "limitation": LIMITATION_TEXT,
    }


__all__ = [
    "EXPRESSION_FIT_RANKING_KIND",
    "LIMITATION_TEXT",
    "RECOMMENDATION_STATUS",
    "SCORE_WEIGHTS",
    "ExpressionFitPreferences",
    "infer_candidate_direction",
    "rank_expression_candidates",
    "score_expression_candidate",
]
