"""Reset ntfy send quota / loop-down cooldown after an alert storm."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.ppe_notify_push import (
    LOOP_DOWN_STATE_REL,
    QUOTA_STATUS_REL,
    SEND_STATE_REL,
    loop_down_state_path,
    quota_status_path,
    send_state_path,
)


def reset(repo: Path, *, loop_down: bool = True) -> dict[str, bool]:
    repo = repo.resolve()
    removed: dict[str, bool] = {}
    for rel, key in (
        (SEND_STATE_REL, "send_state"),
        (QUOTA_STATUS_REL, "quota_status"),
        (LOOP_DOWN_STATE_REL, "loop_down_state"),
    ):
        path = repo / rel
        if key == "loop_down_state" and not loop_down:
            removed[key] = False
            continue
        if path.is_file():
            path.unlink()
            removed[key] = True
        else:
            removed[key] = False
    return removed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Reset ntfy quota and loop-down cooldown state")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--keep-loop-down", action="store_true", help="Keep loop-down pending/cooldown state")
    args = ap.parse_args(argv)
    removed = reset(args.repo_root, loop_down=not args.keep_loop_down)
    print(json.dumps({"reset": removed, "paths": {
        "send": str(send_state_path(args.repo_root)),
        "quota": str(quota_status_path(args.repo_root)),
        "loop_down": str(loop_down_state_path(args.repo_root)),
    }}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
