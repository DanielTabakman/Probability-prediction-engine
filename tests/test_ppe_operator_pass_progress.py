"""Tests for operator pass progress — streak, wait health, evidence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_operator_pass_progress import (
    OPERATOR_PASSES_FILE,
    _budget_for_phase,
    assess_pass_progress,
    assess_wait_program,
    backfill_operator_passes,
    classify_wait_health,
    collect_evidence_fingerprint,
    format_pass_lines,
    read_operator_passes,
    record_operator_pass,
    scan_operator_pass_friction,
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
    assert outcome["progress_class"] == "low"
    lines = format_pass_lines(outcome)
    assert any("Progress:" in ln and "low" in ln.lower() for ln in lines)
    assert any("Waiting:" in ln for ln in lines)


def test_format_pass_lines_includes_monitor(tmp_path: Path) -> None:
    outcome = {
        "had_progress": False,
        "progress_summary": "none",
        "consecutive_no_progress": 1,
        "wait_health": "quiet",
        "wait": {"waiting_for": "VM wait"},
        "wait_elapsed_s": 600,
        "wait_expected_s": 3600,
        "monitor": {
            "phase": "FINISH_IN_FLIGHT",
            "elapsed_in_phase_m": 10,
            "next_poll_m": 30,
            "mirror_stale": True,
        },
    }
    lines = format_pass_lines(outcome)
    assert any("**Monitor:**" in ln for ln in lines)
    assert any("mirror stale" in ln for ln in lines)


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


def test_low_progress_when_vm_in_flight(tmp_path: Path) -> None:
    status = _base_status(
        vm_trust={"wait_for_vm": True, "vm_phase": "FINISH_IN_FLIGHT"},
    )
    (tmp_path / "docs/SOP").mkdir(parents=True)
    (tmp_path / "docs/SOP/VM_OPERATOR_PHASE.json").write_text(
        json.dumps({"phase": "FINISH_IN_FLIGHT", "as_of": _utc_now()}) + "\n",
        encoding="utf-8",
    )
    outcome = assess_pass_progress(tmp_path, status)
    assert outcome["progress_class"] == "low"
    assert outcome["had_progress"] is False
    lines = format_pass_lines(outcome)
    assert any("low" in ln.lower() for ln in lines)


def test_backfill_from_context_windows(tmp_path: Path) -> None:
    from scripts.workflow_metrics_cli import CONTEXT_WINDOWS_FILE

    _append_jsonl(
        _metrics_dir(tmp_path) / CONTEXT_WINDOWS_FILE,
        {
            "closed_at": "2026-06-01T12:00:00Z",
            "slices_closed_in_thread": 0,
            "operator_verdict": "RUN_LOCAL",
            "chapter_id": "test",
        },
    )
    report = backfill_operator_passes(tmp_path, limit=10)
    assert report["added"] == 1
    rows = read_operator_passes(tmp_path)
    assert rows[0].get("backfill") is True


def test_scan_operator_pass_friction(tmp_path: Path) -> None:
    for i in range(8):
        _append_jsonl(
            _metrics_dir(tmp_path) / OPERATOR_PASSES_FILE,
            {
                "pass_at": f"2026-06-0{i+1}T12:00:00Z",
                "had_progress": False,
                "consecutive_no_progress": i + 1,
            },
        )
    latest = tmp_path / "artifacts/control_plane/OPERATOR_PASS_LATEST.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(
        json.dumps({"consecutive_no_progress": 8, "wait_health": "quiet"}) + "\n",
        encoding="utf-8",
    )
    candidates, signals = scan_operator_pass_friction(tmp_path)
    assert signals.get("operator_no_progress_streak", 0) >= 7
    assert any(c.id == "operator-no-progress-streak" for c in candidates)


def test_median_budget_from_slices(tmp_path: Path) -> None:
    for i, hours in enumerate((1, 2, 3)):
        _append_jsonl(
            _metrics_dir(tmp_path) / "slices.jsonl",
            {
                "slice_id": f"Test-Closeout-Slice00{i}",
                "started_at": f"2026-06-0{i+1}T10:00:00Z",
                "completed_at": f"2026-06-0{i+1}T{10+hours}:00:00Z",
            },
        )
    budget = _budget_for_phase(tmp_path, "FINISH_IN_FLIGHT")
    assert budget >= 3600
