"""Tests for unified BUILD worker selection."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_build_worker import (
    PREF_AUTO,
    PREF_CODEX,
    WORKER_CODEX_CLI,
    WORKER_CURSOR_CLI,
    WORKER_MANUAL,
    build_product_prompt,
    load_build_worker_pref,
    resolve_build_worker,
)


def test_load_build_worker_pref_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_WORKER", "codex")
    assert load_build_worker_pref(tmp_path) == PREF_CODEX


def test_resolve_auto_prefers_cursor_when_available(tmp_path, monkeypatch):
    monkeypatch.delenv("PPE_BUILD_WORKER", raising=False)
    with (
        patch("scripts.ppe_build_worker._cursor_cli_available", return_value=True),
        patch("scripts.ppe_build_worker._cursor_cli_exhausted", return_value=False),
        patch("scripts.ppe_build_worker.codex_available", return_value=True),
        patch("scripts.ppe_ide_handoff.prefer_ide_over_cli", return_value=False),
    ):
        out = resolve_build_worker(tmp_path)
    assert out["worker"] == WORKER_CURSOR_CLI
    assert out["mode"] == "headless"


def test_resolve_auto_falls_back_to_codex_when_cursor_exhausted(tmp_path, monkeypatch):
    monkeypatch.delenv("PPE_BUILD_WORKER", raising=False)
    with (
        patch("scripts.ppe_build_worker._cursor_cli_available", return_value=True),
        patch("scripts.ppe_build_worker._cursor_cli_exhausted", return_value=True),
        patch("scripts.ppe_build_worker.codex_available", return_value=True),
        patch("scripts.ppe_build_worker._codex_cli_exhausted", return_value=False),
        patch("scripts.ppe_ide_handoff.prefer_ide_over_cli", return_value=False),
    ):
        out = resolve_build_worker(tmp_path)
    assert out["worker"] == WORKER_CODEX_CLI
    assert out["mode"] == "headless"


def test_resolve_handoff_uses_codex_when_cursor_exhausted(tmp_path, monkeypatch):
    with (
        patch("scripts.ppe_build_worker._cursor_cli_exhausted", return_value=True),
        patch("scripts.ppe_build_worker.codex_available", return_value=True),
        patch("scripts.ppe_ide_handoff.prefer_ide_over_cli", return_value=True),
    ):
        out = resolve_build_worker(tmp_path, for_handoff=True)
    assert out["worker"] == WORKER_CODEX_CLI
    assert out["mode"] == "manual"


def test_build_product_prompt_codex_includes_protocol():
    text = build_product_prompt(
        slice_id="Slice001",
        starter_rel="artifacts/orchestrator/IDE_BUILD_STARTER_Slice001.md",
        plan_path="docs/SOP/PHASE_PLANS/foo.json",
        worker=WORKER_CODEX_CLI,
    )
    assert "PROTOCOL: CODEX_AUTONOMY_V1" in text
    assert "Slice001" in text


def test_build_product_prompt_manual_uses_closeout():
    text = build_product_prompt(
        slice_id="Slice001",
        starter_rel="artifacts/orchestrator/IDE_BUILD_STARTER_Slice001.md",
        plan_path="docs/SOP/PHASE_PLANS/foo.json",
        worker=WORKER_MANUAL,
    )
    assert "mark_ide_product_ready.cmd Slice001" in text


def test_run_codex_uses_workspace_write_without_legacy_approval_flag(tmp_path, monkeypatch):
    from scripts.ppe_build_worker import run_codex

    repo = tmp_path
    log_path = repo / "codex.log"
    monkeypatch.setattr("scripts.ppe_build_worker.resolve_codex_cli", lambda: "codex")
    monkeypatch.setattr("scripts.ppe_build_worker.codex_authenticated", lambda: True)

    def fake_run(cmd, **kwargs):
        assert "-a" not in cmd
        assert "-s" in cmd and "workspace-write" in cmd
        assert '-c' in cmd and 'approval_policy="never"' in cmd
        class Proc:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Proc()

    monkeypatch.setattr("scripts.ppe_build_worker.subprocess.run", fake_run)
    out = run_codex(repo, prompt="build slice", log_path=log_path)
    assert out["ok"] is True
