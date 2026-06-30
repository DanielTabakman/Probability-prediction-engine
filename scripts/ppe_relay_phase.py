"""Run a docs/SOP phase plan sequentially using local workers (no ACP npm)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from scripts.ppe_active_run import clear_active_run, write_active_run
from scripts.ppe_manifest import load_manifest, load_phase_plan, save_manifest, set_manifest_status
from scripts.ppe_slice_worker_mode import resolve_declared_plane, resolve_worker_mode
from scripts.ppe_promotion_recovery import try_recover


def _commit_manifest_delta(repo: Path, message: str) -> None:
    """Local relay pins manifest status on main so worktree preflight stays clean."""
    if os.environ.get("PPE_OPERATOR_PROFILE", "").strip().lower() != "local":
        return
    proc = subprocess.run(
        ["git", "status", "--porcelain", "docs/SOP/ACTIVE_PHASE_MANIFEST.json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if not (proc.stdout or "").strip():
        return
    subprocess.run(["git", "add", "docs/SOP/ACTIVE_PHASE_MANIFEST.json"], cwd=repo, check=False)
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=False)


def _run_slice_cmd(
    repo: Path,
    *,
    slice_id: str,
    sprint_spec: str,
    plane: str,
    plan_path: str,
    build_branch: str,
    slice_obj: dict | None,
) -> tuple[int, Path | None]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    env["PPE_PHASE_PLAN"] = plan_path
    mode = resolve_worker_mode(slice_id=slice_id, slice_obj=slice_obj)
    if mode == "deterministic":
        from scripts.ppe_slice_worker import run_deterministic_slice
        from scripts.resolve_slice_orchestrator_args import main as resolve_args_main

        sus, hard, mx = 15, 30, 2
        try:
            import io
            from contextlib import redirect_stdout

            buf = io.StringIO()
            with redirect_stdout(buf):
                resolve_args_main(
                    [
                        "--repo-root",
                        str(repo),
                        "--slice-id",
                        slice_id,
                        "--phase-plan",
                        plan_path,
                    ]
                )
            parts = buf.getvalue().strip().split()
            if len(parts) >= 3:
                sus, hard, mx = int(parts[0]), int(parts[1]), int(parts[2])
        except Exception:
            pass
        return run_deterministic_slice(
            repo,
            slice_id=slice_id,
            sprint_spec=sprint_spec,
            declared_plane=plane,
            build_branch=build_branch,
            phase_plan=plan_path,
            sus_minutes=sus,
            hard_minutes=hard,
        )

    if mode == "local-agent":
        from scripts.phase_orchestrator_v0 import Orchestrator, SliceRun, TimeBudget

        orch = Orchestrator(repo)
        from scripts.repo_layer_paths import resolve_slice_layer_scope

        scope = resolve_slice_layer_scope(
            repo,
            slice_obj=slice_obj,
            slice_id=slice_id,
            declared_plane=plane,
        )
        run = SliceRun(
            slice_id=slice_id,
            sprint_spec_path=sprint_spec,
            declared_plane=plane,
            baseline_branch="main",
            build_branch=build_branch,
            repo_layer=scope.to_envelope_dict(),
        )
        r = orch.run_slice(run=run, budgets=TimeBudget(), worker_mode="agent-cli", slice_obj=slice_obj)
        st = r.get("status")
        if st == "CONTINUE":
            return 0, None
        if st == "STOP_FOR_REVIEW":
            return 20, None
        if st == "BLOCKED":
            return 40, None
        return 2, None

    slice_cmd = repo / "run_slice.cmd"
    rc = subprocess.run(
        ["cmd", "/c", str(slice_cmd), slice_id, sprint_spec, plane, plan_path],
        cwd=repo,
        env=env,
    ).returncode
    return rc, None


def run_phase(repo_root: Path, plan_path: str) -> int:
    repo = repo_root.resolve()
    norm_plan = plan_path.replace("\\", "/").strip()
    from scripts.ppe_phase_plan_window import (
        active_slice_window,
        mark_slice_complete,
        phase_slice_batching_enabled,
        plan_slice_count,
        windowed_phase_plan,
    )

    plan = windowed_phase_plan(repo, norm_plan) if phase_slice_batching_enabled(repo) else load_phase_plan(repo, plan_path)
    batch_slices = plan.get("slices") or []
    if phase_slice_batching_enabled(repo) and not batch_slices:
        from scripts.ppe_ide_product_ready import load_marker

        marker = load_marker(repo)
        manifest = load_manifest(repo)
        mstat = str(manifest.get("status") or "").upper()
        if marker and mstat not in ("COMPLETE", ""):
            try:
                from scripts.ppe_queue_health import chapter_marked_complete_in_repo

                chapter_closed = chapter_marked_complete_in_repo(repo, norm_plan)
            except Exception:
                chapter_closed = False
            if not chapter_closed:
                print(
                    "ppe_relay_phase: batch empty but chapter not closed — "
                    "stale progress or closeout pending; "
                    "run: python scripts/ppe_repair_relay_progress.py",
                    file=sys.stderr,
                )
                return 2
        print("ppe_relay_phase: all slices complete for plan (batching)")
        return 0
    if phase_slice_batching_enabled(repo):
        meta = plan.get("_sliceBatch") or {}
        print(
            f"ppe_relay_phase: slice batch {meta.get('batchSize')} of "
            f"{meta.get('totalSlices')} (limit {meta.get('limit')}, done {meta.get('completedCount')})"
        )
    sprint_default = str(plan.get("sprintSpecPath") or "")
    baseline = str(plan.get("baselineBranch") or "main")
    try:
        set_manifest_status(repo, "RUNNING")
        manifest = load_manifest(repo)
        manifest["phasePlanPath"] = plan_path.replace("\\", "/")
        manifest["sprintSpecPath"] = sprint_default
        save_manifest(repo, manifest)
        _commit_manifest_delta(repo, "ops(local): manifest RUNNING for relay pass")
    except Exception as e:
        print(f"WARN: manifest RUNNING: {e}")

    write_active_run(
        repo,
        kind="phase",
        plan_path=norm_plan,
        baseline_branch=baseline,
    )

    exit_code = 0
    try:
        exit_code = _run_phase_slices(
            repo,
            norm_plan=norm_plan,
            plan_path=plan_path,
            batch_slices=batch_slices,
            sprint_default=sprint_default,
        )
    finally:
        clear_active_run(repo)
        try:
            manifest = load_manifest(repo)
            status = str(manifest.get("status") or "").upper()
            if status == "RUNNING":
                set_manifest_status(repo, "READY")
                _commit_manifest_delta(repo, "ops(local): manifest READY after relay pass")
                print("ppe_relay_phase: manifest RUNNING -> READY (pass complete)")
        except Exception as e:
            print(f"WARN: manifest READY after pass: {e}")

    return exit_code


def _run_phase_slices(
    repo: Path,
    *,
    norm_plan: str,
    plan_path: str,
    batch_slices: list,
    sprint_default: str,
) -> int:
    from scripts.ppe_phase_plan_window import (
        active_slice_window,
        mark_slice_complete,
        phase_slice_batching_enabled,
        plan_slice_count,
    )

    for sl in batch_slices:
        if not isinstance(sl, dict):
            continue
        slice_id = str(sl.get("sliceId") or "").strip()
        if not slice_id:
            continue
        sprint = str(sl.get("sprintSpecPath") or sprint_default)
        plane = resolve_declared_plane(sl, "EVIDENCE-PLANE")
        build_branch = str(sl.get("buildBranch") or f"build/auto/{slice_id}-local")
        print(f"ppe_relay_phase: slice {slice_id} worker={resolve_worker_mode(slice_id=slice_id, slice_obj=sl)}")
        exit_code, relay_run_dir = _run_slice_cmd(
            repo,
            slice_id=slice_id,
            sprint_spec=sprint,
            plane=plane,
            plan_path=plan_path,
            build_branch=build_branch,
            slice_obj=sl,
        )
        post_cmd = [
            sys.executable,
            str(repo / "scripts" / "post_relay_continue.py"),
            "--repo-root",
            str(repo),
            "--phase-plan",
            plan_path,
            "--orchestrator-exit-code",
            str(exit_code),
        ]
        if relay_run_dir is not None:
            post_cmd.extend(["--relay-run-dir", str(relay_run_dir)])
        subprocess.run(post_cmd, cwd=repo, check=False)
        is_closeout = isinstance(sl.get("closeout"), dict)
        if exit_code == 0:
            if phase_slice_batching_enabled(repo) and not is_closeout:
                mark_slice_complete(repo, norm_plan, slice_id)
            if not is_closeout:
                try:
                    from scripts.ppe_progress_notify import notify_slice_complete

                    closeout = sl.get("closeout") or {}
                    chapter_id = str(closeout.get("chapterId") or "").strip()
                    notify_slice_complete(
                        slice_id,
                        plan_path=plan_path.replace("\\", "/"),
                        chapter_id=chapter_id,
                    )
                except Exception as exc:
                    print(f"ppe_relay_phase: progress notify skipped: {exc}")
        if exit_code != 0:
            rc = try_recover(
                repo,
                exit_code=exit_code,
                phase_plan=(repo / plan_path).resolve(),
                slice_id=slice_id,
                build_branch=build_branch,
                relay_run_dir=relay_run_dir,
            )
            if rc == 100:
                if phase_slice_batching_enabled(repo) and not is_closeout:
                    mark_slice_complete(repo, norm_plan, slice_id)
                continue
            return exit_code

    if phase_slice_batching_enabled(repo):
        remaining = active_slice_window(repo, norm_plan)
        if remaining:
            print(f"ppe_relay_phase: batch complete — {len(remaining)} slice(s) remain in next pass")
        elif plan_slice_count(repo, norm_plan) > len(batch_slices):
            pass
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run phase plan with local/deterministic workers")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--plan", required=True)
    args = ap.parse_args(argv)
    return run_phase(args.repo_root, args.plan)


if __name__ == "__main__":
    raise SystemExit(main())
