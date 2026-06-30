from __future__ import annotations

from datetime import date
from pathlib import Path

from scripts.ppe_remote_build_policy import (
    record_usage,
    resolve_auto_remote_build,
)


def test_option_a_before_midmonth(tmp_path: Path) -> None:
    cfg = {"autoRemoteBuild": False, "remoteBuildPolicy": {"midMonthBurnBoost": True, "enableAfterDay": 16}}
    on, reason = resolve_auto_remote_build(cfg, budget=None, when=date(2026, 6, 10))
    assert on is False
    assert "before day 16" in reason


def test_option_b_boost_when_underused(tmp_path: Path) -> None:
    cfg = {
        "autoRemoteBuild": False,
        "remoteBuildPolicy": {
            "midMonthBurnBoost": True,
            "enableAfterDay": 16,
            "underuseThresholdPct": 0.35,
        },
    }
    budget = {"month": "2026-06", "used_pct": 0.12}
    on, reason = resolve_auto_remote_build(cfg, budget=budget, when=date(2026, 6, 20))
    assert on is True
    assert "burn boost" in reason


def test_no_boost_when_credits_well_used(tmp_path: Path) -> None:
    cfg = {
        "autoRemoteBuild": False,
        "remoteBuildPolicy": {"midMonthBurnBoost": True, "enableAfterDay": 16, "underuseThresholdPct": 0.35},
    }
    budget = {"month": "2026-06", "used_pct": 0.55}
    on, _ = resolve_auto_remote_build(cfg, budget=budget, when=date(2026, 6, 20))
    assert on is False


def test_record_usage_writes_budget(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "artifacts" / "control_plane").mkdir(parents=True)
    out = record_usage(tmp_path, used_pct=0.2, notes="dashboard check", when=date(2026, 6, 18))
    assert out.is_file()
    import json

    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["month"] == "2026-06"
    assert data["used_pct"] == 0.2
