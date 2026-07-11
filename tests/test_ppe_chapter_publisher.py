"""Deterministic tests for one-chapter/one-PR publication policy."""

from __future__ import annotations

import unittest
from datetime import datetime, timezone

from scripts.ppe_chapter_publisher import (
    PublicationDecision,
    chapter_branch,
    chapter_marker,
    evaluate_circuit_breakers,
    extract_chapter_id,
    is_runtime_only_path,
    runtime_only_paths,
    slugify_chapter_id,
)


class TestPpeChapterPublisher(unittest.TestCase):
    def test_stable_chapter_branch_and_marker(self) -> None:
        self.assertEqual(slugify_chapter_id("MSOS / Demo Slice 1"), "msos-demo-slice-1")
        self.assertEqual(chapter_branch("MSOS / Demo Slice 1"), "chapter/msos-demo-slice-1")
        marker = chapter_marker("MSOS / Demo Slice 1")
        self.assertEqual(extract_chapter_id(marker), "msos-demo-slice-1")

    def test_runtime_paths_are_rejected(self) -> None:
        paths = [
            "src/ppe/app.py",
            "artifacts/control_plane/VM_OPERATOR_PHASE.json",
            "docs/SOP/VM_OPERATOR_PHASE.json",
            "docs/SOP/PHASE_QUEUE.json",
        ]
        self.assertEqual(
            runtime_only_paths(paths),
            [
                "artifacts/control_plane/VM_OPERATOR_PHASE.json",
                "docs/SOP/PHASE_QUEUE.json",
                "docs/SOP/VM_OPERATOR_PHASE.json",
            ],
        )
        self.assertFalse(is_runtime_only_path("src/ppe/app.py"))

    def test_existing_chapter_pr_is_updated_not_replaced(self) -> None:
        prs = [
            {
                "number": 10,
                "headRefName": "chapter/demo",
                "headRefOid": "abc",
                "createdAt": "2026-07-11T17:00:00Z",
                "body": "<!-- ppe-chapter-id: demo -->",
            }
        ]
        decision = evaluate_circuit_breakers(
            prs,
            chapter_id="demo",
            branch="chapter/demo",
            sha="abc",
            now=datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc),
        )
        self.assertEqual(decision, PublicationDecision(True, "update_existing_pr", prs[0]))

    def test_same_chapter_on_another_branch_blocks(self) -> None:
        prs = [
            {
                "number": 10,
                "headRefName": "ops/closeout-old",
                "headRefOid": "abc",
                "createdAt": "2026-07-11T17:00:00Z",
                "body": "<!-- ppe-chapter-id: demo -->",
            }
        ]
        decision = evaluate_circuit_breakers(
            prs,
            chapter_id="demo",
            branch="chapter/demo",
            sha="def",
            now=datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("another branch", decision.reason)

    def test_duplicate_sha_blocks(self) -> None:
        prs = [
            {"number": 1, "headRefName": "ops/a", "headRefOid": "same", "createdAt": "2026-07-11T16:00:00Z", "body": "Auto-published"},
            {"number": 2, "headRefName": "ops/b", "headRefOid": "same", "createdAt": "2026-07-11T16:00:00Z", "body": "Auto-published"},
        ]
        decision = evaluate_circuit_breakers(
            prs,
            chapter_id="demo",
            branch="chapter/demo",
            sha="same",
            now=datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("duplicate", decision.reason)

    def test_rate_breaker_blocks_three_recent_auto_prs(self) -> None:
        prs = [
            {
                "number": i,
                "headRefName": f"ops/loop-publish-{i}",
                "headRefOid": str(i),
                "createdAt": f"2026-07-11T17:{40 + i:02d}:00Z",
                "body": "Auto-published",
            }
            for i in range(3)
        ]
        decision = evaluate_circuit_breakers(
            prs,
            chapter_id="demo",
            branch="chapter/demo",
            sha="new",
            now=datetime(2026, 7, 11, 18, 0, tzinfo=timezone.utc),
        )
        self.assertFalse(decision.allowed)
        self.assertIn("30 minutes", decision.reason)


if __name__ == "__main__":
    unittest.main()
