"""CLI: write artifacts/control_plane/active_slice_touch_set.json from phase plan."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.relay.slice_touch_set import write_active_slice_touch_set


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write active slice touch-set artifact.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--phase-plan", type=Path, required=True)
    parser.add_argument("--slice-id", required=True)
    parser.add_argument("--declared-plane", default=None)
    args = parser.parse_args(argv)

    try:
        out = write_active_slice_touch_set(
            args.repo_root.resolve(),
            phase_plan_path=args.phase_plan,
            slice_id=args.slice_id,
            declared_plane=args.declared_plane,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1

    print(f"write_slice_touch_set: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
