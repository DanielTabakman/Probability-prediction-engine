"""Subscribe to ntfy and execute remote operator commands from the phone."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterator

from scripts.ppe_notify_push import (
    bootstrap_operator_notify_env,
    ntfy_configured,
    ntfy_server,
    ntfy_topic,
    notify_enabled,
)
from scripts.ppe_ntfy_commands import (
    command_security_warnings,
    commands_enabled,
    execute_command,
    notify_command_result,
    parse_command_message,
    should_ignore_message,
)

STATE_REL = "artifacts/control_plane/NTFY_CMD_STATE.json"


def state_path(repo: Path) -> Path:
    return repo / STATE_REL


def load_state(repo: Path) -> dict[str, Any]:
    path = state_path(repo)
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_state(repo: Path, state: dict[str, Any]) -> None:
    path = state_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _auth_headers() -> dict[str, str]:
    headers: dict[str, str] = {}
    token = os.environ.get("PPE_NTFY_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def stream_messages(*, since: str | None = None) -> Iterator[dict[str, Any]]:
    import requests

    topic = ntfy_topic()
    url = f"{ntfy_server()}/{topic}/sse"
    params: dict[str, str] = {}
    if since:
        params["since"] = since
    with requests.get(
        url,
        headers=_auth_headers(),
        params=params,
        stream=True,
        timeout=(15, None),
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if not line or not str(line).startswith("data: "):
                continue
            try:
                payload = json.loads(str(line)[6:])
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                yield payload


def poll_messages(*, since: str | None = None) -> list[dict[str, Any]]:
    import requests

    topic = ntfy_topic()
    url = f"{ntfy_server()}/{topic}/json"
    params: dict[str, str | int] = {"poll": 1, "since": since or "all"}
    response = requests.get(url, headers=_auth_headers(), params=params, timeout=30)
    response.raise_for_status()
    messages: list[dict[str, Any]] = []
    for line in response.text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            messages.append(item)
    return messages


def handle_message(repo: Path, message: dict[str, Any], *, notify: bool = True) -> dict[str, Any] | None:
    if should_ignore_message(message):
        return None
    command = parse_command_message(message)
    if command is None:
        return None
    result = execute_command(repo, command)
    if notify:
        notify_command_result(command, result)
    return {"command": command.name, "args": command.args, "result": result, "message_id": message.get("id")}


def process_messages(
    repo: Path,
    messages: list[dict[str, Any]],
    *,
    state: dict[str, Any],
    notify: bool = True,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    last_id = str(state.get("last_message_id") or "")
    handled: list[dict[str, Any]] = []
    newest = last_id

    for message in messages:
        msg_id = str(message.get("id") or "")
        if not msg_id:
            continue
        if last_id and msg_id == last_id:
            continue
        command = parse_command_message(message)
        if command is not None and command.name == "restart":
            # Ack before execute_restart stops workers — otherwise listener dies and replays this message.
            state = {**state, "last_message_id": msg_id}
            save_state(repo, state)
            last_id = msg_id
        outcome = handle_message(repo, message, notify=notify)
        if outcome is not None:
            handled.append(outcome)
        newest = msg_id

    if newest and newest != last_id:
        state = {**state, "last_message_id": newest}
    if handled:
        state = {**state, "last_command": handled[-1], "last_command_count": len(handled)}
    return handled, state


def ensure_cmd_listener_watermark(repo: Path, state: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    """First connect: advance cursor to newest message without replaying phone command history."""
    if state.get("cmd_listener_initialized") or state.get("last_message_id"):
        return state, False
    try:
        messages = poll_messages(since="all")
    except Exception:
        messages = []
    if messages:
        newest = str(messages[-1].get("id") or "")
        if newest:
            state = {**state, "last_message_id": newest, "cmd_listener_initialized": True}
            save_state(repo, state)
            return state, True
    state = {**state, "cmd_listener_initialized": True}
    save_state(repo, state)
    return state, True


def listen_once(repo: Path, *, notify: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    state, seeded = ensure_cmd_listener_watermark(repo, state)
    if seeded:
        return {
            "handled": [],
            "polled": 0,
            "initialized": True,
            "state_path": str(state_path(repo)),
        }
    since = str(state.get("last_message_id") or "") or None
    messages = poll_messages(since=since)
    handled, state = process_messages(repo, messages, state=state, notify=notify)
    save_state(repo, state)
    return {"handled": handled, "polled": len(messages), "state_path": str(state_path(repo))}


def cmd_poll_seconds() -> int:
    raw = os.environ.get("PPE_NTFY_CMD_POLL_SEC", "30").strip()
    try:
        return max(10, int(raw))
    except ValueError:
        return 30


def sse_preferred() -> bool:
    raw = os.environ.get("PPE_NTFY_CMD_SSE", "0").strip().lower()
    return raw in ("1", "true", "yes", "on")


def poll_loop(repo: Path, *, notify: bool = True) -> None:
    interval = cmd_poll_seconds()
    print(
        f"ppe_ntfy_listen: poll every {interval}s on topic={ntfy_topic()} — Ctrl+C to stop",
        flush=True,
    )
    while True:
        try:
            result = listen_once(repo, notify=notify)
            if result.get("handled"):
                print(json.dumps(result["handled"][-1], indent=2), flush=True)
        except KeyboardInterrupt:
            print("ppe_ntfy_listen: stopped", flush=True)
            return
        except Exception as exc:
            print(f"ppe_ntfy_listen: poll error: {exc}; retry in {interval}s", file=sys.stderr, flush=True)
        time.sleep(interval)


def sse_loop(repo: Path, *, notify: bool = True) -> None:
    state = load_state(repo)
    state, _seeded = ensure_cmd_listener_watermark(repo, state)
    since = str(state.get("last_message_id") or "") or None
    print(
        f"ppe_ntfy_listen: SSE on topic={ntfy_topic()} since={since or 'all'} — Ctrl+C to stop",
        flush=True,
    )
    while True:
        try:
            for message in stream_messages(since=since):
                msg_id = str(message.get("id") or "")
                if msg_id:
                    since = msg_id
                handled, state = process_messages(
                    repo,
                    [message],
                    state=state,
                    notify=notify,
                )
                save_state(repo, state)
                if handled:
                    print(json.dumps(handled[-1], indent=2), flush=True)
        except KeyboardInterrupt:
            print("ppe_ntfy_listen: stopped", flush=True)
            return
        except Exception as exc:
            print(f"ppe_ntfy_listen: stream error: {exc}; retry in 10s", file=sys.stderr, flush=True)
            time.sleep(10)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Listen for remote ntfy operator commands")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--once", action="store_true", help="Poll once and exit")
    ap.add_argument("--no-notify", action="store_true", help="Do not send result ntfy replies")
    ap.add_argument("--sse", action="store_true", help="Use SSE stream instead of poll loop")
    args = ap.parse_args(argv)

    if not notify_enabled() or not ntfy_configured():
        print("ppe_ntfy_listen: ntfy not configured (set PPE_NTFY_TOPIC)", file=sys.stderr)
        return 1
    if not commands_enabled():
        print("ppe_ntfy_listen: remote commands disabled (PPE_NTFY_CMD_ENABLED=0)", file=sys.stderr)
        return 1

    from scripts.ppe_loop_host_guard import loop_host_blocked

    blocked = loop_host_blocked()
    if blocked:
        print(
            f"ppe_ntfy_listen: blocked on this host ({blocked['guard_code']}) — "
            "phone commands run on the VM loop host only.",
            file=sys.stderr,
        )
        return 8

    repo = args.repo_root.resolve()
    bootstrap_operator_notify_env(repo)
    notify = not args.no_notify

    for warning in command_security_warnings():
        print(f"ppe_ntfy_listen: WARNING: {warning}", file=sys.stderr, flush=True)

    if args.once:
        result = listen_once(repo, notify=notify)
        print(json.dumps(result, indent=2))
        return 0

    if args.sse or sse_preferred():
        sse_loop(repo, notify=notify)
        return 0

    poll_loop(repo, notify=notify)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
