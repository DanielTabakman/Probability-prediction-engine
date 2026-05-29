"""Pytest witness for MVP1-Sprint003-Witness-Slice003 (EVIDENCE-PLANE)."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Recorded at Witness-Slice003 BUILD (main + 2 witness tests in this module).
WITNESS_PYTEST_COUNT = 247


def test_ruff_check_scripts_tests_passes() -> None:
    proc = subprocess.run(
        ["python", "-m", "ruff", "check", "scripts", "tests"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_pytest_collect_count_matches_witness() -> None:
    proc = subprocess.run(
        ["python", "-m", "pytest", "--collect-only", "-q"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    tail = proc.stdout.strip().splitlines()[-1]
    collected = int(tail.split()[0])
    assert collected == WITNESS_PYTEST_COUNT

