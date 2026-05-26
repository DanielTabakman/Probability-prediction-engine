from __future__ import annotations

from scripts.watch_active_run import SliceLimits, stall_level


def test_stall_level_none_before_sus() -> None:
    limits = SliceLimits("Slice001", sus_minutes=15, hard_minutes=30)
    assert stall_level(14 * 60, limits) is None


def test_stall_level_sus_at_threshold() -> None:
    limits = SliceLimits("Slice001", sus_minutes=15, hard_minutes=30)
    assert stall_level(15 * 60, limits) == "sus"


def test_stall_level_hard_after_grace() -> None:
    limits = SliceLimits("Slice001", sus_minutes=15, hard_minutes=30)
    # hard = 30*60 + 90s grace
    assert stall_level(30 * 60 + 89, limits) == "sus"
    assert stall_level(30 * 60 + 90, limits) == "hard"
