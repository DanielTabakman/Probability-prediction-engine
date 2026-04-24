from __future__ import annotations

from typing import Any

from src.data.fetch_deribit import fetch_deribit_spreads_around_predictions
from src.data.fetch_polymarket import markets_to_probabilities
from src.data.parse_btc_markets import btc_price_questions_from_polymarket


def polymarket_events_to_probabilities(
    events: list[dict[str, Any]],
    *,
    topic_keywords: list[str] | None,
) -> list[dict[str, Any]]:
    return markets_to_probabilities(events, topic_keywords=topic_keywords) if events else []


def polymarket_probs_to_btc_price_questions(
    polymarket_probs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return btc_price_questions_from_polymarket(polymarket_probs) if polymarket_probs else []


def get_deribit_spreads_around_predictions(
    *,
    btc_questions: list[dict[str, Any]],
    current_spot: float,
    max_questions: int,
    instruments: Any,
    option_book_marks: Any,
) -> list[dict[str, Any]]:
    return (
        fetch_deribit_spreads_around_predictions(
            btc_questions=btc_questions,
            current_spot=current_spot,
            max_questions=max_questions,
            instruments=instruments,
            option_book_marks=option_book_marks,
        )
        or []
    )

