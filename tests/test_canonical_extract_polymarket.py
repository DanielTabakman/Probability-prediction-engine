from __future__ import annotations

import unittest

from src.probability_engine.services.canonical_extract_polymarket import (
    extract_polymarket_btc_above_by_date,
    polymarket_btc_canonical_event_id,
)


def _synthetic_gamma_event(
    *,
    title: str,
    slug: str,
    end_date: str,
    question: str,
    yes_price: float,
    outcomes: str = '["Yes", "No"]',
    prices: str | None = None,
) -> dict:
    p = prices if prices is not None else f'[{yes_price}, {1.0 - yes_price}]'
    return {
        "title": title,
        "slug": slug,
        "endDate": end_date,
        "markets": [
            {
                "question": question,
                "outcomes": outcomes,
                "outcomePrices": p,
                "endDateIso": end_date,
            }
        ],
    }


class TestCanonicalExtractPolymarket(unittest.TestCase):
    def test_polymarket_btc_canonical_event_id_is_stable(self) -> None:
        a = polymarket_btc_canonical_event_id(
            asset="BTC",
            comparator="ge",
            threshold=150_000.0,
            resolution_date="2026-12-31",
        )
        b = polymarket_btc_canonical_event_id(
            asset="BTC",
            comparator="ge",
            threshold=150000,
            resolution_date="2026-12-31",
        )
        self.assertEqual(a, b)
        self.assertTrue(a.startswith("pm_"))
        self.assertEqual(len(a), len("pm_") + 64)

    def test_extracts_yes_probability_and_fixed_as_of(self) -> None:
        events = [
            _synthetic_gamma_event(
                title="Bitcoin 2026",
                slug="btc-2026",
                end_date="2026-12-31",
                question="Will Bitcoin hit $150,000 by December 31, 2026?",
                yes_price=0.31,
            )
        ]
        as_of = "2026-04-24T12:00:00+00:00"
        got = extract_polymarket_btc_above_by_date(events, as_of_utc=as_of)
        self.assertEqual(len(got.canonical_events), 1)
        self.assertEqual(len(got.probability_observations), 1)
        ev = got.canonical_events[0]
        obs = got.probability_observations[0]
        self.assertEqual(ev.asset, "BTC")
        self.assertEqual(ev.type, "bitcoin_above_by_date")
        self.assertEqual(ev.threshold, 150_000.0)
        self.assertEqual(ev.resolution_date, "2026-12-31T00:00:00Z")
        self.assertEqual(obs.canonical_event_id, ev.id)
        self.assertAlmostEqual(obs.probability, 0.31)
        self.assertEqual(obs.source, "polymarket")
        self.assertEqual(obs.as_of_utc, as_of)
        self.assertIn("polymarket", obs.raw_ref or "")
        self.assertIn("btc-2026", obs.raw_ref or "")

    def test_skips_below_style_question(self) -> None:
        events = [
            _synthetic_gamma_event(
                title="Bitcoin",
                slug="x",
                end_date="2026-06-30",
                question="Will Bitcoin dip below $20,000 by June 30, 2026?",
                yes_price=0.05,
            )
        ]
        got = extract_polymarket_btc_above_by_date(
            events, as_of_utc="2026-01-01T00:00:00Z"
        )
        self.assertEqual(got.canonical_events, ())
        self.assertEqual(got.probability_observations, ())

    def test_deterministic_ordering(self) -> None:
        e_high = _synthetic_gamma_event(
            title="BTC",
            slug="a",
            end_date="2027-12-31",
            question="Will Bitcoin hit $200,000 by December 31, 2027?",
            yes_price=0.2,
        )
        e_low = _synthetic_gamma_event(
            title="BTC",
            slug="b",
            end_date="2026-12-31",
            question="Will Bitcoin hit $100,000 by December 31, 2026?",
            yes_price=0.4,
        )
        ids_forward = [
            e.id for e in extract_polymarket_btc_above_by_date(
                [e_high, e_low], as_of_utc="2026-01-01T00:00:00Z"
            ).canonical_events
        ]
        ids_reverse = [
            e.id for e in extract_polymarket_btc_above_by_date(
                [e_low, e_high], as_of_utc="2026-01-01T00:00:00Z"
            ).canonical_events
        ]
        self.assertEqual(ids_forward, ids_reverse)
        self.assertEqual(sorted(ids_forward), ids_forward)

    def test_dedupes_same_market_question_strike_and_day(self) -> None:
        dup = _synthetic_gamma_event(
            title="Bitcoin",
            slug="dup",
            end_date="2026-12-31",
            question="Will Bitcoin hit $100k by December 31, 2026?",
            yes_price=0.5,
        )
        got = extract_polymarket_btc_above_by_date(
            [dup, dup], as_of_utc="2026-01-01T00:00:00Z"
        )
        self.assertEqual(len(got.canonical_events), 1)
        self.assertEqual(len(got.probability_observations), 1)

    def test_btc_in_market_question_when_event_title_generic(self) -> None:
        events = [
            _synthetic_gamma_event(
                title="Macro outlook",
                slug="macro",
                end_date="2026-09-30",
                question="Will Bitcoin reach $95,000 by September 30, 2026?",
                yes_price=0.55,
            )
        ]
        got = extract_polymarket_btc_above_by_date(
            events, as_of_utc="2026-01-01T00:00:00Z"
        )
        self.assertEqual(len(got.canonical_events), 1)
        self.assertEqual(got.canonical_events[0].threshold, 95_000.0)


if __name__ == "__main__":
    unittest.main()
