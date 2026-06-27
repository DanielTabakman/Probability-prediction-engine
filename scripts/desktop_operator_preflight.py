"""Desktop loop-host bootstrap checks (ntfy, git identity, ssh, tailscale, operator verdict)."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _ok(msg: str) -> None:
    print(f"OK: {msg}")


def _warn(msg: str) -> None:
    print(f"WARN: {msg}")


def _fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)


def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)


def check_ntfy() -> bool:
    from scripts.ppe_notify_push import ntfy_configured, notify_enabled

    if not notify_enabled():
        _warn("PPE_NOTIFY disabled")
        return True
    if ntfy_configured():
        _ok("ntfy topic configured")
        return True
    _fail("PPE_NTFY_TOPIC not set (see ppe_operator_notify.local.cmd)")
    return False


def check_git_identity() -> bool:
    name = os.environ.get("GIT_AUTHOR_NAME", "").strip()
    email = os.environ.get("GIT_AUTHOR_EMAIL", "").strip()
    if name and email:
        _ok(f"git identity via env: {name} <{email}>")
        return True
    proc = _run(["git", "config", "user.email"], cwd=Path.cwd())
    email_cfg = (proc.stdout or "").strip()
    proc2 = _run(["git", "config", "user.name"], cwd=Path.cwd())
    name_cfg = (proc2.stdout or "").strip()
    if name_cfg and email_cfg:
        _ok(f"git identity via config: {name_cfg} <{email_cfg}>")
        return True
    _fail("no git identity (add ppe_operator_git.local.cmd or git config user.name/email)")
    return False


def check_gh() -> bool:
    if shutil.which("gh") is None:
        _warn("gh CLI not installed (PR recovery may skip)")
        return True
    proc = _run(["gh", "auth", "status"], cwd=Path.cwd())
    if proc.returncode == 0:
        _ok("gh authenticated")
        return True
    _warn("gh not logged in (run: gh auth login -h github.com -p https -w)")
    return True


def check_tailscale() -> bool:
    ts = Path(r"C:\Program Files\Tailscale\tailscale.exe")
    if not ts.is_file():
        _warn("Tailscale not installed")
        return True
    proc = subprocess.run([str(ts), "status"], capture_output=True, text=True, check=False)
    if proc.returncode == 0 and "Logged out" not in (proc.stdout or ""):
        _ok("Tailscale connected")
        return True
    _fail("Tailscale logged out")
    return False


def check_agent_cli() -> bool:
    from scripts.ppe_remote_agent import resolve_agent_cli

    exe = resolve_agent_cli()
    if not exe:
        _warn("agent CLI not installed (optional fallback — run setup_cursor_agent.cmd)")
        return True
    proc = _run([exe, "status"], cwd=Path.cwd())
    if proc.returncode == 0 and "Not logged in" not in (proc.stdout or ""):
        _ok("agent CLI logged in")
        return True
    _warn("agent CLI not logged in (run: agent login)")
    return True


def check_codex_cli() -> bool:
    from scripts.ppe_build_worker import codex_available, resolve_codex_cli

    exe = resolve_codex_cli()
    if not exe:
        _warn("codex CLI not installed (run setup_codex.cmd)")
        return True
    if codex_available():
        _ok("codex CLI authenticated")
        return True
    _warn("codex not logged in (run: codex login)")
    return True


def check_cursor_tokens_first(repo: Path) -> bool:
    from scripts.ppe_build_worker import evaluate_cursor_first_policy

    policy = evaluate_cursor_first_policy(repo)
    line = (
        f"Cursor-first: pref={policy.get('pref')} worker={policy.get('worker')} "
        f"mode={policy.get('mode')} cursor_quota={policy.get('cursor_has_quota')}"
    )
    print(line)
    verdict = str(policy.get("verdict") or "warn")
    detail = str(policy.get("detail") or "")
    if verdict == "ok" or verdict == "info":
        _ok(detail)
        return True
    _warn(detail)
    return False


def check_codex_tokens_first(repo: Path) -> bool:
    from scripts.ppe_build_worker import evaluate_codex_first_policy

    policy = evaluate_codex_first_policy(repo)
    line = (
        f"Codex-first: pref={policy.get('pref')} worker={policy.get('worker')} "
        f"mode={policy.get('mode')} codex_quota={policy.get('codex_has_quota')}"
    )
    print(line)
    verdict = str(policy.get("verdict") or "warn")
    detail = str(policy.get("detail") or "")
    if verdict == "ok" or verdict == "info":
        _ok(detail)
        return True
    _warn(detail)
    return False


def check_build_worker(repo: Path) -> bool:
    from scripts.ppe_build_worker import collect_build_worker_status

    status = collect_build_worker_status(repo)
    worker = status.get("worker")
    pref = status.get("pref")
    reason = status.get("reason")
    mode = status.get("mode")
    handoff = status.get("handoff_worker")
    print(
        f"BUILD worker: pref={pref} worker={worker} mode={mode} "
        f"handoff={handoff} reason={reason}"
    )
    if mode == "headless" and worker in ("cursor-cli", "codex-cli"):
        _ok(f"headless BUILD worker ready ({worker})")
        return True
    if worker == "manual" or mode == "manual":
        if handoff == "codex-cli":
            _warn("headless blocked — desktop Codex handoff available")
        else:
            _warn("no headless worker — desktop Codex or Cursor handoff (setup_codex.cmd / setup_cursor_agent.cmd)")
        return True
    _warn(f"unexpected worker state: {status}")
    return True


def check_sshd() -> bool:
    proc = _run(
        ["powershell", "-NoProfile", "-Command", "(Get-Service sshd).Status"],
        cwd=Path.cwd(),
    )
    if "Running" in (proc.stdout or ""):
        _ok("OpenSSH Server running")
        return True
    _warn("OpenSSH Server not running (phone SSH triage unavailable)")
    return True


def check_operator(repo: Path) -> bool:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    env.setdefault("PPE_OPERATOR_PROFILE", "local")
    proc = subprocess.run(
        [sys.executable, str(repo / "scripts" / "ppe_operator_status.py"), "--repo-root", str(repo), "--brief"],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    line = (proc.stdout or "").strip().splitlines()[-1] if proc.stdout else ""
    if line:
        print(line)
    if proc.returncode in (0, 7):
        return True
    _warn(f"operator status exit {proc.returncode}")
    return proc.returncode == 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Desktop operator bootstrap preflight")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--agent-only", action="store_true", help="Check Cursor agent CLI login only")
    ap.add_argument("--codex-only", action="store_true", help="Check Codex CLI + resolved BUILD worker")
    ap.add_argument("--build-worker", action="store_true", help="Check Codex, Cursor, and resolved BUILD worker")
    ap.add_argument(
        "--cursor-first",
        action="store_true",
        help="Check Cursor CLI is used before Codex when Cursor has quota",
    )
    ap.add_argument(
        "--codex-first",
        action="store_true",
        help="Check Codex CLI is preferred to preserve Cursor quota (local default)",
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    local = repo / "ppe_operator_local.cmd"
    if local.is_file():
        subprocess.run(["cmd", "/c", str(local)], cwd=repo, check=False)

    if args.agent_only:
        return 0 if check_agent_cli() else 1

    if args.codex_only:
        return 0 if check_codex_cli() and check_build_worker(repo) else 1

    if args.build_worker:
        return 0 if check_codex_cli() and check_agent_cli() and check_build_worker(repo) else 1

    if args.cursor_first:
        return (
            0
            if check_agent_cli()
            and check_codex_cli()
            and check_cursor_tokens_first(repo)
            and check_build_worker(repo)
            else 1
        )

    if args.codex_first:
        return (
            0
            if check_codex_cli()
            and check_codex_tokens_first(repo)
            and check_build_worker(repo)
            else 1
        )

    checks = [
        check_ntfy(),
        check_codex_cli(),
        check_agent_cli(),
        check_build_worker(repo),
        check_git_identity(),
        check_gh(),
        check_tailscale(),
        check_sshd(),
        check_operator(repo),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
