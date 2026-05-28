"""Phase 3 commercial wrapper v0 — copy, guardrails, operator checklist."""

from __future__ import annotations

import unittest

from src.viz.commercial_wrapper import (
    COMMERCIAL_FORBIDDEN_SIGNAL_TOKENS,
    assert_commercial_copy_safe,
    commercial_surface_copy,
    operator_checklist,
    resolve_demo_ctas,
)


class TestCommercialWrapper(unittest.TestCase):
    def test_surface_copy_is_non_advisory(self) -> None:
        copy = commercial_surface_copy()
        self.assertIn("exploration", copy.tagline.lower())
        self.assertEqual(copy.private_app_label, "Get full access")
        self.assertIn("Research beta", copy.research_offer_blurb)

    def test_operator_checklist_covers_env_and_boundary(self) -> None:
        items = operator_checklist()
        step_ids = {item.step_id for item in items}
        self.assertIn("env_snapshots", step_ids)
        self.assertIn("env_private_url", step_ids)
        self.assertIn("env_offer_url", step_ids)
        self.assertIn("commercial_boundary", step_ids)
        self.assertGreaterEqual(len(items), 5)

    def test_forbidden_signal_language_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            assert_commercial_copy_safe("This is guaranteed returns for everyone.")

    def test_resolve_demo_ctas_validates_offer_label(self) -> None:
        private_url, offer = resolve_demo_ctas(
            snapshots_enabled=False,
            private_app_url="https://app.example.com",
            offer_url="https://cal.example.com/book",
            offer_label="Book a research demo",
        )
        self.assertEqual(private_url, "https://app.example.com")
        self.assertEqual(offer, ("https://cal.example.com/book", "Book a research demo"))

    def test_forbidden_tokens_cover_product_shell_subset(self) -> None:
        from src.viz.mvp1_product_shell import FORBIDDEN_SIGNAL_TOKENS

        for tok in FORBIDDEN_SIGNAL_TOKENS:
            self.assertIn(tok, COMMERCIAL_FORBIDDEN_SIGNAL_TOKENS)


if __name__ == "__main__":
    unittest.main()
