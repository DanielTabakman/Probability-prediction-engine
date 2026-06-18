"""Single-instance guard for auto-loop."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from scripts.ppe_loop_singleton import main as singleton_main


class TestPpeLoopSingleton(unittest.TestCase):
    def test_exits_when_loop_already_running(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "PPE_HEADLESS_SUPERVISED_LOOP"}
        with patch.dict(os.environ, env, clear=True):
            with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=True):
                self.assertEqual(singleton_main([]), 1)

    def test_ok_when_no_loop(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "PPE_HEADLESS_SUPERVISED_LOOP"}
        with patch.dict(os.environ, env, clear=True):
            with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=False):
                self.assertEqual(singleton_main([]), 0)

    def test_ok_when_headless_supervised_loop_even_if_loop_running(self) -> None:
        with patch.dict(os.environ, {"PPE_HEADLESS_SUPERVISED_LOOP": "1"}, clear=False):
            with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=True):
                self.assertEqual(singleton_main([]), 0)


if __name__ == "__main__":
    unittest.main()
