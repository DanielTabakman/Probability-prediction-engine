"""Tests for scripts/ppe_between_chapter_housekeeping.py."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_between_chapter_housekeeping import (
    HOUSEKEEPING_CHAPTER_ID,
    HOUSEKEEPING_PLAN_PATH,
    is_housekeeping_chapter,
    load_state,
    schedule_after_product_closeout,
)
from scripts.ppe_propagate_queue import load_backlog
from scripts.ppe_structural_health import STATE_REL


def _write_min_backlog(repo: Path) -> None:
    backlog = {
        "version": 1,
        "items": [
            {
                "chapterId": HOUSEKEEPING_CHAPTER_ID,
                "status": "done",
                "sideChannel": True,
                "betweenChapterHousekeeping": True,
                "planPath": HOUSEKEEPING_PLAN_PATH,
                "workerMode": "deterministic",
            }
        ],
    }
    path = repo / "docs" / "SOP" / "PHASE_CHAPTER_BACKLOG.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")


def _write_min_queue(repo: Path) -> None:
    queue = {
        "version": 1,
        "items": [
            {
                "planPath": HOUSEKEEPING_PLAN_PATH,
                "status": "DONE",
                "doneReason": "previous run",
            }
        ],
    }
    path = repo / "docs" / "SOP" / "PHASE_QUEUE.json"
    path.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")


def test_is_housekeeping_chapter() -> None:
    assert is_housekeeping_chapter(chapter_id=HOUSEKEEPING_CHAPTER_ID)
    assert is_housekeeping_chapter(plan_path=HOUSEKEEPING_PLAN_PATH)
    assert not is_housekeeping_chapter(chapter_id="msos_p4_strategy_lab")


def test_schedule_after_product_closeout_resets_backlog(tmp_path: Path) -> None:
    repo = tmp_path
    _write_min_backlog(repo)
    _write_min_queue(repo)
    (repo / "docs" / "SOP" / "PHASE_PLANS").mkdir(parents=True)
    (repo / HOUSEKEEPING_PLAN_PATH).write_text('{"name":"hk","slices":[]}', encoding="utf-8")

    out = schedule_after_product_closeout(
        repo,
        closed_chapter_id="msos_forward_consistency_radar_v1",
        closed_plan_path="docs/SOP/PHASE_PLANS/msos_forward_consistency_radar_v1_relay.json",
        apply=True,
    )
    assert out["scheduled"] is True
    backlog = load_backlog(repo)
    item = next(i for i in backlog["items"] if i["chapterId"] == HOUSEKEEPING_CHAPTER_ID)
    assert item["status"] == "blocked"
    state = load_state(repo)
    assert state["product_chapters_since_run"] == 0
    assert (repo / STATE_REL).is_file()


def test_schedule_skips_housekeeping_self_closeout(tmp_path: Path) -> None:
    repo = tmp_path
    _write_min_backlog(repo)
    out = schedule_after_product_closeout(
        repo,
        closed_chapter_id=HOUSEKEEPING_CHAPTER_ID,
        closed_plan_path=HOUSEKEEPING_PLAN_PATH,
        apply=True,
    )
    assert out["scheduled"] is False
    assert "skip" in out["reason"].lower()
