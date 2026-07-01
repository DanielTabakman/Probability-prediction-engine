"""Tests for operator doctor, closeout preflight, morning health line."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_morning_report import build_morning_report
from scripts.ppe_operator_branch_preflight import assess_operator_branch_preflight
from scripts.ppe_operator_doctor import format_doctor_report, run_operator_doctor
from scripts.ppe_preflight import run_preflight


def test_closeout_branch_preflight_allows_control_plane(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        "scripts.ppe_operator_branch_preflight._current_branch",
        lambda repo: "control-plane/foo",
    )
    monkeypatch.setattr("scripts.ppe_operator_branch_preflight._dirty_paths", lambda repo: [])
    pf = assess_operator_branch_preflight(
        tmp_path,
        verdict="RUN_LOCAL",
        loop_host_allowed=False,
        chapter_mode={"mode": "CLOSEOUT_ONLY"},
    )
    assert pf["blocks_relay"] is False


def test_preflight_closeout_skips_branch_warning(tmp_path, monkeypatch) -> None:
    (tmp_path / "docs" / "SOP").mkdir(parents=True)
    (tmp_path / "docs" / "SOP" / "ACTIVE_PHASE_MANIFEST.json").write_text(
        json.dumps({"status": "READY", "phasePlanPath": "docs/SOP/PHASE_PLANS/x_relay.json"})
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "SOP" / "PHASE_QUEUE.json").write_text('{"items":[]}\n', encoding="utf-8")
    (tmp_path / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json").write_text('{"items":[]}\n', encoding="utf-8")
    monkeypatch.setattr(
        "subprocess.run",
        lambda *a, **k: type(
            "P",
            (),
            {
                "returncode": 0,
                "stdout": "control-plane/test\n" if a[0][:2] == ["git", "branch"] else " M docs/foo.md\n",
                "stderr": "",
            },
        )(),
    )
    monkeypatch.setattr("scripts.ppe_preflight._closeout_only_context", lambda repo, manifest: True)
    monkeypatch.setattr("scripts.ppe_preflight._orchestrator_root", lambda repo: tmp_path)
    monkeypatch.setattr(
        "scripts.ppe_queue_health.run_queue_health",
        lambda repo, apply=True: {"fixes": [], "remaining_issues": []},
    )
    result = run_preflight(tmp_path, check_orchestrator=False)
    joined = " ".join(result.get("warnings") or [])
    assert "not main" not in joined
    assert "uncommitted changes" not in joined


def test_morning_report_includes_health_line(tmp_path) -> None:
    _title, body = build_morning_report(
        tmp_path,
        {"verdict": "RUN_LOCAL", "operator_health_line": "health: gh=ok ntfy=ok spots=0"},
    )
    assert "health: gh=ok" in body
    assert "Infra:" in body


def test_doctor_format_report() -> None:
    text = format_doctor_report(
        {
            "ok": False,
            "verdict": "RUN_LOCAL",
            "checks": [{"id": "gh_auth", "ok": True}],
            "blind_spots": {
                "operator_health_line": "health: gh=ok spots=1",
                "issues": [{"severity": "high", "message": "test", "fix": "fix it"}],
            },
        }
    )
    assert "ACTION NEEDED" in text
    assert "test" in text


def test_run_operator_doctor_no_ssh(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("PPE_NTFY_TOPIC", "t")
    with patch("scripts.ppe_operator_status.prepare_operator_status", return_value={"verdict": "RUN_AUTO"}):
        with patch("scripts.ppe_operator_blind_spots._gh_auth_ok", return_value=(True, "")):
            with patch("scripts.ppe_operator_blind_spots._open_vm_mirror_prs", return_value=[]):
                with patch(
                    "scripts.check_vm_host_health.collect_host_health",
                    return_value={"healthy": True, "alerts": []},
                ):
                    with patch(
                        "scripts.ppe_chapter_coordination.assess_chapter_coordination_health",
                        return_value={"ok": True, "issue_count": 0, "high_count": 0},
                    ):
                        report = run_operator_doctor(tmp_path, probe_ssh=False, write_artifacts=False)
    assert "checks" in report
    check_ids = {c.get("id") for c in report.get("checks") or [] if isinstance(c, dict)}
    assert "chapter_coordination" in check_ids
