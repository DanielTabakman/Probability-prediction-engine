"""Tests for Polymarket BTC price-question parsing."""

from __future__ import annotations

from src.data.parse_btc_markets import _parse_price, btc_price_questions_from_polymarket


def test_parse_price_k_suffix() -> None:
    assert _parse_price("Will Bitcoin hit $150k by Dec 2026?") == 150_000.0


def test_parse_price_plain_dollars() -> None:
    assert _parse_price("BTC above $95,000") == 95_000.0


def test_btc_price_questions_filters_non_btc_and_no_strike() -> None:
    rows = [
        {
            "outcome": "Yes",
            "event_title": "Ethereum",
            "market_question": "Will ETH hit $5k?",
            "probability": 0.4,
            "end_date_iso": "2026-12-31",
        },
        {
            "outcome": "No",
            "event_title": "Bitcoin",
            "market_question": "Will Bitcoin hit $100k by 2026-12-31?",
            "probability": 0.6,
            "end_date_iso": "2026-12-31",
        },
        {
            "outcome": "Yes",
            "event_title": "Bitcoin",
            "market_question": "Will Bitcoin hit $100k by 2026-12-31?",
            "probability": 0.55,
            "end_date_iso": "2026-12-31",
        },
    ]
    out = btc_price_questions_from_polymarket(rows)
    assert len(out) == 1
    assert out[0]["strike"] == 100_000.0
    assert out[0]["yes_probability"] == 0.55
    assert out[0]["resolution_date"] == "2026-12-31"
