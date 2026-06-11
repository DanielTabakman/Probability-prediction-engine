"""Guard-stop notification dedup."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_guard_notify_dedup import (
    notify_fingerprint,
    record_guard_notify,
    should_skip_guard_notify,
    state_path,
)


class TestPpeGuardNotifyDedup(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "PPE_AUTO_OPERATOR.json").write_text(
            json.dumps({"guardStopSleepSeconds": 120}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_skip_after_recent_identical_notify(self) -> None:
        status = {
            "verdict": "IDE_BUILD",
            "blocker": "needs IDE BUILD",
            "phase_plan_path": "docs/SOP/PHASE_PLANS/foo.json",
        }
        record_guard_notify(self.repo, status)
        self.assertTrue(should_skip_guard_notify(self.repo, status))

    def test_no_skip_when_verdict_changes(self) -> None:
        first = {"verdict": "IDE_BUILD", "blocker": "a", "phase_plan_path": "p1"}
        second = {"verdict": "FIX_PLAN", "blocker": "a", "phase_plan_path": "p1"}
        record_guard_notify(self.repo, first)
        self.assertFalse(should_skip_guard_notify(self.repo, second))

    def test_no_skip_after_cooldown_elapsed(self) -> None:
        status = {"verdict": "IDE_BUILD", "blocker": "blocked", "phase_plan_path": "p"}
        record_guard_notify(self.repo, status)
        old = (datetime.now(timezone.utc) - timedelta(seconds=400)).isoformat().replace("+00:00", "Z")
        state_path(self.repo).write_text(
            json.dumps({"fingerprint": notify_fingerprint(status), "last_notified_at": old}),
            encoding="utf-8",
        )
        self.assertFalse(should_skip_guard_notify(self.repo, status))


if __name__ == "__main__":
    unittest.main()
