"""Tests for minimal IDE BUILD starter generation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_ide_build_starter import (
    STARTER_LINE_ESCALATE,
    build_starter_md,
    format_build_closeout_section,
    starter_line_band,
)


class TestPpeIdeBuildStarter(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop.mkdir(parents=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/phase.json"
        (sop / "phase.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_X.md",
                    "slices": [
                        {
                            "sliceId": "Ch-Product-Slice002",
                            "declaredPlane": "PRODUCT-PLANE",
                            "layerPreset": "PPE_UI",
                            "buildBranch": "build/auto/Ch-Product-Slice002-local",
                            "touchSet": ["src/viz/app.py"],
                            "acceptance": [
                                {"id": "renders", "check": "App renders", "verify": "tests/test_app_smoke.py"},
                            ],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (self.repo / "docs" / "SOP" / "SPRINT_X.md").write_text(
            "## Sprint intent\n\nDo thing.\n\n## Slice map\n\n| Ch-Product-Slice002 | PRODUCT | PPE_UI | x |\n",
            encoding="utf-8",
        )
        presets_src = Path(__file__).resolve().parents[1] / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json"
        if presets_src.is_file():
            (self.repo / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json").write_text(
                presets_src.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_minimal_starter_under_budget(self) -> None:
        md = build_starter_md(self.repo, slice_id="Ch-Product-Slice002", phase_plan=self.plan_rel)
        lines = len(md.splitlines())
        self.assertLessEqual(lines, STARTER_LINE_ESCALATE, msg=f"starter too long: {lines} lines")
        self.assertIn("**Acceptance:**", md)
        self.assertIn("`renders`", md)
        self.assertIn("touchSet", md)
        self.assertNotIn("Continuity excerpt", md)
        self.assertNotIn("Slim BUILD packet", md)
        self.assertEqual(starter_line_band(lines), "NORMAL")

    def test_format_build_closeout_section(self) -> None:
        body = format_build_closeout_section(slice_id="Ch-Product-Slice002", phase_plan=self.plan_rel)
        self.assertIn("run_pushable_gate.py", body)
        self.assertIn(self.plan_rel, body)


if __name__ == "__main__":
    unittest.main()
