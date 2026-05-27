"""Pytest witness for MVP1-Sprint003-Witness-Slice003 (EVIDENCE-PLANE)."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVIDENCE_STATUS = REPO / "docs" / "SOP" / "MVP1_SPRINT003_EVIDENCE_PLANE_EVIDENCE_STATUS.md"

# Recorded at Witness-Slice003 closeout on steward branch (197 baseline + 3 witness tests).
WITNESS_PYTEST_COUNT = 215


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
    # pytest -q collect-only ends with "N tests collected in ..."
    tail = proc.stdout.strip().splitlines()[-1]
    collected = int(tail.split()[0])
    assert collected == WITNESS_PYTEST_COUNT


def test_evidence_status_records_pytest_and_ruff_witness() -> None:
    text = EVIDENCE_STATUS.read_text(encoding="utf-8")
    assert str(WITNESS_PYTEST_COUNT) in text
    assert "Witness-Slice003" in text
    assert "**PASS**" in text
    assert "ruff" in text.lower()
