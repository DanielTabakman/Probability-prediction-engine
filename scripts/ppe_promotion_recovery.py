"""Recover from relay exit 20/40 when BUILD succeeded but promotion or closeout stalled."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from scripts.ppe_manifest import clear_manifest_plan_path, load_manifest, maybe_mark_manifest_complete
from scripts.ppe_queue import mark_queue_item_done
from scripts.ppe_queue_health import repair_queue
from scripts.post_relay_continue import _find_newest_relay_run, _load_decision, _load_relay_result
from scripts.ppe_slice_worker_mode import infer_slice_kind
from scripts.relay.apply_control_closeout import (
    CloseoutSpec,
    apply_control_closeout,
    find_closeout_for_slice,
    load_phase_plan,
)


def _run(cmd: list[str], *, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=check)


def _relay_stop_condition(relay: dict | None) -> str:
    if not relay:
        return ""
    sc = relay.get("stop_condition")
    if isinstance(sc, dict):
        return str(sc.get("code") or sc.get("id") or "")
    return str(sc or "")


def _promotion_performed(relay: dict | None) -> bool:
    if not relay:
        return False
    promo = relay.get("promotion")
    return isinstance(promo, dict) and bool(promo.get("performed"))


def _build_branch_from_relay(relay: dict | None, fallback: str) -> str:
    if relay:
        branch = relay.get("build_branch") or relay.get("buildBranch")
        if branch:
            return str(branch)
    return fallback


def _gh_available() -> bool:
    try:
        proc = _run(["gh", "--version"], cwd=Path.cwd(), check=False)
        return proc.returncode == 0
    except FileNotFoundError:
        return False


def _open_pr_for_branch(repo: Path, branch: str, *, title: str, body: str) -> str | None:
    if not _gh_available():
        print("ppe_promotion_recovery: gh CLI not available; skip PR")
        return None
    existing = _run(
        ["gh", "pr", "list", "--head", branch, "--json", "url", "--limit", "1"],
        cwd=repo,
        check=False,
    )
    if existing.returncode == 0 and existing.stdout.strip():
        data = json.loads(existing.stdout)
        if data:
            return str(data[0].get("url") or "")
    proc = _run(
        [
            "gh",
            "pr",
            "create",
            "--base",
            "main",
            "--head",
            branch,
            "--title",
            title,
            "--body",
            body,
        ],
        cwd=repo,
        check=False,
    )
    if proc.returncode != 0:
        print(proc.stderr or proc.stdout)
        return None
    return (proc.stdout or "").strip()


def _wait_pr_merged(repo: Path, branch: str, *, timeout_s: int = 600) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        proc = _run(
            ["gh", "pr", "view", branch, "--json", "state", "--jq", ".state"],
            cwd=repo,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip() == "MERGED":
            return True
        time.sleep(15)
    return False


def _try_cherry_pick_pr(repo: Path, branch: str, commit: str, *, title: str) -> str | None:
    retry_branch = f"{branch}-retry"
    _run(["git", "fetch", "origin"], cwd=repo, check=False)
    _run(["git", "checkout", "-B", retry_branch, "origin/main"], cwd=repo, check=False)
    proc = _run(["git", "cherry-pick", commit], cwd=repo, check=False)
    if proc.returncode != 0:
        _run(["git", "cherry-pick", "--abort"], cwd=repo, check=False)
        return None
    _run(["git", "push", "-u", "origin", "HEAD"], cwd=repo, check=False)
    return _open_pr_for_branch(repo, retry_branch, title=title, body=f"Cherry-pick {commit} onto main after promotion drift.")


def _run_control_closeout(repo: Path, phase_plan: Path, slice_id: str, relay_run_dir: Path | None) -> int:
    plan = load_phase_plan(phase_plan)
    block = find_closeout_for_slice(plan, slice_id)
    if block is None:
        print(f"ppe_promotion_recovery: no closeout block for {slice_id}")
        return 0
    spec = CloseoutSpec.from_dict(block, slice_id)
    report = apply_control_closeout(repo, closeout=spec, relay_run_dir=relay_run_dir)
    if not report.get("passed"):
        print(f"ppe_promotion_recovery: closeout alignment failed: {report}")
        return 1
    subprocess.run(["git", "add", "-A", "docs/SOP"], cwd=repo, check=False)
    subprocess.run(
        ["git", "commit", "-m", f"control-closeout: {slice_id} (promotion recovery)"],
        cwd=repo,
        check=False,
    )
    if maybe_mark_manifest_complete(repo, phase_plan, slice_id):
        try:
            rel_plan = str(phase_plan.resolve().relative_to(repo)).replace("\\", "/")
        except ValueError:
            rel_plan = str(phase_plan)
        ok, reason = mark_queue_item_done(repo, plan_path=rel_plan)
        print(f"ppe_promotion_recovery: queue mark-done {ok!r} ({reason})")
        clear_manifest_plan_path(repo, note=f"Chapter closeout {slice_id} via promotion recovery.")
        try:
            from scripts.ppe_roadmap import maybe_advance_roadmap_and_select

            road = maybe_advance_roadmap_and_select(
                repo,
                closed_plan_path=rel_plan,
                apply=True,
            )
            print(f"ppe_promotion_recovery: roadmap advance {road}")
        except Exception as exc:
            print(f"ppe_promotion_recovery: roadmap advance skipped: {exc}")
    print(f"ppe_promotion_recovery: control-closeout OK for {slice_id}")
    try:
        from scripts.ppe_google_docs_refresh import run_google_docs_refresh

        gdocs_rc = run_google_docs_refresh(repo, write_report=True)
        if gdocs_rc != 0:
            print(f"ppe_promotion_recovery: google docs refresh failed ({gdocs_rc})")
    except Exception as exc:
        print(f"ppe_promotion_recovery: google docs refresh skipped: {exc}")
    try:
        from scripts.ppe_operator_git_sync import publish_ahead

        pub = publish_ahead(repo)
        print(f"ppe_promotion_recovery: git publish {json.dumps(pub)}")
    except Exception as exc:
        print(f"ppe_promotion_recovery: git publish skipped: {exc}")
    return 0


def _slice_obj(plan: dict, slice_id: str) -> dict | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and str(sl.get("sliceId") or "") == slice_id:
            return sl
    return None


def _build_branch_has_product_commits(
    repo: Path,
    *,
    build_branch: str,
    baseline_branch: str = "main",
) -> bool:
    if not build_branch.strip():
        return False
    proc = _run(
        ["git", "rev-list", "--count", f"origin/{baseline_branch}..{build_branch}"],
        cwd=repo,
        check=False,
    )
    if proc.returncode != 0:
        proc = _run(
            ["git", "rev-list", "--count", f"{baseline_branch}..{build_branch}"],
            cwd=repo,
            check=False,
        )
    if proc.returncode != 0:
        return False
    try:
        return int((proc.stdout or "0").strip() or "0") > 0
    except ValueError:
        return False


def _should_block_product_auto_resume(
    repo: Path,
    *,
    plan: dict,
    slice_id: str,
    stop: str,
    promoted: bool,
    build_branch: str,
    baseline_branch: str = "main",
    plan_path: str = "",
) -> bool:
    if stop != "SCOPE_AMBIGUITY":
        return False
    sl = _slice_obj(plan, slice_id)
    if infer_slice_kind(slice_id, sl) != "product":
        return False
    if promoted:
        return False
    norm_plan = plan_path.replace("\\", "/").strip() or str(plan.get("phasePlanPath") or "").replace("\\", "/")
    if norm_plan:
        from scripts.ppe_ide_product_ready import marker_covers_product_slices

        if marker_covers_product_slices(repo, plan_path=norm_plan, product_slice_ids=[slice_id]):
            return False
    plan_branch = str((sl or {}).get("buildBranch") or build_branch or "").strip()
    if _build_branch_has_product_commits(
        repo, build_branch=plan_branch or build_branch, baseline_branch=baseline_branch
    ):
        return False
    print(
        "ppe_promotion_recovery: product slice SCOPE_AMBIGUITY without promotion or "
        "build-branch commits — do not auto-resume; use IDE BUILD then run_ppe_local.cmd"
    )
    return True


def _next_slice_id(plan: dict, current: str) -> str | None:
    slices = plan.get("slices") or []
    ids = [str(s.get("sliceId") or "") for s in slices]
    if current not in ids:
        return None
    idx = ids.index(current)
    if idx + 1 >= len(ids):
        return None
    return ids[idx + 1]


def try_recover(
    repo: Path,
    *,
    exit_code: int,
    phase_plan: Path,
    slice_id: str,
    build_branch: str,
    relay_run_dir: Path | None = None,
) -> int:
    if exit_code == 0:
        return 0
    if exit_code not in (20, 40):
        print(f"ppe_promotion_recovery: exit {exit_code} not recoverable here")
        return 0

    fixes, remaining = repair_queue(repo, apply=True)
    if fixes:
        print(f"ppe_promotion_recovery: queue auto-repair {len(fixes)} fix(es)")
    if remaining:
        print(f"ppe_promotion_recovery: queue health {len(remaining)} issue(s) remain")

    run_dir = relay_run_dir.resolve() if relay_run_dir is not None else _find_newest_relay_run(repo)
    relay = _load_relay_result(run_dir) if run_dir else None
    decision = _load_decision(run_dir) if run_dir else None
    dec_val = (decision or {}).get("decision") if decision else None
    stop = _relay_stop_condition(relay)
    promoted = _promotion_performed(relay)
    branch = _build_branch_from_relay(relay, build_branch)

    print(
        f"ppe_promotion_recovery: exit={exit_code} slice={slice_id} "
        f"decision={dec_val!r} stop={stop!r} promoted={promoted} branch={branch}"
    )

    plan = load_phase_plan(phase_plan)
    closeout_block = find_closeout_for_slice(plan, slice_id)

    # After merge to main: run control-closeout for closeout slices.
    _run(["git", "fetch", "origin"], cwd=repo, check=False)
    head_proc = _run(["git", "rev-parse", "origin/main"], cwd=repo, check=False)
    on_main = head_proc.returncode == 0

    if closeout_block and on_main:
        plan_rel = str(phase_plan.relative_to(repo)).replace("\\", "/") if phase_plan.is_relative_to(repo) else str(phase_plan)
        try:
            from scripts.ppe_phase_plan_window import non_closeout_slices_pending

            pending = non_closeout_slices_pending(repo, plan_rel)
        except Exception:
            pending = []
        if pending:
            print(
                f"ppe_promotion_recovery: skip closeout {slice_id} — "
                f"non-closeout slices still pending: {pending}"
            )
        else:
            sha = relay.get("product_commit_sha") if relay else None
            if sha and sha not in (head_proc.stdout.strip(), "null", None):
                print(
                    f"ppe_promotion_recovery: main at {head_proc.stdout.strip()[:8]}; "
                    f"closeout commit {sha[:8]} may need PR"
                )
            return _run_control_closeout(repo, phase_plan, slice_id, run_dir)

    sl_obj = _slice_obj(plan, slice_id)
    sl_kind = infer_slice_kind(slice_id, sl_obj)
    if (
        not promoted
        and sl_kind == "product"
        and stop in ("REPO_STATE_DRIFT", "BASELINE_LOCKED")
    ):
        product_sha = ""
        if relay:
            product_sha = str(relay.get("product_commit_sha") or "")
        title = f"{slice_id}: promotion recovery"
        body = f"Auto-opened after relay exit {exit_code} ({stop or 'promotion blocked'})."
        url = _open_pr_for_branch(repo, branch, title=title, body=body)
        if not url and product_sha:
            url = _try_cherry_pick_pr(repo, branch, product_sha, title=title)
        if url:
            print(f"ppe_promotion_recovery: opened {url}")
            if _wait_pr_merged(repo, branch.split("/")[-1] if "/" in branch else branch):
                print("ppe_promotion_recovery: PR merged")
                _run(["git", "fetch", "origin"], cwd=repo, check=False)
                if closeout_block:
                    return _run_control_closeout(repo, phase_plan, slice_id, run_dir)
                nxt = _next_slice_id(plan, slice_id)
                if nxt:
                    print(f"ppe_promotion_recovery: resume with slice {nxt}")
                    return 100  # signal caller to run next slice
        return 0

    if exit_code == 20 and dec_val in ("STOP_FOR_REVIEW", "CONTINUE", None):
        baseline = str((relay or {}).get("baseline_branch") or "main")
        if _should_block_product_auto_resume(
            repo,
            plan=plan,
            slice_id=slice_id,
            stop=stop,
            promoted=promoted,
            build_branch=build_branch,
            baseline_branch=baseline,
            plan_path=str(phase_plan.relative_to(repo)).replace("\\", "/")
            if phase_plan.is_relative_to(repo)
            else str(phase_plan),
        ):
            return 0
        nxt = _next_slice_id(plan, slice_id)
        if nxt:
            print(f"ppe_promotion_recovery: suggest next slice {nxt} (exit 20 steward review)")
            return 100
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Recover from promotion/closeout stalls")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--phase-plan", type=Path, required=True)
    ap.add_argument("--slice-id", type=str, required=True)
    ap.add_argument("--build-branch", type=str, default="")
    ap.add_argument("--orchestrator-exit-code", type=int, required=True)
    ap.add_argument("--run-next-slice", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    rc = try_recover(
        repo,
        exit_code=args.orchestrator_exit_code,
        phase_plan=args.phase_plan.resolve(),
        slice_id=args.slice_id,
        build_branch=args.build_branch,
    )
    if rc == 100 and args.run_next_slice:
        plan = load_phase_plan(args.phase_plan.resolve())
        nxt = _next_slice_id(plan, args.slice_id)
        if not nxt:
            return 0
        manifest = load_manifest(repo)
        sprint = str(manifest.get("sprintSpecPath") or "")
        slice_cmd = repo / "run_slice.cmd"
        return subprocess.run(
            ["cmd", "/c", str(slice_cmd), nxt, sprint, "", str(args.phase_plan)],
            cwd=repo,
        ).returncode
    return 0 if rc in (0, 100) else rc


if __name__ == "__main__":
    raise SystemExit(main())
