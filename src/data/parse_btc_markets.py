"""
Parse Polymarket rows into Bitcoin price-target questions: strike, resolution date, Yes probability.
"""
from __future__ import annotations

import re
from typing import Any

# Match "Will Bitcoin hit $150k by December 31, 2026?" or "Bitcoin hit $100k by 2025?"
# Also "When will Bitcoin hit $150k?" with market_question like "Will Bitcoin hit $150k by September 30?"
PRICE_PAT = re.compile(r"\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)\s*k?", re.I)
DATE_PAT = re.compile(
    r"(?:by|before)\s+"
    r"(?:(\w+)\s+(\d{1,2}),?\s+(\d{4})|"  # December 31, 2026
    r"(\d{4})-(\d{2})-(\d{2})|"  # 2026-12-31
    r"(\w+)\s+(\d{1,2})(?:\s|$)|"  # September 30
    r"(\d{1,2})/(\d{1,2})/(\d{4}))",
    re.I,
)


def _parse_price(s: str) -> float | None:
    m = PRICE_PAT.search(s)
    if not m:
        return None
    raw = m.group(1).replace(",", "")
    try:
        v = float(raw)
        if "k" in s[m.start() : m.end()].lower():
            v *= 1000
        return v
    except ValueError:
        return None


def _parse_resolution_date(question: str, end_date_iso: str) -> str | None:
    """Return YYYY-MM-DD for resolution if we can infer it."""
    if end_date_iso and len(end_date_iso) >= 10:
        return end_date_iso[:10]
    # Try to get from question text (e.g. "December 31, 2026")
    m = re.search(r"(?:by|before)\s+(\w+)\s+(\d{1,2}),?\s+(\d{4})", question, re.I)
    if m:
        month_str, day, year = m.group(1), m.group(2), m.group(3)
        months = "january february march april may june july august september october november december".split()
        try:
            month = months.index(month_str.lower()) + 1
            return f"{year}-{month:02d}-{int(day):02d}"
        except (ValueError, IndexError):
            pass
    return end_date_iso[:10] if end_date_iso else None


def btc_price_questions_from_polymarket(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    From flattened Polymarket rows, keep only Bitcoin price-target questions (e.g. hit $150k by date).
    For each unique (question, strike, resolution_date) keep the Yes outcome probability.
    """
    seen = set()
    out = []
    for r in rows:
        if r.get("outcome") != "Yes":
            continue
        title = (r.get("event_title") or "") + " " + (r.get("market_question") or "")
        if "bitcoin" not in title.lower() and "btc" not in title.lower():
            continue
        strike = _parse_price(title)
        if strike is None:
            continue
        end_iso = r.get("end_date_iso") or ""
        res_date = _parse_resolution_date(r.get("market_question") or "", end_iso)
        key = (r.get("market_question"), strike, res_date)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "market_question": r.get("market_question"),
            "event_title": r.get("event_title"),
            "strike": strike,
            "resolution_date": res_date,
            "yes_probability": r.get("probability"),
            "outcome": r.get("outcome"),
        })
    return out
