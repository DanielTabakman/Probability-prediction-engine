"""Witness: MSOS public copy banned-term scanner."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_msos_public_copy_validation_passes() -> None:
    script = REPO_ROOT / "scripts" / "validate_msos_public_copy.py"
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_msos_public_copy_catches_banned_fixture() -> None:
    from scripts.validate_msos_public_copy import _check_literal

    errors = _check_literal(1, "This is a fixture label", "test.ts")
    assert any("fixture" in e for e in errors)


def test_msos_public_copy_allows_probability_engine() -> None:
    from scripts.validate_msos_public_copy import _check_literal

    errors = _check_literal(1, "Probability Engine", "test.ts")
    assert not errors
