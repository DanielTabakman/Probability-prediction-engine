"""Shared Cursor Agent launcher for phone-triggered remote commands."""

from __future__ import annotations

import os
import shutil
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scripts.ppe_notify_push import OUTBOUND_TAG, ntfy_configured, notify_enabled, send_ntfy


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_agent_cli() -> str | None:
    exe = shutil.which("agent")
    if exe:
        return exe
    local_app = os.environ.get("LOCALAPPDATA", "").strip()
    if local_app:
        candidate = Path(local_app) / "cursor-agent" / "agent.cmd"
        if candidate.is_file():
            return str(candidate)
    return None


def agent_available() -> bool:
    if resolve_agent_cli():
        return True
    api_key = (
        os.environ.get("CURSOR_API_KEY") or os.environ.get("CURSOR_AUTH_TOKEN") or ""
    ).strip()
    return bool(api_key)


def run_agent(repo: Path, *, prompt: str, log_path: Path) -> dict[str, Any]:
    repo = repo.resolve()
    exe = resolve_agent_cli()
    if exe:
        cmd = [
            exe,
            "--print",
            "--output-format",
            "text",
            "--trust",
            "--force",
            "--workspace",
            str(repo),
            prompt,
        ]
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"\n--- agent cli start {_utc_now()} ---\n")
            proc = subprocess.run(
                cmd,
                cwd=repo,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=int(os.environ.get("PPE_REMOTE_AGENT_TIMEOUT_SEC", "7200")),
                check=False,
            )
            if proc.stdout:
                log.write(proc.stdout)
            if proc.stderr:
                log.write("\n[stderr]\n")
                log.write(proc.stderr)
            log.write(f"\n--- agent cli exit {proc.returncode} {_utc_now()} ---\n")
        return {
            "ok": proc.returncode == 0,
            "mode": "agent-cli",
            "exit_code": proc.returncode,
            "stdout_head": (proc.stdout or "")[:500],
            "stderr_head": (proc.stderr or "")[:300],
        }

    api_key = (
        os.environ.get("CURSOR_API_KEY") or os.environ.get("CURSOR_AUTH_TOKEN") or ""
    ).strip()
    if not api_key:
        return {"ok": False, "reason": "Need agent CLI on PATH or CURSOR_API_KEY"}

    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
    except ImportError:
        return {"ok": False, "reason": "cursor-sdk not installed"}

    model = os.environ.get("PPE_REMOTE_BUILD_MODEL", "composer-2.5").strip()
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n--- cursor-sdk start {_utc_now()} ---\n")
        try:
            result = Agent.prompt(
                prompt,
                AgentOptions(
                    api_key=api_key,
                    model=model,
                    local=LocalAgentOptions(cwd=str(repo)),
                ),
            )
        except Exception as exc:
            return {"ok": False, "mode": "cursor-sdk", "reason": str(exc)}
        status = getattr(result, "status", None)
        body = getattr(result, "result", None) or ""
        log.write(str(body))
    return {"ok": status != "error", "mode": "cursor-sdk", "status": status}


def notify_agent_done(*, title_ok: str, title_fail: str, result: dict[str, Any], log_path: Path) -> None:
    if not notify_enabled() or not ntfy_configured():
        return
    if result.get("ok"):
        send_ntfy(title_ok, f"Log: {log_path.as_posix()}", tags=["ppe", "cmd", OUTBOUND_TAG], priority="default")
    else:
        send_ntfy(
            title_fail,
            str(result.get("reason") or "see log"),
            tags=["ppe", "cmd", OUTBOUND_TAG],
            priority="high",
        )


def launch_agent_background(
    repo: Path,
    *,
    prompt: str,
    log_name: str,
    on_complete: Callable[[dict[str, Any]], None] | None,
    started_message: str,
) -> dict[str, Any]:
    if not agent_available():
        return {"started": False, "reason": "Need agent CLI (setup_cursor_agent.cmd) or CURSOR_API_KEY"}

    log_path = repo / "artifacts/orchestrator" / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"remote agent log start {_utc_now()}\n", encoding="utf-8")

    def _worker() -> None:
        result = run_agent(repo, prompt=prompt, log_path=log_path)
        if on_complete:
            on_complete(result)
        else:
            notify_agent_done(
                title_ok="PPE agent finished",
                title_fail="PPE agent failed",
                result=result,
                log_path=log_path,
            )

    threading.Thread(target=_worker, name=f"ppe-remote-{log_name}", daemon=True).start()
    return {"started": True, "message": started_message, "log": str(log_path)}
