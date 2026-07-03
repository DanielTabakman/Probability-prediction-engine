"""One-shot diagnostic: phone ntfy commands (status) path."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from scripts.ppe_desktop_operator_stack import stack_status
from scripts.ppe_loop_host_guard import loop_host_blocked
from scripts.ppe_notify_push import bootstrap_operator_notify_env, ntfy_configured, notify_enabled
from scripts.ppe_ntfy_commands import command_secret, commands_enabled, parse_command_text


def _load_full_operator_env(repo: Path) -> None:
    """Match .cmd entrypoints: notify + no_loop guard on desktop."""
    bootstrap_operator_notify_env(repo)
    no_loop = repo / "ppe_operator_no_loop.local.cmd"
    if not no_loop.is_file():
        return
    try:
        import subprocess

        proc = subprocess.run(
            ["cmd", "/c", f'call "{no_loop}" && set PPE'],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        for line in (proc.stdout or "").splitlines():
            if "=" not in line or not line.startswith("PPE"):
                continue
            key, _, value = line.partition("=")
            if key.strip():
                os.environ[key.strip()] = value
    except (OSError, subprocess.TimeoutExpired):
        pass


def diagnose_local(repo: Path) -> dict:
    repo = repo.resolve()
    _load_full_operator_env(repo)
    secret = command_secret()
    blocked = loop_host_blocked()
    stack = stack_status(repo)
    return {
        "host": "desktop",
        "notify_enabled": notify_enabled(),
        "ntfy_configured": ntfy_configured(),
        "commands_enabled": commands_enabled(),
        "loop_host_blocked": blocked,
        "secret_configured": bool(secret),
        "plain_status_works": parse_command_text("status") is not None,
        "plain_help_works": parse_command_text("help") is not None,
        "prefixed_status_works": parse_command_text(f"{secret} status") is not None if secret else None,
        "stack": stack,
        "likely_cause": _likely_cause(blocked, stack, secret),
    }


def _likely_cause(blocked: dict | None, stack: dict, secret: str) -> str:
    if blocked:
        if secret and not parse_command_text("status"):
            return (
                "Phone commands run on the VM loop host only. On desktop, prefix with your secret "
                f"(e.g. `{secret} status`) — plain `status` is ignored. "
                "If still silent, the VM ntfy listener may be down (run VM stack ensure)."
            )
        return "Phone commands are handled on the VM loop host, not this desktop."
    if not stack.get("ntfy_listen_running"):
        return "ntfy command listener is not running on this machine."
    if secret and not parse_command_text("status"):
        return f"Prefix with secret: `{secret} status` (plain `status` is rejected)."
    return "Listener should accept commands; try `help` or `{secret} status`."


def diagnose_vm(repo: Path) -> dict:
    from scripts.ppe_operator_vm_ssh import VM_REPO, VM_SSH_HOST, ssh_vm

    cmd = f"cd /d {VM_REPO} && call call_ppe_operator_local.cmd && run_ppe_headless_stack.cmd --ensure"
    proc = ssh_vm(cmd, timeout=120)
    stack: dict = {}
    stdout = (proc.get("stdout") or "").strip()
    if stdout:
        start = stdout.find("{")
        if start >= 0:
            try:
                stack = json.loads(stdout[start:])
            except json.JSONDecodeError:
                stack = {"raw": stdout[-500:]}
    return {
        "host": VM_SSH_HOST,
        "ssh_ok": bool(proc.get("ok")),
        "stack": stack,
        "ntfy_listener_running": bool(stack.get("ntfy_listen_running")),
        "supervisor_running": bool(stack.get("supervisor_running") or stack.get("headless_supervisor_running")),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Diagnose phone ntfy status command path")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-vm", action="store_true")
    ap.add_argument("--heal-vm", action="store_true", help="Run run_ppe_headless_stack.cmd --ensure on VM")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    report: dict = {"local": diagnose_local(repo)}
    if not args.skip_vm or args.heal_vm:
        try:
            report["vm"] = diagnose_vm(repo)
        except Exception as exc:
            report["vm"] = {"error": str(exc)}

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        loc = report["local"]
        secret = command_secret()
        print("=== Phone ntfy command diagnostic ===")
        print(f"Desktop commands_enabled: {loc['commands_enabled']}")
        print(f"Plain 'status' works: {loc['plain_status_works']}")
        print(f"Plain 'help' works: {loc['plain_help_works']}")
        if secret:
            print(f"Prefixed '{secret} status' works: {loc['prefixed_status_works']}")
        print()
        print(f"Likely cause: {loc['likely_cause']}")
        if "vm" in report:
            vm = report["vm"]
            print()
            print(f"VM ({vm.get('host', '?')}) SSH ok: {vm.get('ssh_ok', False)}")
            print(f"VM ntfy listener: {vm.get('ntfy_listener_running')}")
            print(f"VM supervisor: {vm.get('supervisor_running')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
