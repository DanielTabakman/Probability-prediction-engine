"""Chapter coordination audit — detect factory/steering desync (product-on-main, markers, queue)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_chapter_mode import plan_chapter_id, product_slices_on_main
from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_queue import load_queue
from scripts.ppe_queue_health import chapter_marked_complete_in_repo

COORDINATION_DOC = "docs/SOP/CHAPTER_COORDINATION_V1.md"
STEERING_REL = "docs/SOP/AGENT_STEERING_V1.json"
FRONTIER_REL = "docs/SOP/MSOS_FRONTIER.md"
MARKER_REL = "artifacts/orchestrator/IDE_PRODUCT_READY.json"

# Changes to these paths can desync factory layers — gate warns after commit.
COORDINATION_SENSITIVE_PREFIXES = (
    "docs/SOP/PHASE_QUEUE.json",
    "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
    "docs/SOP/AGENT_STEERING_V1.json",
    "docs/SOP/MSOS_FRONTIER.md",
    "docs/SOP/PHASE_PLANS/",
    "artifacts/orchestrator/IDE_PRODUCT_READY.json",
    "apps/msos-web/",
    "apps/msos-web\\",
)

Issue = dict[str, Any]
Fix = dict[str, Any]


def _norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _load_steering(repo: Path) -> dict[str, Any]:
    path = repo / STEERING_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def _closeout_registry_ids(repo: Path) -> set[str]:
    raw = _load_steering(repo).get("closeoutOnlyChapterIds") or []
    if not isinstance(raw, list):
        return set()
    return {str(x).strip() for x in raw if str(x).strip()}


def _active_manifest_plan_path(repo: Path) -> str:
    try:
        from scripts.ppe_manifest import load_manifest

        return _norm_plan(str(load_manifest(repo).get("phasePlanPath") or ""))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ""


def _marker_required_for_chapter(
    repo: Path,
    *,
    plan_path: str,
    chapter_id: str,
    registry: set[str],
    on_main: bool,
    missing_marker: list[str],
) -> bool:
    """IDE_PRODUCT_READY is a single active-plan marker — skip stale checks for closeout registry rows."""
    if not on_main or not missing_marker:
        return False
    if chapter_id not in registry:
        return True
    return _norm_plan(plan_path) == _active_manifest_plan_path(repo)


def _frontier_claims_chapter_complete(repo: Path, chapter_id: str) -> bool:
    path = repo / FRONTIER_REL
    if not path.is_file() or not chapter_id:
        return False
    body = path.read_text(encoding="utf-8", errors="replace")
    title_token = chapter_id.replace("_", " ").lower()
    # Section header like: ### MSOS storyboard visual parity v1 — relay queue — **COMPLETE**
    header_patterns = (
        re.compile(
            rf"^###[^\n]*{re.escape(title_token)}[^\n]*\*\*COMPLETE\*\*",
            re.I | re.M,
        ),
        re.compile(
            rf"^###[^\n]*`{re.escape(chapter_id)}`[^\n]*\*\*COMPLETE\*\*",
            re.I | re.M,
        ),
    )
    return any(p.search(body) for p in header_patterns)


def _product_slice_ids(repo: Path, plan_path: str) -> list[str]:
    from scripts.ppe_operator_guards import _plan_product_slice_ids

    return _plan_product_slice_ids(repo, plan_path)


def _marker_missing_slices(repo: Path, plan_path: str) -> list[str]:
    from scripts.ppe_ide_product_ready import completed_product_slice_ids

    product_ids = _product_slice_ids(repo, plan_path)
    if not product_ids:
        return []
    completed = completed_product_slice_ids(repo, plan_path=plan_path)
    return [sid for sid in product_ids if sid not in completed]


def paths_touch_coordination(paths: list[str]) -> bool:
    """True when a change set may desync queue, markers, frontier, or evidence."""
    for raw in paths:
        norm = raw.replace("\\", "/")
        for prefix in COORDINATION_SENSITIVE_PREFIXES:
            p = prefix.replace("\\", "/")
            if norm == p or norm.startswith(p):
                return True
        if norm.endswith("_EVIDENCE_STATUS.md") and "/docs/SOP/" in f"/{norm}":
            return True
    return False


def audit_chapter(repo: Path, plan_path: str) -> list[Issue]:
    """Return coordination issues for one relay plan."""
    repo = repo.resolve()
    norm = _norm_plan(plan_path)
    if not norm:
        return []

    issues: list[Issue] = []
    chapter_id = plan_chapter_id(norm)
    on_main = product_slices_on_main(repo, norm)
    missing_marker = _marker_missing_slices(repo, norm)
    registry = _closeout_registry_ids(repo)
    evidence_complete = chapter_marked_complete_in_repo(repo, norm)
    frontier_complete = _frontier_claims_chapter_complete(repo, chapter_id)

    queue = load_queue(repo)
    queue_status = ""
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        if _norm_plan(str(item.get("planPath") or "")) == norm:
            queue_status = str(item.get("status") or "").upper()
            break

    if _marker_required_for_chapter(
        repo,
        plan_path=norm,
        chapter_id=chapter_id,
        registry=registry,
        on_main=on_main,
        missing_marker=missing_marker,
    ):
        issues.append(
            {
                "code": "PRODUCT_ON_MAIN_NO_MARKER",
                "severity": "high",
                "planPath": norm,
                "chapterId": chapter_id,
                "missingSlices": missing_marker,
                "message": (
                    f"Product touchsets on main for [{chapter_id}] but IDE_PRODUCT_READY "
                    f"missing: {', '.join(missing_marker)}"
                ),
                "fix": f"python scripts/ppe_chapter_coordination.py --repair --plan {norm}",
            }
        )

    if on_main and chapter_id and chapter_id not in registry:
        issues.append(
            {
                "code": "CLOSEOUT_REGISTRY_MISSING",
                "severity": "high",
                "planPath": norm,
                "chapterId": chapter_id,
                "message": (
                    f"Chapter [{chapter_id}] has product on main but is not in "
                    "AGENT_STEERING_V1.closeoutOnlyChapterIds"
                ),
                "fix": f"python scripts/ppe_chapter_coordination.py --repair --plan {norm}",
            }
        )

    if frontier_complete and not evidence_complete:
        issues.append(
            {
                "code": "FRONTIER_AHEAD_OF_EVIDENCE",
                "severity": "high",
                "planPath": norm,
                "chapterId": chapter_id,
                "message": (
                    f"MSOS_FRONTIER claims COMPLETE for [{chapter_id}] but evidence doc "
                    "is not COMPLETE (witness/closeout may still be pending)"
                ),
                "fix": f"Align evidence + frontier per {COORDINATION_DOC}",
            }
        )

    if queue_status == "READY" and _marker_required_for_chapter(
        repo,
        plan_path=norm,
        chapter_id=chapter_id,
        registry=registry,
        on_main=on_main,
        missing_marker=missing_marker,
    ):
        issues.append(
            {
                "code": "QUEUE_ACTIVE_PRODUCT_DESYNC",
                "severity": "high",
                "planPath": norm,
                "chapterId": chapter_id,
                "message": (
                    f"PHASE_QUEUE READY for [{chapter_id}] while product is on main without "
                    "IDE marker — relay will deadlock (IDE_BUILD + CLOSEOUT_ONLY)"
                ),
                "fix": f"python scripts/ppe_chapter_coordination.py --repair --plan {norm}",
            }
        )

    return issues


def audit_repo(repo: Path, *, plan_path: str | None = None) -> list[Issue]:
    """Audit active manifest plan or all READY queue rows."""
    repo = repo.resolve()
    plans: list[str] = []
    if plan_path:
        plans.append(_norm_plan(plan_path))
    else:
        try:
            from scripts.ppe_manifest import load_manifest

            manifest = load_manifest(repo)
            mp = _norm_plan(str(manifest.get("phasePlanPath") or ""))
            if mp:
                plans.append(mp)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        queue = load_queue(repo)
        for item in queue.get("items") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status") or "").upper() == "READY":
                p = _norm_plan(str(item.get("planPath") or ""))
                if p and p not in plans:
                    plans.append(p)
    issues: list[Issue] = []
    seen: set[str] = set()
    for plan in plans:
        plan_file = repo / _norm_plan(plan)
        if not plan_file.is_file():
            continue
        try:
            chapter_issues = audit_chapter(repo, plan)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            continue
        for issue in chapter_issues:
            key = f"{issue.get('code')}|{issue.get('planPath')}"
            if key not in seen:
                seen.add(key)
                issues.append(issue)
    return issues


def repair_chapter(repo: Path, plan_path: str, *, apply: bool) -> tuple[list[Fix], list[Issue]]:
    """Apply safe repairs: markers for product-on-main, closeout registry entry."""
    repo = repo.resolve()
    norm = _norm_plan(plan_path)
    fixes: list[Fix] = []
    remaining = audit_chapter(repo, norm)
    chapter_id = plan_chapter_id(norm)
    on_main = product_slices_on_main(repo, norm)
    missing_marker = _marker_missing_slices(repo, norm)

    if on_main and missing_marker and apply:
        from scripts.ppe_ide_product_ready import mark_product_slices_batch_ready

        rc, msg, marked = mark_product_slices_batch_ready(
            repo, plan_path=norm, slice_ids=missing_marker
        )
        if rc == 0 and marked:
            fixes.append(
                {
                    "action": "mark_ide_product_ready_batch",
                    "sliceIds": marked,
                    "planPath": norm,
                }
            )
        elif rc != 0:
            remaining.append(
                {
                    "code": "MARKER_REPAIR_FAILED",
                    "severity": "high",
                    "planPath": norm,
                    "sliceIds": missing_marker,
                    "message": msg,
                }
            )

    registry = _closeout_registry_ids(repo)
    if on_main and chapter_id and chapter_id not in registry and apply:
        steering_path = repo / STEERING_REL
        data = _load_steering(repo)
        ids = list(data.get("closeoutOnlyChapterIds") or [])
        if chapter_id not in ids:
            ids.append(chapter_id)
            data["closeoutOnlyChapterIds"] = sorted(ids)
            steering_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            fixes.append(
                {
                    "action": "add_closeout_registry",
                    "chapterId": chapter_id,
                    "path": STEERING_REL,
                }
            )

    if apply:
        remaining = audit_chapter(repo, norm)
    return fixes, remaining


REPAIRABLE_ISSUE_CODES = frozenset(
    {
        "PRODUCT_ON_MAIN_NO_MARKER",
        "CLOSEOUT_REGISTRY_MISSING",
        "QUEUE_ACTIVE_PRODUCT_DESYNC",
    }
)


def _repairable_plan_paths(issues: list[Issue]) -> list[str]:
    plans: list[str] = []
    seen: set[str] = set()
    for issue in issues:
        if str(issue.get("code") or "") not in REPAIRABLE_ISSUE_CODES:
            continue
        plan = _norm_plan(str(issue.get("planPath") or ""))
        if plan and plan not in seen:
            seen.add(plan)
            plans.append(plan)
    return plans


def assess_chapter_coordination_health(repo: Path) -> dict[str, Any]:
    """Operator/doctor snapshot for factory vs steering desync."""
    issues = audit_repo(repo)
    high = [i for i in issues if str(i.get("severity") or "").lower() == "high"]
    repairable = _repairable_plan_paths(issues)
    return {
        "ok": not high,
        "issue_count": len(issues),
        "high_count": len(high),
        "repairable_plan_count": len(repairable),
        "repairable_plans": repairable,
        "top_issue": high[0] if high else (issues[0] if issues else None),
        "issues": issues,
    }


def plan_coordination_repair(repo: Path) -> dict[str, Any]:
    issues = audit_repo(repo)
    plans = _repairable_plan_paths(issues)
    return {
        "issue_count": len(issues),
        "repairable_plan_count": len(plans),
        "plans": plans,
    }


def repair_repo_coordination(repo: Path, *, apply: bool) -> dict[str, Any]:
    """Apply safe marker + closeout-registry repairs for all repairable plans."""
    plan = plan_coordination_repair(repo)
    all_fixes: list[Fix] = []
    all_remaining: list[Issue] = []
    if apply:
        for plan_path in plan.get("plans") or []:
            fixes, remaining = repair_chapter(repo, str(plan_path), apply=True)
            all_fixes.extend(fixes)
            for issue in remaining:
                key = f"{issue.get('code')}|{issue.get('planPath')}"
                if not any(
                    f"{r.get('code')}|{r.get('planPath')}" == key for r in all_remaining
                ):
                    all_remaining.append(issue)
    else:
        all_remaining = audit_repo(repo)
    return {
        "applied": apply,
        "fixes": all_fixes,
        "fix_count": len(all_fixes),
        "remaining": all_remaining,
        "remaining_count": len(all_remaining),
        "repairable_plan_count": plan.get("repairable_plan_count"),
    }


def format_operator_coordination_lines(repo: Path, *, max_high: int = 1) -> list[str]:
    """Compact coordination block for OPERATOR_STATUS.md."""
    health = assess_chapter_coordination_health(repo)
    if health.get("ok"):
        return ["**Chapter coordination:** OK"]
    high_count = int(health.get("high_count") or 0)
    if high_count == 0:
        return [
            f"**Chapter coordination:** {health.get('issue_count')} issue(s) — "
            "`python scripts/ppe_chapter_coordination.py`"
        ]
    lines: list[str] = []
    issues = [i for i in (health.get("issues") or []) if str(i.get("severity")).lower() == "high"]
    for issue in issues[:max_high]:
        msg = str(issue.get("message") or "Chapter coordination desync")
        lines.append(f"**Chapter coordination:** WARN — {msg}")
        fix = str(issue.get("fix") or "").strip()
        if fix:
            lines.append(f"  fix: `{fix}`")
    extra_high = high_count - min(max_high, len(issues))
    if extra_high > 0:
        lines.append(
            f"  (+{extra_high} more HIGH — `python scripts/ppe_chapter_coordination.py` "
            "or `sop_discovery_maintenance.cmd --coordination-repair --apply`)"
        )
    return lines


def format_warning_lines(issues: list[Issue], *, max_lines: int = 8) -> list[str]:
    lines: list[str] = []
    for issue in issues[:max_lines]:
        sev = str(issue.get("severity") or "medium").upper()
        lines.append(f"  [{sev}] {issue.get('message')}")
        fix = str(issue.get("fix") or "").strip()
        if fix:
            lines.append(f"         → {fix}")
    if len(issues) > max_lines:
        lines.append(f"  ... {len(issues) - max_lines} more (see {COORDINATION_DOC})")
    return lines


def warn_if_coordination_needed(
    repo: Path,
    changed_paths: list[str] | None = None,
    *,
    plan_path: str | None = None,
) -> list[Issue]:
    """Print coordination warnings; return issues. Non-blocking."""
    repo = repo.resolve()
    if changed_paths is not None and not paths_touch_coordination(changed_paths):
        return []
    issues = audit_repo(repo, plan_path=plan_path)
    if not issues:
        return []
    print("WARN: chapter coordination review needed (see docs/SOP/CHAPTER_COORDINATION_V1.md):", file=sys.stderr)
    for line in format_warning_lines(issues):
        print(line, file=sys.stderr)
    return issues


def _plan_path_for_chapter(repo: Path, chapter_id: str) -> str | None:
    rel = f"docs/SOP/PHASE_PLANS/{chapter_id}_relay.json"
    if (repo / rel).is_file():
        return rel
    return None


def _evidence_pending_closeout_slices(repo: Path, plan_path: str) -> list[str]:
    """Slice ids still PENDING in evidence doc (witness/platform/closeout)."""
    try:
        plan = load_phase_plan(repo, plan_path)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    closeout = None
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and isinstance(sl.get("closeout"), dict):
            closeout = sl["closeout"]
            break
    evidence_rel = str((closeout or {}).get("evidenceDoc") or "").strip()
    if not evidence_rel:
        return []
    evidence_path = repo / evidence_rel.replace("\\", "/")
    if not evidence_path.is_file():
        return ["<evidence doc missing>"]
    from scripts.ppe_queue_health import _evidence_has_pending_slices

    body = evidence_path.read_text(encoding="utf-8", errors="replace")
    if not _evidence_has_pending_slices(body):
        return []
    pending: list[str] = []
    for line in body.splitlines():
        if "|" not in line:
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 3:
            continue
        status_cell = cells[2].strip("*").strip() if len(cells) > 2 else ""
        if status_cell.upper() != "PENDING":
            continue
        sid = cells[1].strip().strip("`")
        if not sid or sid.lower() == "slice" or sid.startswith("---"):
            continue
        if sid not in pending:
            pending.append(sid)
    return pending


def audit_closeout_spine(repo: Path) -> dict[str, Any]:
    """Summarize closeout-only registry chapters: markers, evidence, relay readiness."""
    repo = repo.resolve()
    registry = sorted(_closeout_registry_ids(repo))
    chapters: list[dict[str, Any]] = []
    for chapter_id in registry:
        plan_path = _plan_path_for_chapter(repo, chapter_id)
        row: dict[str, Any] = {"chapterId": chapter_id, "planPath": plan_path}
        if not plan_path:
            row["status"] = "no_plan"
            chapters.append(row)
            continue
        on_main = product_slices_on_main(repo, plan_path)
        missing_marker = _marker_missing_slices(repo, plan_path)
        registry_set = _closeout_registry_ids(repo)
        evidence_complete = chapter_marked_complete_in_repo(repo, plan_path)
        pending_slices = _evidence_pending_closeout_slices(repo, plan_path)
        active_plan = _active_manifest_plan_path(repo)
        is_active = _norm_plan(plan_path) == active_plan
        marker_required = _marker_required_for_chapter(
            repo,
            plan_path=plan_path,
            chapter_id=chapter_id,
            registry=registry_set,
            on_main=bool(on_main),
            missing_marker=missing_marker,
        )
        row["productOnMain"] = on_main
        row["missingMarkerSlices"] = missing_marker
        row["evidenceComplete"] = evidence_complete
        row["pendingEvidenceSlices"] = pending_slices
        row["isActiveManifest"] = is_active
        if evidence_complete and not pending_slices:
            row["status"] = "complete"
        elif is_active and marker_required:
            row["status"] = "marker_gap"
        elif is_active and on_main and pending_slices:
            row["status"] = "closeout_pending"
        elif on_main and pending_slices:
            row["status"] = "closeout_queued"
        elif on_main and chapter_id in registry_set:
            row["status"] = "closeout_queued"
        elif on_main:
            row["status"] = "ready_for_relay"
        else:
            row["status"] = "product_not_on_main"
        chapters.append(row)

    summary = {
        "registryCount": len(registry),
        "complete": sum(1 for c in chapters if c.get("status") == "complete"),
        "closeoutPending": sum(1 for c in chapters if c.get("status") == "closeout_pending"),
        "closeoutQueued": sum(1 for c in chapters if c.get("status") == "closeout_queued"),
        "markerGap": sum(1 for c in chapters if c.get("status") == "marker_gap"),
        "activePlanPath": active_plan or None,
    }
    return {"summary": summary, "chapters": chapters}


def format_closeout_spine_report(audit: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = audit.get("summary") or {}
    lines.append(
        "Closeout spine: "
        f"{summary.get('complete', 0)}/{summary.get('registryCount', 0)} complete, "
        f"{summary.get('closeoutPending', 0)} active pending, "
        f"{summary.get('closeoutQueued', 0)} queued (product on main, await manifest), "
        f"{summary.get('markerGap', 0)} marker gaps (active chapter only)"
    )
    if summary.get("activePlanPath"):
        lines.append(f"  Active manifest: {summary['activePlanPath']}")
    for ch in audit.get("chapters") or []:
        status = str(ch.get("status") or "?")
        cid = ch.get("chapterId")
        if status == "complete":
            continue
        detail = ""
        if status == "closeout_queued" and ch.get("pendingEvidenceSlices"):
            pending = ch["pendingEvidenceSlices"]
            detail = f" ({len(pending)} slice(s) when active)"
        elif ch.get("missingMarkerSlices") and status == "marker_gap":
            detail = f" marker missing: {', '.join(ch['missingMarkerSlices'][:3])}"
        elif ch.get("pendingEvidenceSlices"):
            pending = ch["pendingEvidenceSlices"]
            detail = f" pending: {', '.join(pending[:3])}"
            if len(pending) > 3:
                detail += f" (+{len(pending) - 3} more)"
        lines.append(f"  [{status}] {cid}{detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit/repair chapter coordination (factory vs steering)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--plan", type=str, default="", help="Single phase plan path")
    ap.add_argument("--repair", action="store_true", help="Apply safe repairs (markers + registry)")
    ap.add_argument("--spine-audit", action="store_true", help="Report closeout-only registry progress")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    plan = _norm_plan(args.plan) or None

    if args.spine_audit:
        audit = audit_closeout_spine(repo)
        if args.json:
            print(json.dumps(audit, indent=2))
        else:
            print(format_closeout_spine_report(audit))
        summary = audit.get("summary") or {}
        return 0 if int(summary.get("markerGap") or 0) == 0 else 2

    if args.repair:
        if plan:
            targets = [plan]
        else:
            targets = plan_coordination_repair(repo).get("plans") or []
            if not targets:
                for issue in audit_repo(repo):
                    p = _norm_plan(str(issue.get("planPath") or ""))
                    if p and p not in targets:
                        targets.append(p)
        all_fixes: list[Fix] = []
        all_remaining: list[Issue] = []
        for p in targets:
            fixes, remaining = repair_chapter(repo, p, apply=True)
            all_fixes.extend(fixes)
            all_remaining.extend(remaining)
        payload = {"fixes": all_fixes, "remaining": all_remaining}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            for fix in all_fixes:
                print(f"ppe_chapter_coordination: repaired {fix}")
            for issue in all_remaining:
                print(f"ppe_chapter_coordination: remaining [{issue.get('code')}] {issue.get('message')}")
        return 1 if all_remaining else 0

    issues = audit_repo(repo, plan_path=plan)
    if args.json:
        print(json.dumps({"issues": issues}, indent=2))
    else:
        for issue in issues:
            print(f"[{issue.get('severity')}] {issue.get('code')}: {issue.get('message')}")
        if not issues:
            print("ppe_chapter_coordination: ok")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
