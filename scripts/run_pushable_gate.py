"""Tiered local gate before pushable commits (see docs/SOP/COMMIT_POLICY_V1.md)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[1]

# Non-obvious script → extra test files (unioned with tests/test_<stem>.py when present).
SCRIPT_EXTRA_TESTS: dict[str, tuple[str, ...]] = {
    "scripts/msos/build_snapshot.py": (
        "tests/test_msos_snapshot.py",
        "tests/test_sync_msos_repo_truth.py",
    ),
}

RUFF_CMD = [sys.executable, "-m", "ruff", "check", "src", "tests", "scripts"]


class GateTier(IntEnum):
    DOCS_ONLY = 0
    CONTROL_PLANE = 1
    PRODUCT = 2


@dataclass(frozen=True)
class GatePlan:
    tier: GateTier
    changed_paths: tuple[str, ...]
    pytest_paths: tuple[str, ...]  # empty for tier 0; full suite uses ("tests",) sentinel
    escalate_reason: str | None = None

    @property
    def uses_full_pytest(self) -> bool:
        return self.tier == GateTier.PRODUCT or (
            self.tier == GateTier.CONTROL_PLANE and self.escalate_reason is not None
        )


def _normalize_path(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).as_posix()


def _test_for_script(script_path: str) -> str | None:
    stem = PurePosixPath(script_path).stem
    candidate = REPO_ROOT / "tests" / f"test_{stem}.py"
    if candidate.is_file():
        return f"tests/test_{stem}.py"
    return None


def _resolve_pytest_paths(changed: tuple[str, ...]) -> tuple[list[str], str | None]:
    """Return sorted unique pytest paths; escalate_reason set when tier-1 must use full suite."""
    paths: set[str] = set()
    unmapped_scripts: list[str] = []

    for raw in changed:
        p = _normalize_path(raw)
        if p.startswith("tests/") and p.endswith(".py"):
            paths.add(p)
            continue
        if not p.startswith("scripts/") or not p.endswith(".py"):
            continue
        contributed = False
        mapped = _test_for_script(p)
        if mapped:
            paths.add(mapped)
            contributed = True
        for extra in SCRIPT_EXTRA_TESTS.get(p, ()):
            if (REPO_ROOT / extra).is_file():
                paths.add(extra)
                contributed = True
        if not contributed:
            unmapped_scripts.append(p)

    if unmapped_scripts:
        return [], f"no test file for script(s): {', '.join(unmapped_scripts)}"

    if not paths:
        return [], "no pytest targets resolved for control-plane diff"

    return sorted(paths), None


def classify_paths(changed: tuple[str, ...]) -> GatePlan:
    if not changed:
        return GatePlan(
            tier=GateTier.DOCS_ONLY,
            changed_paths=changed,
            pytest_paths=(),
            escalate_reason="no changed paths (nothing to gate)",
        )

    normalized = tuple(_normalize_path(p) for p in changed)

    if all(p.startswith("docs/") for p in normalized):
        return GatePlan(tier=GateTier.DOCS_ONLY, changed_paths=normalized, pytest_paths=())

    if any(p.startswith("src/") for p in normalized):
        return GatePlan(
            tier=GateTier.PRODUCT,
            changed_paths=normalized,
            pytest_paths=("tests",),
        )

    pytest_list, escalate = _resolve_pytest_paths(normalized)
    if escalate:
        return GatePlan(
            tier=GateTier.PRODUCT,
            changed_paths=normalized,
            pytest_paths=("tests",),
            escalate_reason=escalate,
        )

    return GatePlan(
        tier=GateTier.CONTROL_PLANE,
        changed_paths=normalized,
        pytest_paths=tuple(pytest_list),
    )


def git_changed_paths() -> tuple[str, ...]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"git diff failed: {result.stderr.strip() or result.stdout}")
    lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
    return tuple(lines)


def plan_commands(plan: GatePlan) -> list[list[str]]:
    if plan.tier == GateTier.DOCS_ONLY:
        return []
    cmds = [RUFF_CMD]
    if plan.uses_full_pytest:
        cmds.append([sys.executable, "-m", "pytest", "-q"])
    else:
        cmds.append([sys.executable, "-m", "pytest", "-q", *plan.pytest_paths])
    return cmds


def _run_cmd(cmd: list[str]) -> int:
    print("+", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT).returncode


def execute_plan(plan: GatePlan, *, dry_run: bool) -> int:
    tier_name = plan.tier.name.lower()
    print(f"pushable_gate: tier={plan.tier} ({tier_name})", flush=True)
    print(f"pushable_gate: changed={len(plan.changed_paths)} path(s)", flush=True)
    if plan.escalate_reason:
        print(f"pushable_gate: escalate_to_full_pytest={plan.escalate_reason}", flush=True)

    if plan.tier == GateTier.DOCS_ONLY:
        if plan.escalate_reason:
            print(f"pushable_gate: skip ({plan.escalate_reason})", flush=True)
        else:
            print("pushable_gate: skip ruff and pytest (docs-only)", flush=True)
        return 0

    commands = plan_commands(plan)
    if dry_run:
        for cmd in commands:
            print("+", " ".join(cmd), flush=True)
        return 0

    for cmd in commands:
        code = _run_cmd(cmd)
        if code != 0:
            return code
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run tiered pushable commit gate.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print tier and commands without running ruff/pytest.",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Override changed paths (posix); for tests/debugging.",
    )
    args = parser.parse_args(argv)

    changed = tuple(_normalize_path(p) for p in args.paths) if args.paths is not None else git_changed_paths()
    plan = classify_paths(changed)
    return execute_plan(plan, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
