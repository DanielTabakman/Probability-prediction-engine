"""Tests for unified BUILD worker selection."""

from __future__ import annotations

from unittest.mock import patch

from scripts.ppe_build_worker import (
    BUILD_WORKER_EVENTS_REL,
    PREF_AUTO,
    PREF_CODEX,
    WORKER_CODEX_CLI,
    WORKER_CURSOR_CLI,
    WORKER_MANUAL,
    build_product_prompt,
    load_build_worker_pref,
    read_build_worker_events,
    resolve_build_worker,
    resolve_codex_cli,
)


def test_load_build_worker_pref_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_WORKER", "codex")
    assert load_build_worker_pref(tmp_path) == PREF_CODEX


def test_resolve_codex_cli_prefers_authenticated_standalone(tmp_path, monkeypatch):
    npm_stub = tmp_path / "npm" / "codex.cmd"
    npm_stub.parent.mkdir(parents=True)
    npm_stub.write_text("@echo broken\n", encoding="utf-8")
    standalone = tmp_path / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe"
    standalone.parent.mkdir(parents=True)
    standalone.write_text("", encoding="utf-8")

    monkeypatch.setattr("scripts.ppe_build_worker.shutil.which", lambda _name: str(npm_stub))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path / "npm_parent"))
    monkeypatch.delenv("USERPROFILE", raising=False)

    def fake_login(exe: str) -> bool:
        return str(exe).endswith("codex.exe")

    monkeypatch.setattr("scripts.ppe_build_worker._codex_login_ok", fake_login)
    assert resolve_codex_cli() == str(standalone)


def test_resolve_codex_cli_finds_standalone_windows_install(tmp_path, monkeypatch):
    fake_exe = tmp_path / "Programs" / "OpenAI" / "Codex" / "bin" / "codex.exe"
    fake_exe.parent.mkdir(parents=True, exist_ok=True)
    fake_exe.write_text("", encoding="utf-8")
    monkeypatch.setattr("scripts.ppe_build_worker.shutil.which", lambda _name: None)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.setattr("scripts.ppe_build_worker._codex_login_ok", lambda exe: str(exe) == str(fake_exe))
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


def test_handoff_prefers_desktop_build_lane_file(tmp_path, monkeypatch) -> None:
    from scripts.ppe_worker_lease import LANE_CURSOR, write_desktop_build_handoff

    monkeypatch.chdir(tmp_path)
    write_desktop_build_handoff(
        tmp_path,
        {
            "preferred_lane": LANE_CURSOR,
            "blocked": False,
            "lane_preference": {"reason": "product_path_scope"},
        },
    )
    with patch("scripts.ppe_build_worker.load_build_worker_pref", return_value="auto"):
        with patch("scripts.ppe_build_worker._cursor_cli_exhausted", return_value=False):
            out = resolve_build_worker(tmp_path, for_handoff=True)
    assert out["worker"] == WORKER_MANUAL


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


def test_codex_first_ok_when_codex_headless(tmp_path):
    from scripts.ppe_build_worker import PREF_CODEX, WORKER_CODEX_CLI, evaluate_codex_first_policy

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
        policy = evaluate_codex_first_policy(tmp_path)
    assert policy["verdict"] == "ok"
    assert "Codex CLI headless" in policy["detail"]


def test_codex_first_warn_when_auto_uses_cursor(tmp_path):
    from scripts.ppe_build_worker import PREF_AUTO, WORKER_CURSOR_CLI, evaluate_codex_first_policy

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
        policy = evaluate_codex_first_policy(tmp_path)
    assert policy["verdict"] == "warn"
    assert "buildWorker=codex" in policy["detail"]


def test_resolve_codex_prefers_codex_when_available(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_WORKER", "codex")
    with (
        patch("scripts.ppe_build_worker.codex_available", return_value=True),
        patch("scripts.ppe_build_worker._codex_cli_exhausted", return_value=False),
        patch("scripts.ppe_ide_handoff.prefer_ide_over_cli", return_value=False),
    ):
        out = resolve_build_worker(tmp_path)
    assert out["worker"] == WORKER_CODEX_CLI
    assert out["mode"] == "headless"


def test_clear_cli_usage_exhausted_ignores_stale_log(tmp_path):
    from scripts.ppe_ide_handoff import clear_cli_usage_exhausted, cli_usage_exhausted

    log_dir = tmp_path / "artifacts" / "orchestrator"
    log_dir.mkdir(parents=True)
    fix_log = log_dir / "REMOTE_FIX_AGENT.log"
    fix_log.write_text(
        "out of usage. Switch to Auto, or ask your admin to increase your limit.\n",
        encoding="utf-8",
    )
    assert cli_usage_exhausted(tmp_path) is True
    clear_cli_usage_exhausted(tmp_path)
    assert cli_usage_exhausted(tmp_path) is False


def test_resolve_build_worker_logs_event(tmp_path, monkeypatch):
    monkeypatch.setenv("PPE_BUILD_WORKER", "codex")
    with (
        patch("scripts.ppe_build_worker.codex_available", return_value=True),
        patch("scripts.ppe_build_worker._codex_cli_exhausted", return_value=False),
        patch("scripts.ppe_ide_handoff.prefer_ide_over_cli", return_value=False),
    ):
        resolve_build_worker(tmp_path)
    events = read_build_worker_events(tmp_path, limit=5)
    assert events
    assert events[-1].get("event") == "worker_resolve"
    assert (tmp_path / BUILD_WORKER_EVENTS_REL).is_file()
