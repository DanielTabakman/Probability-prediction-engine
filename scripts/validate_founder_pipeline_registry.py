"""Validate the founder portfolio pipeline registry."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.founder_portfolio_registry import validate_registry  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate config/founder_pipeline_registry.json")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    args = ap.parse_args(argv)

    errors = validate_registry(args.repo_root.resolve())
    if errors:
        for err in errors:
            print(f"validate_founder_pipeline_registry: {err}", file=sys.stderr)
        return 1
    print("validate_founder_pipeline_registry: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
