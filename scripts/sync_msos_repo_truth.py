"""
Generate the repo-grounded MSOS mirror snapshot artifacts.

This script is intentionally local-only: it does NOT push to Google Docs.
Cursor agents push the generated marker block into the Google Doc using the
google-docs MCP tools (see docs/SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md).

Outputs (default):
  - artifacts/msos_repo_truth_snapshot.md
  - artifacts/control_plane/msos_sync_report.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _ensure_parent(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate MSOS repo-truth mirror snapshot artifacts")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument(
        "--snapshot-out",
        type=Path,
        default=None,
        help="Path to write snapshot markdown (default artifacts/msos_repo_truth_snapshot.md)",
    )
    ap.add_argument(
        "--report-out",
        type=Path,
        default=None,
        help="Path to write JSON report (default artifacts/control_plane/msos_sync_report.json)",
    )
    ap.add_argument("--print", action="store_true", help="Also print the snapshot to stdout")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    # Ensure `import scripts.*` works when invoked as `python scripts/foo.py`.
    sys.path.insert(0, str(repo))
    from scripts.msos.repo_truth_snapshot import build_repo_truth_snapshot  # noqa: PLC0415

    snapshot_out = args.snapshot_out or (repo / "artifacts" / "msos_repo_truth_snapshot.md")
    report_out = args.report_out or (repo / "artifacts" / "control_plane" / "msos_sync_report.json")

    snap = build_repo_truth_snapshot(repo_root=repo)

    _ensure_parent(snapshot_out)
    snapshot_out.write_text(snap.snapshot_markdown, encoding="utf-8")

    report = {
        "ok": True,
        "generated_at_utc": snap.generated_at_utc,
        "branch": snap.branch,
        "head": snap.head,
        "working_tree_clean": snap.working_tree_clean,
        "snapshot_path": str(snapshot_out.as_posix()),
        "report_path": str(report_out.as_posix()),
        "next_selection_rel": snap.continuity_next_selection_rel,
    }

    _ensure_parent(report_out)
    report_out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.print:
        print(snap.snapshot_markdown)

    print(f"sync_msos_repo_truth: wrote {snapshot_out}")
    print(f"sync_msos_repo_truth: wrote {report_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

