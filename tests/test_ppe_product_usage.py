"""Tests for ppe_product_usage."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_product_usage import (
    PRODUCT_USAGE_FILENAME,
    pull_usage_from_container,
    read_usage_events,
    resolve_usage_path,
    summarize_usage,
)


class TestPpeProductUsage(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_summarize_empty(self) -> None:
        summary = summarize_usage(self.repo, days=7)
        self.assertEqual(summary["total_events"], 0)
        self.assertFalse(summary["exists"])

    def test_read_jsonl_rows(self) -> None:
        path = self.repo / "data" / "ppe_product_usage.jsonl"
        path.parent.mkdir(parents=True)
        row = {"event_name": "page_view", "created_at_utc": datetime.now(timezone.utc).isoformat()}
        path.write_text(json.dumps(row) + "\n", encoding="utf-8")
        rows = read_usage_events(path)
        self.assertEqual(len(rows), 1)
        summary = summarize_usage(self.repo, days=7)
        self.assertEqual(summary["total_events"], 1)
        self.assertEqual(summary["top_event"], "page_view")

    def test_resolve_usage_path_jsonl_env(self) -> None:
        custom = self.repo / "mirror" / PRODUCT_USAGE_FILENAME
        custom.parent.mkdir(parents=True)
        with patch.dict(os.environ, {"PPE_PRODUCT_USAGE_JSONL": str(custom)}, clear=False):
            self.assertEqual(resolve_usage_path(self.repo), custom)

    def test_pull_usage_from_container(self) -> None:
        dest = self.repo / "data" / PRODUCT_USAGE_FILENAME
        with patch("scripts.ppe_product_usage.subprocess.run") as run:
            run.return_value.returncode = 0
            out = pull_usage_from_container(self.repo, container="msos_web")
        self.assertEqual(out, dest)
        run.assert_called_once()
        args = run.call_args[0][0]
        self.assertEqual(args[0], "docker")
        self.assertEqual(args[1], "cp")
        self.assertEqual(args[2], f"msos_web:/data/{PRODUCT_USAGE_FILENAME}")


if __name__ == "__main__":
    unittest.main()
