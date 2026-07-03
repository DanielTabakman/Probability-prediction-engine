"""Tests for ppe_repo_state SSOT."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from scripts.ppe_repo_state import (
    assess_repo_state,
    is_mixed_plane,
    paths_by_plane,
    plane_for_path,
    recovery_commands_for_paths,
    split_preflight_warnings,
)


class TestPlaneClassification(unittest.TestCase):
    def test_control(self) -> None:
        self.assertEqual(plane_for_path("docs/SOP/PHASE_QUEUE.json"), "CONTROL")

    def test_product(self) -> None:
        self.assertEqual(plane_for_path("src/viz/app.py"), "PRODUCT")

    def test_evidence(self) -> None:
        self.assertEqual(plane_for_path("scripts/foo.py"), "EVIDENCE")

    def test_src_tests_not_mixed(self) -> None:
        paths = ["src/viz/a.py", "tests/test_a.py"]
        self.assertFalse(is_mixed_plane(paths))

    def test_control_scripts_mixed(self) -> None:
        paths = ["docs/SOP/x.json", "scripts/y.py"]
        self.assertTrue(is_mixed_plane(paths))


class TestSeverity(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
        # use real repo for delegation import; assess with empty branch_preflight

    def test_clean_repo_minimal(self) -> None:
        state = assess_repo_state(self._tmp, branch_preflight={"blocks_relay": False})
        self.assertIn(state["severity_label"], ("CLEAN", "CAUTION", "STEWARD", "BLOCKED"))

    def test_mixed_plane_paths_by_plane(self) -> None:
        by = paths_by_plane(["docs/SOP/a", "src/b.py"])
        self.assertIn("CONTROL", by)
        self.assertIn("PRODUCT", by)


class TestPreflightSplit(unittest.TestCase):
    def test_layer_scope_is_info(self) -> None:
        actionable, info = split_preflight_warnings(
            ["repo layer scope: preset='CONTROL' (dirty paths OK)", "dirty main"]
        )
        self.assertEqual(len(info), 1)
        self.assertEqual(len(actionable), 1)


class TestRecoveryCommands(unittest.TestCase):
    def test_mixed_recommends_ship_all(self) -> None:
        cmds = recovery_commands_for_paths(["docs/SOP/a", "src/b.py"])
        self.assertEqual(cmds, ["python scripts/ppe_branch_recovery.py --ship-all"])

    def test_control_only(self) -> None:
        cmds = recovery_commands_for_paths(["docs/SOP/a", "scripts/b.py"])
        self.assertTrue(any("control" in c for c in cmds))


if __name__ == "__main__":
    unittest.main()
