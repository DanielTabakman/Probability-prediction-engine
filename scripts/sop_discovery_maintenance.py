#!/usr/bin/env python3
"""One-shot SOP discovery maintenance (backfill + READY starter regen)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.sop_discovery_core import (  # noqa: E402
    assess_sop_discovery_health,
    backfill_evidence_front_matter,
    plan_evidence_front_matter_backfill,
    refresh_sop_discovery_artifacts,
    repair_active_evidence_front_matter,
)
from scripts.ppe_ide_build_starter import (  # noqa: E402
    plan_regen_ready_starters,
    regenerate_starters_for_ready_queue,
)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="SOP discovery maintenance (backfill + regen)")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", action="store_true", help="Write changes (default is dry-run plan)")
    ap.add_argument("--evidence-backfill", action="store_true", help="Stamp archived YAML on evidence docs")
    ap.add_argument("--regen-ready-starters", action="store_true", help="Regen IDE BUILD starters for READY queue")
    ap.add_argument("--refresh-index", action="store_true", help="Regenerate CHAPTER_DOC_INDEX + archive catalog")
    ap.add_argument("--repair-active-evidence", action="store_true", help="Strip archived YAML from active queue rows")
    ap.add_argument(
        "--all",
        action="store_true",
        help="Run repair + evidence backfill + READY starter regen + index refresh",
    )
    ap.add_argument("--status", action="store_true", help="Print assess_sop_discovery_health only")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.status:
        report = assess_sop_discovery_health(repo)
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print("SOP discovery health:", "OK" if report.get("ok") else "WARN")
            for key in (
                "index_fresh_detail",
                "link_error_count",
                "evidence_backfill_pending",
                "ready_starter_regen_pending",
            ):
                if report.get(key) is not None:
                    print(f"  {key}: {report[key]}")
        return 0 if report.get("ok") else 1

    run_repair = args.all or args.repair_active_evidence
    run_evidence = args.all or args.evidence_backfill
    run_starters = args.all or args.regen_ready_starters
    run_refresh = args.all or args.refresh_index
    if not (run_repair or run_evidence or run_starters or run_refresh):
        ap.error(
            "Specify --all, --status, or one of --repair-active-evidence / "
            "--evidence-backfill / --regen-ready-starters / --refresh-index"
        )

    out: dict[str, object] = {"applied": args.apply}
    if run_repair:
        if args.apply:
            out["repair_active_evidence"] = repair_active_evidence_front_matter(repo, apply=True)
        else:
            from scripts.sop_discovery_core import plan_repair_active_evidence_front_matter

            out["repair_active_evidence"] = plan_repair_active_evidence_front_matter(repo)
    if run_evidence:
        if args.apply:
            out["evidence_backfill"] = backfill_evidence_front_matter(repo, apply=True)
        else:
            out["evidence_backfill"] = plan_evidence_front_matter_backfill(repo)
    if run_starters:
        if args.apply:
            out["ready_starters"] = regenerate_starters_for_ready_queue(repo)
        else:
            out["ready_starters"] = plan_regen_ready_starters(repo)
    if run_refresh:
        if args.apply:
            out["index_refresh"] = refresh_sop_discovery_artifacts(repo)
        else:
            from scripts.sop_discovery_core import chapter_doc_index_fresh

            fresh, detail = chapter_doc_index_fresh(repo)
            out["index_refresh"] = {"would_refresh": not fresh, "detail": detail}

    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        if run_repair:
            block = out.get("repair_active_evidence") or {}
            if args.apply:
                print(f"repair active evidence: {block.get('repaired_count', 0)} unstamped")
            else:
                print(f"repair active evidence: pending {block.get('pending_count', 0)} (dry-run)")
        if run_evidence:
            block = out.get("evidence_backfill") or {}
            if args.apply:
                print(f"evidence backfill: stamped {block.get('stamped_count', 0)}")
            else:
                print(f"evidence backfill: pending {block.get('pending_count', 0)} (dry-run)")
        if run_starters:
            block = out.get("ready_starters") or {}
            if args.apply:
                plans = block if isinstance(block, dict) else {}
                print(f"READY starters: regen {len(plans)} plan(s)")
            else:
                print(f"READY starters: pending {block.get('pending_count', 0)} (dry-run)")
        if run_refresh:
            block = out.get("index_refresh") or {}
            if args.apply:
                print(
                    "index refresh: "
                    f"{block.get('active_chapter_count')} active / "
                    f"{block.get('archived_chapter_count')} archived"
                )
            else:
                print(f"index refresh: {block.get('detail')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
