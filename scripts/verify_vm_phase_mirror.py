"""Verify VM phase mirror is populated and fresh (desktop or loop host)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_operator_vm_mirror_refresh import (
    assess_mirror_health,
    mirror_is_populated,
    refresh_vm_mirror_from_git,
)
from scripts.ppe_vm_phase_mirror import load_vm_phase_mirror


def verify_vm_phase_mirror(repo: Path, *, refresh: bool = True) -> dict[str, object]:
    repo = repo.resolve()
    refresh_report = refresh_vm_mirror_from_git(repo, force_fetch=refresh) if refresh else {}
    mirror = load_vm_phase_mirror(repo)
    health = assess_mirror_health(mirror, local_verdict="RUN_LOCAL")
    ok = mirror_is_populated(mirror) and not health.get("stale")
    return {
        "ok": ok,
        "mirror": mirror,
        "health": health,
        "refresh": refresh_report or None,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify docs/SOP/VM_OPERATOR_PHASE.json mirror")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-refresh", action="store_true")
    args = ap.parse_args(argv)

    result = verify_vm_phase_mirror(args.repo_root, refresh=not args.no_refresh)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        health = result.get("health") or {}
        mirror = result.get("mirror") or {}
        if result.get("ok"):
            print(
                f"verify_vm_phase_mirror: OK phase={mirror.get('phase')} "
                f"age_s={health.get('age_seconds')}"
            )
        else:
            print(f"verify_vm_phase_mirror: FAIL — {health.get('agent_note')}", file=sys.stderr)
            if mirror:
                print(f"  phase={mirror.get('phase')} as_of={mirror.get('as_of')}", file=sys.stderr)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
