"""Operator branch/tree preflight — blocking relay when desktop checkout is wrong."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

RELAY_VERDICTS = frozenset({"RUN_LOCAL", "IDE_BUILD", "RUN_AUTO"})
ALLOWED_DESKTOP_PREFIXES = ("control-plane/", "ops/", "docs/", "chore/")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip()


def _dirty_paths(repo: Path) -> list[str]:
    proc = _git(repo, "status", "--porcelain")
    if proc.returncode != 0:
        return []
    paths: list[str] = []
    for line in (proc.stdout or "").splitlines():
        if len(line) < 4 or line.startswith("##"):
            continue
        paths.append(line[3:].strip().split(" -> ")[-1])
    return paths


def _is_loop_host() -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return False


def assess_operator_branch_preflight(
    repo: Path,
    *,
    verdict: str,
    loop_host_allowed: bool | None = None,
) -> dict[str, Any]:
    """Return branch preflight assessment for operator status."""
    repo = repo.resolve()
    if loop_host_allowed is None:
        loop_host_allowed = _is_loop_host()
    branch = _current_branch(repo)
    dirty = _dirty_paths(repo)
    on_main = branch == "main"
    blocks_relay = False
    reasons: list[str] = []
    commands: list[str] = []

    if loop_host_allowed:
        return {
            "branch": branch,
            "on_main": on_main,
            "dirty_count": len(dirty),
            "blocks_relay": False,
            "reasons": [],
            "commands": [],
        }

    if verdict not in RELAY_VERDICTS:
        return {
            "branch": branch,
            "on_main": on_main,
            "dirty_count": len(dirty),
            "blocks_relay": False,
            "reasons": [],
            "commands": [],
        }

    if not on_main:
        if branch.startswith(("product/", "build/")) and verdict in ("RUN_LOCAL", "IDE_BUILD"):
            blocks_relay = True
            reasons.append(
                f"checkout is {branch!r} — product/build branch blocks relay handoff; use main after merge"
            )
            commands.extend(["git checkout main && git pull origin main"])
        elif not any(branch.startswith(p) for p in ALLOWED_DESKTOP_PREFIXES):
            blocks_relay = True
            reasons.append(
                f"checkout is {branch!r}, not main — unexpected branch for operator relay"
            )
            commands.extend(["git checkout main && git pull origin main"])

    product_dirty = [p for p in dirty if p.replace("\\", "/").startswith("src/")]
    if product_dirty and verdict in ("RUN_LOCAL", "IDE_BUILD"):
        blocks_relay = True
        reasons.append(
            f"dirty product tree ({len(product_dirty)} path(s) under src/) — commit/stash before relay"
        )
        if not commands:
            commands.append("git stash push -u -m 'operator-park' OR commit product WIP on feature branch")

    return {
        "branch": branch,
        "on_main": on_main,
        "dirty_count": len(dirty),
        "blocks_relay": blocks_relay,
        "reasons": reasons,
        "commands": commands,
    }
