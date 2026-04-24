from __future__ import annotations

import unittest

import pandas as pd

from src.probability_engine.contracts.convert import (
    normalize_deribit_book_marks,
    normalize_polymarket_prob_dict_rows,
    normalize_yahoo_prices_df,
)
from src.probability_engine.services.snapshots import (
    normalize_deribit_option_marks,
    normalize_polymarket_probabilities,
    normalize_yahoo_prices,
)


class TestSnapshotConverters(unittest.TestCase):
    def test_normalize_yahoo_prices_df_best_effort(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "symbol": "AAPL",
                    "asset": "equity",
                    "timestamp": "2024-01-01T00:00:00Z",
                    "close": 123.45,
                    "volume": 1000,
                },
                # missing symbol -> skip
                {"symbol": "", "timestamp": "2024-01-01T00:00:00Z", "close": 1.0},
                # missing timestamp -> skip
                {"symbol": "MSFT", "timestamp": None, "close": 2.0},
                # unparseable timestamp -> keep as string
                {"symbol": "TSLA", "timestamp": object(), "close": None, "volume": None},
            ]
        )

        rows = normalize_yahoo_prices_df(df, as_of="ASOF", source="yahoo")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].symbol, "AAPL")
        self.assertEqual(rows[0].timestamp, "2024-01-01T00:00:00+00:00")
        self.assertEqual(rows[0].close, 123.45)
        self.assertEqual(rows[0].volume, 1000.0)
        self.assertEqual(rows[0].as_of, "ASOF")
        self.assertEqual(rows[0].source, "yahoo")

        self.assertEqual(rows[1].symbol, "TSLA")
        self.assertIsInstance(rows[1].timestamp, str)
        # Pandas will materialize None as NaN in float columns; best-effort behavior
        # should preserve that (and crucially not crash).
        self.assertTrue(rows[1].close is None or pd.isna(rows[1].close))
        self.assertTrue(rows[1].volume is None or pd.isna(rows[1].volume))

    def test_normalize_polymarket_prob_dict_rows_best_effort(self) -> None:
        inp = [
            {
                "event_slug": "e1",
                "market_question": "Will X happen?",
                "outcome": "YES",
                "probability": "0.25",
                "end_date_iso": "2026-01-01",
            },
            # invalid probability -> skip
            {
                "event_slug": "e2",
                "market_question": "Will Y happen?",
                "outcome": "YES",
                "probability": None,
            },
            # missing required strings -> skip
            {"event_slug": "", "market_question": "Q", "outcome": "YES", "probability": 0.5},
        ]

        rows = normalize_polymarket_prob_dict_rows(inp, as_of="ASOF", source="polymarket")
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r.event_slug, "e1")
        self.assertEqual(r.market_question, "Will X happen?")
        self.assertEqual(r.outcome, "YES")
        self.assertEqual(r.probability, 0.25)
        self.assertEqual(r.end_date_iso, "2026-01-01")
        self.assertEqual(r.as_of, "ASOF")
        self.assertEqual(r.source, "polymarket")

    def test_normalize_deribit_book_marks_best_effort(self) -> None:
        book_marks = {
            "BTC-26SEP25-80000-C": 0.0123,
            "": 0.9,  # skip empty instrument
            "BTC-26SEP25-90000-C": "0.01",
            "BTC-26SEP25-100000-C": None,  # skip invalid mark
        }

        rows = normalize_deribit_book_marks(book_marks, as_of="ASOF", source="deribit")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0].instrument_name, "BTC-26SEP25-80000-C")
        self.assertEqual(rows[0].mark_price, 0.0123)
        self.assertEqual(rows[0].as_of, "ASOF")

        self.assertEqual(rows[1].instrument_name, "BTC-26SEP25-90000-C")
        self.assertEqual(rows[1].mark_price, 0.01)

    def test_services_normalization_stays_callable_and_non_empty_as_of(self) -> None:
        # Services functions are the stable entrypoints; they should still work and
        # produce rows with best-effort defaults.
        df = pd.DataFrame(
            [{"symbol": "AAPL", "asset": None, "timestamp": "2024-01-01", "close": 1.0}]
        )
        yahoo_rows = normalize_yahoo_prices(df)
        self.assertEqual(len(yahoo_rows), 1)
        self.assertTrue(isinstance(yahoo_rows[0].as_of, str) and len(yahoo_rows[0].as_of) > 10)

        poly_rows = normalize_polymarket_probabilities(
            [{"event_slug": "e", "market_question": "q", "outcome": "YES", "probability": 0.1}]
        )
        self.assertEqual(len(poly_rows), 1)
        self.assertTrue(isinstance(poly_rows[0].as_of, str) and len(poly_rows[0].as_of) > 10)

        der_rows = normalize_deribit_option_marks({"BTC-TEST": 0.1})
        self.assertEqual(len(der_rows), 1)
        self.assertTrue(isinstance(der_rows[0].as_of, str) and len(der_rows[0].as_of) > 10)


if __name__ == "__main__":
    unittest.main()

