"""Bootstrap gitignored operator notify config (private ntfy topic)."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER_TOPIC = "ppe-your-secret-topic-here"


def _repo_root(explicit: Path | None) -> Path:
    return (explicit or Path.cwd()).resolve()


def bootstrap_notify_cmd(repo: Path) -> dict[str, str]:
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
        target.write_text(text, encoding="utf-8")

    topic_match = re.search(r'^set "PPE_NTFY_TOPIC=(.*)"\s*$', text, re.MULTILINE)
    topic = topic_match.group(1).strip() if topic_match else ""
    topic_placeholder = topic == PLACEHOLDER_TOPIC or not topic

    return {
        "path": str(target),
        "created": str(created),
        "topic_placeholder": str(topic_placeholder),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ensure ppe_operator_notify.local.cmd exists with private topic")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = ap.parse_args(argv)
    try:
        result = bootstrap_notify_cmd(args.repo_root)
    except OSError as exc:
        print(f"bootstrap_operator_notify: {exc}", file=sys.stderr)
        return 1

    print(f"bootstrap_operator_notify: {result['path']}")
    if result["created"] == "True":
        print("  created from example")
    if result["topic_placeholder"] == "True":
        print("  WARN: set PPE_NTFY_TOPIC to your private ntfy topic and subscribe on your phone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
