"""Tests for IDE BUILD starter doc-resolve injection."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_ide_build_starter import build_starter_md


class TestPpeIdeBuildStarterDocResolve(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        plans = self.repo / "docs" / "SOP" / "PHASE_PLANS"
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True, exist_ok=True)
        plans.mkdir(parents=True, exist_ok=True)
        self.plan_rel = "docs/SOP/PHASE_PLANS/ppe_exposure_menu_v1_relay.json"
        (plans / "ppe_exposure_menu_v1_relay.json").write_text(
            json.dumps(
                {
                    "sprintSpecPath": "docs/SOP/SPRINT_PPE_EXPOSURE_MENU_V1.md",
                    "selectionRecord": "docs/SOP/POST_PPE_EXPOSURE_MENU_V1_SELECTION.md",
                    "slices": [
                        {
                            "sliceId": "Ch-Exposure-Slice002",
                            "declaredPlane": "PRODUCT-PLANE",
                            "layerPreset": "PPE_UI",
                            "buildBranch": "build/auto/Ch-Exposure-Slice002",
                            "touchSet": ["src/viz/exposure_menu.py"],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )
        (sop / "SPRINT_PPE_EXPOSURE_MENU_V1.md").write_text("# sprint\n", encoding="utf-8")
        (sop / "POST_PPE_EXPOSURE_MENU_V1_SELECTION.md").write_text("# sel\n", encoding="utf-8")
        (sop / "EXPOSURE_MENU_PROGRAM_V1.md").write_text("# program\n", encoding="utf-8")
        presets_src = Path(__file__).resolve().parents[1] / "docs" / "SOP" / "REPO_LAYER_PATH_PREFIXES.json"
        if presets_src.is_file():
            (sop / "REPO_LAYER_PATH_PREFIXES.json").write_text(
                presets_src.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_starter_includes_doc_resolve_block(self) -> None:
        md = build_starter_md(
            self.repo,
            slice_id="Ch-Exposure-Slice002",
            phase_plan=self.plan_rel,
        )
        self.assertIn("**Doc resolve:**", md)
        self.assertIn("load_for_build:", md)
        self.assertIn("**skip:**", md)
        self.assertIn("SPRINT_PPE_EXPOSURE_MENU_V1.md", md)


if __name__ == "__main__":
    unittest.main()
