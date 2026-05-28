"""Run a docs/SOP phase plan sequentially using local workers (no ACP npm)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from scripts.ppe_manifest import load_manifest, load_phase_plan, save_manifest, set_manifest_status
from scripts.ppe_slice_worker_mode import resolve_declared_plane, resolve_worker_mode
from scripts.ppe_promotion_recovery import try_recover


def _run_slice_cmd(
    repo: Path,
    *,
    slice_id: str,
    sprint_spec: str,
    plane: str,
    plan_path: str,
    build_branch: str,
    slice_obj: dict | None,
) -> int:
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
        run = SliceRun(
            slice_id=slice_id,
            sprint_spec_path=sprint_spec,
            declared_plane=plane,
            baseline_branch="main",
            build_branch=build_branch,
        )
        r = orch.run_slice(run=run, budgets=TimeBudget(), worker_mode="agent-cli")
        st = r.get("status")
        if st == "CONTINUE":
            return 0
        if st == "STOP_FOR_REVIEW":
            return 20
        if st == "BLOCKED":
            return 40
        return 2

    slice_cmd = repo / "run_slice.cmd"
    return subprocess.run(
        ["cmd", "/c", str(slice_cmd), slice_id, sprint_spec, plane, plan_path],
        cwd=repo,
        env=env,
    ).returncode


def run_phase(repo_root: Path, plan_path: str) -> int:
    repo = repo_root.resolve()
    plan = load_phase_plan(repo, plan_path)
    sprint_default = str(plan.get("sprintSpecPath") or "")
    try:
        set_manifest_status(repo, "RUNNING")
        manifest = load_manifest(repo)
        manifest["phasePlanPath"] = plan_path.replace("\\", "/")
        manifest["sprintSpecPath"] = sprint_default
        save_manifest(repo, manifest)
    except Exception as e:
        print(f"WARN: manifest RUNNING: {e}")

    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        slice_id = str(sl.get("sliceId") or "").strip()
        if not slice_id:
            continue
        sprint = str(sl.get("sprintSpecPath") or sprint_default)
        plane = resolve_declared_plane(sl, "EVIDENCE-PLANE")
        build_branch = str(sl.get("buildBranch") or f"build/auto/{slice_id}-local")
        print(f"ppe_relay_phase: slice {slice_id} worker={resolve_worker_mode(slice_id=slice_id, slice_obj=sl)}")
        exit_code = _run_slice_cmd(
            repo,
            slice_id=slice_id,
            sprint_spec=sprint,
            plane=plane,
            plan_path=plan_path,
            build_branch=build_branch,
            slice_obj=sl,
        )
        subprocess.run(
            [
                sys.executable,
                str(repo / "scripts" / "post_relay_continue.py"),
                "--repo-root",
                str(repo),
                "--phase-plan",
                plan_path,
                "--orchestrator-exit-code",
                str(exit_code),
            ],
            cwd=repo,
            check=False,
        )
        if exit_code != 0:
            rc = try_recover(
                repo,
                exit_code=exit_code,
                phase_plan=(repo / plan_path).resolve(),
                slice_id=slice_id,
                build_branch=build_branch,
            )
            if rc == 100:
                continue
            return exit_code
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run phase plan with local/deterministic workers")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--plan", required=True)
    args = ap.parse_args(argv)
    return run_phase(args.repo_root, args.plan)


if __name__ == "__main__":
    raise SystemExit(main())
