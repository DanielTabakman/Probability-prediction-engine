"""Mark IDE product BUILD complete so local continuous guards allow the phase to run."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_manifest, load_phase_plan
from scripts.ppe_slice_worker_mode import infer_slice_kind

MARKER_REL = "artifacts/orchestrator/IDE_PRODUCT_READY.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def marker_path(repo: Path) -> Path:
    return (repo / MARKER_REL).resolve()


def load_marker(repo: Path) -> dict[str, Any] | None:
    p = marker_path(repo)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _branch_has_commits(repo: Path, *, build_branch: str, baseline: str = "main") -> bool:
    bb = (build_branch or "").strip()
    bl = (baseline or "main").strip()
    if bb == bl or bb == f"origin/{bl}":
        return True
    if not bb:
        return False
    for ref_pair in (f"origin/{baseline}..{build_branch}", f"{baseline}..{build_branch}"):
        proc = _git(repo, "rev-list", "--count", ref_pair)
        if proc.returncode == 0:
            try:
                if int((proc.stdout or "0").strip() or "0") > 0:
                    return True
            except ValueError:
                pass
    for base_ref in (bl, f"origin/{bl}"):
        anc = _git(repo, "merge-base", "--is-ancestor", bb, base_ref)
        if anc.returncode == 0:
            return True
    return False


def _product_touchset_on_main(repo: Path, *, slice_id: str, plan_path: str) -> bool:
    """True when slice touchSet paths exist on the current checkout (e.g. after squash merge to main)."""
    try:
        plan = load_phase_plan(repo, plan_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return False
    touch: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict) or str(sl.get("sliceId") or "") != slice_id:
            continue
        raw = sl.get("touchSet") or []
        if isinstance(raw, list):
            touch = [str(p).strip() for p in raw if str(p).strip()]
        break
    if not touch:
        return False
    return all((repo / p).exists() for p in touch)


def _resolve_slice_and_branch(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    build_branch: str | None,
) -> tuple[str, str, str]:
    plan = load_phase_plan(repo, plan_path)
    sl_obj: dict[str, Any] | None = None
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and str(sl.get("sliceId") or "") == slice_id:
            sl_obj = sl
            break
    if infer_slice_kind(slice_id, sl_obj) != "product":
        raise ValueError(f"{slice_id} is not a product slice")
    branch = (build_branch or "").strip()
    if not branch and sl_obj:
        branch = str(sl_obj.get("buildBranch") or "").strip()
    if not branch:
        branch = f"build/auto/{slice_id}-local"
    baseline = "main"
    if sl_obj:
        baseline = str(sl_obj.get("baselineBranch") or plan.get("baselineBranch") or "main").strip() or "main"
    return slice_id, branch, baseline


def write_marker(
    repo: Path,
    *,
    phase_plan_path: str,
    slice_id: str,
    build_branch: str,
    commit_sha: str,
    completed_product_slices: list[str] | None = None,
) -> Path:
    p = marker_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    norm_plan = phase_plan_path.replace("\\", "/").strip()
    if completed_product_slices is not None:
        completed = [str(s).strip() for s in completed_product_slices if str(s).strip()]
        if slice_id and slice_id not in completed:
            completed.append(slice_id)
    else:
        prior = load_marker(repo) or {}
        completed = []
        if str(prior.get("phasePlanPath") or "").replace("\\", "/").strip() == norm_plan:
            for sid in prior.get("completedProductSlices") or []:
                s = str(sid or "").strip()
                if s and s not in completed:
                    completed.append(s)
            legacy = str(prior.get("sliceId") or "").strip()
            if legacy and legacy not in completed:
                completed.append(legacy)
        if slice_id not in completed:
            completed.append(slice_id)
    payload = {
        "phasePlanPath": norm_plan,
        "sliceId": slice_id or (completed[-1] if completed else ""),
        "completedProductSlices": completed,
        "buildBranch": build_branch,
        "commitSha": commit_sha,
        "markedAt": _utc_now(),
    }
    p.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return p


def mark_product_slices_batch_ready(
    repo: Path,
    *,
    plan_path: str,
    slice_ids: list[str],
) -> tuple[int, str, list[str]]:
    """Atomically mark multiple product slices for one phase plan."""
    repo = repo.resolve()
    norm_plan = plan_path.replace("\\", "/").strip()
    from scripts.ppe_operator_guards import _plan_product_slice_ids

    product_order = _plan_product_slice_ids(repo, norm_plan)
    if not product_order:
        return 2, f"no product slices in plan {norm_plan}", []

    want = {str(s).strip() for s in slice_ids if str(s).strip()}
    ordered = [sid for sid in product_order if sid in want]
    if not ordered:
        return 2, "no valid product slice ids to mark", []

    build_branch = "main"
    baseline = "main"
    try:
        plan = load_phase_plan(repo, norm_plan)
        baseline = str(plan.get("baselineBranch") or "main").strip() or "main"
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    for sid in ordered:
        try:
            _, branch, bl = _resolve_slice_and_branch(
                repo, slice_id=sid, plan_path=norm_plan, build_branch=None
            )
        except ValueError as exc:
            return 2, str(exc), []
        if not _branch_has_commits(repo, build_branch=branch, baseline=bl):
            if not _product_touchset_on_main(repo, slice_id=sid, plan_path=norm_plan):
                return 2, f"build branch {branch!r} has no commits ahead of {bl} for {sid}", []

    head = _git(repo, "rev-parse", baseline)
    sha = (head.stdout or "").strip() if head.returncode == 0 else ""
    out = write_marker(
        repo,
        phase_plan_path=norm_plan,
        slice_id=ordered[-1],
        build_branch=build_branch,
        commit_sha=sha,
        completed_product_slices=ordered,
    )
    try:
        from scripts.ppe_ide_handoff import clear_cli_usage_exhausted

        clear_cli_usage_exhausted(repo)
    except ImportError:
        pass
    return 0, str(out), ordered


def mark_product_ready(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    build_branch: str | None = None,
) -> tuple[int, str]:
    repo = repo.resolve()
    norm_plan = plan_path.replace("\\", "/").strip()
    try:
        slice_id, branch, baseline = _resolve_slice_and_branch(
            repo, slice_id=slice_id, plan_path=norm_plan, build_branch=build_branch
        )
    except ValueError as e:
        return 2, str(e)

    if not _branch_has_commits(repo, build_branch=branch, baseline=baseline):
        if _product_touchset_on_main(repo, slice_id=slice_id, plan_path=norm_plan):
            branch = baseline
        else:
            return 2, f"build branch {branch!r} has no commits ahead of {baseline}; commit IDE BUILD first"

    head = _git(repo, "rev-parse", branch)
    sha = (head.stdout or "").strip() if head.returncode == 0 else ""
    out = write_marker(
        repo,
        phase_plan_path=norm_plan,
        slice_id=slice_id,
        build_branch=branch,
        commit_sha=sha,
    )
    try:
        from scripts.ppe_ide_handoff import clear_cli_usage_exhausted

        clear_cli_usage_exhausted(repo)
    except ImportError:
        pass
    try:
        from scripts.ppe_ide_build_automation_trigger import write_trigger_idle

        write_trigger_idle(repo, completed_slice=slice_id)
    except ImportError:
        pass
    try:
        from scripts.ppe_workflow_cost import record_ide_product_ready

        if record_ide_product_ready(repo, slice_id=slice_id):
            print(f"ppe_ide_product_ready: workflow cost recorded for {slice_id}")
    except Exception as exc:
        print(f"ppe_ide_product_ready: workflow cost skipped: {exc}")
    try:
        from scripts.ppe_worker_lease import maybe_release_lease_on_mark_ready

        lease_result = maybe_release_lease_on_mark_ready(
            repo, slice_id=slice_id, build_branch=branch
        )
        if lease_result.get("released"):
            print(
                f"ppe_ide_product_ready: released worker lease {lease_result.get('lease_id')!r}"
            )
    except Exception as exc:
        print(f"ppe_ide_product_ready: worker lease release skipped: {exc}")
    return 0, str(out)


def marker_covers_product_slices(
    repo: Path,
    *,
    plan_path: str,
    product_slice_ids: list[str],
) -> bool:
    """True when marker matches plan and covers every listed product slice."""
    if not product_slice_ids:
        return True
    data = load_marker(repo)
    if not data:
        return False
    norm_plan = plan_path.replace("\\", "/").strip()
    if str(data.get("phasePlanPath") or "").replace("\\", "/").strip() != norm_plan:
        return False
    branch = str(data.get("buildBranch") or "").strip()
    if not branch or not _branch_has_commits(repo, build_branch=branch):
        return False
    completed: set[str] = set()
    for sid in data.get("completedProductSlices") or []:
        s = str(sid or "").strip()
        if s:
            completed.add(s)
    legacy = str(data.get("sliceId") or "").strip()
    if legacy:
        completed.add(legacy)
    return all(sid in completed for sid in product_slice_ids)


def completed_product_slice_ids(repo: Path, *, plan_path: str) -> set[str]:
    """Product slices already marked ready for this phase plan."""
    norm_plan = plan_path.replace("\\", "/").strip()
    data = load_marker(repo)
    if not data:
        return set()
    if str(data.get("phasePlanPath") or "").replace("\\", "/").strip() != norm_plan:
        return set()
    completed: set[str] = set()
    for sid in data.get("completedProductSlices") or []:
        s = str(sid or "").strip()
        if s:
            completed.add(s)
    legacy = str(data.get("sliceId") or "").strip()
    if legacy:
        completed.add(legacy)
    return completed


def next_pending_product_slice(repo: Path, *, plan_path: str) -> str | None:
    """First plan-order product slice not yet in IDE_PRODUCT_READY marker."""
    from scripts.ppe_operator_guards import _plan_product_slice_ids

    product_ids = _plan_product_slice_ids(repo, plan_path)
    if not product_ids:
        return None
    completed = completed_product_slice_ids(repo, plan_path=plan_path)
    for sid in product_ids:
        if sid not in completed:
            return sid
    return None


def check_marker(repo: Path) -> int:
    repo = repo.resolve()
    data = load_marker(repo)
    if not data:
        print("ppe_ide_product_ready: no marker")
        return 1
    try:
        manifest = load_manifest(repo)
    except FileNotFoundError:
        print("ppe_ide_product_ready: marker present but no manifest")
        return 1
    plan_path = str(manifest.get("phasePlanPath") or data.get("phasePlanPath") or "").strip()
    if not plan_path:
        print(f"ppe_ide_product_ready: marker {json.dumps(data, indent=2)}")
        return 0
    product_ids = []
    plan = load_phase_plan(repo, plan_path)
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict):
            sid = str(sl.get("sliceId") or "").strip()
            if sid and infer_slice_kind(sid, sl) == "product":
                product_ids.append(sid)
    if marker_covers_product_slices(repo, plan_path=plan_path, product_slice_ids=product_ids):
        print(f"ppe_ide_product_ready: OK for {plan_path}")
        return 0
    print("ppe_ide_product_ready: marker stale or branch has no commits")
    return 1


def clear_marker(repo: Path) -> bool:
    p = marker_path(repo)
    if p.is_file():
        p.unlink()
        print(f"ppe_ide_product_ready: cleared {MARKER_REL}")
        try:
            from scripts.ppe_ide_build_starter import prune_starters_for_completed_chapters

            pruned = prune_starters_for_completed_chapters(repo)
            if pruned:
                print(f"ppe_ide_product_ready: pruned {len(pruned)} stale starter(s)")
        except Exception:
            pass
        return True
    return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="IDE product-ready marker for local operator")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--mark", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--clear", action="store_true")
    ap.add_argument("--slice-id", type=str, default="")
    ap.add_argument("--plan", type=str, default="")
    ap.add_argument("--build-branch", type=str, default="")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.clear:
        clear_marker(repo)
        return 0
    if args.check:
        return check_marker(repo)
    if args.mark:
        plan = args.plan.strip()
        if not plan:
            try:
                manifest = load_manifest(repo)
                plan = str(manifest.get("phasePlanPath") or "").strip()
            except FileNotFoundError:
                plan = ""
        if not plan:
            print("ERROR: --plan or manifest phasePlanPath required", file=sys.stderr)
            return 2
        if not args.slice_id.strip():
            print("ERROR: --slice-id required for --mark", file=sys.stderr)
            return 2
        rc, msg = mark_product_ready(
            repo,
            slice_id=args.slice_id.strip(),
            plan_path=plan,
            build_branch=args.build_branch.strip() or None,
        )
        if rc != 0:
            print(f"ERROR: {msg}", file=sys.stderr)
            return rc
        print(f"ppe_ide_product_ready: {msg}")
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
