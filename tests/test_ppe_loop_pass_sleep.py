"""Tests for adaptive loop pass sleep."""

from __future__ import annotations

import json
from unittest.mock import patch

from scripts.ppe_loop_pass_sleep import loop_pass_sleep_seconds


def test_min_sleep_for_run_local(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_OPERATOR_PROFILE", "local")
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    (sop / "PPE_AUTO_OPERATOR.local.json").write_text(
        json.dumps({"enabled": True, "minLoopSleepSeconds": 5, "idleSleepSeconds": 120}),
        encoding="utf-8",
    )
    with patch(
        "scripts.ppe_loop_pass_sleep.collect_operator_status",
        return_value={"verdict": "RUN_LOCAL"},
    ):
        assert loop_pass_sleep_seconds(tmp_path) == 5


def test_supply_low_uses_longer_sleep(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_OPERATOR_PROFILE", "local")
    sop = tmp_path / "docs" / "SOP"
    sop.mkdir(parents=True)
    (sop / "PPE_AUTO_OPERATOR.local.json").write_text(
        json.dumps({"enabled": True, "supplyLowSleepSeconds": 45, "minLoopSleepSeconds": 5}),
        encoding="utf-8",
    )
    with patch(
        "scripts.ppe_loop_pass_sleep.collect_operator_status",
        return_value={"verdict": "SUPPLY_LOW"},
    ):
        assert loop_pass_sleep_seconds(tmp_path) == 45
