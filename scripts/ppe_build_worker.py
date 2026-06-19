"""Unified product BUILD worker selection (Cursor CLI, Codex CLI, manual handoff).

Canon read path: artifacts/orchestrator/CONTROL_PLANE_STATUS.json → runtime.build.worker
Config: docs/SOP/PPE_AUTO_OPERATOR*.json → ideHandoff.buildWorker
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

PROTOCOL = "CODEX_AUTONOMY_V1"

WorkerKind = Literal["cursor-cli", "codex-cli", "manual"]
BuildWorkerPref = Literal["auto", "cursor", "codex", "manual"]

WORKER_CURSOR_CLI: WorkerKind = "cursor-cli"
WORKER_CODEX_CLI: WorkerKind = "codex-cli"
WORKER_MANUAL: WorkerKind = "manual"

PREF_AUTO: BuildWorkerPref = "auto"
PREF_CURSOR: BuildWorkerPref = "cursor"
PREF_CODEX: BuildWorkerPref = "codex"
PREF_MANUAL: BuildWorkerPref = "manual"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def resolve_codex_cli() -> str | None:
    exe = shutil.which("codex")
    if exe:
        return exe
    npm_global = os.environ.get("APPDATA", "").strip()
    if npm_global:
        candidate = Path(npm_global) / "npm" / "codex.cmd"
        if candidate.is_file():
            return str(candidate)
    return None


def codex_authenticated() -> bool:
    exe = resolve_codex_cli()
    if not exe:
        return False
    proc = subprocess.run(
        [exe, "login", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode == 0


def codex_available() -> bool:
    return codex_authenticated()


def load_build_worker_pref(repo: Path) -> BuildWorkerPref:
    env = os.environ.get("PPE_BUILD_WORKER", "").strip().lower()
    mapping = {
        "auto": PREF_AUTO,
        "cursor": PREF_CURSOR,
        "codex": PREF_CODEX,
        "manual": PREF_MANUAL,
    }
    if env in mapping:
        return mapping[env]  # type: ignore[return-value]
    try:
        from scripts.ppe_operator_config import load_operator_config

        cfg = load_operator_config(repo)
        handoff = cfg.get("ideHandoff")
        if isinstance(handoff, dict):
            raw = str(handoff.get("buildWorker") or "").strip().lower()
            if raw in mapping:
                return mapping[raw]  # type: ignore[return-value]
    except ImportError:
        pass
    return PREF_AUTO


def _cursor_cli_available() -> bool:
    try:
        from scripts.ppe_remote_agent import agent_available

        return agent_available()
    except ImportError:
        return False


def _cursor_cli_exhausted(repo: Path) -> bool:
    try:
        from scripts.ppe_ide_handoff import cli_usage_exhausted

        return cli_usage_exhausted(repo)
    except ImportError:
        return False


def codex_cli_exhausted(repo: Path) -> bool:
    return _codex_cli_exhausted(repo)


def _codex_cli_exhausted(repo: Path) -> bool:
    try:
        from scripts.ppe_ide_handoff import load_handoff_state

        state = load_handoff_state(repo)
        return bool(state.get("codex_cli_usage_exhausted"))
    except ImportError:
        return False


def mark_codex_usage_exhausted(repo: Path, *, detail: str = "") -> None:
    from scripts.ppe_ide_handoff import load_handoff_state, save_handoff_state

    state = load_handoff_state(repo)
    state.update(
        {
            "codex_cli_usage_exhausted": True,
            "codex_cli_usage_exhausted_at": _utc_now(),
            "codex_cli_usage_detail": detail[:500] if detail else state.get("codex_cli_usage_detail"),
        }
    )
    save_handoff_state(repo, state)


def _worker_available(worker: WorkerKind, repo: Path) -> bool:
    if worker == WORKER_CURSOR_CLI:
        return _cursor_cli_available() and not _cursor_cli_exhausted(repo)
    if worker == WORKER_CODEX_CLI:
        return codex_available() and not _codex_cli_exhausted(repo)
    return True


def resolve_build_worker(
    repo: Path,
    *,
    for_handoff: bool = False,
    force_handoff: bool = False,
) -> dict[str, Any]:
    """Pick the BUILD worker for dispatch or desktop handoff."""
    repo = repo.resolve()
    pref = load_build_worker_pref(repo)
    prefer_ide = False
    try:
        from scripts.ppe_ide_handoff import prefer_ide_over_cli

        prefer_ide = prefer_ide_over_cli(repo)
    except ImportError:
        pass

    if force_handoff or pref == PREF_MANUAL:
        worker = _resolve_handoff_worker(repo, pref=pref)
        return _worker_result(repo, worker, pref=pref, reason="manual_handoff", mode="manual")

    if for_handoff or prefer_ide:
        worker = _resolve_handoff_worker(repo, pref=pref)
        reason = "near_zero_api_profile" if prefer_ide else "desktop_handoff"
        return _worker_result(repo, worker, pref=pref, reason=reason, mode="manual")

    if pref == PREF_CODEX:
        if _worker_available(WORKER_CODEX_CLI, repo):
            return _worker_result(
                repo, WORKER_CODEX_CLI, pref=pref, reason="buildWorker=codex", mode="headless"
            )
        worker = _resolve_handoff_worker(repo, pref=pref)
        return _worker_result(repo, worker, pref=pref, reason="codex_unavailable", mode="manual")

    if pref == PREF_CURSOR:
        if _worker_available(WORKER_CURSOR_CLI, repo):
            return _worker_result(
                repo, WORKER_CURSOR_CLI, pref=pref, reason="buildWorker=cursor", mode="headless"
            )
        if _worker_available(WORKER_CODEX_CLI, repo):
            return _worker_result(
                repo,
                WORKER_CODEX_CLI,
                pref=pref,
                reason="cursor_unavailable_fallback_codex",
                mode="headless",
            )
        worker = _resolve_handoff_worker(repo, pref=pref)
        return _worker_result(repo, worker, pref=pref, reason="cursor_unavailable", mode="manual")

    # auto — prefer Cursor CLI, then Codex CLI, then manual (Codex when Cursor quota low)
    if _worker_available(WORKER_CURSOR_CLI, repo):
        return _worker_result(repo, WORKER_CURSOR_CLI, pref=pref, reason="auto_cursor_cli", mode="headless")
    if _worker_available(WORKER_CODEX_CLI, repo):
        return _worker_result(repo, WORKER_CODEX_CLI, pref=pref, reason="auto_codex_cli", mode="headless")
    worker = _resolve_handoff_worker(repo, pref=pref)
    reason = "auto_manual"
    if _cursor_cli_exhausted(repo):
        reason = "cursor_quota_exhausted"
    elif not codex_available():
        reason = "no_headless_worker"
    return _worker_result(repo, worker, pref=pref, reason=reason, mode="manual")


def _resolve_handoff_worker(repo: Path, *, pref: BuildWorkerPref) -> WorkerKind:
    """Desktop handoff target (Cursor Agent or Codex session)."""
    if pref == PREF_CODEX:
        return WORKER_CODEX_CLI
    if _cursor_cli_exhausted(repo) and codex_available():
        return WORKER_CODEX_CLI
    return WORKER_MANUAL


def _worker_result(
    repo: Path,
    worker: WorkerKind,
    *,
    pref: BuildWorkerPref,
    reason: str,
    mode: Literal["headless", "manual"],
) -> dict[str, Any]:
    return {
        "worker": worker,
        "pref": pref,
        "mode": mode,
        "reason": reason,
        "cursor_cli_available": _cursor_cli_available(),
        "codex_cli_available": codex_available(),
        "cursor_cli_exhausted": _cursor_cli_exhausted(repo),
        "codex_cli_exhausted": _codex_cli_exhausted(repo),
    }


def build_product_prompt(
    *,
    slice_id: str,
    starter_rel: str,
    plan_path: str,
    worker: WorkerKind,
    note: str = "",
) -> str:
    from scripts.ppe_ide_build_starter import format_build_closeout_section

    closeout = format_build_closeout_section(slice_id=slice_id, phase_plan=plan_path)
    if worker == WORKER_CODEX_CLI:
        parts = [
            f"PROTOCOL: {PROTOCOL}",
            "",
            f"Build product slice **{slice_id}**.",
            f"Load ONLY `{starter_rel}` (includes **## When done (required)**).",
            f"Phase plan: `{plan_path}`.",
            "Stay inside ALLOWED_PATHS; one plane, one layer. Stop before CONTROL-CLOSEOUT.",
            "",
            closeout,
            "",
            "Execute autonomously; do not ask for confirmation.",
        ]
    elif worker == WORKER_CURSOR_CLI:
        parts = [
            "You are the PPE desktop BUILD agent.",
            "",
            f"SLICE_ID: {slice_id}",
            f"PHASE_PLAN: {plan_path}",
            f"Load ONLY `@{starter_rel}`. Implement the product slice within ALLOWED_PATHS.",
            "",
            "When done, in order:",
            "1. python scripts/run_pushable_gate.py",
            "2. git commit on plan buildBranch",
            f"3. mark_ide_product_ready.cmd {slice_id} {plan_path}",
            "4. run_ppe_local.cmd",
            "",
            "Execute autonomously; do not ask for confirmation.",
        ]
    else:
        parts = [
            f"Build product slice **{slice_id}**.",
            f"Load ONLY `@{starter_rel}` (includes **## When done (required)**).",
            f"Phase plan: `{plan_path}`.",
            "",
            closeout,
        ]
    if note.strip():
        parts.extend(["", note.strip()])
    return "\n".join(parts)


def handoff_instructions(worker: WorkerKind) -> list[str]:
    if worker == WORKER_CODEX_CLI:
        return [
            "Open **Codex** in this repo folder (`codex` in terminal, or Codex desktop).",
            "Start a **new session**.",
            "Paste the build prompt from clipboard (**Ctrl+V**) and send.",
            "Let Codex finish gate, commit, and closeout.",
            "After PR merges → double-click **DESKTOP CONTINUE**.",
        ]
    return [
        "Open **Cursor** on this machine (repo folder).",
        "Start a **new Agent chat**.",
        "Press **Ctrl+V** then Enter — build prompt is on clipboard.",
        "Let the agent finish gate, commit, and closeout.",
        "After PR merges → double-click **DESKTOP CONTINUE**.",
    ]


def open_worker_for_handoff(repo: Path, *, worker: WorkerKind, starter_file: Path) -> dict[str, Any]:
    repo = repo.resolve()
    starter_file = starter_file.resolve()
    if worker == WORKER_CODEX_CLI:
        return _open_codex(repo)
    try:
        from scripts.ppe_ide_handoff import open_cursor_for_handoff

        return open_cursor_for_handoff(repo, starter_file)
    except ImportError:
        return {"ok": False, "reason": "cursor handoff unavailable"}


def _open_codex(repo: Path) -> dict[str, Any]:
    exe = resolve_codex_cli()
    if not exe:
        return {"ok": False, "reason": "codex CLI not installed (npm install -g @openai/codex)"}
    try:
        from scripts.ppe_ide_handoff import _detached_open

        opened = _detached_open([exe], cwd=repo)
        return {**opened, "worker": WORKER_CODEX_CLI}
    except ImportError:
        return {"ok": False, "reason": "could not launch codex"}


def run_build_worker_cli(
    repo: Path,
    *,
    prompt: str,
    worker: WorkerKind,
    log_path: Path,
) -> dict[str, Any]:
    if worker == WORKER_CODEX_CLI:
        return run_codex(repo, prompt=prompt, log_path=log_path)
    from scripts.ppe_remote_agent import run_agent

    return run_agent(repo, prompt=prompt, log_path=log_path)


def run_codex(repo: Path, *, prompt: str, log_path: Path) -> dict[str, Any]:
    repo = repo.resolve()
    exe = resolve_codex_cli()
    if not exe:
        return {"ok": False, "mode": "codex-cli", "reason": "codex CLI not installed"}
    if not codex_authenticated():
        return {"ok": False, "mode": "codex-cli", "reason": "codex not authenticated (codex login)"}

    cmd = [
        exe,
        "exec",
        "-C",
        str(repo),
        "-s",
        "workspace-write",
        "-a",
        "never",
        prompt,
    ]
    with log_path.open("a", encoding="utf-8") as log:
        log.write(f"\n--- codex cli start {_utc_now()} ---\n")
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
        log.write(f"\n--- codex cli exit {proc.returncode} {_utc_now()} ---\n")
    return {
        "ok": proc.returncode == 0,
        "mode": "codex-cli",
        "exit_code": proc.returncode,
        "stdout_head": (proc.stdout or "")[:500],
        "stderr_head": (proc.stderr or "")[:300],
    }


def launch_build_worker_background(
    repo: Path,
    *,
    prompt: str,
    worker: WorkerKind,
    log_name: str = "REMOTE_BUILD_AGENT.log",
    started_message: str,
    clear_build_lock: bool = False,
    notify_ok_title: str = "PPE build finished",
    notify_fail_title: str = "PPE build failed",
    handoff: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if worker == WORKER_MANUAL:
        return {"started": False, "reason": "manual worker requires desktop handoff"}

    if worker == WORKER_CURSOR_CLI:
        from scripts.ppe_remote_agent import agent_available

        if not agent_available():
            return {"started": False, "reason": "Need agent CLI (setup_cursor_agent.cmd) or CURSOR_API_KEY"}
    elif not codex_available():
        return {"started": False, "reason": "Need codex CLI (npm install -g @openai/codex; codex login)"}

    from scripts.ppe_remote_agent_spawn import spawn_python_worker

    repo = repo.resolve()
    log_path = repo / "artifacts" / "orchestrator" / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(f"remote build worker ({worker}) start {_utc_now()}\n", encoding="utf-8")

    job_dir = repo / "artifacts" / "orchestrator"
    job_dir.mkdir(parents=True, exist_ok=True)
    job_path = job_dir / f"REMOTE_AGENT_JOB_{os.getpid()}_{int(datetime.now(timezone.utc).timestamp())}.json"
    job: dict[str, Any] = {
        "repo_root": str(repo),
        "prompt": prompt,
        "log_name": log_name,
        "build_worker": worker,
        "clear_build_lock": clear_build_lock,
        "notify_ok_title": notify_ok_title,
        "notify_fail_title": notify_fail_title,
    }
    if handoff:
        job["handoff"] = handoff
    job_path.write_text(json.dumps(job, indent=2) + "\n", encoding="utf-8")

    try:
        proc = spawn_python_worker(
            repo,
            "scripts/ppe_remote_agent_worker.py",
            "--job",
            str(job_path),
            "--delete-job",
        )
    except OSError as exc:
        job_path.unlink(missing_ok=True)
        return {"started": False, "reason": f"failed to spawn worker: {exc}"}

    return {
        "started": True,
        "message": started_message,
        "log": str(log_path),
        "worker_pid": proc.pid,
        "job_path": str(job_path),
        "build_worker": worker,
    }


def format_handoff_banner(repo: Path) -> str:
    """Human-readable steps for DESKTOP_BUILD.cmd after handoff."""
    resolved = resolve_build_worker(repo, for_handoff=True)
    worker = resolved["worker"]
    lines = [
        "DESKTOP BUILD — your real PC only (NOT the VM)",
        "",
        f"Worker: {worker} ({resolved.get('reason')})",
        "Build prompt is on your clipboard.",
        "",
    ]
    for idx, step in enumerate(handoff_instructions(worker), start=1):
        lines.append(f"{idx}. {step}")
    lines.extend(
        [
            "",
            "The VM loop keeps waiting — you do not run anything on the VM.",
            "Status: ppe_request.cmd reconcile → CONTROL_PLANE_STATUS.json",
        ]
    )
    return "\n".join(lines)


def collect_build_worker_status(repo: Path) -> dict[str, Any]:
    resolved = resolve_build_worker(repo)
    handoff = resolve_build_worker(repo, for_handoff=True)
    return {
        "pref": resolved.get("pref"),
        "worker": resolved.get("worker"),
        "handoff_worker": handoff.get("worker"),
        "mode": resolved.get("mode"),
        "reason": resolved.get("reason"),
        "cursor_cli_available": resolved.get("cursor_cli_available"),
        "codex_cli_available": resolved.get("codex_cli_available"),
        "cursor_cli_exhausted": _cursor_cli_exhausted(repo),
        "codex_cli_exhausted": _codex_cli_exhausted(repo),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE unified BUILD worker")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("print-handoff", help="Print DESKTOP BUILD instructions for current worker")
    p_status = sub.add_parser("status", help="Show resolved worker")
    p_status.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "print-handoff":
        print(format_handoff_banner(repo))
        return 0

    status = collect_build_worker_status(repo)
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(
            f"worker={status['worker']} handoff={status['handoff_worker']} "
            f"pref={status['pref']} reason={status['reason']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
