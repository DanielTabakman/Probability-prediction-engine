"""Deprecated — phone commands no longer use PPE_NTFY_CMD_SECRET prefixes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def ensure_secret(repo: Path, *, secret: str = "") -> dict[str, str]:
    """No-op retained for VM_RESTART / DESKTOP_VM_MAINTAIN compatibility."""
    repo = repo.resolve()
    path = repo / "ppe_operator_notify.local.cmd"
    return {
        "action": "deprecated_noop",
        "path": str(path),
        "detail": "PPE_NTFY_CMD_SECRET prefix removed — phone commands use plain text (status, build, …).",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deprecated no-op (command secret prefix removed)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--secret", default="")
    args = ap.parse_args(argv)
    result = ensure_secret(args.repo_root, secret=args.secret.strip())
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
