"""Tests for smoke mode resolution in ppe_slice_worker."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.ppe_slice_worker import _resolve_smoke_mode


class TestPpeSliceWorkerSmokeMode(unittest.TestCase):
    def test_default_is_a(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_resolve_smoke_mode(None), "a")

    def test_slice_smoke_mode_dual(self) -> None:
        self.assertEqual(_resolve_smoke_mode({"smokeMode": "dual"}), "dual")

    def test_env_dual_smoke(self) -> None:
        with patch.dict(os.environ, {"PPE_DUAL_SMOKE": "1"}, clear=False):
            self.assertEqual(_resolve_smoke_mode(None), "dual")


if __name__ == "__main__":
    unittest.main()
