"""CLI: verify git diff against active_slice_touch_set.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.relay.slice_touch_set import load_active_slice_touch_set, verify_active_touch_set


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify slice diff against touch-set artifact.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--baseline-branch", default=None)
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Compare working tree vs HEAD (pushable gate style).",
    )
    args = parser.parse_args(argv)

    repo = args.repo_root.resolve()
    if load_active_slice_touch_set(repo) is None:
        print("verify_slice_touch_set: no active artifact; skip")
        return 0

    ok, errors = verify_active_touch_set(
        repo,
        baseline_branch=args.baseline_branch,
        use_worktree=args.worktree,
    )
    if ok:
        print("verify_slice_touch_set: OK")
        return 0

    for err in errors:
        print(err, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
