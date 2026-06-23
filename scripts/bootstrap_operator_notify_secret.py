"""Bootstrap gitignored operator notify config with a strong command secret."""

from __future__ import annotations

import argparse
import re
import secrets
import sys
from pathlib import Path

PLACEHOLDER_SECRET = "your-long-random-secret-here"
PLACEHOLDER_TOPIC = "ppe-your-secret-topic-here"


def _repo_root(explicit: Path | None) -> Path:
    return (explicit or Path.cwd()).resolve()


def _needs_secret(text: str) -> bool:
    match = re.search(r'^set "PPE_NTFY_CMD_SECRET=(.*)"\s*$', text, re.MULTILINE)
    if not match:
        return True
    value = match.group(1).strip()
    return not value or value == PLACEHOLDER_SECRET


def bootstrap_notify_cmd(repo: Path, *, force_secret: bool = False) -> dict[str, str]:
    repo = _repo_root(repo)
    example = repo / "ppe_operator_notify.local.cmd.example"
    target = repo / "ppe_operator_notify.local.cmd"
    if not example.is_file():
        raise FileNotFoundError(f"missing example: {example}")

    if target.is_file():
        text = target.read_text(encoding="utf-8")
        created = False
    else:
        text = example.read_text(encoding="utf-8")
        created = True

    secret = secrets.token_urlsafe(24)
    if force_secret or _needs_secret(text):
        if f'set "PPE_NTFY_CMD_SECRET={PLACEHOLDER_SECRET}"' in text:
            text = text.replace(
                f'set "PPE_NTFY_CMD_SECRET={PLACEHOLDER_SECRET}"',
                f'set "PPE_NTFY_CMD_SECRET={secret}"',
                1,
            )
        elif 'PPE_NTFY_CMD_SECRET=' not in text:
            text = text.rstrip() + f'\nset "PPE_NTFY_CMD_SECRET={secret}"\n'
        else:
            text = re.sub(
                r'^set "PPE_NTFY_CMD_SECRET=.*"$',
                f'set "PPE_NTFY_CMD_SECRET={secret}"',
                text,
                count=1,
                flags=re.MULTILINE,
            )
        secret_rotated = True
    else:
        secret_rotated = False
        secret = "(unchanged)"

    if created or secret_rotated or force_secret:
        target.write_text(text, encoding="utf-8")

    topic_match = re.search(r'^set "PPE_NTFY_TOPIC=(.*)"\s*$', text, re.MULTILINE)
    topic = topic_match.group(1).strip() if topic_match else ""
    topic_placeholder = topic == PLACEHOLDER_TOPIC or not topic

    return {
        "path": str(target),
        "created": str(created),
        "secret_rotated": str(secret_rotated),
        "topic_placeholder": str(topic_placeholder),
        "secret_hint": secret[:4] + "…" if secret_rotated and secret != "(unchanged)" else secret,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ensure ppe_operator_notify.local.cmd has a command secret")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--force-secret", action="store_true", help="Rotate secret even if one is already set")
    args = ap.parse_args(argv)
    try:
        result = bootstrap_notify_cmd(args.repo_root, force_secret=args.force_secret)
    except OSError as exc:
        print(f"bootstrap_operator_notify_secret: {exc}", file=sys.stderr)
        return 1

    print(f"bootstrap_operator_notify_secret: {result['path']}")
    if result["created"] == "True":
        print("  created from example")
    if result["secret_rotated"] == "True":
        print(f"  command secret set ({result['secret_hint']}) — prefix phone commands with it")
    if result["topic_placeholder"] == "True":
        print("  WARN: set PPE_NTFY_TOPIC to your private ntfy topic and subscribe on your phone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
