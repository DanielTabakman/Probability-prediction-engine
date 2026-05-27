"""Tier classification for scripts/run_pushable_gate.py (tier 0/1/2)."""

from __future__ import annotations

import unittest

from scripts.run_pushable_gate import GatePlan, _classify


class TestRunPushableGateTiers(unittest.TestCase):
    def test_tier0_docs_only(self) -> None:
        plan = _classify(["docs/SOP/HANDOFF.md", "docs/VISION/foo.md"])
        self.assertEqual(plan.tier, 0)
        self.assertEqual(plan.commands, [])

    def test_tier1_control_plane_without_src(self) -> None:
        plan = _classify(["scripts/run_pushable_gate.py", "tests/test_foo.py"])
        self.assertEqual(plan.tier, 1)
        self.assertIn(["python", "-m", "ruff", "check", "scripts", "tests"], plan.commands)
        self.assertIn(["python", "-m", "pytest", "-q"], plan.commands)

    def test_tier2_any_src_touch(self) -> None:
        plan = _classify(["src/viz/app.py", "tests/test_app.py"])
        self.assertEqual(plan.tier, 2)
        self.assertIn(["python", "-m", "ruff", "check", "src", "tests", "scripts"], plan.commands)

    def test_tier0_empty_change_set(self) -> None:
        plan = _classify([])
        self.assertEqual(plan.tier, 0)
        self.assertIsInstance(plan, GatePlan)


if __name__ == "__main__":
    unittest.main()
