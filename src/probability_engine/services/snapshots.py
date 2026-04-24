from __future__ import annotations

from typing import Any, Iterable

import pandas as pd

from src.probability_engine.contracts.convert import (
    normalize_deribit_book_marks,
    normalize_polymarket_prob_dict_rows,
    normalize_yahoo_prices_df,
)
from src.probability_engine.contracts.snapshots import (
    DeribitOptionMarkRow,
    PolymarketProbRow,
    YahooPriceRow,
)
from src.probability_engine.infra.store import Store, store_from_env


def normalize_yahoo_prices(
    df: pd.DataFrame, *, source: str = "yahoo"
) -> list[YahooPriceRow]:
    return normalize_yahoo_prices_df(df, source=source)


def normalize_polymarket_probabilities(
    rows: Iterable[dict[str, Any]], *, source: str = "polymarket"
) -> list[PolymarketProbRow]:
    return normalize_polymarket_prob_dict_rows(rows, source=source)


def normalize_deribit_option_marks(
    book_marks: dict[str, float] | None, *, source: str = "deribit"
) -> list[DeribitOptionMarkRow]:
    return normalize_deribit_book_marks(book_marks, source=source)


def write_yahoo_prices_snapshot(df: pd.DataFrame, store: Store | None = None) -> None:
    s = store or store_from_env()
    s.write_yahoo_prices(normalize_yahoo_prices(df))


def write_polymarket_probs_snapshot(
    rows: Iterable[dict[str, Any]], store: Store | None = None
) -> None:
    s = store or store_from_env()
    s.write_polymarket_probs(normalize_polymarket_probabilities(rows))


def write_deribit_option_marks_snapshot(
    book_marks: dict[str, float] | None, store: Store | None = None
) -> None:
    s = store or store_from_env()
    s.write_deribit_option_marks(normalize_deribit_option_marks(book_marks))
