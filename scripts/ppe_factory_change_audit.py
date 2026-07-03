"""FC-2: warn when factory SSOT files change without companion docs/tests.

Canon: docs/SOP/FACTORY_CHANGE_COORDINATION_V1.md
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any

# trigger path -> required companion paths (any one match in diff suffices per group)
FACTORY_SSOT_COMPANIONS: dict[str, tuple[str, ...]] = {
    "scripts/ppe_operator_status.py": (
        "tests/test_ppe_operator_status",
        "tests/test_ppe_operator_monitor_enrich",
        "tests/test_ppe_operator_status_chapter_mode",
        "docs/SOP/OPERATOR_BUTTON_MAP.md",
        "docs/SOP/PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md",
    ),
    "scripts/ppe_burst_plan.py": (
        "tests/test_ppe_burst_plan.py",
        "docs/SOP/OPERATOR_BUTTON_MAP.md",
    ),
    "scripts/ppe_coordination_check.py": (
        "tests/test_ppe_coordination",
        "docs/SOP/CHAPTER_COORDINATION_V1.md",
    ),
    "scripts/ppe_operator_dispatch.py": (
        "tests/test_ppe_operator_dispatch.py",
        "docs/SOP/OPERATOR_BUTTON_MAP.md",
        "docs/SOP/DESKTOP_OPERATOR_AUTOMATION_PLAN_V1.md",
    ),
    "scripts/ppe_in_flight_monitor.py": (
        "tests/test_ppe_in_flight_monitor.py",
        "docs/SOP/OPERATOR_BUTTON_MAP.md",
    ),
}


def _norm(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _changed_in_diff(repo: Path, rel: str) -> bool:
    rel = _norm(rel)
    for ref in ("origin/main...HEAD", "HEAD"):
        try:
            proc = subprocess.run(
                ["git", "diff", "--name-only", ref],
                cwd=repo,
                capture_output=True,
                text=True,
                check=False,
            )
            if proc.returncode != 0:
                continue
            for line in (proc.stdout or "").splitlines():
                if _norm(line) == rel:
                    return True
        except OSError:
            continue
    return False


def _companion_touched(changed_paths: set[str], companions: tuple[str, ...]) -> bool:
    for path in changed_paths:
        norm = _norm(path)
        for companion in companions:
            c = _norm(companion)
            if norm == c or norm.startswith(c) or c in norm:
                return True
    return False


def audit_factory_ssot(repo: Path, changed_paths: list[str] | None = None) -> list[dict[str, Any]]:
    repo = repo.resolve()
    if changed_paths is None:
        proc = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        changed_paths = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
    changed_set = {_norm(p) for p in changed_paths}
    issues: list[dict[str, Any]] = []
    for trigger, companions in FACTORY_SSOT_COMPANIONS.items():
        trigger_n = _norm(trigger)
        if trigger_n not in changed_set:
            continue
        if _companion_touched(changed_set, companions):
            continue
        issues.append(
            {
                "code": "FACTORY_SSOT_INCOMPLETE",
                "trigger": trigger_n,
                "missing_companions": list(companions),
            }
        )
    return issues


def warn_if_factory_ssot_incomplete(
    repo: Path,
    changed_paths: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Print FC-2 warnings; non-blocking."""
    issues = audit_factory_ssot(repo, changed_paths)
    if not issues:
        return []
    print(
        "WARN: factory SSOT touch-surface incomplete (see docs/SOP/FACTORY_CHANGE_COORDINATION_V1.md):",
        file=sys.stderr,
    )
    for row in issues:
        companions = ", ".join(row.get("missing_companions") or [])
        print(f"  - {row.get('trigger')}: update one of [{companions}]", file=sys.stderr)
    return issues
