"""Tests for triggered ideas parking lot."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_triggered_ideas import (
    active_items,
    add_item,
    close_item,
    find_matches,
    load_backlog,
    match_item,
    render_markdown,
    resolve_chapter_id,
)


class TestPpeTriggeredIdeas(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        plans = sop / "PHASE_PLANS"
        plans.mkdir(parents=True)
        (plans / "msos_wallet_connect_v1_relay.json").write_text(
            json.dumps(
                {
                    "name": "MSOS wallet connect v1",
                    "sprintSpecPath": "docs/SOP/SPRINT_MSOS_WALLET_CONNECT_V1.md",
                    "slices": [{"sliceId": "X", "closeout": {}}],
                }
            ),
            encoding="utf-8",
        )
        (sop / "SPRINT_MSOS_WALLET_CONNECT_V1.md").write_text(
            "# Wallet connect\n\nConnect user wallet for on-chain reads.\n",
            encoding="utf-8",
        )
        (sop / "TRIGGERED_IDEAS.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "items": [
                        {
                            "id": "web3_uniblock_revisit",
                            "title": "Revisit Uniblock",
                            "summary": "Deferred vendor decision",
                            "status": "parked",
                            "priority": "low",
                            "triggers": {
                                "chapterIds": ["msos_wallet_connect_v1"],
                                "keywords": ["wallet connect"],
                            },
                            "notFor": ["msos_user_state_v1"],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_resolve_chapter_id_from_plan_filename(self) -> None:
        cid = resolve_chapter_id(
            self.repo,
            "docs/SOP/PHASE_PLANS/msos_wallet_connect_v1_relay.json",
        )
        self.assertEqual(cid, "msos_wallet_connect_v1")

    def test_match_wallet_chapter(self) -> None:
        plan = "docs/SOP/PHASE_PLANS/msos_wallet_connect_v1_relay.json"
        matches = find_matches(self.repo, plan_path=plan)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].item_id, "web3_uniblock_revisit")

    def test_not_for_excludes(self) -> None:
        item = load_backlog(self.repo)["items"][0]
        ctx = {
            "chapter_id": "msos_user_state_v1",
            "plan_path": "docs/SOP/PHASE_PLANS/msos_user_state_v1_relay.json",
            "text": "msos_user_state_v1 wallet connect",
        }
        self.assertIsNone(match_item(item, ctx))

    def test_dismiss_removes_from_active(self) -> None:
        close_item(self.repo, "web3_uniblock_revisit", status="dismissed", resolution="not needed")
        self.assertEqual(len(active_items(self.repo)), 0)

    def test_purge_removes_row(self) -> None:
        close_item(self.repo, "web3_uniblock_revisit", status="dismissed", purge=True)
        self.assertEqual(len(load_backlog(self.repo).get("items") or []), 0)

    def test_add_item(self) -> None:
        add_item(
            self.repo,
            title="Try feature X",
            summary="Later",
            idea_id="feature_x",
            trigger_keywords=["feature x"],
        )
        items = load_backlog(self.repo)["items"]
        self.assertEqual(len(items), 2)

    def test_render_markdown_lists_active(self) -> None:
        md = render_markdown(self.repo)
        self.assertIn("Revisit Uniblock", md)
        self.assertIn("web3_uniblock_revisit", md)


if __name__ == "__main__":
    unittest.main()
