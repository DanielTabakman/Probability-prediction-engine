"""Tests for Do The Thing operator queue."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.ppe_autobuilder import PHASE_AWAITING_BUILD
from scripts.ppe_do_the_thing import (
    BUTTON_NAME,
    add_queue_item,
    clear_queue,
    derive_actions,
    load_queue,
    resolve_plan,
    run_plan,
)


def test_add_and_clear_queue(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    add_queue_item(tmp_path, action="git_pull", label="sync main", source="test")
    data = load_queue(tmp_path)
    assert len(data["items"]) == 1
    assert data["items"][0]["action"] == "git_pull"
    add_queue_item(tmp_path, action="git_pull", label="dup", source="test")
    assert len(load_queue(tmp_path)["items"]) == 1
    clear_queue(tmp_path)
    assert load_queue(tmp_path)["items"] == []


def test_resolve_plan_prefers_queue(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    add_queue_item(tmp_path, action="vm_advance", label="vm", source="test")
    plan = resolve_plan(tmp_path, include_derived=False)
    assert len(plan) == 1
    assert plan[0]["action"] == "vm_advance"


def test_derive_desktop_build_when_ide_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ppe_operator_no_loop.local.cmd").write_text("x\n", encoding="utf-8")

    def fake_status(repo):
        return {
            "phase": PHASE_AWAITING_BUILD,
            "verdict": "IDE_BUILD",
            "closeout": {"pending": False},
            "marker_present": False,
        }

    monkeypatch.setattr("scripts.ppe_do_the_thing.collect_autobuilder_status", fake_status)
    plan = derive_actions(tmp_path)
    assert any(x["action"] == "desktop_build" for x in plan)


def test_run_plan_clears_queue_on_success(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    add_queue_item(tmp_path, action="git_pull", label="pull", source="test")

    def fake_pull(repo):
        return {"action": "git_pull", "ok": True, "exit_code": 0}

    monkeypatch.setattr("scripts.ppe_do_the_thing._run_git_pull", fake_pull)
    out = run_plan(tmp_path)
    assert out["ok"] is True
    assert load_queue(tmp_path)["items"] == []


def test_run_plan_dry_run_keeps_queue(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    add_queue_item(tmp_path, action="git_pull", label="pull", source="test")
    out = run_plan(tmp_path, dry_run=True)
    assert out["ok"] is True
    assert len(load_queue(tmp_path)["items"]) == 1


def test_button_name():
    assert BUTTON_NAME == "DO THE THING"
