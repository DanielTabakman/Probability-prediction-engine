"""Tests for phase plan agent schema validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_manifest import (
    format_acceptance_checklist,
    is_product_plane_slice,
    recommended_loads_for_slice,
    validate_phase_plan,
    validate_manifest,
)
from scripts.validate_phase_plans import validate_plans


class TestValidatePhasePlan(unittest.TestCase):
    def test_product_slice_requires_touch_set_when_strict(self) -> None:
        plan = {
            "slices": [
                {
                    "sliceId": "X-Product-Slice001",
                    "declaredPlane": "PRODUCT-PLANE",
                },
                {"sliceId": "X-Closeout", "closeout": {"chapterId": "x"}},
            ]
        }
        assert not validate_phase_plan(plan)
        assert validate_phase_plan(plan, strict_agent_schema=True)

    def test_acceptance_shape(self) -> None:
        plan = {
            "slices": [
                {
                    "sliceId": "X-Product-Slice001",
                    "declaredPlane": "PRODUCT-PLANE",
                    "touchSet": ["src/viz/app.py"],
                    "acceptance": [{"id": "a", "check": "ok", "verify": "tests/test_x.py"}],
                },
                {"sliceId": "X-Closeout", "closeout": {"chapterId": "x"}},
            ]
        }
        assert not validate_phase_plan(plan, strict_agent_schema=True)

    def test_format_acceptance_checklist(self) -> None:
        md = format_acceptance_checklist([{"id": "x", "check": "does y", "verify": "tests/t.py"}])
        self.assertIn("`x`", md)
        self.assertIn("does y", md)

    def test_recommended_loads_includes_touch_set(self) -> None:
        sl = {
            "declaredPlane": "PRODUCT-PLANE",
            "touchSet": ["src/viz/app.py"],
            "acceptance": [{"id": "a", "check": "c", "verify": "tests/test_foo.py"}],
        }
        loads = recommended_loads_for_slice(
            Path("."),
            slice_obj=sl,
            slice_id="Slice-A",
            phase_plan="docs/SOP/PHASE_PLANS/p.json",
            layer_preset="PPE_UI",
        )
        self.assertIn("src/viz/app.py", loads)
        self.assertIn("docs/SOP/agent_index/ppe-ui.md", loads)
        self.assertIn("tests/test_foo.py", loads)

    def test_is_product_plane_slice(self) -> None:
        self.assertTrue(is_product_plane_slice({"declaredPlane": "PRODUCT-PLANE"}))
        self.assertFalse(is_product_plane_slice({"declaredPlane": "EVIDENCE-PLANE"}))

    def test_manifest_validates_active_plan_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            sop = repo / "docs" / "SOP"
            sop.mkdir(parents=True)
            plan_path = sop / "PHASE_PLANS" / "ok_relay.json"
            plan_path.parent.mkdir(parents=True)
            plan_path.write_text(
                json.dumps(
                    {
                        "slices": [
                            {
                                "sliceId": "P-Slice001",
                                "declaredPlane": "PRODUCT-PLANE",
                                "touchSet": ["src/viz/a.py"],
                            },
                            {"sliceId": "P-Closeout", "closeout": {"chapterId": "p"}},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
                json.dumps(
                    {
                        "status": "READY",
                        "phasePlanPath": "docs/SOP/PHASE_PLANS/ok_relay.json",
                    }
                ),
                encoding="utf-8",
            )
            (sop / "SPRINT_X.md").write_text("# x\n", encoding="utf-8")
            errors = validate_manifest(repo)
            self.assertEqual(errors, [])

    def test_validate_plans_cli_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            plan_dir = repo / "docs" / "SOP" / "PHASE_PLANS"
            plan_dir.mkdir(parents=True)
            plan_file = plan_dir / "t_relay.json"
            plan_file.write_text(
                json.dumps(
                    {
                        "slices": [
                            {
                                "sliceId": "T-Product",
                                "declaredPlane": "PRODUCT-PLANE",
                                "touchSet": ["a.py"],
                            },
                            {"sliceId": "T-Close", "closeout": {}},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            errors, warnings = validate_plans(repo, paths=[plan_file], strict=True, check_test_names=False)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
