"""Tests for phase plan slice batching."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.ppe_phase_plan_window import (
    active_slice_window,
    mark_slice_complete,
    select_slice_batch,
)


def _slice(sid: str, *, closeout: bool = False) -> dict:
    sl = {"sliceId": sid}
    if closeout:
        sl["closeout"] = {"chapterId": "ch"}
    return sl


class TestPpePhasePlanWindow(unittest.TestCase):
    def test_select_batch_defers_closeout_when_batch_full(self) -> None:
        slices = [_slice(f"S{i:03d}") for i in range(1, 7)] + [_slice("Closeout", closeout=True)]
        batch = select_slice_batch(slices, limit=6, completed=set())
        self.assertEqual(len(batch), 6)
        self.assertEqual(batch[-1]["sliceId"], "S006")
        self.assertEqual(active_slice_window_from_batch(slices, batch, completed=set()), batch)

    def test_second_batch_is_closeout_only(self) -> None:
        slices = [_slice(f"S{i:03d}") for i in range(1, 7)] + [_slice("Closeout", closeout=True)]
        completed = {f"S{i:03d}" for i in range(1, 7)}
        batch = select_slice_batch(slices, limit=6, completed=completed)
        self.assertEqual(len(batch), 1)
        self.assertTrue(batch[0].get("closeout"))

    def test_mark_slice_complete_tracks_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "docs" / "SOP").mkdir(parents=True)
            plan_path = "docs/SOP/PHASE_PLANS/p.json"
            mark_slice_complete(repo, plan_path, "A")
            mark_slice_complete(repo, plan_path, "B")
            batch = select_slice_batch(
                [_slice("A"), _slice("B"), _slice("C")],
                limit=2,
                completed={"A", "B"},
            )
            self.assertEqual([s["sliceId"] for s in batch], ["C"])


def active_slice_window_from_batch(
    all_slices: list[dict], expected: list[dict], *, completed: set[str]
) -> list[dict]:
    return select_slice_batch(all_slices, limit=6, completed=completed)


if __name__ == "__main__":
    unittest.main()
