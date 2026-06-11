"""Detached worker: mark IDE product ready + run_ppe_local after commit detected."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.ppe_ide_product_ready import mark_product_ready
from scripts.ppe_notify_push import OUTBOUND_TAG, ntfy_configured, notify_enabled, send_ntfy
from scripts.ppe_post_build_watcher import _utc_now, load_state, save_state, state_path
from scripts.ppe_remote_build_agent import clear_build_lock


def _notify(*, title: str, body: str) -> None:
    if notify_enabled() and ntfy_configured():
        send_ntfy(title, body, tags=["ppe", "finish", OUTBOUND_TAG], priority="default")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Finish IDE build: mark + run_ppe_local")
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--delete-job", action="store_true")
    args = ap.parse_args(argv)

    job_path = args.job.resolve()
    ok = False
    repo: Path | None = None
    slice_id = ""
    try:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        repo = Path(str(job["repo_root"])).resolve()
        log_path = Path(str(job.get("log_path") or repo / "artifacts/orchestrator/POST_BUILD_FINISH.log"))
        slice_id = str(job["slice_id"])
        plan_path = str(job["plan_path"])
        sha = str(job.get("commit_sha") or "")

        lines: list[str] = [f"post_build_finish worker start slice={slice_id}\n"]
        rc_mark, msg_mark = mark_product_ready(repo, slice_id=slice_id, plan_path=plan_path)
        lines.append(f"mark: rc={rc_mark} {msg_mark}\n")
        if rc_mark != 0:
            log_path.write_text("".join(lines), encoding="utf-8")
            _notify(title=f"PPE finish failed: {slice_id}", body=msg_mark)
            return 1

        proc = subprocess.run(
            ["cmd", "/c", "run_ppe_local.cmd"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        lines.append(proc.stdout or "")
        lines.append(proc.stderr or "")
        lines.append(f"\nrun_ppe_local exit={proc.returncode}\n")
        log_path.write_text("".join(lines), encoding="utf-8")
        ok = proc.returncode == 0

        state = load_state(repo)
        state.pop("worker_pid", None)
        last_key = f"{plan_path}::{slice_id}"
        last_finished = dict(state.get("last_finished") or {})
        last_finished[last_key] = {
            "commit_sha": sha,
            "finished_at": _utc_now(),
            "ok": ok,
        }
        state["last_finished"] = last_finished
        save_state(repo, state)
        clear_build_lock(repo)

        if ok:
            _notify(
                title=f"PPE finish OK: {slice_id}",
                body=f"Marked ready and run_ppe_local succeeded ({sha[:8]}).",
            )
        else:
            _notify(
                title=f"PPE finish failed: {slice_id}",
                body=f"run_ppe_local exit {proc.returncode} — see {log_path.name}",
            )
    finally:
        if repo is not None and state_path(repo).is_file():
            state = load_state(repo)
            if state.get("worker_pid") is not None:
                state.pop("worker_pid", None)
                save_state(repo, state)
        if args.delete_job and job_path.is_file():
            job_path.unlink(missing_ok=True)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
