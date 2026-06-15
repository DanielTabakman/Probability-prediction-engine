"""After orchestrator slice/phase exit 0: chain apply_control_closeout_v1 on CONTINUE."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.ppe_manifest import (
    clear_manifest_plan_path,
    load_manifest,
    maybe_mark_manifest_complete,
)
from scripts.ppe_queue import mark_queue_item_done
from scripts.ppe_queue_health import repair_queue, repair_roadmap
from scripts.relay.apply_control_closeout import find_closeout_for_slice, load_phase_plan


def _find_newest_relay_run(repo_root: Path) -> Path | None:
    candidates: list[Path] = []
    relay_runs = repo_root / "artifacts" / "relay" / "runs"
    if relay_runs.is_dir():
        candidates.extend(relay_runs.glob("*/relay_result.json"))
    wt = repo_root / "_worktrees" / "acp_orchestrator"
    if wt.is_dir():
        candidates.extend(wt.glob("*/artifacts/relay/runs/*/relay_result.json"))
    wt_local = repo_root / "_worktrees" / "orchestrator"
    if wt_local.is_dir():
        candidates.extend(wt_local.glob("*/artifacts/relay/runs/*/relay_result.json"))
    existing = [p.parent for p in candidates if p.is_file()]
    if not existing:
        return None
    return max(existing, key=lambda p: p.stat().st_mtime)


def _load_decision(run_dir: Path) -> dict | None:
    p = run_dir / "decision.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _load_relay_result(run_dir: Path) -> dict | None:
    p = run_dir / "relay_result.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8-sig"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Post-CONTINUE closeout hook")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--phase-plan", type=Path, required=True)
    parser.add_argument("--relay-run-dir", type=Path, default=None)
    parser.add_argument("--orchestrator-exit-code", type=int, default=0)
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if args.orchestrator_exit_code != 0:
        print(f"post_relay_continue: skip (orchestrator exit {args.orchestrator_exit_code})")
        return 0

    repo = args.repo_root.resolve()
    run_dir = args.relay_run_dir
    if run_dir is None:
        run_dir = _find_newest_relay_run(repo)
    if run_dir is None:
        print("post_relay_continue: no relay run found; skip")
        return 0

    decision = _load_decision(run_dir)
    relay = _load_relay_result(run_dir)
    if decision is None and relay is None:
        print(f"post_relay_continue: no artifacts in {run_dir}; skip")
        return 0

    dec_val = (decision or {}).get("decision")
    if dec_val != "CONTINUE":
        print(f"post_relay_continue: decision={dec_val!r}; skip closeout")
        return 0

    slice_id = (relay or {}).get("slice_id")
    if not slice_id:
        print("post_relay_continue: missing slice_id; skip")
        return 0

    plan = load_phase_plan(args.phase_plan.resolve())
    if find_closeout_for_slice(plan, slice_id) is None:
        print(f"post_relay_continue: slice {slice_id} has no closeout block; skip")
        return 0

    if args.dry_run:
        print(f"post_relay_continue: would run closeout for {slice_id}")
        return 0

    import os

    env = os.environ.copy()
    env["PYTHONPATH"] = str(repo)
    cmd = [
        sys.executable,
        str(repo / "scripts" / "relay_runtime_v0.py"),
        "--repo-root",
        str(repo),
        "stage",
        "apply_control_closeout_v1",
        "--phase-plan",
        str(args.phase_plan.resolve()),
        "--relay-run-dir",
        str(run_dir.resolve()),
        "--slice-id",
        slice_id,
    ]
    proc = subprocess.run(cmd, cwd=repo, env=env)
    if proc.returncode != 0:
        return proc.returncode

    chapter_closed = maybe_mark_manifest_complete(repo, args.phase_plan.resolve(), slice_id)

    if chapter_closed:
        try:
            from scripts.ppe_dev_changelog import append_chapter_closed_event

            append_chapter_closed_event(
                repo,
                slice_id=slice_id,
                phase_plan=args.phase_plan.resolve(),
            )
        except Exception as exc:
            print(f"post_relay_continue: dev changelog event skipped: {exc}")

    if args.commit:
        subprocess.run(["git", "add", "-A", "docs/SOP", "docs/RELEASES"], cwd=repo, check=False)
        msg = f"control-closeout: {slice_id}"
        subprocess.run(["git", "commit", "-m", msg], cwd=repo, check=False)

    if chapter_closed:
        try:
            from scripts.ppe_phase_plan_window import clear_progress

            clear_progress(repo, str(args.phase_plan.resolve().relative_to(repo)).replace("\\", "/"))
        except Exception:
            pass
        print(f"post_relay_continue: manifest status -> COMPLETE ({slice_id})")
        try:
            plan_rel = str(args.phase_plan.resolve().relative_to(repo)).replace("\\", "/")
        except ValueError:
            plan_rel = ""
        try:
            rel_manifest_plan = str(load_manifest(repo).get("phasePlanPath") or "").replace("\\", "/")
        except Exception:
            rel_manifest_plan = plan_rel
        queue_plan = rel_manifest_plan or plan_rel
        prop: dict = {}
        prom: dict = {}
        road: dict = {}
        ok, qreason = mark_queue_item_done(repo, plan_path=queue_plan)
        print(f"post_relay_continue: queue mark-done {ok!r} ({qreason})")
        clear_manifest_plan_path(
            repo,
            note=f"Chapter closeout {slice_id}; queue item marked DONE.",
        )
        print("post_relay_continue: cleared manifest phasePlanPath")
        roadmap_fixes, roadmap_remaining = repair_roadmap(repo, apply=True)
        if roadmap_fixes:
            print(f"post_relay_continue: roadmap auto-repair {len(roadmap_fixes)} fix(es)")
        if roadmap_remaining:
            print(f"post_relay_continue: roadmap health {len(roadmap_remaining)} issue(s): {roadmap_remaining}")
        fixes, remaining = repair_queue(repo, apply=True)
        if fixes:
            print(f"post_relay_continue: queue auto-repair {len(fixes)} fix(es)")
        if remaining:
            print(f"post_relay_continue: queue health {len(remaining)} issue(s): {remaining}")
        try:
            from scripts.ppe_propagate_queue import (
                maybe_propagate_queue,
                promote_first_blocked_with_plan,
                reconcile_closed_chapters,
            )

            recon = reconcile_closed_chapters(repo, apply=True)
            print(f"post_relay_continue: backlog reconcile {json.dumps(recon)}")
            prom = promote_first_blocked_with_plan(repo, apply=True)
            print(f"post_relay_continue: backlog promote {json.dumps(prom)}")
            prop = maybe_propagate_queue(repo, apply=True)
            print(f"post_relay_continue: backlog propagate {json.dumps(prop)}")
        except Exception as exc:
            print(f"post_relay_continue: backlog promote/propagate skipped: {exc}")
            prop = {}
            prom = {}
        try:
            from scripts.ppe_roadmap import maybe_advance_roadmap_and_select

            road = maybe_advance_roadmap_and_select(
                repo,
                closed_plan_path=queue_plan,
                apply=True,
            )
            print(f"post_relay_continue: roadmap advance {json.dumps(road)}")
        except Exception as exc:
            print(f"post_relay_continue: roadmap advance skipped: {exc}")
            road = {}
        try:
            from scripts.ppe_progress_notify import notify_chapter_complete

            closeout = find_closeout_for_slice(plan, slice_id) or {}
            chapter_id = str(closeout.get("chapterId") or slice_id).strip()
            next_chapter = ""
            if isinstance(prop, dict):
                next_chapter = str(prop.get("chapterId") or "").strip()
            if not next_chapter and isinstance(prom, dict):
                next_chapter = str(prom.get("chapterId") or "").strip()
            adv = (road or {}).get("advance") or {}
            if not next_chapter:
                next_chapter = str(adv.get("nextPlan") or "").split("/")[-1].replace("_relay.json", "")
            notify_chapter_complete(
                chapter_id,
                slice_id=slice_id,
                plan_path=queue_plan,
                next_chapter=next_chapter,
            )
            if not next_chapter:
                from scripts.ppe_progress_notify import notify_pipeline_idle
                from scripts.ppe_queue import load_queue

                manifest = load_manifest(repo)
                plan_active = bool(str(manifest.get("phasePlanPath") or "").strip())
                queue = load_queue(repo)
                ready = any(
                    isinstance(item, dict) and str(item.get("status") or "").upper() == "READY"
                    for item in (queue.get("items") or [])
                )
                if not plan_active and not ready:
                    notify_pipeline_idle(last_chapter=chapter_id)
        except Exception as exc:
            print(f"post_relay_continue: progress notify skipped: {exc}")

    print(f"post_relay_continue: closeout OK for {slice_id}")
    try:
        from scripts.ppe_google_docs_refresh import run_google_docs_refresh

        gdocs_rc = run_google_docs_refresh(repo, write_report=True)
        if gdocs_rc != 0:
            print(f"post_relay_continue: google docs refresh failed ({gdocs_rc}); continuing")
    except Exception as exc:
        print(f"post_relay_continue: google docs refresh skipped: {exc}")
    try:
        from scripts.ppe_operator_git_sync import publish_ahead

        pub = publish_ahead(repo)
        print(f"post_relay_continue: git publish {json.dumps(pub)}")
    except Exception as exc:
        print(f"post_relay_continue: git publish skipped: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
