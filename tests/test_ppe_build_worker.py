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
    resolve_codex_cli,
)


def test_load_build_worker_pref_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_WORKER", "codex")
    assert load_build_worker_pref(tmp_path) == PREF_CODEX


def test_resolve_codex_cli_finds_standalone_windows_install(tmp_path, monkeypatch):
    fake_exe = tmp_path / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe"
    fake_exe.parent.mkdir(parents=True, exist_ok=True)
    fake_exe.write_text("", encoding="utf-8")
    monkeypatch.setattr("scripts.ppe_build_worker.shutil.which", lambda _name: None)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("APPDATA", raising=False)
    assert resolve_codex_cli() == str(fake_exe)


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
    monkeypatch.setattr("scripts.ppe_build_worker.sys.platform", "linux")

    def fake_run(cmd, **kwargs):
        assert "-a" not in cmd
        assert "-s" in cmd and "workspace-write" in cmd
        assert "--dangerously-bypass-approvals-and-sandbox" not in cmd
        assert '-c' in cmd and 'approval_policy="never"' in cmd

        class Proc:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Proc()

    monkeypatch.setattr("scripts.ppe_build_worker.subprocess.run", fake_run)
    out = run_codex(repo, prompt="build slice", log_path=log_path)
    assert out["ok"] is True


def test_run_codex_bypasses_sandbox_on_windows(tmp_path, monkeypatch):
    from scripts.ppe_build_worker import run_codex

    repo = tmp_path
    log_path = repo / "codex.log"
    monkeypatch.setattr("scripts.ppe_build_worker.resolve_codex_cli", lambda: "codex")
    monkeypatch.setattr("scripts.ppe_build_worker.codex_authenticated", lambda: True)
    monkeypatch.setattr("scripts.ppe_build_worker.sys.platform", "win32")

    def fake_run(cmd, **kwargs):
        assert "--dangerously-bypass-approvals-and-sandbox" in cmd
        assert "-s" not in cmd

        class Proc:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Proc()

    monkeypatch.setattr("scripts.ppe_build_worker.subprocess.run", fake_run)
    out = run_codex(repo, prompt="build slice", log_path=log_path)
    assert out["ok"] is True


def test_cursor_first_ok_when_cursor_headless(tmp_path, monkeypatch):
    from scripts.ppe_build_worker import PREF_AUTO, WORKER_CURSOR_CLI, evaluate_cursor_first_policy

    monkeypatch.delenv("PPE_BUILD_WORKER", raising=False)
    with (
        patch("scripts.ppe_build_worker.load_build_worker_pref", return_value=PREF_AUTO),
        patch(
            "scripts.ppe_build_worker.collect_build_worker_status",
            return_value={
                "pref": PREF_AUTO,
                "worker": WORKER_CURSOR_CLI,
                "mode": "headless",
                "reason": "auto_cursor_cli",
                "cursor_cli_available": True,
                "cursor_cli_exhausted": False,
                "codex_cli_available": True,
                "codex_cli_exhausted": False,
            },
        ),
    ):
        policy = evaluate_cursor_first_policy(tmp_path)
    assert policy["verdict"] == "ok"
    assert "Cursor CLI headless" in policy["detail"]


def test_cursor_first_warn_when_codex_pref_skips_cursor(tmp_path, monkeypatch):
    from scripts.ppe_build_worker import PREF_CODEX, WORKER_CODEX_CLI, evaluate_cursor_first_policy

    with (
        patch("scripts.ppe_build_worker.load_build_worker_pref", return_value=PREF_CODEX),
        patch(
            "scripts.ppe_build_worker.collect_build_worker_status",
            return_value={
                "pref": PREF_CODEX,
                "worker": WORKER_CODEX_CLI,
                "mode": "headless",
                "reason": "buildWorker=codex",
                "cursor_cli_available": True,
                "cursor_cli_exhausted": False,
                "codex_cli_available": True,
                "codex_cli_exhausted": False,
            },
        ),
    ):
        policy = evaluate_cursor_first_policy(tmp_path)
    assert policy["verdict"] == "warn"
    assert "buildWorker=codex" in policy["detail"]


def test_cursor_first_ok_when_cursor_exhausted_codex_fallback(tmp_path):
    from scripts.ppe_build_worker import PREF_AUTO, WORKER_CODEX_CLI, evaluate_cursor_first_policy

    with (
        patch("scripts.ppe_build_worker.load_build_worker_pref", return_value=PREF_AUTO),
        patch(
            "scripts.ppe_build_worker.collect_build_worker_status",
            return_value={
                "pref": PREF_AUTO,
                "worker": WORKER_CODEX_CLI,
                "mode": "headless",
                "reason": "auto_codex_cli",
                "cursor_cli_available": True,
                "cursor_cli_exhausted": True,
                "codex_cli_available": True,
                "codex_cli_exhausted": False,
            },
        ),
    ):
        policy = evaluate_cursor_first_policy(tmp_path)
    assert policy["verdict"] == "ok"
    assert "exhausted" in policy["detail"]
