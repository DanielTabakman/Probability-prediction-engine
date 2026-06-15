"""Tests for smoke mode resolution in ppe_slice_worker."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.ppe_slice_worker import _pytest_targets, _resolve_smoke_mode, _smoke_required


class TestPpeSliceWorkerSmokeMode(unittest.TestCase):
    def test_default_is_a(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_resolve_smoke_mode(None), "a")

    def test_slice_smoke_mode_dual(self) -> None:
        self.assertEqual(_resolve_smoke_mode({"smokeMode": "dual"}), "dual")

    def test_env_dual_smoke(self) -> None:
        with patch.dict(os.environ, {"PPE_DUAL_SMOKE": "1"}, clear=False):
            self.assertEqual(_resolve_smoke_mode(None), "dual")

    def test_docs_only_witness_skips_smoke(self) -> None:
        slice_obj = {
            "touchSet": ["docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md"],
        }
        self.assertFalse(_smoke_required(slice_obj))

    def test_smoke_mode_skip(self) -> None:
        self.assertFalse(_smoke_required({"smokeMode": "skip", "touchSet": ["apps/msos-web/"]}))

    def test_platform_pytest_scope(self) -> None:
        targets = _pytest_targets(
            "MSOS-ProdWireV1-Platform-Slice003",
            {"layerPreset": "PLATFORM", "touchSet": ["docker-compose.yml"]},
        )
        self.assertEqual(targets, ["tests/test_msos_web_platform_production_wiring.py"])

    def test_docs_witness_skips_pytest(self) -> None:
        targets = _pytest_targets(
            "MSOS-ProdWireV1-Witness-Slice004",
            {"touchSet": ["docs/SOP/MSOS_PRODUCTION_WIRING_V1_EVIDENCE_STATUS.md"]},
        )
        self.assertEqual(targets, [])


if __name__ == "__main__":
    unittest.main()
