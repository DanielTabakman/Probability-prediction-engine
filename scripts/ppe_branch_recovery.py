"""Recover mixed dirty trees onto a clean plane branch and optionally ship.

Canon: docs/SOP/COMMIT_POLICY.md § Gate failed · AGENTS.md
"""

from __future__ import annotations

import argparse
import json
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
    from scripts.ppe_worker_lease import _current_branch, scoped_dirty_paths

    branch = _current_branch(repo)
    if branch in ("main", "master", ""):
        return bool(scoped or scoped_dirty_paths(repo, path_globs=["**"], forbidden_globs=[]))
    if not scoped:
        return False
    try:
        import subprocess
        import sys

        proc = subprocess.run(
            [sys.executable, str(repo / "scripts" / "frontier_preflight.py"), "--json"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode in (0, 1) and proc.stdout.strip():
            pf = json.loads(proc.stdout)
            if isinstance(pf, dict) and pf.get("mixed_plane_dirty"):
                return True
    except Exception:
        pass
    return False


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
        step("ship", ship_report)
        report["ok"] = bool(ship_report.get("ok"))
        if ship_report.get("pr_url"):
            report["pr_url"] = ship_report["pr_url"]
        if ship_report.get("blocked"):
            report["blocked"] = True
            report["reason"] = ship_report.get("reason")
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
    ap.add_argument("--ship", action="store_true")
    ap.add_argument("--acquire-lease", action="store_true")
    ap.add_argument("--pre-push", action="store_true")
    ap.add_argument("--message", type=str, default=None)
    args = ap.parse_args(argv)

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
