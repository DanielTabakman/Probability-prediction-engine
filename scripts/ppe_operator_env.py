"""Apply docs/SOP/PPE_AUTO_OPERATOR.json to the current process environment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_operator_config import OPERATOR_REL, apply_operator_env, continuous_max


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Apply PPE_AUTO_OPERATOR.json to os.environ")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--print-continuous-max", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.print_continuous_max:
        print(continuous_max(repo))
        return 0

    out = apply_operator_env(repo)
    if out.get("applied"):
        print(f"ppe_operator_env: enabled ({OPERATOR_REL})")
    else:
        print("ppe_operator_env: no config or disabled (set env manually if needed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
