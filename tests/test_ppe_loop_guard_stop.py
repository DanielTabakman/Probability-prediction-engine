"""Tests for guard-stop loop keepalive helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_loop_guard_stop import main as loop_guard_main


class TestPpeLoopGuardStop(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_keepalive_prints_sleep_seconds(self) -> None:
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps({"keepLoopAliveOnGuardStop": True, "guardStopSleepSeconds": 420}),
            encoding="utf-8",
        )
        rc = loop_guard_main(["--repo-root", str(self.repo)])
        self.assertEqual(rc, 0)

    def test_exit_when_keepalive_disabled(self) -> None:
        (self.repo / "docs" / "SOP" / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps({"keepLoopAliveOnGuardStop": False}),
            encoding="utf-8",
        )
        rc = loop_guard_main(["--repo-root", str(self.repo)])
        self.assertEqual(rc, 7)


if __name__ == "__main__":
    unittest.main()
