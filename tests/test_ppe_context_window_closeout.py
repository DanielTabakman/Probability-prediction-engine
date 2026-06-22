"""Tests for context window closeout gather script."""

from __future__ import annotations

import json
import tempfile
import unittest
from datetime import date, datetime, timezone
from pathlib import Path

from scripts.ppe_context_window_closeout import (
    append_closeout_record,
    build_closeout_record,
    build_sweep_commit_message,
    collect_snapshot,
    committable_dirty_paths,
    effective_working_tree_clean,
    infer_commit_plane,
    infer_whats_next,
    is_never_commit_path,
    load_whats_next_markdown,
    promote_whats_next,
    record_context_closeout,
    render_draft_markdown,
    run_operational_sweep,
    write_artifacts,
)
from scripts.ppe_operator_status import write_status_report
from scripts.ppe_workflow_radar import scan_workflow_friction
from scripts.workflow_metrics_cli import CONTEXT_WINDOWS_FILE, _metrics_dir, read_context_windows


class TestPpeContextWindowCloseout(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        sop = self.repo / "docs" / "SOP"
        sop.mkdir(parents=True)
        (sop / "ACTIVE_PHASE_MANIFEST.json").write_text(
            json.dumps(
                {
                    "status": "READY",
                    "phasePlanPath": "docs/SOP/PHASE_PLANS/msos_user_state_v1_relay.json",
                    "sprintSpecPath": "",
                }
            ),
            encoding="utf-8",
        )
        (sop / "PHASE_QUEUE.json").write_text(json.dumps({"items": []}), encoding="utf-8")
        (sop / "PHASE_CHAPTER_BACKLOG.json").write_text(
            json.dumps({"items": [{"chapterId": "x", "status": "blocked"}]}),
            encoding="utf-8",
        )
        (sop / "HUMAN_STEWARD_BACKLOG.json").write_text(
            json.dumps({"version": 1, "items": []}),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_render_draft_contains_agent_fill_and_machine_sections(self) -> None:
        snapshot = collect_snapshot(self.repo)
        md = render_draft_markdown(self.repo, snapshot)
        self.assertIn("## Machine facts", md)
        self.assertIn("<!-- AGENT_FILL", md)
        self.assertIn("## Follow-up triage", md)
        self.assertIn("AGENT CONTINUITY", md)

    def test_write_artifacts_creates_control_plane_files(self) -> None:
        snapshot = collect_snapshot(self.repo)
        json_path, md_path = write_artifacts(self.repo, snapshot)
        self.assertTrue(json_path.is_file())
        self.assertTrue(md_path.is_file())
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertIn("preflight", payload)
        self.assertIn("operator", payload)

    def test_record_appends_jsonl_and_promotes_whats_next(self) -> None:
        snapshot = {
            "generated_at_utc": "2026-06-10T12:00:00Z",
            "head": "abc",
            "preflight": {"branch": "main", "working_tree": "clean"},
            "manifest": {"phasePlanPath": "docs/SOP/PHASE_PLANS/msos_user_state_v1_relay.json"},
            "manifest_summary": {},
            "operator": {"verdict": "RUN_LOCAL", "commands": ["run_ppe_local.cmd"]},
        }
        record = record_context_closeout(
            self.repo,
            snapshot,
            whats_next="Continue relay",
            thread_role="steward",
        )
        jsonl = _metrics_dir(self.repo) / CONTEXT_WINDOWS_FILE
        self.assertTrue(jsonl.is_file())
        rows = read_context_windows(self.repo)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["closeout_id"], record["closeout_id"])
        wn = load_whats_next_markdown(self.repo)
        self.assertIn("Continue relay", wn or "")
        self.assertEqual(record["chapter_id"], "msos_user_state_v1")

    def test_infer_whats_next_from_operator_commands(self) -> None:
        snap = {"operator": {"commands": ["run_ppe_local.cmd"], "verdict": "RUN_LOCAL"}}
        self.assertIn("run_ppe_local.cmd", infer_whats_next(snap))

    def test_operator_status_includes_whats_next_block(self) -> None:
        snapshot = {
            "generated_at_utc": "2026-06-10T12:00:00Z",
            "head": "abc",
            "preflight": {"branch": "main", "working_tree": "clean"},
            "manifest": {},
            "manifest_summary": {},
            "operator": {"verdict": "RUN_AUTO", "commands": []},
        }
        record_context_closeout(self.repo, snapshot, whats_next="Run the loop")
        status = {
            "as_of": "2026-06-10T12:00:00Z",
            "verdict": "RUN_AUTO",
            "exit_code": 0,
            "phase_plan_path": "",
            "commands": [],
            "avoid": [],
            "preflight_warnings": [],
            "errors": [],
        }
        path = write_status_report(self.repo, status)
        text = path.read_text(encoding="utf-8")
        self.assertIn("What's next", text)
        self.assertIn("Run the loop", text)

    def test_radar_context_chat_churn_signal(self) -> None:
        week = date(2026, 6, 8)
        closed = datetime(2026, 6, 10, 12, 0, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        for _ in range(3):
            append_closeout_record(
                self.repo,
                build_closeout_record(
                    {"generated_at_utc": closed, "preflight": {}, "operator": {}, "manifest": {}},
                    whats_next="x",
                    slices_closed_in_thread=0,
                ),
            )
        candidates, signals = scan_workflow_friction(self.repo, week)
        self.assertIn("context_chat_churn", signals)
        self.assertTrue(any(c.id == "context-chat-churn" for c in candidates))

    def test_is_never_commit_path_blocks_artifacts_and_env(self) -> None:
        self.assertTrue(is_never_commit_path("artifacts/orchestrator/foo.json"))
        self.assertTrue(is_never_commit_path(".env"))
        self.assertFalse(is_never_commit_path("docs/SOP/FOO.md"))

    def test_committable_dirty_paths_filters_exempt(self) -> None:
        preflight = {
            "modified_untracked_paths": [
                "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
                "artifacts/orchestrator/x.json",
                "scripts/ppe_context_window_closeout.py",
            ]
        }
        paths = committable_dirty_paths(preflight)
        self.assertEqual(paths, ["docs/SOP/ACTIVE_PHASE_MANIFEST.json", "scripts/ppe_context_window_closeout.py"])

    def test_effective_working_tree_clean_ignores_artifacts_only(self) -> None:
        preflight = {"modified_untracked_paths": ["artifacts/orchestrator/x.json"]}
        self.assertTrue(effective_working_tree_clean(preflight))

    def test_infer_commit_plane_single_plane(self) -> None:
        self.assertEqual(infer_commit_plane(["docs/SOP/A.md", "docs/SOP/B.md"]), "CONTROL-PLANE")

    def test_build_sweep_commit_message(self) -> None:
        msg = build_sweep_commit_message(
            chapter_id="msos_user_state_v1",
            plane="CONTROL-PLANE",
            paths=["docs/SOP/FOO.md"],
        )
        self.assertIn("msos_user_state_v1", msg)
        self.assertIn("context-closeout sweep", msg)

    def test_render_draft_marks_sweep_checklist(self) -> None:
        snapshot = collect_snapshot(self.repo)
        snapshot["sweep"] = {
            "safe_to_switch": True,
            "committed": True,
            "pushed": True,
            "park_paths": [],
            "blockers": [],
        }
        md = render_draft_markdown(self.repo, snapshot)
        self.assertIn("### Auto sweep result", md)
        self.assertIn("safe_to_switch", md)

    def test_sweep_dry_run_parks_on_main(self) -> None:
        result = run_operational_sweep(
            self.repo,
            dry_run=True,
            chapter_id="test_chapter",
        )
        self.assertIn("actions", result)
        self.assertIsInstance(result["safe_to_switch"], bool)


if __name__ == "__main__":
    unittest.main()
