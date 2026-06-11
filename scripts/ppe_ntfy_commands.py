"""Parse and execute remote operator commands (phone -> desktop via ntfy)."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import OUTBOUND_TAG, ntfy_configured, notify_enabled, send_ntfy

KNOWN_COMMANDS = frozenset({"build", "restart", "fix", "status", "help"})


@dataclass(frozen=True)
class RemoteCommand:
    name: str
    args: str = ""


def commands_enabled() -> bool:
    return os.environ.get("PPE_NTFY_CMD_ENABLED", "1").strip().lower() not in ("0", "false", "no", "off")


def command_secret() -> str:
    return os.environ.get("PPE_NTFY_CMD_SECRET", "").strip()


def is_outbound_message(message: dict[str, Any]) -> bool:
    tags = message.get("tags") or []
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",") if t.strip()]
    return OUTBOUND_TAG in [str(t) for t in tags]


def should_ignore_message(message: dict[str, Any]) -> bool:
    if not isinstance(message, dict) or str(message.get("event") or "message") != "message":
        return True
    if is_outbound_message(message):
        return True
    if str(message.get("title") or "").startswith("PPE OK"):
        return True
    return not str(message.get("message") or "").strip()


def parse_command_text(text: str) -> RemoteCommand | None:
    tokens = (text or "").strip().lower().split()
    if tokens and tokens[0] in ("/ppe", "ppe"):
        tokens = tokens[1:]
    if tokens and tokens[0].startswith("/"):
        tokens[0] = tokens[0][1:]
    secret = command_secret()
    if secret:
        if not tokens or tokens[0] != secret.lower():
            return None
        tokens = tokens[1:]
    if not tokens or tokens[0] not in KNOWN_COMMANDS:
        return None
    return RemoteCommand(name=tokens[0], args=" ".join(tokens[1:]).strip())


def parse_command_message(message: dict[str, Any]) -> RemoteCommand | None:
    title = str(message.get("title") or "").strip()
    body = str(message.get("message") or "").strip()
    if title.lower().startswith("cmd:"):
        return parse_command_text(title[4:].strip() or body)
    return parse_command_text(body)


def stop_stack_processes() -> int:
    ps = (
        "$k=0; Get-CimInstance Win32_Process -EA SilentlyContinue | "
        "Where-Object { $_.CommandLine -match 'run_ppe_auto_local_loop|watch_operator_mobile' "
        "-and $_.CommandLine -notmatch 'ppe_ntfy_listen' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue; $k++ }; $k"
    )
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
        return max(0, int((proc.stdout or "0").strip()))
    except (OSError, subprocess.TimeoutExpired):
        return 0


def execute_restart(repo: Path) -> dict[str, Any]:
    killed = stop_stack_processes()
    time.sleep(2)
    from scripts.ppe_desktop_operator_stack import ensure_stack

    return {"action": "restart", "killed": killed, "stack": ensure_stack(repo.resolve(), start=True)}


def execute_status(repo: Path) -> dict[str, Any]:
    from scripts.ppe_desktop_operator_stack import collect_status

    result = collect_status(repo.resolve(), apply_propagate=False, ensure=False)
    brief = str(result.get("operator_brief") or "")
    stack = result.get("stack") or {}
    body = f"loop={stack.get('loop_running')} watch={stack.get('watch_running')}\n{brief}"
    sent = send_ntfy("PPE status", body, tags=["ppe", "cmd", OUTBOUND_TAG])
    return {"action": "status", "body": body, "notified": sent}


def execute_build(repo: Path, *, note: str = "") -> dict[str, Any]:
    from scripts.ppe_ide_handoff import respond_to_ide_build

    return respond_to_ide_build(repo, source="phone", note=note)


def execute_fix(repo: Path, *, note: str = "") -> dict[str, Any]:
    from scripts.ppe_remote_fix_agent import launch_fix_agent

    return launch_fix_agent(repo, user_note=note)


def execute_help(repo: Path) -> dict[str, Any]:
    prefix = f"{command_secret()} " if command_secret() else ""
    from scripts.ppe_operator_hint import PPE_GO_HINT

    body = (
        f"{prefix}build - IDE BUILD for queued slice\n"
        f"Desktop: {PPE_GO_HINT}\n"
        f"{prefix}restart - restart stack\n"
        f"{prefix}fix - investigate blocker (CLI or IDE handoff)\n"
        f"{prefix}status - operator status\n"
        f"{prefix}help - this list"
    )
    sent = send_ntfy("PPE remote commands", body, tags=["ppe", "cmd", OUTBOUND_TAG], priority="low")
    return {"action": "help", "body": body, "notified": sent}


def execute_command(repo: Path, command: RemoteCommand) -> dict[str, Any]:
    if command.name == "build":
        return execute_build(repo, note=command.args)
    if command.name == "restart":
        return execute_restart(repo)
    if command.name == "status":
        return execute_status(repo)
    if command.name == "fix":
        return execute_fix(repo, note=command.args)
    return execute_help(repo)


def notify_command_result(command: RemoteCommand, result: dict[str, Any]) -> bool:
    if not notify_enabled() or not ntfy_configured():
        return False
    action = str(result.get("action") or command.name)
    if action == "restart":
        stack = result.get("stack") or {}
        return send_ntfy(
            "PPE restarted",
            f"killed={result.get('killed')} loop={stack.get('loop_running')}",
            tags=["ppe", "cmd", OUTBOUND_TAG],
        )
    if command.name in ("build", "fix"):
        if result.get("started"):
            if result.get("notified"):
                return True
            label = result.get("slice_id") or result.get("verdict") or ""
            return send_ntfy(
                f"PPE {command.name} started{(' ' + label) if label else ''}",
                str(result.get("message") or "started"),
                tags=["ppe", "cmd", OUTBOUND_TAG],
                priority="high",
            )
        if result.get("debounced"):
            return False
        return send_ntfy(
            f"PPE {command.name} failed",
            str(result.get("reason") or "did not start"),
            tags=["ppe", "cmd", OUTBOUND_TAG],
            priority="high",
        )
    if action == "status":
        return bool(result.get("notified"))
    return bool(result.get("notified"))


def main(argv: list[str] | None = None) -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--text", required=True)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    args = ap.parse_args(argv)
    cmd = parse_command_text(args.text)
    if cmd is None:
        print(f"unknown command: {args.text!r}", file=sys.stderr)
        return 2
    result = execute_command(args.repo_root.resolve(), cmd)
    if not args.no_notify:
        notify_command_result(cmd, result)
    print(json.dumps(result, indent=2) if args.json else result)
    return 0 if result.get("started", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
