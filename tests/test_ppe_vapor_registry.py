"""Tests for product vapor registry auto-populate / depopulate."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_vapor_registry import (
    discover_vapor,
    merge_vapor_items,
    open_vapor_items,
    render_markdown,
    sync_registry,
)


class TestPpeVaporRegistry(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PRODUCT_VAPOR_REGISTRY.json").write_text(
            json.dumps({"version": 1, "manual": [], "items": []}),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "planPath": "docs/SOP/PHASE_PLANS/shipped_chapter_v1_relay.json",
                            "status": "DONE",
                        },
                        {
                            "planPath": "docs/SOP/PHASE_PLANS/active_chapter_v1_relay.json",
                            "status": "READY",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "chapterId": "deferred_chapter_v1",
                            "status": "deferred",
                            "priority": "low",
                            "reason": "test deferred chapter",
                        },
                        {
                            "chapterId": "shipped_chapter_v1",
                            "status": "deferred",
                            "priority": "low",
                            "reason": "should depopulate when queue DONE",
                        },
                        {
                            "chapterId": "active_chapter_v1",
                            "status": "chartered",
                            "priority": "medium",
                            "reason": "should depopulate when queue READY",
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_discover_includes_static_and_backlog(self) -> None:
        found = discover_vapor(self.repo)
        ids = {i["id"] for i in found}
        self.assertIn("mode:hedging", ids)
        self.assertIn("chapter:deferred_chapter_v1", ids)

    def test_depopulate_done_and_ready_chapters(self) -> None:
        open_items, closed = merge_vapor_items(self.repo)
        open_ids = {i["id"] for i in open_items}
        closed_ids = {c.get("id") for c in closed}
        self.assertIn("chapter:deferred_chapter_v1", open_ids)
        self.assertIn("chapter:shipped_chapter_v1", closed_ids)
        self.assertIn("chapter:active_chapter_v1", closed_ids)
        shipped = next(c for c in closed if c.get("id") == "chapter:shipped_chapter_v1")
        self.assertEqual(shipped.get("status"), "shipped")
        active = next(c for c in closed if c.get("id") == "chapter:active_chapter_v1")
        self.assertEqual(active.get("status"), "in_queue")

    def test_manual_pin_survives(self) -> None:
        reg = self.repo / "docs" / "SOP" / "PRODUCT_VAPOR_REGISTRY.json"
        data = json.loads(reg.read_text(encoding="utf-8"))
        data["manual"] = [
            {
                "id": "custom:steward_note",
                "title": "Steward note",
                "vaporType": "doc",
                "priority": "high",
                "why": "Pinned by operator",
                "pin": True,
                "status": "open",
            }
        ]
        reg.write_text(json.dumps(data), encoding="utf-8")
        open_items = open_vapor_items(self.repo)
        self.assertTrue(any(i["id"] == "custom:steward_note" for i in open_items))

    def test_sync_writes_markdown(self) -> None:
        sync_registry(self.repo, render_md=True, patch_compass=False)
        md = (self.repo / "docs" / "SOP" / "PRODUCT_VAPOR_REGISTRY.md").read_text(encoding="utf-8")
        self.assertIn("Product vapor registry", md)
        self.assertIn("Open (not in active relay)", md)

    def test_render_markdown_table(self) -> None:
        md = render_markdown(
            self.repo,
            {
                "items": [
                    {
                        "id": "x",
                        "title": "Test",
                        "priority": "high",
                        "vaporType": "ui",
                        "why": "Because",
                        "auto": True,
                    }
                ],
                "open_count": 1,
            },
        )
        self.assertIn("Test", md)


if __name__ == "__main__":
    unittest.main()
