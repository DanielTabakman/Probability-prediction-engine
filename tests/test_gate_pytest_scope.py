"""Tests for scripts/gate_pytest_scope.py."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.gate_pytest_scope import resolve_scoped_tests


REPO = Path(__file__).resolve().parents[1]


class TestGatePytestScope(unittest.TestCase):
    def test_scripts_ppe_maps_to_ppe_tests(self) -> None:
        paths = resolve_scoped_tests(["scripts/ppe_auto_select.py"], REPO)
        assert paths is not None
        self.assertIn("tests/test_ppe_auto_select.py", paths)
        self.assertIn("tests/test_run_pushable_gate.py", paths)

    def test_scripts_ppe_notify_maps_without_fallback(self) -> None:
        paths = resolve_scoped_tests(["scripts/ppe_notify_push.py"], REPO)
        assert paths is not None
        self.assertIn("tests/test_ppe_notify_push.py", paths)

    def test_src_viz_maps_to_viz_tests(self) -> None:
        paths = resolve_scoped_tests(["src/viz/app.py"], REPO)
        assert paths is not None
        self.assertIn("tests/test_mvp1_lab_ui.py", paths)

    def test_queue_json_falls_back_to_none(self) -> None:
        self.assertIsNone(resolve_scoped_tests(["docs/SOP/PHASE_QUEUE.json"], REPO))

    def test_changed_test_file_included(self) -> None:
        paths = resolve_scoped_tests(["tests/test_signup_cta.py"], REPO)
        assert paths is not None
        self.assertIn("tests/test_signup_cta.py", paths)


if __name__ == "__main__":
    unittest.main()
