"""One-shot mobile ntfy setup for desktop operator (creates gitignored local config)."""

from __future__ import annotations

import argparse
import secrets
import sys
from pathlib import Path
from typing import Any

NOTIFY_LOCAL = "ppe_operator_notify.local.cmd"
NOTIFY_EXAMPLE = "ppe_operator_notify.local.cmd.example"
TOPIC_PLACEHOLDER = "ppe-your-secret-topic-here"
SECRET_PLACEHOLDER = "your-long-random-secret-here"


def init_notify_config(repo: Path, *, force: bool = False) -> dict[str, Any]:
    repo = repo.resolve()
    dest = repo / NOTIFY_LOCAL
    if dest.is_file() and not force:
        return {"ok": True, "action": "already_exists", "path": str(dest)}

    example = repo / NOTIFY_EXAMPLE
    if not example.is_file():
        return {"ok": False, "error": f"missing {NOTIFY_EXAMPLE}"}

    topic = f"ppe-{secrets.token_hex(8)}"
    cmd_secret = secrets.token_urlsafe(24)
    text = example.read_text(encoding="utf-8")
    text = text.replace(TOPIC_PLACEHOLDER, topic)
    text = text.replace(SECRET_PLACEHOLDER, cmd_secret)
    dest.write_text(text, encoding="utf-8")

    return {
        "ok": True,
        "action": "created" if not force else "recreated",
        "path": str(dest),
        "topic": topic,
        "subscribe_hint": f"Subscribe to topic {topic!r} in the ntfy app on your phone.",
    }


def maybe_init_notify_config(repo: Path) -> dict[str, Any]:
    """Create notify config only when missing — safe to call from doctor/status."""
    dest = (repo / NOTIFY_LOCAL).resolve()
    if dest.is_file():
        return {"ok": True, "action": "already_exists", "path": str(dest)}
    return init_notify_config(repo)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Initialize ppe_operator_notify.local.cmd from example")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--force", action="store_true", help="Overwrite existing notify config")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    result = init_notify_config(repo, force=bool(args.force))
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    elif result.get("ok"):
        action = result.get("action")
        if action == "already_exists":
            print(f"ppe_notify_setup: {NOTIFY_LOCAL} already exists")
        else:
            print(f"ppe_notify_setup: wrote {NOTIFY_LOCAL}")
            print(result.get("subscribe_hint") or "")
    else:
        print(f"ppe_notify_setup: ERROR {result.get('error')}", file=sys.stderr)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
