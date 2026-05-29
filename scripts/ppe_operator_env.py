"""Apply docs/SOP/PPE_AUTO_OPERATOR.json to the current process environment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.ppe_operator_config import (
    active_operator_profile,
    apply_operator_env,
    continuous_max,
    operator_config_path,
    operator_env_cmd_lines,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Apply PPE_AUTO_OPERATOR.json to os.environ")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--print-continuous-max", action="store_true")
    ap.add_argument(
        "--emit-cmd",
        action="store_true",
        help="Print SET lines for parent cmd.exe (for /f %%a in (`... --emit-cmd`))",
    )
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.print_continuous_max:
        print(continuous_max(repo))
        return 0

    if args.emit_cmd:
        for line in operator_env_cmd_lines(repo):
            print(line)
        return 0

    out = apply_operator_env(repo)
    if out.get("applied"):
        try:
            rel = operator_config_path(repo).relative_to(repo)
        except ValueError:
            rel = operator_config_path(repo)
        print(f"ppe_operator_env: profile={active_operator_profile(repo)} ({rel})")
    else:
        print("ppe_operator_env: no config or disabled (set env manually if needed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
