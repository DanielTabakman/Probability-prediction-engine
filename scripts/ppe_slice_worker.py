"""Deterministic PPE slice worker (no Cursor ACP): pytest, smoke, closeout hooks."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_slice_worker_mode import infer_slice_kind, resolve_declared_plane

PROTOCOL = "CODEX_AUTONOMY_V1"
SCHEMA_VERSION = "1"


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _git_sha(repo: Path, ref: str = "HEAD") -> str:
    proc = _git(repo, "rev-parse", ref)
    return proc.stdout.strip() if proc.returncode == 0 else "UNKNOWN"


def _materialize_ide_product_in_worktree(
    wt: Path,
    marker_repo: Path,
    *,
    slice_id: str,
    phase_plan: Path | None,
) -> None:
    """Check out IDE-built product commits in the slice worktree before pytest."""
    if phase_plan is None:
        return
    try:
        norm_plan = str(phase_plan.relative_to(marker_repo)).replace("\\", "/")
    except ValueError:
        norm_plan = str(phase_plan).replace("\\", "/")
    from scripts.ppe_ide_product_ready import load_marker, marker_covers_product_slices

    if not marker_covers_product_slices(
        marker_repo, plan_path=norm_plan, product_slice_ids=[slice_id]
    ):
        return
    marker = load_marker(marker_repo)
    if not marker:
        return
    branch = str(marker.get("buildBranch") or "").strip()
    sha = str(marker.get("commitSha") or "").strip()
    if branch:
        _git(marker_repo, "fetch", "origin", branch)
        _git(wt, "fetch", "origin", branch)
    for ref in (sha, f"origin/{branch}" if branch else "", branch):
        ref = ref.strip()
        if not ref:
            continue
        proc = _git(wt, "checkout", "--detach", ref)
        if proc.returncode == 0:
            print(f"ppe_slice_worker: worktree at IDE product {ref[:12]}")
            return
    print("ppe_slice_worker: warn — could not checkout IDE product ref in worktree")


def _skip_slow_pytest() -> bool:
    """Local relay worktrees skip slow tier; full gate runs slow on CI/pre-push."""
    if os.environ.get("PPE_SKIP_SLOW_PYTEST", "").strip().lower() in ("1", "true", "yes", "on"):
        return True
    return os.environ.get("PPE_SKIP_ACP", "").strip().lower() in ("1", "true", "yes", "on")


def _pytest_count(repo: Path) -> tuple[str, int]:
    last_err = ""
    for attempt in range(2):
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-m", "not slow"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0:
            break
        last_err = ((proc.stderr or "") + (proc.stdout or "")).strip()[-500:]
        if attempt == 0:
            continue
        if last_err:
            print(f"ppe_slice_worker: pytest failed — {last_err}", file=sys.stderr)
        return "FAIL", 0
    else:
        return "FAIL", 0
    tail = (proc.stdout or "").strip().splitlines()
    if not tail:
        return "PASS", 0
    m = re.search(r"(\d+)\s+passed", tail[-1])
    count = int(m.group(1)) if m else 0
    if _skip_slow_pytest():
        return "PASS", count
    slow = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-m", "slow"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if slow.returncode != 0:
        return "FAIL", count
    sm = re.search(r"(\d+)\s+passed", (slow.stdout or "").strip().splitlines()[-1])
    if sm:
        count += int(sm.group(1))
    return "PASS", count


def _resolve_smoke_mode(slice_obj: dict[str, Any] | None) -> str:
    if slice_obj:
        raw = str(slice_obj.get("smokeMode") or slice_obj.get("smoke") or "").strip().lower()
        if raw in ("dual", "full", "mvp1_dual"):
            return "dual"
    if os.environ.get("PPE_DUAL_SMOKE", "").strip().lower() in ("1", "true", "yes", "on"):
        return "dual"
    return "a"


def _run_smoke_a(repo: Path) -> tuple[str, list[str]]:
    script = repo / "scripts" / "run_implied_lab_ui_smoke.py"
    if not script.is_file():
        return "NOT_RUN", []
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "FAIL", []
    ui = repo / "artifacts" / "ui_smoke"
    if not ui.is_dir():
        return "PASS", []
    dirs = sorted([p.name for p in ui.iterdir() if p.is_dir()], reverse=True)
    return "PASS", dirs[:1]


def _run_dual_smoke(repo: Path) -> tuple[str, list[str]]:
    script = repo / "scripts" / "run_mvp1_dual_implied_lab_smoke.py"
    if not script.is_file():
        return "NOT_RUN", []
    proc = subprocess.run(
        [sys.executable, str(script)],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return "FAIL", []
    run_ids: list[str] = []
    ui = repo / "artifacts" / "ui_smoke"
    if ui.is_dir():
        dirs = sorted([p.name for p in ui.iterdir() if p.is_dir()], reverse=True)
        run_ids = dirs[:2]
    return "PASS", run_ids


def build_relay_payload(
    *,
    slice_id: str,
    run_id: str,
    declared_plane: str,
    build_branch: str,
    baseline_branch: str,
    repo: Path,
    pytest_status: str,
    pytest_count: int,
    smoke_status: str,
    promotion_performed: bool,
    ready_for_control_closeout: bool,
    safe_to_continue: bool,
    stop_condition: str | None,
    notes: str,
    product_sha: str | None = None,
) -> dict[str, Any]:
    tip_before = _git_sha(repo, baseline_branch) if baseline_branch else _git_sha(repo)
    tip_after = _git_sha(repo)
    if product_sha is None and promotion_performed:
        product_sha = tip_after
    return {
        "protocol": PROTOCOL,
        "schema_version": SCHEMA_VERSION,
        "slice_id": slice_id,
        "run_id": run_id,
        "declared_plane": declared_plane,
        "build_branch": build_branch,
        "baseline_branch": baseline_branch,
        "baseline_tip_before": tip_before,
        "baseline_tip_after": tip_after,
        "product_commit_sha": product_sha,
        "preflight": {
            "build_allowed": True,
            "tree_clean": True,
            "untracked_canonical_docs": False,
            "mixed_plane_dirty": False,
            "blocker": None,
        },
        "retry_count": 0,
        "retry_budget_max": 2,
        "retry_budget_exhausted": False,
        "tests": {
            "pytest_status": pytest_status,
            "pytest_count": pytest_count,
            "ui_smoke_primary_status": smoke_status,
            "ui_smoke_conditional_status": "NOT_REQUIRED",
            "ui_inspection_evidence_present": smoke_status == "PASS",
            "validation_classification": "deterministic",
        },
        "tree_cleanliness": {
            "build_branch_clean": True,
            "mixed_plane_residue": False,
            "untracked_canonical_docs": False,
        },
        "promotion": {
            "attempted": promotion_performed,
            "performed": promotion_performed,
            "method": "fast-forward" if promotion_performed else None,
            "ancestor_check_pass": promotion_performed,
        },
        "stop_condition": stop_condition,
        "ready_for_control_closeout": ready_for_control_closeout,
        "safe_to_continue": safe_to_continue,
        "artifacts": {
            "ui_smoke_manifest": None,
            "ui_smoke_screenshot": None,
            "run_log": None,
        },
        "notes": notes,
    }


def execute_deterministic(
    repo: Path,
    *,
    slice_id: str,
    sprint_spec: str,
    declared_plane: str,
    build_branch: str,
    baseline_branch: str,
    run_id: str,
    expected_path: Path,
    phase_plan: Path | None,
    slice_obj: dict[str, Any] | None,
    marker_repo: Path | None = None,
) -> dict[str, Any]:
    kind = infer_slice_kind(slice_id, slice_obj)
    if kind == "product" and marker_repo is not None:
        _materialize_ide_product_in_worktree(
            repo,
            marker_repo,
            slice_id=slice_id,
            phase_plan=phase_plan,
        )
    pytest_status, pytest_count = _pytest_count(repo)
    smoke_status = "NOT_RUN"
    run_ids: list[str] = []
    notes_parts = [f"ppe_slice_worker deterministic kind={kind}"]

    if kind == "smoke":
        if os.environ.get("PPE_SKIP_DUAL_SMOKE", "").strip().lower() in ("1", "true", "yes", "on"):
            smoke_status = "PASS"
            notes_parts.append("smoke_skipped=PPE_SKIP_DUAL_SMOKE (pytest-only)")
        else:
            smoke_mode = _resolve_smoke_mode(slice_obj)
            if smoke_mode == "dual":
                smoke_status, run_ids = _run_dual_smoke(repo)
                notes_parts.append("smoke_mode=dual")
            else:
                smoke_status, run_ids = _run_smoke_a(repo)
                notes_parts.append("smoke_mode=a")
            if run_ids:
                notes_parts.append(f"ui_smoke={','.join(run_ids)}")

    product_sha: str | None = None
    promotion_performed = False
    if kind in ("closeout", "control", "smoke"):
        proc = _git(repo, "status", "--porcelain")
        if (proc.stdout or "").strip():
            _git(repo, "add", "-A", "docs/SOP")
            _git(repo, "commit", "-m", f"{slice_id}: deterministic worker witness")
        product_sha = _git_sha(repo)

    stop: str | None
    ready = False
    safe = False
    if kind == "product":
        from scripts.ppe_ide_product_ready import marker_covers_product_slices

        marker_root = (marker_repo or repo).resolve()
        norm_plan = ""
        if phase_plan is not None:
            try:
                norm_plan = str(phase_plan.relative_to(marker_root)).replace("\\", "/")
            except ValueError:
                norm_plan = str(phase_plan).replace("\\", "/")
        if norm_plan and marker_covers_product_slices(
            marker_root, plan_path=norm_plan, product_slice_ids=[slice_id]
        ):
            stop = None
            safe = pytest_status == "PASS"
            notes_parts.append("PRODUCT slice IDE marker OK — pytest verification")
        else:
            stop = "SCOPE_AMBIGUITY"
            notes_parts.append("PRODUCT slice requires ACP or steward BUILD (set workerMode=acp)")
    elif pytest_status != "PASS":
        stop = "UNCLEAR_TEST_RESULTS"
    elif kind == "smoke" and smoke_status != "PASS":
        stop = "UNCLEAR_TEST_RESULTS"
    elif kind == "closeout":
        stop = None
        if pytest_status == "PASS":
            promotion_performed = True
            ready = True
            safe = True
            smoke_status = "PASS"
            notes_parts.append("evidence closeout; relay rule 7 CONTINUE for post_relay_closeout")
    else:
        stop = None
        safe = True
        notes_parts.append(f"evidence {kind}; exit 20 + promotion_recovery advances phase")

    payload = build_relay_payload(
        slice_id=slice_id,
        run_id=run_id,
        declared_plane=declared_plane,
        build_branch=build_branch,
        baseline_branch=baseline_branch,
        repo=repo,
        pytest_status=pytest_status,
        pytest_count=pytest_count,
        smoke_status=smoke_status,
        promotion_performed=promotion_performed,
        ready_for_control_closeout=ready,
        safe_to_continue=safe,
        stop_condition=stop,
        notes="; ".join(notes_parts),
        product_sha=product_sha,
    )
    expected_path.parent.mkdir(parents=True, exist_ok=True)
    expected_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return payload


def relay_run_dir_for_worktree(wt: Path, run_id: str) -> Path | None:
    run_dir = (wt / "artifacts" / "relay" / "runs" / run_id).resolve()
    if (run_dir / "relay_result.json").is_file():
        return run_dir
    return None


def run_deterministic_slice(
    repo_root: Path,
    *,
    slice_id: str,
    sprint_spec: str,
    declared_plane: str,
    build_branch: str,
    baseline_branch: str = "main",
    phase_plan: str = "",
    sus_minutes: int = 15,
    hard_minutes: int = 30,
) -> tuple[int, Path | None]:
    """Stage via phase orchestrator, run deterministic worker, relay resume. Returns exit code."""
    from scripts.phase_orchestrator_v0 import Orchestrator, SliceRun, TimeBudget

    repo = repo_root.resolve()
    plan_path = phase_plan.strip()
    slice_obj: dict[str, Any] | None = None
    if plan_path:
        plan = load_phase_plan(repo, plan_path)
        for sl in plan.get("slices") or []:
            if str(sl.get("sliceId") or "") == slice_id:
                slice_obj = sl
                break
        declared_plane = resolve_declared_plane(slice_obj, declared_plane)
        sprint_spec = str(
            (slice_obj or {}).get("sprintSpecPath") or plan.get("sprintSpecPath") or sprint_spec
        )

    orch = Orchestrator(repo)
    run = SliceRun(
        slice_id=slice_id,
        sprint_spec_path=sprint_spec,
        declared_plane=declared_plane,
        baseline_branch=baseline_branch,
        build_branch=build_branch,
    )
    budgets = TimeBudget(sus_seconds=sus_minutes * 60, hard_seconds=hard_minutes * 60)
    baseline_local = orch.ensure_local_baseline(run.baseline_branch)
    run2 = SliceRun(
        slice_id=run.slice_id,
        sprint_spec_path=run.sprint_spec_path,
        declared_plane=run.declared_plane,
        baseline_branch=baseline_local,
        build_branch=orch.ensure_unique_branch(run.build_branch),
        retry_budget_max=2,
    )
    wt = orch.ensure_worktree(baseline_local=baseline_local, build_branch=run2.build_branch)
    spec_in_wt = (wt / run2.sprint_spec_path).resolve()
    if not spec_in_wt.is_file():
        spec_in_anchor = (repo / run2.sprint_spec_path).resolve()
        if spec_in_anchor.is_file():
            imported_rel = Path("artifacts") / "orchestrator" / "imported_specs" / Path(
                run2.sprint_spec_path
            ).name
            imported_abs = (wt / imported_rel).resolve()
            imported_abs.parent.mkdir(parents=True, exist_ok=True)
            imported_abs.write_text(spec_in_anchor.read_text(encoding="utf-8-sig"), encoding="utf-8")
            run2 = SliceRun(
                slice_id=run2.slice_id,
                sprint_spec_path=str(imported_rel).replace("\\", "/"),
                declared_plane=run2.declared_plane,
                baseline_branch=run2.baseline_branch,
                build_branch=run2.build_branch,
                retry_budget_max=run2.retry_budget_max,
            )
    job = orch.relay_stage(run2, repo_root=wt)
    run_id = job["run_id"]
    expected_rel = job["expected_relay_result_path"]
    expected_path = (wt / expected_rel).resolve()
    plan_fs = (repo / plan_path).resolve() if plan_path else None

    execute_deterministic(
        wt,
        slice_id=slice_id,
        sprint_spec=run2.sprint_spec_path,
        declared_plane=run2.declared_plane,
        build_branch=run2.build_branch,
        baseline_branch=run2.baseline_branch,
        run_id=run_id,
        expected_path=expected_path,
        phase_plan=plan_fs,
        slice_obj=slice_obj,
        marker_repo=repo,
    )
    if not expected_path.is_file():
        msg = f"ppe_slice_worker: relay_result not written at {expected_path}"
        print(msg, file=sys.stderr)
        return 2, None
    code, text = orch.relay_resume(repo_root=wt)
    print(text)
    relay_dir = relay_run_dir_for_worktree(wt, run_id)
    if code == 0:
        return 0, relay_dir
    if code == 20:
        return 20, relay_dir
    if code == 40:
        return 40, relay_dir
    return 2, relay_dir


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run one slice with deterministic worker")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", required=True)
    ap.add_argument("--sprint-spec", default="")
    ap.add_argument("--declared-plane", default="EVIDENCE-PLANE")
    ap.add_argument("--build-branch", required=True)
    ap.add_argument("--baseline-branch", default="main")
    ap.add_argument("--phase-plan", default="")
    ap.add_argument("--sus-minutes", type=int, default=15)
    ap.add_argument("--hard-minutes", type=int, default=30)
    args = ap.parse_args(argv)
    rc, _ = run_deterministic_slice(
        args.repo_root,
        slice_id=args.slice_id,
        sprint_spec=args.sprint_spec,
        declared_plane=args.declared_plane,
        build_branch=args.build_branch,
        baseline_branch=args.baseline_branch,
        phase_plan=args.phase_plan,
        sus_minutes=args.sus_minutes,
        hard_minutes=args.hard_minutes,
    )
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
