"""Phase 3 commercial wrapper v0 — copy, guardrails, operator checklist."""

from __future__ import annotations

import unittest

from src.viz.commercial_wrapper import (
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

    def test_operator_checklist_covers_env_and_boundary(self) -> None:
        items = operator_checklist()
        step_ids = {item.step_id for item in items}
        self.assertIn("env_snapshots", step_ids)
        self.assertIn("env_private_url", step_ids)
        self.assertIn("commercial_boundary", step_ids)
        self.assertGreaterEqual(len(items), 4)

    def test_forbidden_signal_language_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            assert_commercial_copy_safe("This is guaranteed returns for everyone.")

    def test_resolve_demo_ctas_returns_private_url(self) -> None:
        private_url = resolve_demo_ctas(
            snapshots_enabled=False,
            private_app_url="https://app.example.com",
        )
        self.assertEqual(private_url, "https://app.example.com")

    def test_boundary_caption_is_non_advisory(self) -> None:
        from src.viz.commercial_wrapper import COMMERCIAL_BOUNDARY_CAPTION

        assert_commercial_copy_safe(COMMERCIAL_BOUNDARY_CAPTION)
        self.assertIn("Research exploration only", COMMERCIAL_BOUNDARY_CAPTION)


if __name__ == "__main__":
    unittest.main()
