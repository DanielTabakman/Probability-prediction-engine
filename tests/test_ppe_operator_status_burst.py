"""Operator status ↔ adaptive burst integration."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_burst_plan import BURST_PLAN_REL
from scripts.ppe_operator_status import STATUS_BRIEF_REL, VERDICT_IDE_BUILD, write_status_report


def test_write_status_report_syncs_burst_plan(tmp_path) -> None:
    status = {
        "as_of": "2026-06-30T12:00:00Z",
        "verdict": VERDICT_IDE_BUILD,
        "exit_code": 7,
        "phase_plan_path": "docs/SOP/PHASE_TEST.json",
        "blocker": "PRODUCT_BLOCKED [Slice-A]",
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "[Slice-A]"},
        "commands": ["ppe_go.cmd → new Agent → Ctrl+V → Enter"],
        "avoid": [],
        "preflight_warnings": [],
        "errors": [],
        "supply": {"backlog": {"queued": 1, "blocked": 0}, "queue_ready": 1},
    }
    fake_plan = {
        "max_cycles": 2,
        "overall_band": "NORMAL",
        "remaining_count": 2,
        "burst_allowed": True,
        "use_director": True,
        "prompt": "@ppe-director Adaptive burst mode. max_workers=2",
    }
    with patch("scripts.ppe_burst_plan.refresh_burst_plan", return_value=fake_plan):
        report = write_status_report(tmp_path, status)

    text = report.read_text(encoding="utf-8")
    assert "Burst:" in text
    assert "max_workers=2" in text
    assert "allowed=true" in text
    assert "@ppe-director" in text
    assert status["burst_plan"] == fake_plan
    brief = tmp_path / STATUS_BRIEF_REL
    assert brief.is_file()
    brief_text = brief.read_text(encoding="utf-8")
    assert "Operator Status Brief" in brief_text
    assert "Burst: band=NORMAL remaining=2 allowed=True" in brief_text


def test_write_status_report_burst_writes_json_when_not_mocked(tmp_path) -> None:
    plan_rel = "docs/SOP/PHASE_TEST.json"
    (tmp_path / plan_rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / plan_rel).write_text(
        json.dumps(
            {
                "chapterId": "test_ch",
                "sprintSpecPath": "docs/SOP/SPRINT_TEST.md",
                "slices": [{"sliceId": "Slice-A"}, {"sliceId": "Slice-B"}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs/SOP/SPRINT_TEST.md").write_text("# Test\n" + "line\n" * 50, encoding="utf-8")

    status = {
        "as_of": "2026-06-30T12:00:00Z",
        "verdict": VERDICT_IDE_BUILD,
        "exit_code": 7,
        "phase_plan_path": plan_rel,
        "blocker": "PRODUCT_BLOCKED",
        "guard": {"reason": "PRODUCT_BLOCKED", "detail": "[Slice-A]"},
        "commands": [],
        "avoid": [],
        "preflight_warnings": [],
        "errors": [],
        "supply": {"backlog": {}, "queue_ready": 0},
    }
    with patch(
        "scripts.ppe_loop_host_guard.loop_host_start_allowed",
        return_value=(False, "not_loop_host", ""),
    ):
        with patch("scripts.ppe_burst_plan.run_preflight") as mock_pf:
            mock_pf.return_value = {"overall_band": "NORMAL", "slice_count": 2}
            write_status_report(tmp_path, status)

    burst_path = tmp_path / BURST_PLAN_REL
    assert burst_path.is_file()
    loaded = json.loads(burst_path.read_text(encoding="utf-8"))
    assert loaded["burst_allowed"] is True
    assert loaded["max_cycles"] >= 1
