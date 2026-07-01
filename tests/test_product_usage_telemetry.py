"""Tests for product_usage_telemetry.py."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from src.viz.product_usage_telemetry import log_product_usage_event


class TestProductUsageTelemetry(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.usage_path = self.repo / "data" / "ppe_product_usage.jsonl"
        os.environ["PPE_PRODUCT_USAGE_JSONL"] = str(self.usage_path)

    def tearDown(self) -> None:
        self._tmp.cleanup()
        os.environ.pop("PPE_PRODUCT_USAGE_JSONL", None)

    def test_log_event_appends_jsonl(self) -> None:
        log_product_usage_event("streamlit_lab_view", path="/implied-lab", asset_id="BTC")
        self.assertTrue(self.usage_path.is_file())
        row = json.loads(self.usage_path.read_text(encoding="utf-8").strip())
        self.assertEqual(row["event_name"], "streamlit_lab_view")
        self.assertEqual(row["source"], "streamlit")
        self.assertEqual(row["asset_id"], "BTC")


if __name__ == "__main__":
    unittest.main()
