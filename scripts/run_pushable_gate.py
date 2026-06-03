"""Tiered pushable gate for PPE commits.

Canonical local gate runner (see docs/SOP/COMMIT_POLICY_V1.md, docs/SOP/TESTING_TIERS_V1.md).
Classifies changed paths and runs:

- **Tier 0** — docs-only under ``docs/``: no ruff/pytest (exit 0).
- **Tier 1** — control plane (``scripts/``, ``tests/``, config, ``.cursor/``; no ``src/``):
  ``ruff check scripts tests`` + pytest (fast or full profile).
- **Tier 2** — product (any ``src/`` touch): ``ruff check src tests scripts`` + pytest.

**Pytest profiles** (see TESTING_TIERS_V1.md):

- **fast** (default) — ``pytest -m "not witness and not slow"`` for WIP commits.
- **full** — ``pytest -q`` entire suite; use ``--pre-push`` or ``--full`` before push.

By default, changed files are the union of ``{base_ref}...HEAD`` (branch vs main) and
``{upstream}..HEAD`` when the branch is ahead of its upstream.

Use ``--pre-push`` to classify only ``upstream..HEAD`` and run **full** pytest.
Use ``--tier N`` to force a tier for local debugging.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PytestProfile = str  # "fast" | "full"

FAST_PYTEST_MARKER = "not witness and not slow"


@dataclass(frozen=True)
class GatePlan:
    tier: int
    reason: str
    commands: list[list[str]]


def pytest_cmd(profile: PytestProfile) -> list[str]:
    if profile == "full":
        return ["python", "-m", "pytest", "-q"]
    return ["python", "-m", "pytest", "-q", "-m", FAST_PYTEST_MARKER]


def _run(cmd: list[str], *, cwd: Path) -> int:
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd).returncode


def _git_lines(repo: Path, *args: str) -> list[str]:
    out = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def _changed_files_three_dot(repo: Path, base_ref: str) -> list[str]:
    return _git_lines(repo, "diff", "--name-only", f"{base_ref}...HEAD")


def _changed_files_two_dot(repo: Path, base_ref: str, head: str = "HEAD") -> list[str]:
    return _git_lines(repo, "diff", "--name-only", f"{base_ref}..{head}")


def _union_paths(*groups: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for group in groups:
        for path in group:
            norm = path.replace("\\", "/")
            if norm not in seen:
                seen.add(norm)
                out.append(norm)
    return out


def _upstream_ref(repo: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    ref = proc.stdout.strip()
    return ref or None


def _commits_ahead(repo: Path, ref: str) -> int:
    proc = subprocess.run(
        ["git", "rev-list", "--count", f"{ref}..HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    return int(proc.stdout.strip() or "0")


def resolve_changed_files(
    repo: Path,
    *,
    base_ref: str = "origin/main",
    pre_push: bool = False,
    auto_upstream: bool = True,
) -> tuple[list[str], str]:
    """Return (paths, human-readable source label) for tier classification."""
    upstream = _upstream_ref(repo)

    if pre_push:
        if not upstream:
            raise ValueError("no upstream configured; set upstream with git push -u")
        ahead = _commits_ahead(repo, upstream)
        if ahead == 0:
            return [], f"pre-push ({upstream}: nothing ahead)"
        files = _changed_files_two_dot(repo, upstream, "HEAD")
        return files, f"pre-push ({upstream}..HEAD, {ahead} commit(s))"

    groups: list[list[str]] = []
    labels: list[str] = []

    main_files = _changed_files_three_dot(repo, base_ref)
    groups.append(main_files)
    labels.append(f"{base_ref}...HEAD")

    if auto_upstream and upstream:
        ahead = _commits_ahead(repo, upstream)
        if ahead > 0:
            groups.append(_changed_files_two_dot(repo, upstream, "HEAD"))
            labels.append(f"{upstream}..HEAD ({ahead} ahead)")

    return _union_paths(*groups), " + ".join(labels)


def _classify(files: list[str], *, pytest_profile: PytestProfile = "fast") -> GatePlan:
    if not files:
        return GatePlan(tier=0, reason="no changes", commands=[])

    def under(prefix: str) -> bool:
        return any(f.replace("\\", "/").startswith(prefix) for f in files)

    def all_under(prefix: str) -> bool:
        return all(f.replace("\\", "/").startswith(prefix) for f in files)

    ptest = pytest_cmd(pytest_profile)

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
                ptest,
            ],
        )

    # Tier 1 — control plane (scripts/, tests/, config, .cursor, etc.)
    return GatePlan(
        tier=1,
        reason="no src/ touched (control-plane tier)",
        commands=[
            ["python", "-m", "ruff", "check", "scripts", "tests"],
            ptest,
        ],
    )


def _tier_commands(tier: int, *, pytest_profile: PytestProfile) -> list[list[str]]:
    ptest = pytest_cmd(pytest_profile)
    if tier == 0:
        return []
    if tier == 1:
        return [
            ["python", "-m", "ruff", "check", "scripts", "tests"],
            ptest,
        ]
    return [
        ["python", "-m", "ruff", "check", "src", "tests", "scripts"],
        ptest,
    ]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run PPE pushable gate (tiered).")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--base-ref", default="origin/main", help="Base ref for branch vs main (three-dot)")
    ap.add_argument(
        "--pre-push",
        action="store_true",
        help="Classify upstream..HEAD only and run full pytest (required before git push)",
    )
    ap.add_argument(
        "--full",
        action="store_true",
        help="Run full pytest suite (same as CI pytest job)",
    )
    ap.add_argument(
        "--no-auto-upstream",
        action="store_true",
        help="Do not union upstream..HEAD with base-ref...HEAD (default unions when ahead)",
    )
    ap.add_argument(
        "--tier",
        type=int,
        choices=(0, 1, 2),
        default=None,
        help="Force tier (0 docs-only, 1 control-plane, 2 product)",
    )
    args = ap.parse_args(argv)

    pytest_profile: PytestProfile = "full" if args.pre_push or args.full else "fast"

    repo = args.repo_root.resolve()
    try:
        files, source = resolve_changed_files(
            repo,
            base_ref=args.base_ref,
            pre_push=args.pre_push,
            auto_upstream=not args.no_auto_upstream,
        )
    except subprocess.CalledProcessError as e:
        print(f"ERROR: failed to compute changed files: {e}", file=sys.stderr)
        return 2
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    plan = _classify(files, pytest_profile=pytest_profile)
    if args.tier is not None:
        plan = GatePlan(
            tier=args.tier,
            reason=f"forced tier {args.tier}",
            commands=_tier_commands(args.tier, pytest_profile=pytest_profile),
        )

    print(f"pushable gate: tier={plan.tier} ({plan.reason})")
    print(f"pytest profile: {pytest_profile}")
    print(f"sources: {source}")
    if files:
        print(f"changed_files={len(files)}")

    if files and plan.tier >= 1 and os.environ.get("PPE_LAYER_AUDIT", "1") != "0":
        try:
            from scripts.repo_layer_paths import audit_paths, load_presets, scope_from_preset

            # Best-effort: infer preset from diff shape when no manifest scope.
            if any(f.startswith("src/") for f in files):
                preset_name = "PPE_UI" if any(f.startswith("src/viz/") for f in files) else "PPE_CORE"
            elif any(f.startswith("apps/") for f in files):
                preset_name = "MSOS_UI"
            elif all(f.startswith("docs/") for f in files):
                preset_name = "DOCS_ONLY" if all(f.startswith("docs/SOP/") for f in files) else "DOCS_CANON"
            else:
                preset_name = "CONTROL"
            scope = scope_from_preset(load_presets(repo), preset_name)
            violations = audit_paths(files, scope)
            if violations:
                print("ERROR: repo layer audit failed for changed files:", file=sys.stderr)
                for v in violations[:10]:
                    print(f"  {v}", file=sys.stderr)
                if len(violations) > 10:
                    print(f"  ... {len(violations) - 10} more", file=sys.stderr)
                print(
                    "Set PPE_LAYER_AUDIT=0 to skip (not recommended). "
                    "Use one LAYER_PRESET per commit — see docs/SOP/PARALLEL_AGENT_CHECKLIST_V1.md",
                    file=sys.stderr,
                )
                return 1
        except FileNotFoundError:
            pass

    for cmd in plan.commands:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
