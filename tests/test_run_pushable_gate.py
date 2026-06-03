"""Tier classification for scripts/run_pushable_gate.py (tier 0/1/2)."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_pushable_gate import (
    FAST_PYTEST_MARKER,
    GatePlan,
    _classify,
    _union_paths,
    pytest_cmd,
    resolve_changed_files,
)


class TestRunPushableGateTiers(unittest.TestCase):
    def test_tier0_docs_only(self) -> None:
        plan = _classify(["docs/SOP/HANDOFF.md", "docs/VISION/foo.md"])
        self.assertEqual(plan.tier, 0)
        self.assertEqual(plan.commands, [])

    def test_tier1_control_plane_fast_pytest(self) -> None:
        plan = _classify(["scripts/run_pushable_gate.py", "tests/test_foo.py"])
        self.assertEqual(plan.tier, 1)
        self.assertIn(["python", "-m", "ruff", "check", "scripts", "tests"], plan.commands)
        self.assertIn(["python", "-m", "pytest", "-q", "-m", FAST_PYTEST_MARKER], plan.commands)

    def test_tier1_control_plane_full_pytest(self) -> None:
        plan = _classify(["scripts/run_pushable_gate.py"], pytest_profile="full")
        self.assertIn(["python", "-m", "pytest", "-q"], plan.commands)

    def test_tier2_any_src_touch(self) -> None:
        plan = _classify(["src/viz/app.py", "tests/test_app.py"])
        self.assertEqual(plan.tier, 2)
        self.assertIn(["python", "-m", "ruff", "check", "src", "tests", "scripts"], plan.commands)

    def test_tier0_empty_change_set(self) -> None:
        plan = _classify([])
        self.assertEqual(plan.tier, 0)
        self.assertIsInstance(plan, GatePlan)

    def test_union_paths_dedupes_and_preserves_order(self) -> None:
        merged = _union_paths(
            ["docs/SOP/HANDOFF.md"],
            ["docs/SOP/HANDOFF.md", "src/viz/app.py"],
        )
        self.assertEqual(merged, ["docs/SOP/HANDOFF.md", "src/viz/app.py"])

    def test_classify_union_with_src_is_tier2(self) -> None:
        """Simulates main...HEAD empty but upstream..HEAD touches src/."""
        plan = _classify(_union_paths([], ["apps/msos-web/page.tsx", "src/foo.py"]))
        self.assertEqual(plan.tier, 2)

    def test_pytest_cmd_profiles(self) -> None:
        self.assertEqual(pytest_cmd("full"), ["python", "-m", "pytest", "-q"])
        self.assertEqual(
            pytest_cmd("fast"),
            ["python", "-m", "pytest", "-q", "-m", FAST_PYTEST_MARKER],
        )


class TestResolveChangedFiles(unittest.TestCase):
    def test_pre_push_requires_upstream(self) -> None:
        with patch("scripts.run_pushable_gate._upstream_ref", return_value=None):
            with self.assertRaises(ValueError):
                resolve_changed_files(Path("."), pre_push=True)


if __name__ == "__main__":
    unittest.main()
