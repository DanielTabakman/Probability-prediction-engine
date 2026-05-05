"""MVP1 lab UI flags."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.viz.mvp1_lab_ui import post_mvp1_lab_ui_enabled


class TestPostMvp1LabUi(unittest.TestCase):
    def test_default_off(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(post_mvp1_lab_ui_enabled())
        with patch.dict("os.environ", {"PPE_POST_MVP1_LAB_UI": ""}, clear=True):
            self.assertFalse(post_mvp1_lab_ui_enabled())
        with patch.dict("os.environ", {"PPE_POST_MVP1_LAB_UI": "0"}, clear=True):
            self.assertFalse(post_mvp1_lab_ui_enabled())

    def test_truthy_values(self) -> None:
        for v in ("1", "true", "TRUE", "yes", "on"):
            with patch.dict("os.environ", {"PPE_POST_MVP1_LAB_UI": v}, clear=True):
                self.assertTrue(
                    post_mvp1_lab_ui_enabled(),
                    msg=f"expected truthy for {v!r}",
                )
