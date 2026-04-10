from __future__ import annotations

import math
import unittest

from src.viz.belief_disagreement_hints import belief_disagreement_hints_payload
from src.viz.belief_uncertainty import (
    move_pct_1sigma_to_sigma_ln,
    sigma_ln_to_move_pct_1sigma,
)
from src.viz.disagreement_thresholds import WIDTH_NARROWER_RATIO, WIDTH_WIDER_RATIO


class TestBeliefUncertaintyConversions(unittest.TestCase):
    def test_sigma_to_pct_and_back_round_trip(self) -> None:
        for sigma in (0.02, 0.10, 0.20, 0.50, 0.80):
            pct = sigma_ln_to_move_pct_1sigma(sigma)
            sigma2 = move_pct_1sigma_to_sigma_ln(pct)
            self.assertTrue(math.isfinite(pct))
            self.assertTrue(math.isfinite(sigma2))
            self.assertAlmostEqual(sigma, sigma2, places=10)

    def test_pct_to_sigma_and_back_round_trip(self) -> None:
        for pct in (1.0, 5.0, 20.0, 80.0, 150.0, 200.0):
            sigma = move_pct_1sigma_to_sigma_ln(pct)
            pct2 = sigma_ln_to_move_pct_1sigma(sigma)
            self.assertTrue(math.isfinite(sigma))
            self.assertTrue(math.isfinite(pct2))
            self.assertAlmostEqual(pct, pct2, places=10)


class TestBeliefDisagreementEquivalence(unittest.TestCase):
    def test_percent_equivalent_to_sigma_for_classification(self) -> None:
        sigma_mkt = 0.10
        sigmas_user = (
            sigma_mkt * (WIDTH_NARROWER_RATIO - 0.01),  # narrower
            sigma_mkt * 1.00,  # similar
            sigma_mkt * (WIDTH_WIDER_RATIO + 0.01),  # wider
        )
        for sigma_user in sigmas_user:
            pct = sigma_ln_to_move_pct_1sigma(sigma_user)
            sigma_from_pct = move_pct_1sigma_to_sigma_ln(pct)
            self.assertAlmostEqual(sigma_user, sigma_from_pct, places=10)

            pl_sigma = belief_disagreement_hints_payload(
                center_usd=100_000.0,
                market_peak=95_000.0,
                sigma_user=float(sigma_user),
                sigma_mkt=float(sigma_mkt),
                shape_gap_strength="Moderate",
                market_reference_kind="market-implied",
            )
            pl_pct = belief_disagreement_hints_payload(
                center_usd=100_000.0,
                market_peak=95_000.0,
                sigma_user=float(sigma_from_pct),
                sigma_mkt=float(sigma_mkt),
                shape_gap_strength="Moderate",
                market_reference_kind="market-implied",
            )
            self.assertEqual(pl_sigma["category_id"], pl_pct["category_id"])
            self.assertEqual(
                pl_sigma["belief_disagreement"]["width_band"],
                pl_pct["belief_disagreement"]["width_band"],
            )


if __name__ == "__main__":
    unittest.main()

