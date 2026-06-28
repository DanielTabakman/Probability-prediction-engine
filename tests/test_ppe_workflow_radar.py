"""Tests for ppe_workflow_radar."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts.ppe_workflow_radar import (
    auto_cleanup_orphans,
    build_radar_report,
    cmd_generate,
    load_radar_friction_lines,
    radar_json_path,
    scan_orphans,
    scan_workflow_friction,
    write_radar_artifacts,
)
from scripts.workflow_metrics_cli import _append_jsonl, _metrics_dir


class TestPpeWorkflowRadar(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        (self.repo / "docs" / "RELEASES").mkdir(parents=True)
        (self.repo / "artifacts" / "orchestrator").mkdir(parents=True)
        (self.repo / ".cursor").mkdir(parents=True)
        self.week = date(2026, 6, 8)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _seed_slices(self, rows: list[dict]) -> None:
        path = _metrics_dir(self.repo) / "slices.jsonl"
        for row in rows:
            _append_jsonl(path, row)

    def test_high_roundtrips_candidate(self) -> None:
        completed = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        self._seed_slices(
            [
                {"slice_id": "A", "completed_at": completed, "roundtrips": 4},
                {"slice_id": "B", "completed_at": completed, "roundtrips": 3},
            ]
        )
        candidates, signals = scan_workflow_friction(self.repo, self.week)
        self.assertIn("high_roundtrips", signals)
        ids = [c.id for c in candidates]
        self.assertIn("high-roundtrips", ids)

    def test_guard_stop_candidate(self) -> None:
        guard = self.repo / "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
        mid_week = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc).timestamp()
        guard.write_text(
            "# Operator guard stop\n\n**Reason:** `CONTEXT_WATCH`\n",
            encoding="utf-8",
        )
        import os

        os.utime(guard, (mid_week, mid_week))
        candidates, _ = scan_workflow_friction(self.repo, self.week)
        self.assertTrue(any(c.id == "guard-stop" for c in candidates))

    def test_stale_build_lock_orphan(self) -> None:
        lock = self.repo / "artifacts/orchestrator/REMOTE_BUILD_LOCK.json"
        lock.write_text(
            json.dumps({"worker_pid": 999999, "started_at": "2026-01-01T00:00:00Z"}),
            encoding="utf-8",
        )
        with mock.patch("scripts.ppe_remote_agent_spawn.process_alive", return_value=False):
            findings = scan_orphans(self.repo)
        self.assertTrue(any(f.id == "stale-build-lock" and f.auto_cleanable for f in findings))

    def test_cleanup_stale_build_lock(self) -> None:
        lock = self.repo / "artifacts/orchestrator/REMOTE_BUILD_LOCK.json"
        lock.write_text(json.dumps({"worker_pid": 999999}), encoding="utf-8")
        with mock.patch("scripts.ppe_remote_agent_spawn.process_alive", return_value=False):
            actions = auto_cleanup_orphans(self.repo, dry_run=False)
        self.assertTrue(any(a.action == "cleared" for a in actions))
        self.assertFalse(lock.is_file())

    def test_orphan_post_build_job_cleanup(self) -> None:
        job = self.repo / "artifacts/orchestrator/POST_BUILD_FINISH_JOB_12345.json"
        job.write_text("{}", encoding="utf-8")
        old = (datetime.now(timezone.utc) - timedelta(hours=5)).timestamp()
        import os

        os.utime(job, (old, old))
        actions = auto_cleanup_orphans(self.repo, dry_run=False)
        self.assertTrue(any(a.action == "deleted" for a in actions))
        self.assertFalse(job.is_file())

    def test_generate_and_digest_friction_lines(self) -> None:
        completed = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        self._seed_slices(
            [
                {"slice_id": "A", "completed_at": completed, "roundtrips": 4},
                {"slice_id": "B", "completed_at": completed, "roundtrips": 3},
            ]
        )
        with mock.patch(
            "scripts.ppe_workflow_radar._token_friction_candidates",
            return_value=([], {"verdict": "OK"}),
        ):
            self.assertEqual(cmd_generate(self.repo, week_monday=self.week, run_cleanup=False), 0)
        self.assertTrue(radar_json_path(self.repo, self.week).is_file())
        lines = load_radar_friction_lines(self.repo, self.week)
        self.assertTrue(lines)
        self.assertIn("roundtrips", lines[0].lower())

    def test_write_radar_artifacts(self) -> None:
        report = build_radar_report(self.repo, self.week, run_cleanup=False)
        week_path, md_path = write_radar_artifacts(self.repo, report)
        self.assertTrue(week_path.is_file())
        self.assertTrue(md_path.is_file())
        data = json.loads(week_path.read_text(encoding="utf-8"))
        self.assertEqual(data["week_monday"], "2026-06-08")


if __name__ == "__main__":
    unittest.main()
