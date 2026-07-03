"""Recover mixed dirty trees onto a clean plane branch and optionally ship.

Canon: docs/SOP/COMMIT_POLICY.md § Gate failed · docs/SOP/REPO_STATE_V1.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

PLANE_GLOBS: dict[str, list[str]] = {
    "control": [
        "scripts/**",
        "docs/SOP/**",
        ".cursor/**",
        "tests/**",
        "AGENTS.md",
    ],
    "product": ["src/**", "apps/**"],
}

PLANE_FORBID: dict[str, list[str]] = {
    "control": ["src/**", "apps/**"],
    "product": ["artifacts/**"],
}

PLANE_BRANCH_PREFIX: dict[str, str] = {
    "control": "control-plane/recovery",
    "product": "product/recovery",
}

RECOVERY_REPORT_REL = "artifacts/control_plane/RECOVERY_REPORT.json"


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M")


def suggest_branch(plane: str, *, suffix: str | None = None) -> str:
    pref = PLANE_BRANCH_PREFIX.get(plane, "control-plane/recovery")
    tail = suffix.strip().replace("/", "-") if suffix else _utc_stamp()
    return f"{pref}-{tail}"


def classify_scoped_paths(
    repo: Path,
    *,
    plane: str,
    path_globs: list[str] | None = None,
) -> tuple[list[str], list[str]]:
    from scripts.ppe_worker_lease import scoped_dirty_paths

    globs = path_globs or PLANE_GLOBS.get(plane, PLANE_GLOBS["control"])
    forbidden = PLANE_FORBID.get(plane, [])
    scoped = scoped_dirty_paths(repo, path_globs=globs, forbidden_globs=forbidden)
    dirty = scoped_dirty_paths(repo, path_globs=["**"], forbidden_globs=[])
    outside = [p for p in dirty if p not in scoped]
    return scoped, outside


def needs_branch_recovery(repo: Path, scoped: list[str] | None = None) -> bool:
    from scripts.ppe_repo_state import assess_repo_state, dirty_paths, is_mixed_plane
    from scripts.ppe_worker_lease import _current_branch, scoped_dirty_paths

    branch = _current_branch(repo)
    paths = scoped or scoped_dirty_paths(repo, path_globs=["**"], forbidden_globs=[]) or dirty_paths(repo)
    if branch in ("main", "master", ""):
        return bool(paths)
    if not paths:
        return False
    if is_mixed_plane(paths):
        return True
    try:
        state = assess_repo_state(repo)
        return bool(state.get("mixed_plane")) or state.get("severity", 0) >= 2
    except Exception:
        pass
    return False


def plan_recovery(repo: Path) -> dict[str, Any]:
    """Classify dirty paths and return ordered recovery steps (no git mutations)."""
    from scripts.ppe_repo_state import (
        assess_repo_state,
        dirty_paths,
        paths_by_plane,
        recovery_commands_for_paths,
    )

    repo = repo.resolve()
    paths = dirty_paths(repo)
    before = assess_repo_state(repo)
    by_plane = paths_by_plane(paths)
    steps: list[dict[str, Any]] = []
    for plane in ("control", "product"):
        scoped, outside = classify_scoped_paths(repo, plane=plane)
        if scoped:
            steps.append(
                {
                    "plane": plane,
                    "paths": scoped,
                    "branch": suggest_branch(plane),
                    "outside_scope": outside[:10],
                }
            )
    return {
        "action": "recovery_plan",
        "ok": True,
        "trigger": "mixed_plane" if before.get("mixed_plane") else "dirty_tree",
        "before": {
            "severity": before.get("severity_label"),
            "mixed_plane": before.get("mixed_plane"),
            "planes_active": before.get("planes_active"),
            "dirty_count": before.get("dirty_count"),
        },
        "paths_by_plane": by_plane,
        "steps": steps,
        "recommended_commands": recovery_commands_for_paths(paths),
    }


def verify_recovery(repo: Path) -> dict[str, Any]:
    """Re-assess repo state after recovery; mixed_plane must be false to pass."""
    from scripts.ppe_repo_state import SEVERITY_STEWARD, assess_repo_state, write_repo_state

    after = assess_repo_state(repo)
    write_repo_state(repo, after)
    ok = not after.get("mixed_plane") and after.get("severity", 99) < SEVERITY_STEWARD
    return {
        "ok": ok,
        "severity": after.get("severity_label"),
        "mixed_plane": after.get("mixed_plane"),
        "dirty_count": after.get("dirty_count"),
        "build_allowed": after.get("build_allowed"),
        "burst_allowed": after.get("burst_allowed"),
        "blocker": None if ok else (after.get("blockers") or ["recovery incomplete"])[0],
    }


def write_recovery_report(repo: Path, report: dict[str, Any]) -> Path:
    out = repo.resolve() / RECOVERY_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out


def recover_all(
    repo: Path,
    *,
    dry_run: bool = False,
    pre_push: bool = False,
    message: str | None = None,
) -> dict[str, Any]:
    """Run plane-pure recovery sequence and verify."""
    repo = repo.resolve()
    plan = plan_recovery(repo)
    report: dict[str, Any] = {
        "action": "recovery_transaction",
        "ok": False,
        "dry_run": dry_run,
        "trigger": plan.get("trigger"),
        "before": plan.get("before"),
        "steps": [],
        "verify": None,
    }
    if not plan.get("steps"):
        report["ok"] = True
        report["skipped"] = True
        report["reason"] = "no dirty paths to recover"
        write_recovery_report(repo, report)
        return report

    if dry_run:
        report["ok"] = True
        report["plan"] = plan
        write_recovery_report(repo, report)
        return report

    prev_pass = os.environ.get("PPE_PASS_TYPE")
    os.environ["PPE_PASS_TYPE"] = "RECOVERY"
    try:
        for step_plan in plan["steps"]:
            plane = str(step_plan.get("plane") or "control")
            sub = recover_branch(
                repo,
                plane=plane,
                branch=str(step_plan.get("branch") or suggest_branch(plane)),
                dry_run=False,
                ship=True,
                pre_push=pre_push,
                message=message,
            )
            report["steps"].append(sub)
            if not sub.get("ok") or sub.get("blocked"):
                report["blocked"] = True
                report["reason"] = sub.get("reason") or f"{plane} recovery failed"
                break
        else:
            report["verify"] = verify_recovery(repo)
            report["ok"] = bool(report["verify"].get("ok"))
            if not report["ok"]:
                report["reason"] = report["verify"].get("blocker")
    finally:
        if prev_pass is None:
            os.environ.pop("PPE_PASS_TYPE", None)
        else:
            os.environ["PPE_PASS_TYPE"] = prev_pass

    write_recovery_report(repo, report)
    return report


def recovery_ship_command(*, plane: str = "control", branch: str | None = None) -> str:
    br = branch or suggest_branch(plane)
    return f"python scripts/ppe_branch_recovery.py --plane {plane} --branch {br} --ship"


def recover_branch(
    repo: Path,
    *,
    plane: str = "control",
    branch: str | None = None,
    path_globs: list[str] | None = None,
    dry_run: bool = False,
    ship: bool = False,
    acquire_lease: bool = False,
    pre_push: bool = False,
    message: str | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    plane = plane if plane in PLANE_GLOBS else "control"
    work_branch = branch or suggest_branch(plane)
    globs = path_globs or PLANE_GLOBS[plane]
    forbidden = PLANE_FORBID.get(plane, [])

    report: dict[str, Any] = {
        "action": "branch_recovery",
        "ok": False,
        "plane": plane,
        "branch": work_branch,
        "dry_run": dry_run,
        "steps": [],
    }

    def step(name: str, payload: dict[str, Any]) -> None:
        report["steps"].append({"step": name, **payload})
        if payload.get("ok") is False and not payload.get("optional"):
            report["ok"] = False

    scoped, outside = classify_scoped_paths(repo, plane=plane, path_globs=globs)
    report["paths"] = scoped
    report["outside_scope"] = outside[:20]

    if not scoped:
        report["ok"] = True
        report["skipped"] = True
        report["reason"] = "no scoped dirty paths for plane"
        return report

    if outside and plane == "control":
        step(
            "mixed_plane",
            {
                "ok": True,
                "optional": True,
                "warning": f"{len(outside)} path(s) outside control scope — left unstaged",
            },
        )

    if dry_run:
        report["ok"] = True
        report["message"] = message
        step("dry_run", {"ok": True, "paths": scoped, "branch": work_branch})
        return report

    from scripts.ppe_worker_lease import LANE_CODEX, LANE_CURSOR, _ensure_work_branch, ship_lease_work

    ok_branch, actual_branch, detail = _ensure_work_branch(repo, work_branch)
    step("branch", {"ok": ok_branch, "branch": actual_branch, "detail": detail})
    if not ok_branch:
        report["blocked"] = True
        report["reason"] = detail
        return report

    if acquire_lease:
        from scripts.ppe_worker_lease import acquire_lease as take_lease

        worker = LANE_CURSOR if plane == "product" else LANE_CODEX
        try:
            lease = take_lease(
                repo,
                worker_id=worker,
                branch=actual_branch,
                path_globs=globs,
                forbidden_globs=forbidden,
            )
            step("lease", {"ok": True, "lease_id": lease.get("lease_id")})
        except RuntimeError as exc:
            step("lease", {"ok": False, "error": str(exc)})
            report["blocked"] = True
            report["reason"] = str(exc)
            return report

    if ship:
        prev_pass = os.environ.get("PPE_PASS_TYPE")
        if not prev_pass:
            os.environ["PPE_PASS_TYPE"] = "RECOVERY"
        try:
            ship_report = ship_lease_work(
                repo,
                dry_run=False,
                release_after=acquire_lease,
                message=message,
                pre_push=pre_push,
                path_globs=globs,
                forbidden_globs=forbidden,
                branch=actual_branch,
            )
        finally:
            if prev_pass is None:
                os.environ.pop("PPE_PASS_TYPE", None)
            else:
                os.environ["PPE_PASS_TYPE"] = prev_pass
        step("ship", ship_report)
        report["ok"] = bool(ship_report.get("ok"))
        if ship_report.get("pr_url"):
            report["pr_url"] = ship_report["pr_url"]
        if ship_report.get("blocked"):
            report["blocked"] = True
            report["reason"] = ship_report.get("reason")
        if report.get("ok"):
            report["verify"] = verify_recovery(repo)
            if not report["verify"].get("ok"):
                report["ok"] = False
                report["blocked"] = True
                report["reason"] = report["verify"].get("blocker")
        write_recovery_report(
            repo,
            {
                "action": "branch_recovery",
                "ok": report.get("ok"),
                "plane": plane,
                "trigger": "mixed_plane" if outside else "dirty_tree",
                "paths": scoped,
                "outside_scope": outside[:20],
                "verify": report.get("verify"),
                "pr_url": report.get("pr_url"),
            },
        )
        return report

    report["ok"] = True
    report["reason"] = "branch ready — run with --ship"
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Recover dirty work onto a clean plane branch.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--plane", choices=sorted(PLANE_GLOBS), default="control")
    ap.add_argument("--branch", type=str, default=None)
    ap.add_argument("--paths", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--plan-only", action="store_true", help="Emit recovery plan JSON (no git mutations)")
    ap.add_argument("--ship", action="store_true")
    ap.add_argument("--ship-all", action="store_true", help="Run control+product recovery sequence with verify")
    ap.add_argument("--verify", action="store_true", help="Verify repo state only (post-recovery)")
    ap.add_argument("--acquire-lease", action="store_true")
    ap.add_argument("--pre-push", action="store_true")
    ap.add_argument("--message", type=str, default=None)
    args = ap.parse_args(argv)

    if args.verify:
        report = verify_recovery(args.repo_root.resolve())
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"ppe_branch_recovery verify: {'ok' if report.get('ok') else 'blocked'}")
        return 0 if report.get("ok") else 1

    if args.plan_only:
        report = plan_recovery(args.repo_root.resolve())
        write_recovery_report(args.repo_root.resolve(), report)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"ppe_branch_recovery plan: {len(report.get('steps') or [])} step(s)")
        return 0

    if args.ship_all:
        report = recover_all(
            args.repo_root.resolve(),
            dry_run=args.dry_run,
            pre_push=args.pre_push,
            message=args.message,
        )
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            status = "ok" if report.get("ok") and not report.get("blocked") else "blocked"
            print(f"ppe_branch_recovery ship-all: {status}")
        return 0 if report.get("ok") and not report.get("blocked") else 1

    report = recover_branch(
        args.repo_root.resolve(),
        plane=args.plane,
        branch=args.branch,
        path_globs=args.paths,
        dry_run=args.dry_run,
        ship=args.ship,
        acquire_lease=args.acquire_lease,
        pre_push=args.pre_push,
        message=args.message,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        status = "ok" if report.get("ok") and not report.get("blocked") else "blocked"
        extra = report.get("pr_url") or report.get("reason") or report.get("skipped")
        print(f"ppe_branch_recovery: {status} {extra or ''}".strip())
    return 0 if report.get("ok") and not report.get("blocked") else 1


if __name__ == "__main__":
    raise SystemExit(main())
