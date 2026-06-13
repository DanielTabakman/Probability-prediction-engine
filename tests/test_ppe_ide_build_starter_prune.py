"""Tests for stale IDE BUILD starter pruning."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_ide_build_starter import prune_starters_for_plan, starter_path


def test_prune_starters_for_plan(tmp_path: Path) -> None:
    plan = {
        "slices": [
            {"sliceId": "Test-Product-Slice002"},
            {"sliceId": "Test-Closeout-Slice003"},
        ]
    }
    rel = "docs/SOP/PHASE_PLANS/test_relay.json"
    (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / rel).write_text(json.dumps(plan), encoding="utf-8")
    for sid in ("Test-Product-Slice002", "Test-Closeout-Slice003"):
        p = tmp_path / starter_path(sid)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("starter", encoding="utf-8")

    removed = prune_starters_for_plan(tmp_path, rel)
    assert set(removed) == {"Test-Product-Slice002", "Test-Closeout-Slice003"}
    assert not (tmp_path / starter_path("Test-Product-Slice002")).is_file()
