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


def _frontier_claims_chapter_complete(repo: Path, chapter_id: str) -> bool:
    path = repo / FRONTIER_REL
    if not path.is_file() or not chapter_id:
        return False
    body = path.read_text(encoding="utf-8", errors="replace")
    title_token = chapter_id.replace("_", " ").lower()
    # Section header like: ### MSOS storyboard visual parity v1 — relay queue — **COMPLETE**
    pattern = re.compile(
        rf"^###[^\n]*{re.escape(title_token)}[^\n]*\*\*COMPLETE\*\*",
        re.I | re.M,
    )
    if pattern.search(body):
        return True
    # Alternate: chapter id in backticks near COMPLETE header within ~400 chars
    idx = body.lower().find(title_token)
    if idx < 0:
        idx = body.lower().find(chapter_id.lower())
    if idx < 0:
        return False
    window = body[max(0, idx - 80) : idx + 400]
    return bool(re.search(r"\*\*COMPLETE\*\*", window, re.I))


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

    if on_main and missing_marker:
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

    if queue_status == "READY" and on_main and missing_marker:
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
        plan_file = repo / plan.replace("/", "\\") if "\\" not in plan else repo / plan
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
        from scripts.ppe_ide_product_ready import mark_product_ready

        for sid in missing_marker:
            rc, msg = mark_product_ready(repo, slice_id=sid, plan_path=norm)
            if rc == 0:
                fixes.append({"action": "mark_ide_product_ready", "sliceId": sid, "planPath": norm})
            else:
                remaining.append(
                    {
                        "code": "MARKER_REPAIR_FAILED",
                        "severity": "high",
                        "planPath": norm,
                        "sliceId": sid,
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit/repair chapter coordination (factory vs steering)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--plan", type=str, default="", help="Single phase plan path")
    ap.add_argument("--repair", action="store_true", help="Apply safe repairs (markers + registry)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    plan = _norm_plan(args.plan) or None

    if args.repair:
        targets = [plan] if plan else []
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
