"""Tests for safe classification of Autobuilder PR backlog."""

from __future__ import annotations

import unittest

from scripts.ppe_autobuilder_pr_cleanup import classify


class TestPpeAutobuilderPrCleanup(unittest.TestCase):
    def test_exact_duplicate_closes_only_older_copy(self) -> None:
        prs = [
            {"number": 10, "headRefName": "ops/loop-publish-old", "headRefOid": "same", "url": "u10"},
            {"number": 11, "headRefName": "ops/loop-publish-new", "headRefOid": "same", "url": "u11"},
        ]
        rows = {row.number: row for row in classify(prs, {10: ["src/a.py"], 11: ["src/a.py"]})}
        self.assertTrue(rows[10].safe_to_close)
        self.assertEqual(rows[10].category, "duplicate_head_sha")
        self.assertEqual(rows[10].retained_number, 11)
        self.assertFalse(rows[11].safe_to_close)

    def test_vm_mirror_is_always_safe_to_close(self) -> None:
        pr = {"number": 12, "headRefName": "ops/vm-mirror-123", "headRefOid": "x", "url": "u"}
        row = classify([pr], {12: ["docs/SOP/VM_OPERATOR_PHASE.json"]})[0]
        self.assertTrue(row.safe_to_close)
        self.assertEqual(row.category, "vm_mirror")

    def test_runtime_only_timestamp_branch_is_safe(self) -> None:
        pr = {"number": 13, "headRefName": "ops/loop-publish-123", "headRefOid": "x", "url": "u"}
        row = classify([pr], {13: ["docs/SOP/PHASE_QUEUE.json", "docs/SOP/VM_OPERATOR_PHASE.json"]})[0]
        self.assertTrue(row.safe_to_close)
        self.assertEqual(row.category, "runtime_only_timestamp_branch")

    def test_unique_product_diff_requires_manual_reconciliation(self) -> None:
        pr = {"number": 14, "headRefName": "ops/loop-publish-123", "headRefOid": "x", "url": "u"}
        row = classify([pr], {14: ["src/ppe/app.py"]})[0]
        self.assertFalse(row.safe_to_close)
        self.assertEqual(row.category, "unique_or_mixed_timestamp_branch")


if __name__ == "__main__":
    unittest.main()
