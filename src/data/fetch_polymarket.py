"""
Fetch prediction market events and prices from Polymarket (Gamma + CLOB APIs).
"""

from __future__ import annotations

import json
import re
import time
import requests
from datetime import datetime, timezone
from typing import Any

GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"

_RETRY_STATUSES = {429, 500, 502, 503, 504}


def _get_json_with_retries(
    url: str,
    *,
    params: dict[str, Any] | None = None,
    timeout_s: float = 30.0,
    max_attempts: int = 3,
) -> Any:
    last_err: Exception | None = None
    for attempt in range(max_attempts):
        try:
            r = requests.get(url, params=params, timeout=timeout_s)
            if r.status_code in _RETRY_STATUSES and attempt < (max_attempts - 1):
                time.sleep(0.4 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()
        except (requests.Timeout, requests.ConnectionError) as e:
            last_err = e
            if attempt < (max_attempts - 1):
                time.sleep(0.4 * (attempt + 1))
                continue
            raise
        except requests.HTTPError as e:
            last_err = e
            sc = e.response.status_code if e.response is not None else None
            if sc in _RETRY_STATUSES and attempt < (max_attempts - 1):
                time.sleep(0.4 * (attempt + 1))
                continue
            raise
        except ValueError as e:
            # JSON decode error
            last_err = e
            raise
    if last_err:
        raise last_err
    raise RuntimeError("Polymarket request failed without exception")


def fetch_polymarket_markets(
    active: bool = True,
    closed: bool = False,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Fetch active events from Polymarket Gamma API. Each event can have
    multiple markets with outcomePrices (implied probabilities).
    """
    url = f"{GAMMA_BASE}/events"
    params = {
        "active": str(active).lower(),
        "closed": str(closed).lower(),
        "limit": limit,
    }
    data = _get_json_with_retries(url, params=params, timeout_s=30.0, max_attempts=3)
    # Gamma returns a list of event dicts.
    return data if isinstance(data, list) else []


def markets_to_probabilities(
    events: list[dict[str, Any]],
    topic_keywords: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Flatten events into one row per market outcome with implied probability.
    topic_keywords: only include events whose title/slug match (e.g. bitcoin, gold, silver).
    """
    keywords = (
        [topic_keywords] if isinstance(topic_keywords, str) else (topic_keywords or [])
    )
    pattern = (
        re.compile("|".join(re.escape(k) for k in keywords), re.I) if keywords else None
    )

    rows = []
    for ev in events:
        title = (ev.get("title") or "") or (ev.get("slug") or "")
        if pattern and not pattern.search(title):
            continue
        slug = ev.get("slug") or ""
        end_date_iso = ev.get("endDate") or ev.get("end_date_iso") or ""
        markets = ev.get("markets") or []
        for m in markets:
            raw_outcomes = m.get("outcomes") or "Yes/No"
            if isinstance(raw_outcomes, str):
                try:
                    outcomes = json.loads(raw_outcomes)
                except json.JSONDecodeError:
                    outcomes = (
                        [o.strip() for o in raw_outcomes.split("/")]
                        if "/" in raw_outcomes
                        else [raw_outcomes]
                    )
            else:
                outcomes = raw_outcomes
            raw_prices = m.get("outcomePrices") or m.get("prices") or []
            if isinstance(raw_prices, str):
                try:
                    prices = [float(x) for x in json.loads(raw_prices)]
                except (json.JSONDecodeError, TypeError):
                    prices = (
                        [float(p.strip()) for p in raw_prices.split(",")]
                        if raw_prices
                        else []
                    )
            else:
                prices = [float(x) for x in raw_prices]
            question = m.get("question") or m.get("groupItemTitle") or title
            end_date_iso = m.get("endDateIso") or m.get("endDate") or end_date_iso
            for i, out in enumerate(outcomes):
                prob = prices[i] if i < len(prices) else None
                if prob is None:
                    continue
                rows.append(
                    {
                        "event_title": title,
                        "event_slug": slug,
                        "end_date_iso": end_date_iso
                        if isinstance(end_date_iso, str)
                        else (end_date_iso[:10] if end_date_iso else ""),
                        "market_question": question,
                        "outcome": out,
                        "probability": prob,
                        "source": "polymarket",
                        "fetched_at": datetime.now(timezone.utc).isoformat(),
                    }
                )
    return rows
