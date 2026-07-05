"""Parse and execute remote operator commands (phone -> desktop via ntfy)."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ppe_notify_push import (
    OUTBOUND_TAG,
    apply_snooze_request,
    format_snooze_until,
    ntfy_configured,
    notify_enabled,
    parse_snooze_args,
    send_ntfy,
)
from scripts.ppe_phone_status import format_phone_status, phone_status_title

KNOWN_COMMANDS = frozenset({"build", "restart", "fix", "status", "help", "snooze"})


@dataclass(frozen=True)
class RemoteCommand:
    name: str
    args: str = ""


def commands_enabled() -> bool:
    return os.environ.get("PPE_NTFY_CMD_ENABLED", "1").strip().lower() not in ("0", "false", "no", "off")


def command_security_warnings() -> list[str]:
    """Startup hints when remote commands are enabled but under-protected."""
    if not commands_enabled():
        return []
    warnings: list[str] = []
    if not ntfy_configured():
        warnings.append(
            "PPE_NTFY_TOPIC is unset — set a private topic in ppe_operator_notify.local.cmd "
            "and subscribe in the ntfy app on your phone."
        )
    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if not token and (os.environ.get("PPE_NTFY_SERVER", "https://ntfy.sh").strip().rstrip("/") == "https://ntfy.sh"):
        warnings.append(
            "PPE_NTFY_TOKEN is unset on ntfy.sh — use an unguessable topic name or a private ntfy server with ACL."
        )
    return warnings


def _strip_legacy_command_prefix(tokens: list[str]) -> list[str]:
    """Accept old `{secret} status` messages without requiring the prefix going forward."""
    legacy = os.environ.get("PPE_NTFY_CMD_SECRET", "").strip().lower()
    if legacy and tokens and tokens[0] == legacy:
        return tokens[1:]
    return tokens


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
    title = str(message.get("title") or "")
    if title.startswith("PPE OK") or title.startswith("PPE: restart"):
        return True
    return not str(message.get("message") or "").strip()


def parse_command_text(text: str) -> RemoteCommand | None:
    tokens = (text or "").strip().lower().split()
    if tokens and tokens[0] in ("/ppe", "ppe"):
        tokens = tokens[1:]
    if tokens and tokens[0].startswith("/"):
        tokens[0] = tokens[0][1:]
    tokens = _strip_legacy_command_prefix(tokens)
    if not tokens or tokens[0] not in KNOWN_COMMANDS:
        return None
    name = tokens[0]
    return RemoteCommand(name=name, args=" ".join(tokens[1:]).strip())


def parse_command_message(message: dict[str, Any]) -> RemoteCommand | None:
    title = str(message.get("title") or "").strip()
    body = str(message.get("message") or "").strip()
    if title.lower().startswith("cmd:"):
        return parse_command_text(title[4:].strip() or body)
    return parse_command_text(body)


def stop_stack_processes(*, exclude_pid: int | None = None) -> int:
    pid_filter = ""
    if exclude_pid is not None:
        pid_filter = f" -and $_.ProcessId -ne {int(exclude_pid)}"
    ps = (
        "$k=0; Get-CimInstance Win32_Process -EA SilentlyContinue | "
        "Where-Object { $_.CommandLine -match "
        "'run_ppe_auto_local_loop|watch_operator_mobile|ppe_ntfy_listen|ppe_ide_build_local_watcher|"
        "ppe_headless_stack_supervisor|ppe_watch_operator_mobile|start_ppe_desktop_operator'"
        f"{pid_filter} }} | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue; $k++ }; $k"
    )
    try:
        proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, timeout=60)
        return max(0, int((proc.stdout or "0").strip()))
    except (OSError, subprocess.TimeoutExpired):
        return 0


def execute_restart(repo: Path) -> dict[str, Any]:
    from scripts.ppe_desktop_operator_stack import ensure_stack, stack_status
    from scripts.ppe_loop_host_guard import loop_host_blocked

    repo = repo.resolve()
    blocked = loop_host_blocked()
    if blocked:
        return {
            "action": "restart",
            "refused": True,
            "reason": blocked["guard_detail"],
            "stack": stack_status(repo),
        }

    killed = stop_stack_processes(exclude_pid=os.getpid())
    time.sleep(2)
    stack = ensure_stack(repo, start=True)
    if not stack.get("loop_running") or not stack.get("watch_running"):
        time.sleep(5)
        stack = {**stack, **stack_status(repo)}
    return {"action": "restart", "killed": killed, "stack": stack}


def execute_status(repo: Path) -> dict[str, Any]:
    from scripts.ppe_desktop_operator_stack import stack_status
    from scripts.ppe_operator_status import collect_operator_status

    repo = repo.resolve()
    status = collect_operator_status(repo)
    stack = stack_status()
    body = format_phone_status(status, stack=stack, repo=repo)
    try:
        from scripts.ppe_autobuilder import collect_autobuilder_status, format_status_brief, write_status_artifact

        ab = collect_autobuilder_status(repo)
        write_status_artifact(repo, ab)
        body = f"{body}\n\nAutobuilder: {format_status_brief(ab)}"
    except Exception:
        pass
    title = phone_status_title(status)
    sent = send_ntfy(
        title,
        body,
        tags=["ppe", "cmd", OUTBOUND_TAG],
        bypass_throttle=True,
    )
    return {"action": "status", "body": body, "notified": sent, "title": title}


def execute_build(repo: Path, *, note: str = "") -> dict[str, Any]:
    from scripts.ppe_ide_handoff import respond_to_ide_build

    return respond_to_ide_build(repo, source="phone", note=note)


def execute_fix(repo: Path, *, note: str = "") -> dict[str, Any]:
    from scripts.ppe_remote_fix_agent import launch_fix_agent

    return launch_fix_agent(repo, user_note=note)


def execute_snooze(repo: Path, *, note: str = "") -> dict[str, Any]:
    try:
        request = parse_snooze_args(note)
    except ValueError:
        sent = send_ntfy(
            "PPE snooze help",
            "Use: snooze | snooze 6 | snooze 30m | snooze until 08:00 | snooze clear",
            tags=["ppe", "cmd", OUTBOUND_TAG],
            priority="low",
            bypass_snooze=True,
            bypass_throttle=True,
        )
        return {"action": "snooze", "mode": "help", "notified": sent}
    if request.mode == "clear":
        payload = apply_snooze_request(request, reason="phone-clear", repo=repo)
        sent = send_ntfy(
            "PPE ntfy awake",
            "Phone pushes resumed.",
            tags=["ppe", "cmd", OUTBOUND_TAG],
            priority="low",
            bypass_snooze=True,
            bypass_throttle=True,
        )
        return {"action": "snooze", "mode": "clear", "notified": sent, "payload": payload}
    payload = apply_snooze_request(request, reason="phone", repo=repo) or {}
    until = str(payload.get("until") or "")
    until_local = format_snooze_until(until)
    if request.mode == "until":
        detail = f"No phone pings until {until_local}."
    else:
        detail = f"No phone pings for {request.hours:g}h (until {until_local})."
    sent = send_ntfy(
        "PPE ntfy snoozed",
        f"{detail} Send snooze clear to resume early.",
        tags=["ppe", "cmd", OUTBOUND_TAG],
        priority="low",
        bypass_snooze=True,
        bypass_throttle=True,
    )
    return {
        "action": "snooze",
        "mode": request.mode,
        "hours": request.hours,
        "until": until,
        "until_local": until_local,
        "notified": sent,
    }


def execute_help(repo: Path) -> dict[str, Any]:
    from scripts.ppe_operator_hint import PPE_GO_HINT

    body = (
        "build - start IDE BUILD when verdict is IDE_BUILD\n"
        f"Desktop: {PPE_GO_HINT}\n"
        "restart - restart loop + watch on the VM loop host\n"
        "fix - investigate blocker (CLI or IDE handoff)\n"
        "status - friendly operator snapshot\n"
        "snooze [6|30m|until 08:00|clear] - mute phone pings (default 8h)\n"
        "help - this list"
    )
    sent = send_ntfy(
        "PPE remote commands",
        body,
        tags=["ppe", "cmd", OUTBOUND_TAG],
        priority="low",
        bypass_throttle=True,
    )
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
    if command.name == "snooze":
        return execute_snooze(repo, note=command.args)
    return execute_help(repo)


def notify_command_result(command: RemoteCommand, result: dict[str, Any]) -> bool:
    if not notify_enabled() or not ntfy_configured():
        return False
    action = str(result.get("action") or command.name)
    if action == "restart":
        if result.get("refused"):
            return send_ntfy(
                "PPE: restart refused",
                f"{result.get('reason') or 'This machine cannot run the operator loop.'}\n"
                "Use VM_RESTART on the Hyper-V VM. Do not send phone restart from the daily PC.",
                tags=["ppe", "cmd", OUTBOUND_TAG],
                priority="high",
                bypass_throttle=True,
            )
        stack = result.get("stack") or {}
        loop = "on" if stack.get("loop_running") else "off"
        watch = "on" if stack.get("watch_running") else "off"
        if loop == "off" or watch == "off":
            return send_ntfy(
                "PPE: restart failed",
                f"Operator stack did not come back up (loop {loop} · watch {watch}).\n"
                "On the VM double-click VM_RESTART once — avoid phone restart until stack is healthy.",
                tags=["ppe", "cmd", OUTBOUND_TAG],
                priority="high",
                bypass_throttle=True,
            )
        return send_ntfy(
            "PPE: restarted",
            f"Operator stack restarted ({result.get('killed', 0)} old process(es) stopped).\n"
            f"Loop: {loop} · Watch: {watch}",
            tags=["ppe", "cmd", OUTBOUND_TAG],
            bypass_throttle=True,
        )
    if command.name in ("build", "fix"):
        if result.get("notified"):
            return True
        if result.get("started"):
            label = result.get("slice_id") or result.get("verdict") or ""
            return send_ntfy(
                f"PPE {command.name} started{(' ' + label) if label else ''}",
                str(result.get("message") or "started"),
                tags=["ppe", "cmd", OUTBOUND_TAG],
                priority="high",
                bypass_throttle=True,
            )
        if result.get("debounced"):
            return False
        return send_ntfy(
            f"PPE {command.name} failed",
            str(result.get("reason") or "did not start"),
            tags=["ppe", "cmd", OUTBOUND_TAG],
            priority="high",
            bypass_throttle=True,
        )
    if action in ("status", "snooze"):
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
