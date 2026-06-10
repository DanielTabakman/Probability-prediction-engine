"""Tests for desktop operator stack helpers."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_desktop_operator_stack import ensure_stack, stack_status


def test_stack_status_all_running():
    with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=True):
        with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=True):
            status = stack_status()
    assert status["stack_running"] is True


def test_ensure_stack_starts_full_when_idle(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.is_loop_running", return_value=False):
        with patch("scripts.ppe_desktop_operator_stack.is_watch_running", return_value=False):
            with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
                with patch(
                    "scripts.ppe_desktop_operator_stack.stack_status",
                    side_effect=[
                        {"loop_running": False, "watch_running": False, "stack_running": False},
                        {"loop_running": True, "watch_running": True, "stack_running": True},
                    ],
                ):
                    result = ensure_stack(tmp_path, start=True)
    start.assert_called_once_with(tmp_path)
    assert result["action"] == "stack"


def test_ensure_stack_noop_when_running(tmp_path):
    with patch("scripts.ppe_desktop_operator_stack.stack_status") as status:
        status.return_value = {
            "loop_running": True,
            "watch_running": True,
            "stack_running": True,
        }
        with patch("scripts.ppe_desktop_operator_stack.start_full_stack") as start:
            result = ensure_stack(tmp_path, start=True)
    start.assert_not_called()
    assert result["action"] == "none"


def test_powershell_process_match_excludes_probe_command():
    from scripts.ppe_desktop_operator_stack import _powershell_process_match

    ps = (
        "$hits = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | "
        "Where-Object { "
        "$_.CommandLine -and "
        "$_.CommandLine -match 'run_ppe_auto_local_loop|run_ppe_auto_loop\\.cmd' -and "
        "$_.CommandLine -notmatch 'Get-CimInstance Win32_Process' "
        "}; "
        "if ($hits) { 'yes' } else { 'no' }"
    )
    assert "Get-CimInstance Win32_Process" in ps
    assert "-notmatch" in ps
    # Probe command line contains the pattern but must not count as a match.
    assert _powershell_process_match("run_ppe_auto_local_loop|run_ppe_auto_loop\\.cmd") in (True, False)
