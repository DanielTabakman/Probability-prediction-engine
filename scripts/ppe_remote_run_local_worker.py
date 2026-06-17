"""Detached worker for run_ppe_local.cmd."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.ppe_remote_agent import notify_agent_done


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run run_ppe_local.cmd in a detached worker")
    ap.add_argument("--job", type=Path, required=True)
    ap.add_argument("--delete-job", action="store_true")
    args = ap.parse_args(argv)

    job_path = args.job.resolve()
    result: dict = {"ok": False, "reason": "worker failed"}
    repo: Path | None = None
    try:
        job = json.loads(job_path.read_text(encoding="utf-8"))
        repo = Path(str(job["repo_root"])).resolve()
        log_path = Path(str(job.get("log_path") or repo / "artifacts/orchestrator/REMOTE_RUN_LOCAL.log"))
        proc = subprocess.run(
            ["cmd", "/c", "run_ppe_local.cmd"],
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        log_path.write_text((proc.stdout or "") + "\n" + (proc.stderr or ""), encoding="utf-8")
        result = {"ok": proc.returncode == 0, "exit_code": proc.returncode}
        notify_agent_done(
            title_ok="PPE run_local finished",
            title_fail="PPE run_local failed",
            result=result,
            log_path=log_path,
        )
    finally:
        if repo is not None:
            lock = repo / "artifacts" / "orchestrator" / "REMOTE_RUN_LOCAL_LOCK.json"
            lock.unlink(missing_ok=True)
        if args.delete_job and job_path.is_file():
            job_path.unlink(missing_ok=True)

    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
