"""Tests for zero-churn verification classification."""

from __future__ import annotations

import unittest

from scripts.ppe_autobuilder_churn_verify import is_churn_pr


class TestPpeAutobuilderChurnVerify(unittest.TestCase):
    def test_timestamp_publish_is_churn(self) -> None:
        self.assertTrue(is_churn_pr({"headRefName": "ops/loop-publish-123", "body": ""}))

    def test_vm_mirror_body_is_churn(self) -> None:
        self.assertTrue(is_churn_pr({"headRefName": "other", "body": "Auto-published VM phase mirror"}))

    def test_chapter_pr_is_not_churn(self) -> None:
        self.assertFalse(
            is_churn_pr(
                {
                    "headRefName": "chapter/msos-demo",
                    "body": "<!-- ppe-chapter-id: msos-demo -->",
                }
            )
        )


if __name__ == "__main__":
    unittest.main()
