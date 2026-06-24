"""Tier classification for scripts/run_pushable_gate.py (tier 0/1/2)."""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.run_pushable_gate import (
    FAST_PYTEST_MARKER,
    GatePlan,
    _classify,
    _msos_web_gate_commands,
    _touches_msos_web,
    _union_paths,
    pytest_cmd,
    pytest_commands,
    resolve_changed_files,
)

REPO = Path(__file__).resolve().parents[1]


class TestRunPushableGateTiers(unittest.TestCase):
    def test_tier0_docs_only(self) -> None:
        plan = _classify(["docs/SOP/HANDOFF.md"], repo=REPO)
        self.assertEqual(plan.tier, 0)
        self.assertEqual(plan.commands, [])

    def test_tier1_control_plane_fast_pytest(self) -> None:
        plan = _classify(["scripts/ppe_auto_select.py"], repo=REPO, pytest_profile="fast")
        self.assertEqual(plan.tier, 1)
        self.assertTrue(any(c[0:3] == ["python", "-m", "ruff"] for c in plan.commands))

    def test_tier2_any_src_touch(self) -> None:
        plan = _classify(["src/viz/app.py"], repo=REPO)
        self.assertEqual(plan.tier, 2)

    def test_pytest_cmd_profiles(self) -> None:
        self.assertIn(FAST_PYTEST_MARKER, pytest_cmd("fast"))
        full_cmds = pytest_commands("full")
        self.assertEqual(len(full_cmds), 2)
        self.assertIn("not slow", " ".join(full_cmds[0]))

    def test_union_paths_dedupes_and_preserves_order(self) -> None:
        merged = _union_paths(
            ["docs/SOP/HANDOFF.md"],
            ["docs/SOP/HANDOFF.md", "src/viz/app.py"],
        )
        self.assertEqual(merged, ["docs/SOP/HANDOFF.md", "src/viz/app.py"])

    def test_touches_msos_web_prefix(self) -> None:
        self.assertTrue(_touches_msos_web(["apps/msos-web/src/middleware.ts"]))
        self.assertFalse(_touches_msos_web(["docs/SOP/HANDOFF.md"]))

    def test_msos_web_gate_pre_push_full_build(self) -> None:
        cmds = _msos_web_gate_commands(["apps/msos-web/src/page.tsx"], pre_push=True)
        self.assertEqual(cmds, [["python", "scripts/verify_msos_web_build.py"]])

    def test_msos_web_gate_wip_witness_only(self) -> None:
        cmds = _msos_web_gate_commands(["apps/msos-web/src/page.tsx"], pre_push=False)
        self.assertEqual(
            cmds,
            [["python", "scripts/verify_msos_web_build.py", "--witness-only"]],
        )


class TestResolveChangedFiles(unittest.TestCase):
    def test_pre_push_requires_upstream(self) -> None:
        with patch("scripts.run_pushable_gate._upstream_ref", return_value=None):
            with self.assertRaises(ValueError):
                resolve_changed_files(Path("."), pre_push=True)


if __name__ == "__main__":
    unittest.main()
