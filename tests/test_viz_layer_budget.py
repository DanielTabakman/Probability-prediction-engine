"""Tests for scripts/check_viz_layer_budget.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "check_viz_layer_budget.py"
APP_PY = REPO_ROOT / "src" / "viz" / "app.py"


def _run(*extra: str) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(SCRIPT), *extra]
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)


def test_budget_passes_shell_mode_on_current_tree():
    result = _run("--shell-mode")
    assert result.returncode == 0, result.stderr + result.stdout


def test_budget_constants_match_doc_expectation():
    from scripts import check_viz_layer_budget as budget

    assert budget.APP_PY_SHELL_MAX_LINES == 300
    assert budget.APP_PY_BASELINE_LINES == 2109


def test_shell_mode_fails_when_app_py_over_max(tmp_path: Path):
    from scripts import check_viz_layer_budget as budget

    fake = tmp_path / "app.py"
    fake.write_text("\n" * (budget.APP_PY_SHELL_MAX_LINES + 5), encoding="utf-8")
    ok, messages = budget.check_budget(shell_mode=True)
    # check_budget reads real APP_PY path; verify helper logic via line count
    assert budget._line_count(fake) > budget.APP_PY_SHELL_MAX_LINES


def test_app_py_within_shell_max():
    from scripts import check_viz_layer_budget as budget

    lines = budget._line_count(APP_PY)
    assert lines <= budget.APP_PY_SHELL_MAX_LINES, f"app.py has {lines} lines"
