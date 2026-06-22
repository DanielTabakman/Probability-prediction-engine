"""Tests for bounded BUILD gate repair."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from scripts.ppe_build_repair import (
    build_repair_max_attempts,
    load_repair_state,
    run_bounded_gate,
)


def test_build_repair_max_attempts_default(tmp_path: Path):
    assert build_repair_max_attempts(tmp_path) == 3


def test_build_repair_max_attempts_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_REPAIR_MAX_ATTEMPTS", "5")
    assert build_repair_max_attempts(tmp_path) == 5


def test_run_bounded_gate_pass_clears_state(tmp_path: Path):
    with patch("scripts.ppe_build_repair.run_pushable_gate", return_value=(0, "ok")):
        result = run_bounded_gate(tmp_path, slice_id="Test-Slice001")
    assert result["ok"] is True
    assert load_repair_state(tmp_path).get("attempts") == 0


def test_run_bounded_gate_retries_until_exhausted(tmp_path: Path):
    with patch("scripts.ppe_build_repair.run_pushable_gate", return_value=(1, "fail")):
        r1 = run_bounded_gate(tmp_path, slice_id="Test-Slice001")
        r2 = run_bounded_gate(tmp_path, slice_id="Test-Slice001")
        r3 = run_bounded_gate(tmp_path, slice_id="Test-Slice001")
    assert r1["ok"] is False and not r1["exhausted"]
    assert r2["ok"] is False and not r2["exhausted"]
    assert r3["ok"] is False and r3["exhausted"]
    hint = tmp_path / "artifacts/orchestrator/BUILD_REPAIR_HINT.md"
    assert hint.is_file()
