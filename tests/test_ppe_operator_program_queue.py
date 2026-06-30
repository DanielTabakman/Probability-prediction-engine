"""Tests for program-level operator queue."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_format_est_hours_range() -> None:
    from scripts.ppe_operator_program_queue import format_est_hours

    assert format_est_hours(4, 3) == "~9–15h"
    assert format_est_hours(1, 4) == "~4h"


def test_build_program_queue_counts_slices() -> None:
    from scripts.ppe_operator_program_queue import build_program_queue

    programs = build_program_queue(REPO, {"verdict": "SUPPLY_LOW"})
    by_id = {p["id"]: p for p in programs}
    assert by_id["program_trader_learning_spine"]["slices_remaining"] == 4
    assert by_id["program_asset_batch_wave1"]["slices_remaining"] == 4
