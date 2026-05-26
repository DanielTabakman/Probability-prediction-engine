"""Tests for UI smoke scenario auto-selection and failure diagnosis."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.implied_lab_ui_smoke_harness import (
    PRIMARY_SMOKE_SCENARIO_COMPACT,
    PRIMARY_SMOKE_SCENARIO_FULL_LAB,
    primary_smoke_scenario,
)
from scripts.ui_smoke_diagnose import diagnose_manifest, diagnose_smoke_text


class TestPrimarySmokeScenario(unittest.TestCase):
    def test_primary_is_scenario_a(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(primary_smoke_scenario(), PRIMARY_SMOKE_SCENARIO_FULL_LAB)
        with patch.dict("os.environ", {"PPE_POST_MVP1_LAB_UI": "1"}, clear=True):
            self.assertEqual(primary_smoke_scenario(), PRIMARY_SMOKE_SCENARIO_FULL_LAB)


class TestUiSmokeDiagnose(unittest.TestCase):
    def test_mode_expander_mismatch(self) -> None:
        hit = diagnose_smoke_text(
            notes="RuntimeError: Could not find expander header: Mode & solver (Exact strikes vs Target payoff)",
            scenario="A_width_target_payoff",
        )
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertEqual(hit.category, "mvp1_scenario_mismatch")

    def test_manifest_mode_mismatch(self) -> None:
        manifest = {
            "workflow_hardening_slice003_closeout": {
                "detail": "Could not find expander header: Mode & solver",
            },
            "scenarios": [
                {
                    "scenario": "A_width_target_payoff",
                    "notes": "RuntimeError: Could not find expander header: Mode & solver",
                }
            ],
        }
        hit = diagnose_manifest(manifest)
        self.assertIsNotNone(hit)
        assert hit is not None
        self.assertIn("MVP1_compact", hit.suggested_fix)


if __name__ == "__main__":
    unittest.main()
