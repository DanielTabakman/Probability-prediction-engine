"""Tests for ppe_build_packet."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_build_packet import build_packet_path, build_packet_text, write_build_packet


class TestPpeBuildPacket(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        plans = sop / "PHASE_PLANS"
        sop.mkdir(parents=True)
        plans.mkdir(parents=True)
        (sop / "REPO_LAYER_PATH_PREFIXES.json").write_text(
            json.dumps(
                {
                    "presets": {
                        "MSOS_UI": {
                            "layer": "msos-shell",
                            "allowed_paths": ["apps/msos-web/"],
                            "forbidden_paths": ["src/"],
                        }
                    }
                }
            ),
            encoding="utf-8",
        )
        plan = {
            "baselineBranch": "main",
            "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
            "slices": [
                {
                    "sliceId": "Test-Product-Slice001",
                    "declaredPlane": "PRODUCT-PLANE",
                    "layerPreset": "MSOS_UI",
                    "buildBranch": "build/auto/Test-Product-Slice001",
                    "touchSet": ["apps/msos-web/page.tsx"],
                }
            ],
        }
        self.plan_path = "docs/SOP/PHASE_PLANS/test.json"
        (plans / "test.json").write_text(json.dumps(plan), encoding="utf-8")
        (sop / "SPRINT_TEST.md").write_text("# test sprint\n", encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_build_packet_contains_required_fields(self) -> None:
        text = build_packet_text(
            self.repo,
            slice_id="Test-Product-Slice001",
            phase_plan=self.plan_path,
        )
        self.assertIn("EXECUTION STEP: BUILD", text)
        self.assertIn("SLICE_ID: Test-Product-Slice001", text)
        self.assertIn("LAYER_PRESET: MSOS_UI", text)
        self.assertIn("apps/msos-web/page.tsx", text)
        self.assertIn("SPRINT_SPEC: docs/SOP/SPRINT_TEST.md", text)

    def test_write_build_packet(self) -> None:
        out = write_build_packet(
            self.repo,
            slice_id="Test-Product-Slice001",
            phase_plan=self.plan_path,
        )
        assert out is not None
        self.assertTrue(out.is_file())
        self.assertEqual(out.name, Path(build_packet_path("Test-Product-Slice001")).name)


if __name__ == "__main__":
    unittest.main()
