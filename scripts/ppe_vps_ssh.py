#!/usr/bin/env python3
"""Run non-interactive VPS commands for MSOS production ops.

Reads connection settings from environment (set by ppe_operator_ssh.local.cmd):
  PPE_VPS_HOST, PPE_VPS_USER, PPE_VPS_SSH_KEY, PPE_VPS_ROOT

Never pass secrets on the command line. Do not log private key contents.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
from pathlib import Path


def _env(name: str) -> str:
    return os.environ.get(name, "").strip()


def ssh_config() -> tuple[str, str, str, str]:
    host = _env("PPE_VPS_HOST")
    user = _env("PPE_VPS_USER")
    key = _env("PPE_VPS_SSH_KEY")
    root = _env("PPE_VPS_ROOT") or "/opt/marketstructureos"
    missing = [n for n, v in [("PPE_VPS_HOST", host), ("PPE_VPS_USER", user), ("PPE_VPS_SSH_KEY", key)] if not v]
    if missing:
        raise SystemExit(
            "Missing VPS SSH config: "
            + ", ".join(missing)
            + ". Copy ppe_operator_ssh.local.cmd.example to ppe_operator_ssh.local.cmd."
        )
    key_path = Path(key).expanduser()
    if not key_path.is_file():
        raise SystemExit(f"PPE_VPS_SSH_KEY not found: {key_path}")
    return host, user, str(key_path), root


def run_remote(remote_cmd: str, *, check: bool = True) -> int:
    host, user, key_path, _root = ssh_config()
    target = f"{user}@{host}"
    ssh_argv = [
        "ssh",
        "-i",
        key_path,
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=accept-new",
        target,
        remote_cmd,
    ]
    print(f"remote: {remote_cmd}", file=sys.stderr)
    proc = subprocess.run(ssh_argv, check=False)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def cmd_deploy(_: argparse.Namespace) -> int:
    root = ssh_config()[3]
    remote = f"cd {shlex.quote(root)} && git pull && docker compose up -d --build"
    return run_remote(remote)


def cmd_status(_: argparse.Namespace) -> int:
    root = ssh_config()[3]
    remote = f"cd {shlex.quote(root)} && docker compose ps"
    return run_remote(remote)


def cmd_research_cta(args: argparse.Namespace) -> int:
    if not args.email:
        raise SystemExit("usage: ppe_vps_ssh.py research-cta <email>")
    root = ssh_config()[3]
    email = args.email.strip()
    remote = (
        f"cd {shlex.quote(root)} && "
        f"bash scripts/vps_enable_research_cta.sh {shlex.quote(email)}"
    )
    return run_remote(remote)


def cmd_remote(args: argparse.Namespace) -> int:
    if not args.command:
        raise SystemExit("usage: ppe_vps_ssh.py remote -- <shell command>")
    return run_remote(args.command)


def cmd_print_config(_: argparse.Namespace) -> int:
    host, user, key_path, root = ssh_config()
    print(f"host={host}")
    print(f"user={user}")
    print(f"key={key_path}")
    print(f"root={root}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MSOS VPS SSH operator helper")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("deploy", help="git pull && docker compose up -d --build on VPS")
    sub.add_parser("status", help="docker compose ps on VPS")
    sub.add_parser("config", help="print resolved SSH settings (no connection)")

    p_cta = sub.add_parser("research-cta", help="enable research beta mailto CTA on VPS")
    p_cta.add_argument("email")

    p_remote = sub.add_parser("remote", help="run arbitrary shell command on VPS")
    p_remote.add_argument("command", nargs=argparse.REMAINDER)

    args = parser.parse_args(argv)
    handlers = {
        "deploy": cmd_deploy,
        "status": cmd_status,
        "research-cta": cmd_research_cta,
        "remote": cmd_remote,
        "config": cmd_print_config,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
