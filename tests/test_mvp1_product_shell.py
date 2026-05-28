"""MVP1 product shell copy helpers."""

from __future__ import annotations

import unittest

from src.viz.mvp1_product_shell import (
    WORKSPACE_NAME,
    assert_no_signal_language,
    feedback_path_hint,
    product_hierarchy_line,
    workspace_context_caption,
)


class TestMvp1ProductShell(unittest.TestCase):
    def test_hierarchy_names(self) -> None:
        line = product_hierarchy_line()
        self.assertIn("Probability Engine", line)
        self.assertIn(WORKSPACE_NAME, line)
        assert_no_signal_language(line)

    def test_captions_non_advisory(self) -> None:
        assert_no_signal_language(workspace_context_caption())
        assert_no_signal_language(feedback_path_hint())

    def test_feedback_path_mentions_give_feedback(self) -> None:
        self.assertIn("Give feedback", feedback_path_hint())


if __name__ == "__main__":
    unittest.main()
