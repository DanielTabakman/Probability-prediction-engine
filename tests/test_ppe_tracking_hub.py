"""Tests for ppe_tracking_hub and extended workflow metrics."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.ppe_tracking_hub import (
    collect_asset_enablement,
    collect_factory_signals,
    collect_steering_drift,
    collect_tracking_snapshot,
    format_operator_tracking_lines,
    format_tracking_digest_lines,
    format_usage_line,
    record_event,
    record_validation_session,
    render_tracking_rollup_html,
    scan_tracking_friction,
    write_tracking_artifacts,
    zero_activity_watch_line,
)
from scripts.workflow_metrics_cli import (
    append_slice_close_row,
    cmd_summary,
    events_in_days,
    read_events,
)


class TestPpeTrackingHub(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_record_event_and_factory_signals(self) -> None:
        record_event(self.repo, event_type="usage_note", note="test", value_1=1)
        self.assertEqual(len(read_events(self.repo)), 1)
        self.assertEqual(len(events_in_days(self.repo, 7)), 1)
        factory = collect_factory_signals(self.repo, days=7)
        self.assertEqual(factory["tracking_events"], 1)

    def test_validation_session_dual_write(self) -> None:
        row = {
            "date": "2026-06-30",
            "profile": "tester",
            "clarity": "Y",
            "return_again": "Y",
            "notes": "demo ok",
        }
        record_validation_session(self.repo, row)
        events = read_events(self.repo)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "validation_session")

    def test_slice_incident_flag_auto(self) -> None:
        append_slice_close_row(
            self.repo,
            slice_id="Slice-HighRt",
            size="M",
            roundtrips=3,
            source="test",
        )
        from scripts.workflow_metrics_cli import _read_jsonl, _metrics_dir, SLICES_FILE

        rows = _read_jsonl(_metrics_dir(self.repo) / SLICES_FILE)
        self.assertTrue(rows[0].get("incident_flag"))
        self.assertIn("slice_kind", rows[0])

    def test_collect_snapshot_and_operator_lines(self) -> None:
        snap = collect_tracking_snapshot(self.repo, days=7)
        self.assertIn("steering", snap)
        self.assertIn("assets", snap)
        self.assertIn("trader_outcomes", snap)
        lines = format_operator_tracking_lines(self.repo, days=7)
        self.assertTrue(any("Tracking:" in line for line in lines))

    def test_asset_enablement(self) -> None:
        assets = collect_asset_enablement(self.repo)
        self.assertTrue(assets.get("available"))
        self.assertGreaterEqual(assets.get("enabled_count", 0), 1)

    def test_steering_drift_structure(self) -> None:
        steering = collect_steering_drift(self.repo)
        self.assertIn("aligned", steering)
        self.assertIn("gap_count", steering)

    def test_summary_include_validation_flag(self) -> None:
        append_slice_close_row(
            self.repo,
            slice_id="Slice-X",
            size="S",
            roundtrips=1,
            source="test",
        )
        self.assertEqual(cmd_summary(self.repo, days=7, include_validation=True), 0)

    def test_tracking_digest_lines(self) -> None:
        lines = format_tracking_digest_lines(self.repo, days=7)
        self.assertIsInstance(lines, list)
        self.assertLessEqual(len(lines), 7)

    def test_format_usage_line_sessions(self) -> None:
        line = format_usage_line(
            {
                "total_events": 10,
                "exists": True,
                "unique_users": 2,
                "session_starts": 3,
                "page_views": 5,
                "streamlit_events": 2,
                "top_event": "page_view",
            }
        )
        self.assertIn("sessions=3", line or "")
        self.assertIn("streamlit=2", line or "")

    def test_zero_activity_watch_after_deploy(self) -> None:
        from datetime import datetime, timedelta, timezone

        deploy = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.repo / "data").mkdir(parents=True)
        (self.repo / "data" / "last_vps_deploy.utc").write_text(deploy, encoding="utf-8")
        usage = {"total_events": 0, "exists": True}
        line = zero_activity_watch_line(self.repo, usage)
        self.assertIsNotNone(line)
        self.assertIn("ZERO", line or "")

    def test_render_rollup_html_and_write(self) -> None:
        snap = collect_tracking_snapshot(self.repo, days=7)
        html = render_tracking_rollup_html(snap)
        self.assertIn("PPE tracking rollup", html)
        json_path, md_path, html_path = write_tracking_artifacts(self.repo, snap)
        self.assertTrue(html_path.is_file())
        self.assertTrue(json_path.is_file())
        self.assertTrue(md_path.is_file())

    def test_scan_friction_zero_usage_post_deploy(self) -> None:
        from datetime import date, datetime, timedelta, timezone

        deploy = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.repo / "data").mkdir(parents=True)
        (self.repo / "data" / "last_vps_deploy.utc").write_text(deploy, encoding="utf-8")
        snap = collect_tracking_snapshot(self.repo, days=7)
        candidates = scan_tracking_friction(self.repo, date.today())
        ids = [c.id for c in candidates]
        self.assertIn("product-usage-zero-post-deploy", ids)


if __name__ == "__main__":
    unittest.main()
