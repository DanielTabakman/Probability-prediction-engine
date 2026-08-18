"""Reject unrelated product hosting inside the PPE/MSOS web application."""

from __future__ import annotations

import argparse
from pathlib import Path


ALLOWED_TOP_LEVEL_ROUTES = frozenset(
    {
        "api",
        "command-center",
        "daniel",
        "exposure",
        "feedback",
        "forward-consistency",
        "history",
        "learn",
        "monitor",
        "operator",
        "options-horizon",
        "strategy-lab",
    }
)

ALLOWED_DANIEL_FILES = frozenset(
    {
        "apps/msos-web/src/app/daniel/daniel.module.css",
        "apps/msos-web/src/app/daniel/page.tsx",
    }
)

RUNTIME_TEXT_SUFFIXES = frozenset({".html", ".js", ".jsx", ".mjs", ".ts", ".tsx"})
FORBIDDEN_REMOTE_RUNTIME_MARKERS = (
    "raw.githubusercontent.com/",
    "github.io/",
)


def _relative(repo: Path, path: Path) -> str:
    return path.relative_to(repo).as_posix()


def find_violations(repo: Path) -> list[str]:
    """Return stable, human-readable repository boundary violations."""
    repo = repo.resolve()
    app_root = repo / "apps/msos-web/src/app"
    public_daniel = repo / "apps/msos-web/public/daniel"
    violations: list[str] = []

    if not app_root.is_dir():
        return ["missing MSOS app root: apps/msos-web/src/app"]

    for child in sorted(app_root.iterdir()):
        if child.is_dir() and child.name not in ALLOWED_TOP_LEVEL_ROUTES:
            violations.append(
                f"unowned top-level MSOS route: {_relative(repo, child)}"
            )

    daniel_root = app_root / "daniel"
    if daniel_root.is_dir():
        for path in sorted(p for p in daniel_root.rglob("*") if p.is_file()):
            relative = _relative(repo, path)
            if relative not in ALLOWED_DANIEL_FILES:
                violations.append(f"nested product code under /daniel: {relative}")

    if public_daniel.is_dir():
        for path in sorted(p for p in public_daniel.rglob("*") if p.is_file()):
            violations.append(
                f"product asset stored under public/daniel: {_relative(repo, path)}"
            )

    for path in sorted(p for p in app_root.rglob("*") if p.is_file()):
        if path.suffix.lower() not in RUNTIME_TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        relative = _relative(repo, path)
        if "<iframe" in text:
            violations.append(f"runtime iframe requires a repository-boundary decision: {relative}")
        for marker in FORBIDDEN_REMOTE_RUNTIME_MARKERS:
            if marker in text:
                violations.append(
                    f"remote application content is proxied at runtime ({marker}): {relative}"
                )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)

    violations = find_violations(args.repo_root)
    if violations:
        print("Repository boundary check failed:")
        for violation in violations:
            print(f"- {violation}")
        print("Move unrelated product code to its own repository.")
        return 1

    print("Repository boundary check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
