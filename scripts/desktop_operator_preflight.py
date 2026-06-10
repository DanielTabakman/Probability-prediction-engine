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
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    local = repo / "ppe_operator_local.cmd"
    if local.is_file():
        subprocess.run(["cmd", "/c", str(local)], cwd=repo, check=False)

    checks = [
        check_ntfy(),
        check_git_identity(),
        check_gh(),
        check_tailscale(),
        check_sshd(),
        check_operator(repo),
    ]
    return 0 if all(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
