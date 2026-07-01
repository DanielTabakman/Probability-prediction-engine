"""Regression guards for PPE auto-ship policy artifacts."""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_auto_ship_rule_always_on() -> None:
    text = (REPO / ".cursor" / "rules" / "auto-ship.mdc").read_text(encoding="utf-8")
    assert "alwaysApply: true" in text
    assert "Never ask" in text


def test_agents_md_exists_and_points_to_auto_ship() -> None:
    path = REPO / "AGENTS.md"
    assert path.is_file()
    body = path.read_text(encoding="utf-8")
    assert "auto-ship.mdc" in body
    assert "ppe_worker_lease.py --ship" in body


def test_work_dispatch_includes_ship_acceptance(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    from scripts.ppe_worker_lease import build_work_dispatch

    dispatch = build_work_dispatch(
        tmp_path,
        {
            "verdict": "IDE_BUILD",
            "chapter_mode": {"mode": "IDE_BUILD"},
            "guard": {"detail": "blocked [Slice-A]"},
        },
    )
    assert "ship" in dispatch.get("acceptance", {})
    assert "--ship" in str(dispatch["acceptance"]["ship"])


def test_hooks_json_registers_stop_hook() -> None:
    data = json.loads((REPO / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    stop_hooks = data.get("hooks", {}).get("stop") or []
    assert stop_hooks
    assert any("ppe_auto_ship_stop_hook" in str(h.get("command") or "") for h in stop_hooks)


def test_stop_hook_script_exists() -> None:
    assert (REPO / "scripts" / "ppe_auto_ship_stop_hook.py").is_file()
