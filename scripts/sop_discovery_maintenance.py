#!/usr/bin/env python3
"""One-shot SOP discovery + chapter coordination maintenance."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_chapter_coordination import (  # noqa: E402
    assess_chapter_coordination_health,
    plan_coordination_repair,
    repair_repo_coordination,
)
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
    ap = argparse.ArgumentParser(description="SOP discovery + chapter coordination maintenance")
    ap.add_argument("--repo-root", type=Path, default=_REPO)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", action="store_true", help="Write changes (default is dry-run plan)")
    ap.add_argument("--coordination-repair", action="store_true", help="Repair IDE markers + closeout registry desync")
    ap.add_argument("--evidence-backfill", action="store_true", help="Stamp archived YAML on evidence docs")
    ap.add_argument("--regen-ready-starters", action="store_true", help="Regen IDE BUILD starters for READY queue")
    ap.add_argument("--refresh-index", action="store_true", help="Regenerate CHAPTER_DOC_INDEX + archive catalog")
    ap.add_argument("--repair-active-evidence", action="store_true", help="Strip archived YAML from active queue rows")
    ap.add_argument(
        "--all",
        action="store_true",
        help="Run coordination repair + SOP discovery maintenance (repair, backfill, starters, index)",
    )
    ap.add_argument("--status", action="store_true", help="Print maintenance health (SOP + coordination)")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.status:
        sop = assess_sop_discovery_health(repo)
        coord = assess_chapter_coordination_health(repo)
        report = {"sop_discovery": sop, "chapter_coordination": coord, "ok": bool(sop.get("ok") and coord.get("ok"))}
        if args.json:
            print(json.dumps(report, indent=2, sort_keys=True))
        else:
            print("Maintenance health:", "OK" if report["ok"] else "WARN")
            print("  SOP discovery:", "OK" if sop.get("ok") else "WARN")
            if not sop.get("ok"):
                for key in (
                    "index_fresh_detail",
                    "link_error_count",
                    "evidence_backfill_pending",
                    "ready_starter_regen_pending",
                ):
                    if sop.get(key) is not None:
                        print(f"    {key}: {sop[key]}")
            print("  Chapter coordination:", "OK" if coord.get("ok") else "WARN")
            if not coord.get("ok"):
                top = coord.get("top_issue") if isinstance(coord.get("top_issue"), dict) else {}
                if top.get("message"):
                    print(f"    top: {top['message']}")
                print(f"    repairable_plans: {coord.get('repairable_plan_count')}")
        return 0 if report["ok"] else 1

    run_coord = args.all or args.coordination_repair
    run_repair = args.all or args.repair_active_evidence
    run_evidence = args.all or args.evidence_backfill
    run_starters = args.all or args.regen_ready_starters
    run_refresh = args.all or args.refresh_index
    if not (run_coord or run_repair or run_evidence or run_starters or run_refresh):
        ap.error(
            "Specify --all, --status, --coordination-repair, or one of "
            "--repair-active-evidence / --evidence-backfill / --regen-ready-starters / --refresh-index"
        )

    out: dict[str, object] = {"applied": args.apply}
    if run_coord:
        if args.apply:
            out["coordination_repair"] = repair_repo_coordination(repo, apply=True)
        else:
            out["coordination_repair"] = plan_coordination_repair(repo)
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
        if run_coord:
            block = out.get("coordination_repair") or {}
            if args.apply:
                print(
                    f"coordination repair: {block.get('fix_count', 0)} fix(es), "
                    f"{block.get('remaining_count', 0)} remaining"
                )
            else:
                print(
                    f"coordination repair: {block.get('repairable_plan_count', 0)} plan(s) "
                    f"({block.get('issue_count', 0)} issues, dry-run)"
                )
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
