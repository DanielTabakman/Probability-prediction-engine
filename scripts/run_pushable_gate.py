"""Tiered pushable gate for PPE commits.

Canonical local gate runner (see docs/SOP/COMMIT_POLICY_V1.md). Classifies the
diff vs a base ref (default: origin/main) and runs:

- **Tier 0** — docs-only under ``docs/``: no ruff/pytest (exit 0).
- **Tier 1** — control plane (``scripts/``, ``tests/``, config, ``.cursor/``; no ``src/``):
  ``ruff check scripts tests`` + full ``pytest -q``.
- **Tier 2** — product (any ``src/`` touch): ``ruff check src tests scripts`` + full ``pytest -q``.

Use ``--tier N`` to force a tier for local debugging.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GatePlan:
    tier: int
    reason: str
    commands: list[list[str]]


def _run(cmd: list[str], *, cwd: Path) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def _changed_files(repo: Path, base_ref: str) -> list[str]:
    # Use ... to compare against merge base (branch-friendly).
    out = subprocess.run(
        ["git", "diff", "--name-only", f"{base_ref}...HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _classify(files: list[str]) -> GatePlan:
    if not files:
        return GatePlan(tier=0, reason="no changes", commands=[])

    def under(prefix: str) -> bool:
        return any(f.replace("\\", "/").startswith(prefix) for f in files)

    def all_under(prefix: str) -> bool:
        return all(f.replace("\\", "/").startswith(prefix) for f in files)

    # Tier 0 — docs only
    if all_under("docs/"):
        return GatePlan(tier=0, reason="docs-only changes", commands=[])

    # Tier 2 — product (any src/)
    if under("src/"):
        return GatePlan(
            tier=2,
            reason="src/ touched (product tier)",
            commands=[
                ["python", "-m", "ruff", "check", "src", "tests", "scripts"],
                ["python", "-m", "pytest", "-q"],
            ],
        )

    # Tier 1 — control plane (scripts/, tests/, config, .cursor, etc.)
    # Conservative default: run full pytest to avoid missing coverage.
    return GatePlan(
        tier=1,
        reason="no src/ touched (control-plane tier)",
        commands=[
            ["python", "-m", "ruff", "check", "scripts", "tests"],
            ["python", "-m", "pytest", "-q"],
        ],
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run PPE pushable gate (tiered).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--base-ref", default="origin/main", help="Base ref to diff against")
    ap.add_argument(
        "--tier",
        type=int,
        choices=(0, 1, 2),
        default=None,
        help="Force tier (0 docs-only, 1 control-plane, 2 product)",
    )
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    try:
        files = _changed_files(repo, args.base_ref)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: failed to compute changed files vs {args.base_ref}: {e}", file=sys.stderr)
        return 2

    plan = _classify(files)
    if args.tier is not None:
        forced = args.tier
        if forced == 0:
            plan = GatePlan(tier=0, reason="forced tier 0", commands=[])
        elif forced == 1:
            plan = GatePlan(
                tier=1,
                reason="forced tier 1",
                commands=[
                    ["python", "-m", "ruff", "check", "scripts", "tests"],
                    ["python", "-m", "pytest", "-q"],
                ],
            )
        else:
            plan = GatePlan(
                tier=2,
                reason="forced tier 2",
                commands=[
                    ["python", "-m", "ruff", "check", "src", "tests", "scripts"],
                    ["python", "-m", "pytest", "-q"],
                ],
            )

    print(f"pushable gate: tier={plan.tier} ({plan.reason})")
    if files:
        print(f"changed_files={len(files)}")

    for cmd in plan.commands:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

