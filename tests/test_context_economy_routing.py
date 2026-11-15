"""Tests for the public context-economy routing overlay."""

from __future__ import annotations

import unittest

from scripts.context_economy_routing import (
    ACTIVE_DIRECTION_REL,
    BACKLOG_REL,
    CHAPTER_DOC_INDEX_REL,
    CONTINUITY_REL,
    CONTROL_PLANE_REL,
    resolve_role_context_economy,
    resolve_topic_context_economy,
)


class TestContextEconomyRouting(unittest.TestCase):
    def test_generic_founder_route_uses_control_plane_only(self) -> None:
        report = resolve_topic_context_economy("founder charter")
        self.assertTrue(report["ok"])
        self.assertEqual(report["topic_route_id"], "founder_control_plane")
        self.assertEqual(report["load_always"], [CONTROL_PLANE_REL])
        self.assertNotIn(BACKLOG_REL, report["load_always"])
        self.assertNotIn(ACTIVE_DIRECTION_REL, report["load_always"])

    def test_generic_charter_route_requires_a_specific_scope(self) -> None:
        report = resolve_topic_context_economy("charter thread")
        self.assertTrue(report["ok"])
        self.assertEqual(report["topic_route_id"], "charter_scope_required")
        self.assertEqual(report["load_always"], [])
        self.assertEqual(report["next_action"], "name_relevant_program_or_issue")
        self.assertIn(BACKLOG_REL, report["do_not_load"])
        self.assertIn(ACTIVE_DIRECTION_REL, report["do_not_load"])

    def test_explicit_selection_work_preserves_state_route(self) -> None:
        report = resolve_topic_context_economy("selection prep")
        self.assertEqual(report["topic_route_id"], "steward_selection")
        self.assertIn(BACKLOG_REL, report["load_always"])
        self.assertIn(ACTIVE_DIRECTION_REL, report["load_always"])

    def test_chapter_index_is_on_demand_for_sop_discovery(self) -> None:
        report = resolve_topic_context_economy("which sop")
        self.assertEqual(report["topic_route_id"], "sop_discovery")
        self.assertNotIn(CHAPTER_DOC_INDEX_REL, report["load_always"])
        self.assertIn(CHAPTER_DOC_INDEX_REL, report["load_on_demand"])

    def test_operator_continuity_is_freshness_gated(self) -> None:
        report = resolve_role_context_economy("operator")
        self.assertNotIn(CONTINUITY_REL, report["load_always"])
        self.assertIn(CONTINUITY_REL, report["load_on_demand"])
        self.assertIn("fresh and complete", " ".join(report["agent_steps"]))


if __name__ == "__main__":
    unittest.main()
