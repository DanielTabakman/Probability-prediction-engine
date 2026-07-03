"""Tests for operator pass progress — streak, wait health, evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_operator_pass_progress import (
    OPERATOR_PASSES_FILE,
    assess_pass_progress,
    assess_wait_program,
    classify_wait_health,
    collect_evidence_fingerprint,
    format_pass_lines,
    read_operator_passes,
    record_operator_pass,
)
from scripts.ppe_operator_status import write_status_report
from scripts.workflow_metrics_cli import _append_jsonl, _metrics_dir


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _base_status(**overrides: object) -> dict:
    status = {
        "as_of": _utc_now(),
        "verdict": "RUN_LOCAL",
        "blocker": "IDE product marker present",
        "chapter_name": "test_chapter",
        "phase_plan_path": "docs/SOP/PHASE_PLANS/test_relay.json",
        "manifest_status": "READY",
        "burst_plan": {"remaining_count": 2, "pending_slices": ["A", "B"]},
        "vm_trust": {"wait_for_vm": False, "vm_phase": "HEALTHY_IDLE"},
    }
    status.update(overrides)
    return status


def test_progress_resets_streak_on_slice_close(tmp_path: Path) -> None:
    prior_at = "2026-06-01T10:00:00Z"
    _append_jsonl(
        _metrics_dir(tmp_path) / OPERATOR_PASSES_FILE,
        {
            "pass_at": prior_at,
            "fingerprint": "x",
            "had_progress": False,
            "consecutive_no_progress": 3,
            "no_progress_in_last_10": 3,
            "verdict": "RUN_LOCAL",
            "blocker": "same",
        },
    )
    _append_jsonl(
        _metrics_dir(tmp_path) / "slices.jsonl",
        {
            "slice_id": "Test-Slice-001",
            "completed_at": "2026-06-01T11:00:00Z",
            "status": "closed",
        },
    )
    outcome = assess_pass_progress(tmp_path, _base_status())
    assert outcome["had_progress"] is True
    assert outcome["progress_class"] == "high"
    assert outcome["consecutive_no_progress"] == 0
    assert "Test-Slice-001" in outcome["progress_summary"]


def test_no_progress_increments_streak(tmp_path: Path) -> None:
    record_operator_pass(tmp_path, _base_status(), append=True)
    outcome = assess_pass_progress(tmp_path, _base_status())
    assert outcome["had_progress"] is False
    assert outcome["consecutive_no_progress"] >= 2


def test_waiting_is_not_progress(tmp_path: Path) -> None:
    status = _base_status(
        vm_trust={"wait_for_vm": True, "vm_phase": "FINISH_IN_FLIGHT"},
    )
    (tmp_path / "docs/SOP").mkdir(parents=True)
    (tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json").write_text(
        json.dumps(
            {
                "phase": "FINISH_IN_FLIGHT",
                "as_of": _utc_now(),
                "verdict": "RUN_LOCAL",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    wait = assess_wait_program(tmp_path, status)
    assert wait is not None
    assert wait["kind"] == "vm_in_flight"
    outcome = assess_pass_progress(tmp_path, status)
    assert outcome["had_progress"] is False
    lines = format_pass_lines(outcome)
    assert any("Progress:" in ln and "none" in ln.lower() for ln in lines)
    assert any("Waiting:" in ln for ln in lines)


def test_stuck_when_over_budget_no_evidence(tmp_path: Path) -> None:
    status = _base_status(
        vm_trust={"wait_for_vm": True, "vm_phase": "FINISH_IN_FLIGHT"},
        vm_mirror_health={"stale": False},
    )
    wait = {
        "kind": "vm_in_flight",
        "phase": "FINISH_IN_FLIGHT",
        "waiting_for": "test",
        "expected_seconds": 3600,
        "since_at": "2020-01-01T00:00:00Z",
    }
    evidence = collect_evidence_fingerprint(tmp_path)
    health, _ = classify_wait_health(
        tmp_path,
        wait,
        evidence=evidence,
        prior_evidence=evidence,
        status=status,
    )
    assert health == "stuck"


def test_write_status_report_includes_progress_block(tmp_path: Path) -> None:
    status = _base_status(
        commands=["DESKTOP_CONTINUE.cmd --no-pause"],
        avoid=[],
        preflight_warnings=[],
        errors=[],
        supply={"backlog": {"queued": 0, "blocked": 0}, "queue_ready": 1},
    )
    report = write_status_report(tmp_path, status, sync_burst=False)
    text = report.read_text(encoding="utf-8")
    assert "**Progress:**" in text


def test_dedupe_same_fingerprint_within_window(tmp_path: Path) -> None:
    record_operator_pass(tmp_path, _base_status())
    record_operator_pass(tmp_path, _base_status())
    rows = read_operator_passes(tmp_path)
    assert len(rows) == 1
