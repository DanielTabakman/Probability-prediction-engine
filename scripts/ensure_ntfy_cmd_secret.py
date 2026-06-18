"""Ensure ppe_operator_notify.local.cmd defines PPE_NTFY_CMD_SECRET (restart guard)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

DEFAULT_SECRET = "ppe-msos-remote"
SECRET_LINE = 'set "PPE_NTFY_CMD_SECRET={secret}"'


def ensure_secret(repo: Path, *, secret: str = DEFAULT_SECRET) -> dict[str, str]:
    repo = repo.resolve()
    path = repo / "ppe_operator_notify.local.cmd"
    if not path.is_file():
        return {"action": "missing_notify_file", "path": str(path)}
    text = path.read_text(encoding="utf-8")
    if "PPE_NTFY_CMD_SECRET=" in text:
        return {"action": "already_set", "path": str(path)}
    line = SECRET_LINE.format(secret=secret)
    path.write_text(text.rstrip() + "\n\n" + line + "\n", encoding="utf-8")
    return {"action": "appended", "path": str(path), "line": line}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Append PPE_NTFY_CMD_SECRET when missing")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--secret", default=DEFAULT_SECRET)
    args = ap.parse_args(argv)
    result = ensure_secret(args.repo_root, secret=args.secret.strip())
    print(result)
    return 0 if result["action"] in ("already_set", "appended") else 1


if __name__ == "__main__":
    raise SystemExit(main())
