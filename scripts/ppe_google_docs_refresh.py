"""Best-effort MSOS mirror refresh after chapter closeout (see GOOGLE_DOCS_CONTROL_PLANE_V1.md)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_google_docs_refresh(repo: Path, *, write_report: bool = True) -> int:
    """Regenerate repo-truth snapshot and push marker block to Live Mirror doc."""
    repo = repo.resolve()
    sync = subprocess.run(
        [sys.executable, str(repo / "scripts" / "sync_msos_repo_truth.py")],
        cwd=repo,
    )
    if sync.returncode != 0:
        print(f"ppe_google_docs_refresh: sync_msos_repo_truth failed ({sync.returncode})")
        return sync.returncode

    cmd = [
        sys.executable,
        str(repo / "scripts" / "google_docs_sync.py"),
        "--sync-repo-to-mirror",
    ]
    if write_report:
        cmd.append("--write-report")
    gsync = subprocess.run(cmd, cwd=repo)
    if gsync.returncode != 0:
        print(f"ppe_google_docs_refresh: google_docs_sync failed ({gsync.returncode})")
        return gsync.returncode
    print("ppe_google_docs_refresh: OK (repo truth -> Live Mirror)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Refresh MSOS Live Mirror Google Doc from repo truth")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--no-report", action="store_true")
    args = ap.parse_args(argv)
    return run_google_docs_refresh(args.repo_root, write_report=not args.no_report)


if __name__ == "__main__":
    raise SystemExit(main())
