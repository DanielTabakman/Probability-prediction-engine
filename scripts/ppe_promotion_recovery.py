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
    print(f"ppe_promotion_recovery: control-closeout OK for {slice_id}")
    try:
        from scripts.ppe_google_docs_refresh import run_google_docs_refresh

        gdocs_rc = run_google_docs_refresh(repo, write_report=True)
        if gdocs_rc != 0:
            print(f"ppe_promotion_recovery: google docs refresh failed ({gdocs_rc})")
    except Exception as exc:
        print(f"ppe_promotion_recovery: google docs refresh skipped: {exc}")
    return 0


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

    run_dir = _find_newest_relay_run(repo)
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
        sha = relay.get("product_commit_sha") if relay else None
        if sha and sha not in (head_proc.stdout.strip(), "null", None):
            print(f"ppe_promotion_recovery: main at {head_proc.stdout.strip()[:8]}; closeout commit {sha[:8]} may need PR")
        return _run_control_closeout(repo, phase_plan, slice_id, run_dir)

    if not promoted and stop in ("REPO_STATE_DRIFT", "BASELINE_LOCKED", ""):
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
