"""Run chapter-level queue: mechanical SELECTION + run_ppe.cmd."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import queue_cycle as qc


def _run_ppe(repo: Path, plan_rel: str, *, dry_run_invoke: bool = False) -> int:
    if dry_run_invoke:
        print(f"run_queue_cycle: would run run_ppe.cmd --plan {plan_rel}")
        return 0
    cmd = ["cmd", "/c", str(repo / "run_ppe.cmd"), "--plan", plan_rel]
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = str(repo)
    print(f"run_queue_cycle: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=repo, env=env).returncode


def _process_one_chapter(
    repo: Path,
    *,
    queue_rel: str,
    dry_run: bool,
) -> tuple[int, bool]:
    """
    Process one PENDING chapter.
    Returns (exit_code, should_continue_loop).
    should_continue_loop is False on hard stop or empty queue.
    """
    pre_errors = qc.preflight_cycle(repo)
    if pre_errors:
        for e in pre_errors:
            print(f"run_queue_cycle: ERROR: {e}", file=sys.stderr)
        return 2, False

    queue = qc.load_queue(repo, queue_rel)
    item = qc.pick_next_pending(queue)
    if item is None:
        print("run_queue_cycle: no PENDING chapters in queue")
        return 0, False

    queue_id = str(item["queueId"])
    val_errors = qc.validate_queue_item(item, repo_root=repo)
    if val_errors:
        print(f"run_queue_cycle: queue item {queue_id} invalid:", file=sys.stderr)
        for e in val_errors:
            print(f"  - {e}", file=sys.stderr)
        if not dry_run:
            qc.set_item_status(repo, queue_id, "BLOCKED", queue_rel=queue_rel)
        return 1, False

    if dry_run:
        plan = qc.build_phase_plan_from_item(item, repo)
        print(f"run_queue_cycle: dry-run select queueId={queue_id}")
        print(f"  chapterId={item.get('chapterId')}")
        print(f"  slices={len(plan.get('slices') or [])}")
        print(f"  phasePlanName={plan.get('name')}")
        return 0, False

    plan_abs, plan_rel = qc.write_generated_phase_plan(repo, item)
    print(f"run_queue_cycle: wrote phase plan {plan_rel}")

    qc.write_manifest_for_item(repo, item, plan_rel)
    qc.set_item_status(repo, queue_id, "RUNNING", queue_rel=queue_rel)

    exit_code = _run_ppe(repo, plan_rel)

    final_status, reason = qc.classify_chapter_outcome(
        repo, wrapper_exit_code=exit_code, plan_rel=plan_rel
    )
    qc.set_item_status(repo, queue_id, final_status, queue_rel=queue_rel)
    print(f"run_queue_cycle: queueId={queue_id} -> {final_status} ({reason})")

    if final_status == "BLOCKED":
        return exit_code if exit_code != 0 else 1, False
    return exit_code, True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Chapter queue cycle runner")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--queue", default=qc.QUEUE_REL, help="Repo-relative queue JSON path")
    ap.add_argument("--max-chapters", type=int, default=1, metavar="N")
    ap.add_argument("--continuous", action="store_true", help="Loop until max-chapters or stop")
    ap.add_argument("--sleep-seconds", type=int, default=60, help="Sleep when queue empty (continuous)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.max_chapters < 1:
        print("run_queue_cycle: --max-chapters must be >= 1", file=sys.stderr)
        return 2

    chapters_done = 0
    last_code = 0

    while chapters_done < args.max_chapters:
        if not args.dry_run and qc.pick_next_pending(qc.load_queue(repo, args.queue)) is None:
            if args.continuous and chapters_done == 0:
                print(
                    f"run_queue_cycle: queue empty; sleeping {args.sleep_seconds}s "
                    "(continuous mode)"
                )
                time.sleep(max(0, args.sleep_seconds))
                if qc.pick_next_pending(qc.load_queue(repo, args.queue)) is None:
                    print("run_queue_cycle: still no PENDING chapters; exit 0")
                    return 0
            else:
                if chapters_done == 0:
                    print("run_queue_cycle: no PENDING chapters in queue")
                break

        code, should_continue = _process_one_chapter(
            repo, queue_rel=args.queue, dry_run=args.dry_run
        )
        last_code = code

        if args.dry_run:
            return code

        if code != 0 or not should_continue:
            return code if code != 0 else last_code

        chapters_done += 1
        if chapters_done >= args.max_chapters:
            break
        if not args.continuous:
            break

    print(f"run_queue_cycle: completed {chapters_done} chapter(s)")
    return last_code


if __name__ == "__main__":
    raise SystemExit(main())
