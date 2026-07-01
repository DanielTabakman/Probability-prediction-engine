"""Tests for ppe_jsonl_retention.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_jsonl_retention import apply_retention, rotate_file


class TestPpeJsonlRetention(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_rotate_when_over_threshold(self) -> None:
        path = self.repo / "data" / "ppe_product_usage.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("x" * 200, encoding="utf-8")
        rotated = rotate_file(path, max_bytes=100, keep=2, dry_run=False)
        self.assertTrue(rotated)
        self.assertTrue(path.is_file())
        archives = list(path.parent.glob("ppe_product_usage.*.jsonl"))
        self.assertEqual(len(archives), 1)

    def test_no_rotate_under_threshold(self) -> None:
        path = self.repo / "data" / "ppe_product_usage.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("small", encoding="utf-8")
        rotated = rotate_file(path, max_bytes=1000, keep=2, dry_run=False)
        self.assertFalse(rotated)

    def test_apply_retention_dry_run(self) -> None:
        path = self.repo / "data" / "ppe_product_usage.jsonl"
        path.parent.mkdir(parents=True)
        path.write_text("y" * 500, encoding="utf-8")
        count = apply_retention(self.repo, max_mb=0.0001, keep=1, dry_run=True)
        self.assertEqual(count, 1)
        self.assertEqual(path.stat().st_size, 500)


if __name__ == "__main__":
    unittest.main()
