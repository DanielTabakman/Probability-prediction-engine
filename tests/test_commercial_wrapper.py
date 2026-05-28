"""Unit tests for Phase 3 commercial wrapper copy (no Streamlit)."""

from __future__ import annotations

import unittest

from src.viz.commercial_wrapper import (
    COMMERCIAL_BOUNDARY_CAPTION,
    DEMO_HERO_TAGLINE,
    PRIVATE_APP_CTA_CAPTION,
    PRIVATE_APP_CTA_LABEL,
    PUBLIC_DEMO_BANNER,
    operator_checklist_markdown,
    research_offer_markdown,
    validate_all_wrapper_copy,
)
from src.viz.mvp1_product_shell import assert_no_signal_language


class TestCommercialWrapper(unittest.TestCase):
    def test_validate_all_wrapper_copy(self) -> None:
        validate_all_wrapper_copy()

    def test_research_offer_mentions_beta_not_advice(self) -> None:
        md = research_offer_markdown()
        self.assertIn("Research beta", md)
        self.assertIn("not investment advice", md)
        self.assertNotIn("guaranteed", md.lower())
        assert_no_signal_language(md)

    def test_operator_checklist_covers_env_and_boundary(self) -> None:
        md = operator_checklist_markdown()
        self.assertIn("PPE_ENABLE_SNAPSHOTS", md)
        self.assertIn("PPE_RESEARCH_OFFER_URL", md)
        self.assertIn("Do not say", md)
        assert_no_signal_language(md)

    def test_demo_strings_stable(self) -> None:
        self.assertEqual(PRIVATE_APP_CTA_LABEL, "Get full access")
        self.assertIn("full app", PRIVATE_APP_CTA_CAPTION)
        self.assertIn("exploration", DEMO_HERO_TAGLINE)
        self.assertIn("Public demo", PUBLIC_DEMO_BANNER)
        assert_no_signal_language(COMMERCIAL_BOUNDARY_CAPTION)


if __name__ == "__main__":
    unittest.main()
