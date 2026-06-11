"""Detached worker for remote agent jobs (survives short-lived parent scripts)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_remote_agent import notify_agent_done, run_agent


def _load_job(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("job file must be a JSON object")
    return data


def run_job(job: dict[str, Any]) -> dict[str, Any]:
    repo = Path(str(job["repo_root"])).resolve()
    prompt = str(job["prompt"])
    log_name = str(job.get("log_name") or "REMOTE_AGENT.log")
    log_path = repo / "artifacts" / "orchestrator" / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)

    result = run_agent(repo, prompt=prompt, log_path=log_path)

    if job.get("clear_build_lock"):
        from scripts.ppe_remote_build_agent import clear_build_lock

        clear_build_lock(repo)

    notify_ok = str(job.get("notify_ok_title") or "PPE agent finished")
    notify_fail = str(job.get("notify_fail_title") or "PPE agent failed")
    notify_agent_done(
        title_ok=notify_ok,
        title_fail=notify_fail,
        result=result,
        log_path=log_path,
    )
    if not result.get("ok"):
        from scripts.ppe_ide_handoff import maybe_handoff_after_cli_failure

        maybe_handoff_after_cli_failure(repo, job, result)
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run a detached PPE remote agent job")
    ap.add_argument("--job", type=Path, required=True, help="Path to job JSON file")
    ap.add_argument("--delete-job", action="store_true", help="Remove job file when finished")
    args = ap.parse_args(argv)

    job_path = args.job.resolve()
    if not job_path.is_file():
        print(f"ppe_remote_agent_worker: missing job file {job_path}", file=sys.stderr)
        return 1

    try:
        job = _load_job(job_path)
        result = run_job(job)
    except Exception as exc:
        print(f"ppe_remote_agent_worker: {exc}", file=sys.stderr)
        return 1
    finally:
        if args.delete_job and job_path.is_file():
            job_path.unlink(missing_ok=True)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
