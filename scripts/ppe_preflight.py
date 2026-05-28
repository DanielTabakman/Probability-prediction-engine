"""Preflight checks before run_ppe.cmd (manifest, ACTIVE_RUN, orchestrator)."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.ppe_manifest import (
    MANIFEST_REL,
    load_manifest,
    resolve_summary,
    validate_manifest,
)
from scripts.ppe_queue_health import repair_queue


def _orchestrator_root(repo_root: Path) -> Path | None:
    # Windows note: some setups have Desktop on a different drive than USERPROFILE
    # (e.g., repo at D:\Users\User\Desktop\...). Prefer detecting Desktop from repo_root
    # parents when possible, so worktrees under the repo still resolve correctly.
    repo_desktop = next(
        (p for p in repo_root.resolve().parents if p.name.lower() == "desktop"),
        None,
    )

    candidates = [
        (repo_desktop / "ppe-orchestrator-acp") if repo_desktop else None,
        Path.home() / "Desktop" / "ppe-orchestrator-acp",
        repo_root.parent / "ppe-orchestrator-acp",
    ]
    for c in candidates:
        if c is None:
            continue
        if (c / "package.json").is_file():
            return c
    return None


def run_preflight(
    repo_root: Path,
    *,
    allow_complete: bool = False,
    allow_running: bool = False,
    check_orchestrator: bool = True,
) -> dict[str, object]:
    repo = repo_root.resolve()
    warnings: list[str] = []
    errors: list[str] = []

    try:
        manifest = load_manifest(repo)
    except FileNotFoundError:
        errors.append(f"Missing {MANIFEST_REL}")
        manifest = {}
    except json.JSONDecodeError as e:
        errors.append(f"manifest JSON invalid: {e}")
        manifest = {}

    if manifest:
        errors.extend(validate_manifest(repo, manifest))
        status = str(manifest.get("status") or "")
        if status == "COMPLETE" and not allow_complete:
            errors.append("manifest status is COMPLETE; steward must set READY at SELECTION")
        if status == "RUNNING" and not allow_running:
            warnings.append("manifest status is RUNNING (prior run may have aborted)")

    active_run = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if active_run.is_file():
        warnings.append(f"ACTIVE_RUN present: {active_run.as_posix()} (stale or in-flight)")

    orch = _orchestrator_root(repo) if check_orchestrator else None
    if check_orchestrator:
        if orch is None:
            errors.append(
                "ppe-orchestrator-acp not found (expected Desktop/ppe-orchestrator-acp or sibling repo)"
            )
        else:
            warnings.append(f"orchestrator: {orch.as_posix()}")

    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if branch and branch != "main":
            warnings.append(
                f"checkout is {branch!r}, not main; post-phase closeout patches docs/SOP here — "
                "prefer main for run_ppe.cmd"
            )
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
        dirty = out.stdout.strip()
        if dirty:
            warnings.append("main checkout has uncommitted changes (worktrees do BUILD)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.append("git status unavailable")

    try:
        fixes, remaining = repair_queue(repo, apply=True)
        for fix in fixes:
            warnings.append(f"queue auto-repair: {fix.get('action')} index={fix.get('index')} plan={fix.get('planPath')}")
        for issue in remaining:
            errors.append(f"PHASE_QUEUE: {issue.get('code')} plan={issue.get('planPath', '')} index={issue.get('index', '')}")
    except FileNotFoundError:
        errors.append("Missing docs/SOP/PHASE_QUEUE.json")

    ok = len(errors) == 0
    return {
        "ok": ok,
        "errors": errors,
        "warnings": warnings,
        "orchestrator_root": str(orch) if orch else None,
        "phase_plan_path": (manifest.get("phasePlanPath") if manifest else None),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE run preflight")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--allow-complete", action="store_true")
    ap.add_argument("--allow-running", action="store_true")
    args = ap.parse_args(argv)

    result = run_preflight(
        args.repo_root,
        allow_complete=args.allow_complete,
        allow_running=args.allow_running,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    for w in result.get("warnings") or []:
        print(f"WARN: {w}")
    for e in result.get("errors") or []:
        print(f"ERROR: {e}", file=sys.stderr)
    if result["ok"]:
        summary = resolve_summary(args.repo_root.resolve())
        print(
            f"OK: phase={summary.get('phase_plan_path')} "
            f"slices={summary.get('slice_count')} status={summary.get('status')}"
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
