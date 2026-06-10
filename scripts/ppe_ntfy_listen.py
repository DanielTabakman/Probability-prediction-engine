"""Subscribe to ntfy and execute remote operator commands from the phone."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Iterator

from scripts.ppe_notify_push import ntfy_configured, ntfy_server, ntfy_topic, notify_enabled
from scripts.ppe_ntfy_commands import (
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
        outcome = handle_message(repo, message, notify=notify)
        if outcome is not None:
            handled.append(outcome)
        newest = msg_id

    if newest and newest != last_id:
        state = {**state, "last_message_id": newest}
    if handled:
        state = {**state, "last_command": handled[-1], "last_command_count": len(handled)}
    return handled, state


def listen_once(repo: Path, *, notify: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    state = load_state(repo)
    since = str(state.get("last_message_id") or "") or None
    messages = poll_messages(since=since)
    handled, state = process_messages(repo, messages, state=state, notify=notify)
    save_state(repo, state)
    return {"handled": handled, "polled": len(messages), "state_path": str(state_path(repo))}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Listen for remote ntfy operator commands")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--once", action="store_true", help="Poll once and exit")
    ap.add_argument("--no-notify", action="store_true", help="Do not send result ntfy replies")
    args = ap.parse_args(argv)

    if not notify_enabled() or not ntfy_configured():
        print("ppe_ntfy_listen: ntfy not configured (set PPE_NTFY_TOPIC)", file=sys.stderr)
        return 1
    if not commands_enabled():
        print("ppe_ntfy_listen: remote commands disabled (PPE_NTFY_CMD_ENABLED=0)", file=sys.stderr)
        return 1

    repo = args.repo_root.resolve()
    notify = not args.no_notify

    if args.once:
        result = listen_once(repo, notify=notify)
        print(json.dumps(result, indent=2))
        return 0

    state = load_state(repo)
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
                if handled:
                    save_state(repo, state)
                    print(json.dumps(handled[-1], indent=2), flush=True)
        except KeyboardInterrupt:
            print("ppe_ntfy_listen: stopped", flush=True)
            return 0
        except Exception as exc:
            print(f"ppe_ntfy_listen: stream error: {exc}; retry in 10s", file=sys.stderr, flush=True)
            time.sleep(10)


if __name__ == "__main__":
    raise SystemExit(main())
