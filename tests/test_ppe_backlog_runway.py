"""Tests for ppe_backlog_runway."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_backlog_runway import (
    analyze_backlog_runway,
    build_backlog_runway_markdown,
    build_backlog_runway_phone,
    estimate_plan_sus_minutes,
)


class TestPpeBacklogRunway(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs" / "SOP" / "PHASE_PLANS").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _write_plan(self, name: str, *, sus: list[int]) -> str:
        rel = f"docs/SOP/PHASE_PLANS/{name}_relay.json"
        slices: list[dict] = []
        for i, m in enumerate(sus, start=1):
            entry: dict = {
                "sliceId": f"Test-{name}-{i}",
                "susMinutes": m,
                "hardMinutes": m * 2,
            }
            if i == len(sus):
                entry["closeout"] = {"chapterId": name}
            slices.append(entry)
        (self.repo / rel).write_text(json.dumps({"name": name, "slices": slices}), encoding="utf-8")
        return rel

    def _write_backlog(self, items: list[dict]) -> None:
        path = self.repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"version": 1, "items": items}, indent=2), encoding="utf-8")

    def test_estimate_plan_sus_minutes(self) -> None:
        rel = self._write_plan("alpha", sus=[60, 120])
        self.assertEqual(estimate_plan_sus_minutes(self.repo, rel), 180)

    def test_sufficient_runway(self) -> None:
        p1 = self._write_plan("chapter_one", sus=[240, 240])
        p2 = self._write_plan("chapter_two", sus=[480, 480])
        p3 = self._write_plan("chapter_three", sus=[480, 480])
        self._write_backlog(
            [
                {
                    "chapterId": "active_chapter",
                    "status": "chartered",
                    "planPath": p1,
                    "priority": "high",
                    "reason": "[HIGH] Active work",
                },
                {
                    "chapterId": "next_chapter",
                    "status": "blocked",
                    "planPath": p2,
                    "priority": "medium",
                    "reason": "[MEDIUM] Next up after closeout",
                },
                {
                    "chapterId": "later_chapter",
                    "status": "blocked",
                    "planPath": p3,
                    "priority": "low",
                    "reason": "[LOW] Later",
                },
            ]
        )
        report = analyze_backlog_runway(self.repo)
        self.assertTrue(report.sufficient)
        self.assertEqual(report.promotable_count, 2)
        self.assertEqual(report.active_chapter_id, "active_chapter")
        self.assertEqual(report.items[0].priority, "medium")
        self.assertEqual(report.items[0].chapter_id, "next_chapter")

    def test_low_runway(self) -> None:
        rel = self._write_plan("only_one", sus=[120])
        self._write_backlog(
            [
                {
                    "chapterId": "only_one",
                    "status": "blocked",
                    "planPath": rel,
                    "priority": "high",
                    "reason": "[HIGH] Sole chapter",
                }
            ]
        )
        report = analyze_backlog_runway(self.repo)
        self.assertFalse(report.sufficient)
        phone = build_backlog_runway_phone(report)
        self.assertTrue(any("LOW" in line for line in phone))
        md = build_backlog_runway_markdown(report)
        self.assertTrue(any("LOW" in line for line in md))


if __name__ == "__main__":
    unittest.main()
