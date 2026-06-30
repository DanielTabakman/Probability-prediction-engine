"""Tiered pushable gate for PPE commits.

Canonical local gate runner (see docs/SOP/COMMIT_POLICY.md, docs/SOP/TESTING_TIERS_V1.md).
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

PytestProfile = str  # "fast" | "full" | "scoped"

FAST_PYTEST_MARKER = "not witness and not slow"


@dataclass(frozen=True)
class GatePlan:
    tier: int
    reason: str
    commands: list[list[str]]


def _parallel_enabled() -> bool:
    return os.environ.get("PPE_PYTEST_PARALLEL", "1").strip().lower() not in ("0", "false", "no")


def _parallel_args() -> list[str]:
    return ["-n", "auto"] if _parallel_enabled() else []


def pytest_commands(
    profile: PytestProfile,
    *,
    scoped_tests: list[str] | None = None,
) -> list[list[str]]:
    """Return one or more pytest command lines for the given profile."""
    if profile == "full":
        parallel = _parallel_args()
        return [
            ["python", "-m", "pytest", "-q", *parallel, "-m", "not slow"],
            ["python", "-m", "pytest", "-q", "-m", "slow"],
        ]

    cmd = ["python", "-m", "pytest", "-q", *_parallel_args(), "-m", FAST_PYTEST_MARKER]
    if profile == "scoped" and scoped_tests:
        cmd.extend(scoped_tests)
    return [cmd]


def pytest_cmd(profile: PytestProfile, *, scoped_tests: list[str] | None = None) -> list[str]:
    """First pytest command (backward compat for unit tests)."""
    return pytest_commands(profile, scoped_tests=scoped_tests)[0]


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


def _ruff_for_tier(tier: int) -> list[str]:
    if tier == 1:
        return [["python", "-m", "ruff", "check", "scripts", "tests"]]
    return [["python", "-m", "ruff", "check", "src", "tests", "scripts"]]


def _resolve_pytest_profile(
    *,
    pytest_profile: PytestProfile,
    files: list[str],
    repo: Path,
    force_scoped: bool,
) -> tuple[PytestProfile, list[str] | None, str]:
    if pytest_profile == "full":
        return "full", None, "full"

    from scripts.gate_pytest_scope import resolve_scoped_tests

    scoped = resolve_scoped_tests(files, repo)
    if scoped and (force_scoped or pytest_profile == "fast"):
        return "scoped", scoped, f"scoped ({len(scoped)} files)"

    return "fast", None, "fast (markers)"


def _touches_msos_web(files: list[str]) -> bool:
    return any(f.replace("\\", "/").startswith("apps/msos-web/") for f in files)


def _msos_web_gate_commands(files: list[str], *, pre_push: bool) -> list[list[str]]:
    if not _touches_msos_web(files):
        return []
    if pre_push:
        return [["python", "scripts/verify_msos_web_build.py"]]
    return [["python", "scripts/verify_msos_web_build.py", "--witness-only"]]


_SOP_DISCOVERY_PATHS = frozenset(
    {
        "scripts/sop_discovery_core.py",
        "scripts/resolve_sop.py",
        "scripts/generate_chapter_doc_index.py",
        "scripts/validate_sop_links.py",
        "docs/SOP/CHAPTER_DOC_INDEX.json",
    }
)


def _touches_sop_discovery(files: list[str]) -> bool:
    norms = {f.replace("\\", "/") for f in files}
    if norms & _SOP_DISCOVERY_PATHS:
        return True
    return any(
        n.startswith("docs/SOP/") and n.endswith("_PROGRAM_V1.md") for n in norms
    )


def _sop_discovery_gate_commands(files: list[str]) -> list[list[str]]:
    if not _touches_sop_discovery(files):
        return []
    return [
        ["python", "scripts/generate_chapter_doc_index.py", "--write"],
        ["python", "scripts/validate_sop_links.py"],
    ]


def _classify(
    files: list[str],
    *,
    repo: Path,
    pytest_profile: PytestProfile = "fast",
    force_scoped: bool = False,
) -> GatePlan:
    if not files:
        return GatePlan(tier=0, reason="no changes", commands=[])

    def under(prefix: str) -> bool:
        return any(f.replace("\\", "/").startswith(prefix) for f in files)

    def all_under(prefix: str) -> bool:
        return all(f.replace("\\", "/").startswith(prefix) for f in files)

    if all_under("docs/"):
        return GatePlan(tier=0, reason="docs-only changes", commands=[])

    tier = 2 if under("src/") else 1
    reason = "src/ touched (product tier)" if tier == 2 else "no src/ touched (control-plane tier)"

    profile, scoped_tests, profile_label = _resolve_pytest_profile(
        pytest_profile=pytest_profile,
        files=files,
        repo=repo,
        force_scoped=force_scoped,
    )
    commands = _ruff_for_tier(tier) + pytest_commands(profile, scoped_tests=scoped_tests)
    return GatePlan(tier=tier, reason=f"{reason}; pytest={profile_label}", commands=commands)


def _tier_commands(
    tier: int,
    *,
    repo: Path,
    pytest_profile: PytestProfile,
    files: list[str],
    force_scoped: bool,
) -> list[list[str]]:
    if tier == 0:
        return []
    profile, scoped_tests, _ = _resolve_pytest_profile(
        pytest_profile=pytest_profile,
        files=files,
        repo=repo,
        force_scoped=force_scoped,
    )
    return _ruff_for_tier(tier) + pytest_commands(profile, scoped_tests=scoped_tests)


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
        "--scoped",
        action="store_true",
        help="Force path-scoped pytest when mapping exists (default auto on fast WIP)",
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

    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    pytest_profile: PytestProfile = "full" if args.pre_push or args.full else "fast"

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

    plan = _classify(
        files,
        repo=repo,
        pytest_profile=pytest_profile,
        force_scoped=args.scoped,
    )
    if args.tier is not None:
        plan = GatePlan(
            tier=args.tier,
            reason=f"forced tier {args.tier}",
            commands=_tier_commands(
                args.tier,
                repo=repo,
                pytest_profile=pytest_profile,
                files=files,
                force_scoped=args.scoped,
            ),
        )

    print(f"pushable gate: tier={plan.tier} ({plan.reason})")
    print(f"pytest profile: {pytest_profile}")
    print(f"sources: {source}")
    if files:
        print(f"changed_files={len(files)}")

    if files and plan.tier >= 1 and os.environ.get("PPE_LAYER_AUDIT", "1") != "0":
        try:
            from scripts.repo_layer_paths import audit_paths, load_presets, scope_from_preset

            presets = load_presets(repo)
            violations: list[str] = []

            def _preset_for_path(path: str) -> str:
                if (
                    path in ("docker-compose.yml", "Caddyfile", "Caddyfile.tls")
                    or path.startswith("caddy/")
                ):
                    return "PLATFORM"
                if path.startswith(".github/") or path.startswith("docs/DEPLOY/"):
                    return "PLATFORM"
                if path.startswith("config/"):
                    return "PPE_CORE"
                if path.startswith("src/"):
                    return "PPE_UI" if path.startswith("src/viz/") else "PPE_CORE"
                if path.startswith("tests/test_implied_lab_"):
                    return "PPE_UI"
                if path.startswith("tests/test_caddy"):
                    return "PLATFORM"
                if path.startswith("tests/test_fetch_") or path.startswith("tests/test_assets_registry"):
                    return "PPE_CORE"
                if path.startswith("tests/test_equity_distribution"):
                    return "PPE_CORE"
                if path.startswith("tests/test_horizon_"):
                    return "PPE_CORE"
                if path.startswith("tests/test_implied_distribution"):
                    return "PPE_CORE"
                if path.startswith("tests/test_bl_density"):
                    return "PPE_CORE"
                if path.startswith("apps/") or path.startswith("tests/test_msos_web"):
                    return "MSOS_UI"
                if path.startswith("docs/"):
                    return "DOCS_ONLY" if path.startswith("docs/SOP/") else "DOCS_CANON"
                return "CONTROL"

            for path in files:
                scope = scope_from_preset(presets, _preset_for_path(path))
                violations.extend(audit_paths([path], scope))
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

    if files and os.environ.get("PPE_DELEGATION_AUDIT", "1") != "0":
        try:
            from scripts.ppe_delegation_envelope import gate_check

            pass_type = os.environ.get("PPE_PASS_TYPE", "")
            rc = gate_check(repo, files, pass_type=pass_type)
            if rc != 0:
                return rc
        except ImportError:
            pass

    for cmd in plan.commands:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    for cmd in _sop_discovery_gate_commands(files):
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    msos_cmds = _msos_web_gate_commands(files, pre_push=args.pre_push)
    for cmd in msos_cmds:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    if plan.tier >= 1 or msos_cmds:
        print("\033[1;32mAll checks passed!\033[0m")
    return 0


def run_gate_for_paths(
    repo: Path,
    files: list[str],
    *,
    pre_push: bool = False,
    pytest_profile: PytestProfile | None = None,
    force_scoped: bool = False,
) -> int:
    """Run tiered gate for an explicit path list (e.g. unstaged closeout ship)."""
    repo = repo.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))

    profile: PytestProfile = pytest_profile or ("full" if pre_push else "fast")
    plan = _classify(
        files,
        repo=repo,
        pytest_profile=profile,
        force_scoped=force_scoped,
    )
    if pre_push and plan.tier >= 1:
        plan = GatePlan(
            tier=plan.tier,
            reason=f"{plan.reason}; pre-push",
            commands=_tier_commands(
                plan.tier,
                repo=repo,
                pytest_profile="full",
                files=files,
                force_scoped=force_scoped,
            ),
        )

    print(f"pushable gate: tier={plan.tier} ({plan.reason})")
    print(f"pytest profile: {profile}")
    if files:
        print(f"changed_files={len(files)}")

    if files and plan.tier >= 1 and os.environ.get("PPE_LAYER_AUDIT", "1") != "0":
        try:
            from scripts.repo_layer_paths import audit_paths, load_presets, scope_from_preset

            presets = load_presets(repo)
            violations: list[str] = []

            def _preset_for_path(path: str) -> str:
                if (
                    path in ("docker-compose.yml", "Caddyfile", "Caddyfile.tls")
                    or path.startswith("caddy/")
                ):
                    return "PLATFORM"
                if path.startswith(".github/") or path.startswith("docs/DEPLOY/"):
                    return "PLATFORM"
                if path.startswith("config/"):
                    return "PPE_CORE"
                if path.startswith("src/"):
                    return "PPE_UI" if path.startswith("src/viz/") else "PPE_CORE"
                if path.startswith("tests/test_implied_lab_"):
                    return "PPE_UI"
                if path.startswith("tests/test_caddy"):
                    return "PLATFORM"
                if path.startswith("tests/test_fetch_") or path.startswith("tests/test_assets_registry"):
                    return "PPE_CORE"
                if path.startswith("tests/test_equity_distribution"):
                    return "PPE_CORE"
                if path.startswith("tests/test_horizon_"):
                    return "PPE_CORE"
                if path.startswith("tests/test_implied_distribution"):
                    return "PPE_CORE"
                if path.startswith("tests/test_bl_density"):
                    return "PPE_CORE"
                if path.startswith("apps/") or path.startswith("tests/test_msos_web"):
                    return "MSOS_UI"
                if path.startswith("docs/"):
                    return "DOCS_ONLY" if path.startswith("docs/SOP/") else "DOCS_CANON"
                return "CONTROL"

            for path in files:
                scope = scope_from_preset(presets, _preset_for_path(path))
                violations.extend(audit_paths([path], scope))
            if violations:
                print("ERROR: repo layer audit failed for changed files:", file=sys.stderr)
                for v in violations[:10]:
                    print(f"  {v}", file=sys.stderr)
                return 1
        except FileNotFoundError:
            pass

    for cmd in plan.commands:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    for cmd in _sop_discovery_gate_commands(files):
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    msos_cmds = _msos_web_gate_commands(files, pre_push=pre_push)
    for cmd in msos_cmds:
        rc = _run(cmd, cwd=repo)
        if rc != 0:
            return rc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
