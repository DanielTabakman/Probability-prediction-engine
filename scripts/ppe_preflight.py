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
from scripts.ppe_queue_health import run_queue_health


def maybe_clear_stale_active_run(repo: Path, manifest: dict[str, object]) -> str | None:
    """Remove stale ACTIVE_RUN when manifest is idle or slice already completed."""
    active_path = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if not active_path.is_file():
        return None

    status = str(manifest.get("status") or "").upper()
    plan_path = str(manifest.get("phasePlanPath") or "").strip()
    reason = ""

    if status in ("READY", "COMPLETE", ""):
        reason = f"manifest status {status or 'empty'}"
    elif plan_path:
        try:
            active = json.loads(active_path.read_text(encoding="utf-8-sig"))
            sid = str(active.get("slice_id") or active.get("sliceId") or "").strip()
            if sid:
                from scripts.ppe_phase_plan_window import completed_slice_ids

                if sid in completed_slice_ids(repo, plan_path):
                    reason = f"slice {sid} already completed for plan"
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    if not reason:
        return None

    try:
        active_path.unlink(missing_ok=True)
    except OSError:
        return None
    return reason


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


def _dirty_paths(repo: Path) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    paths: list[str] = []
    for line in (out.stdout or "").splitlines():
        if len(line) < 4 or line.startswith("##"):
            continue
        paths.append(line[3:].strip().split(" -> ")[-1])
    return paths


def _closeout_only_context(repo: Path, manifest: dict[str, object]) -> bool:
    try:
        from scripts.ppe_ide_product_ready import load_marker

        if load_marker(repo):
            return True
    except Exception:
        pass
    plan_path = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_path:
        return False
    try:
        from scripts.ppe_chapter_mode import is_closeout_only_chapter
        from scripts.ppe_manifest import resolve_summary

        summary = resolve_summary(repo)
        return is_closeout_only_chapter(
            repo,
            plan_path=plan_path,
            chapter_name=str(summary.get("chapter_name") or "") or None,
        )
    except Exception:
        return False


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
    if manifest:
        cleared = maybe_clear_stale_active_run(repo, manifest)
        if cleared:
            warnings.append(f"cleared stale ACTIVE_RUN ({cleared})")
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
        closeout_only = _closeout_only_context(repo, manifest) if manifest else False
        dirty_paths = _dirty_paths(repo)
        product_dirty = [p for p in dirty_paths if p.replace("\\", "/").startswith("src/")]
        control_branch = branch.startswith(("control-plane/", "ops/", "fix/", "chore/"))

        if branch and branch != "main":
            if closeout_only and control_branch and not product_dirty:
                pass
            else:
                warnings.append(
                    f"checkout is {branch!r}, not main; post-phase closeout patches docs/SOP here — "
                    "prefer main for run_ppe.cmd"
                )
        if dirty_paths:
            if closeout_only and not product_dirty:
                pass
            else:
                warnings.append("main checkout has uncommitted changes (worktrees do BUILD)")
    except (subprocess.CalledProcessError, FileNotFoundError):
        warnings.append("git status unavailable")

    try:
        health = run_queue_health(repo, apply=True)
        for fix in health.get("fixes") or []:
            warnings.append(
                f"queue/backlog auto-repair: {fix.get('action')} "
                f"index={fix.get('index')} plan={fix.get('planPath')}"
            )
        for issue in health.get("remaining_issues") or []:
            code = issue.get("code", "?")
            plan = issue.get("planPath", "")
            idx = issue.get("index", "")
            errors.append(f"PHASE_QUEUE/BACKLOG: {code} plan={plan} index={idx}")
    except FileNotFoundError:
        errors.append("Missing docs/SOP/PHASE_QUEUE.json")

    layer_warnings: list[str] = []
    layer_errors: list[str] = []
    manifest_status = str(manifest.get("status") or "") if manifest else ""
    if manifest_status in ("RUNNING", "READY") or active_run.is_file():
        try:
            from scripts.repo_layer_paths import audit_git_dirty_preflight, scope_for_active_manifest

            scope = scope_for_active_manifest(repo)
            if scope is not None:
                dirty_v = audit_git_dirty_preflight(repo, scope)
                if dirty_v:
                    layer_errors.extend(dirty_v)
                else:
                    layer_warnings.append(
                        f"repo layer scope: preset={scope.layer_preset!r} (dirty paths OK)"
                    )
        except FileNotFoundError:
            pass

    errors.extend(layer_errors)
    warnings.extend(layer_warnings)

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
