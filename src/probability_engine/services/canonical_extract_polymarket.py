"""
Map Polymarket Gamma events/markets into CanonicalEvent + ProbabilityObservation.

Input shape matches ``fetch_polymarket_markets`` / ``get_polymarket_markets``:
a list of event dicts with nested ``markets`` (see ``markets_to_probabilities``).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from src.data.fetch_polymarket import markets_to_probabilities
from src.data.parse_btc_markets import _parse_price, _parse_resolution_date
from src.probability_engine.contracts.canonical_events import (
    CanonicalEvent,
    ProbabilityObservation,
)

_AS_OF_EXCLUDE_BELOW = re.compile(
    r"\b("
    r"below|under\s+\$|dip\s+below|fall\s+below|less\s+than|"
    r"drop\s+to|crash\s+to"
    r")\b",
    re.I,
)

_ABOVE_OR_HIT = re.compile(
    r"\b(hit|reach|above|exceed|break|cross|surpass|at\s+least)\b|[≥>]",
    re.I,
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _format_threshold_key(threshold: float) -> str:
    """Stable string for hashing (avoid locale / scientific notation drift)."""
    if abs(threshold - round(threshold)) < 1e-9:
        return str(int(round(threshold)))
    s = f"{threshold:.10f}"
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"


def polymarket_btc_canonical_event_id(
    *,
    asset: str,
    comparator: str,
    threshold: float,
    resolution_date: str,
) -> str:
    """
    Deterministic id from (asset, comparator, threshold, resolution_date).

    ``resolution_date`` should be normalized to YYYY-MM-DD where possible.
    """
    asset_n = asset.strip().upper()
    comp_n = comparator.strip().lower()
    rd = (resolution_date or "")[:10]
    payload = "|".join(
        (
            "pm_v1",
            asset_n,
            comp_n,
            _format_threshold_key(threshold),
            rd,
        )
    )
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return f"pm_{digest}"


def _implies_btc_above_or_hit(combined_text: str) -> bool:
    """Exclude obvious 'below $X' style questions; keep hit/reach/above style."""
    if _AS_OF_EXCLUDE_BELOW.search(combined_text):
        return False
    return bool(_ABOVE_OR_HIT.search(combined_text))


@dataclass(frozen=True, slots=True)
class PolymarketBtcCanonicalExtract:
    canonical_events: tuple[CanonicalEvent, ...]
    probability_observations: tuple[ProbabilityObservation, ...]


def extract_polymarket_btc_above_by_date(
    events: list[dict[str, Any]],
    *,
    as_of_utc: str | None = None,
    topic_keywords: list[str] | None = None,
) -> PolymarketBtcCanonicalExtract:
    """
    Flatten Polymarket events, then extract BTC price-at-or-above threshold by date.

    Uses the same flattening as ``markets_to_probabilities``. Only ``Yes`` outcomes
    with a parsable USD strike and resolution day are emitted. Comparator is ``ge``
    (at-or-above / hit-style markets).

    ``as_of_utc`` defaults to current UTC time (ISO-8601). Pass a fixed string in tests.
    """
    as_of = as_of_utc if as_of_utc is not None else _utc_now_iso()
    rows = markets_to_probabilities(events, topic_keywords=topic_keywords)

    events_by_id: dict[str, CanonicalEvent] = {}
    observations: list[ProbabilityObservation] = []
    seen_keys: set[tuple[str | None, float, str | None]] = set()

    for r in rows:
        if (r.get("outcome") or "") != "Yes":
            continue
        mq = (r.get("market_question") or "").strip()
        combined = f"{r.get('event_title') or ''} {mq}"
        if "bitcoin" not in combined.lower() and "btc" not in combined.lower():
            continue
        if not _implies_btc_above_or_hit(combined):
            continue
        # Prefer the market question for USD strike: event titles often contain years (e.g. "Bitcoin 2026").
        strike = _parse_price(mq if mq else combined)
        if strike is None:
            continue
        end_iso = r.get("end_date_iso") or ""
        res_date = _parse_resolution_date(mq, str(end_iso))
        if not res_date or len(res_date) < 10:
            continue
        res_day = res_date[:10]
        dedupe_key = (mq or None, strike, res_day)
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)

        comparator = "ge"
        cid = polymarket_btc_canonical_event_id(
            asset="BTC",
            comparator=comparator,
            threshold=strike,
            resolution_date=res_day,
        )
        slug = (r.get("event_slug") or "").strip()
        raw_ref = "|".join(
            (
                "polymarket",
                slug,
                (mq or "")[:200],
            )
        )

        if cid not in events_by_id:
            events_by_id[cid] = CanonicalEvent(
                id=cid,
                type="bitcoin_above_by_date",
                asset="BTC",
                threshold=float(strike),
                resolution_date=f"{res_day}T00:00:00Z",
                description=(mq or combined.strip()) or None,
            )

        prob = r.get("probability")
        if prob is None:
            continue
        observations.append(
            ProbabilityObservation(
                canonical_event_id=cid,
                probability=float(prob),
                source="polymarket",
                as_of_utc=as_of,
                raw_ref=raw_ref,
            )
        )

    sorted_events = tuple(sorted(events_by_id.values(), key=lambda e: e.id))
    sorted_obs = tuple(
        sorted(
            observations,
            key=lambda o: (o.canonical_event_id, o.raw_ref or ""),
        )
    )
    return PolymarketBtcCanonicalExtract(
        canonical_events=sorted_events,
        probability_observations=sorted_obs,
    )
