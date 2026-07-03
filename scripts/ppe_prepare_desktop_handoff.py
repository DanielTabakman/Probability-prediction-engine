"""Desktop step 0 before DESKTOP_CONTINUE — coordination repair + verify RUN_LOCAL path."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def prepare_desktop_handoff(repo: Path, *, apply_repair: bool = True) -> dict:
    repo = repo.resolve()
    out: dict = {"fixes": [], "remaining": []}

    try:
        from scripts.ppe_operator_vm_mirror_refresh import sync_desktop_mirror_from_main

        out["mirrorSync"] = sync_desktop_mirror_from_main(repo)
    except Exception as exc:
        out["mirrorSync"] = {"ok": False, "error": str(exc)}

    from scripts.ppe_chapter_coordination import (
        audit_chapter,
        audit_closeout_spine,
        repair_chapter,
        repair_repo_coordination,
    )
    from scripts.ppe_manifest import load_manifest
    from scripts.ppe_operator_status import (
        VERDICT_ERROR,
        VERDICT_FIX_PLAN,
        VERDICT_IDE_BUILD,
        VERDICT_RUN_AUTO,
        VERDICT_RUN_LOCAL,
        VERDICT_STALE_STATE,
        collect_operator_status,
    )

    manifest = load_manifest(repo)
    active_plan = str(manifest.get("phasePlanPath") or "").replace("\\", "/").strip()
    out["activePlanPath"] = active_plan or None

    if apply_repair:
        if active_plan:
            fixes, remaining = repair_chapter(repo, active_plan, apply=True)
            out["fixes"].extend(fixes)
            out["remaining"].extend(remaining)
        repo_fix = repair_repo_coordination(repo, apply=True)
        out["repoRepair"] = repo_fix
        if active_plan:
            out["remaining"] = audit_chapter(repo, active_plan)

    status = collect_operator_status(repo)
    out["verdict"] = status.get("verdict")
    out["exitCode"] = status.get("exit_code")
    out["coordinationOk"] = not audit_chapter(repo, active_plan) if active_plan else True
    out["spine"] = audit_closeout_spine(repo).get("summary")
    blocked = {VERDICT_IDE_BUILD, VERDICT_ERROR, VERDICT_FIX_PLAN, VERDICT_STALE_STATE}
    verdict = str(status.get("verdict") or "")
    out["ready"] = (
        bool(out.get("coordinationOk"))
        and verdict not in blocked
        and verdict in (VERDICT_RUN_LOCAL, VERDICT_RUN_AUTO)
    )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Prepare desktop handoff (coordination repair + verify)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--dry-run", action="store_true", help="Audit only; do not repair")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    result = prepare_desktop_handoff(repo, apply_repair=not args.dry_run)
    if args.json:
        import json

        print(json.dumps(result, indent=2))
    else:
        plan = result.get("activePlanPath") or "(none)"
        print(f"ppe_prepare_desktop_handoff: plan={plan} verdict={result.get('verdict')}")
        if result.get("fixes"):
            print(f"  repairs: {len(result['fixes'])}")
        if result.get("remaining"):
            print(f"  remaining issues: {len(result['remaining'])}")
        spine = result.get("spine") or {}
        print(
            f"  closeout spine: {spine.get('complete', 0)}/{spine.get('registryCount', 0)} complete, "
            f"{spine.get('closeoutPending', 0)} active pending, "
            f"{spine.get('closeoutQueued', 0)} queued, "
            f"{spine.get('markerGap', 0)} marker gaps"
        )
        if result.get("ready"):
            print("  ready for DESKTOP_CONTINUE")
        else:
            print("  NOT ready — fix coordination before DESKTOP_CONTINUE", file=sys.stderr)
    return 0 if result.get("ready") else 2


if __name__ == "__main__":
    raise SystemExit(main())
