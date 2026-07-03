"""Milestone gate v2 — closeout debt, steering reconcile, registry hygiene.

Canon: docs/SOP/PIPELINE_HEALTH_V1.md · docs/SOP/CHAPTER_COORDINATION_V1.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

STEERING_REL = "docs/SOP/AGENT_STEERING_V1.json"

ACTIVE_CHAPTER_GATE = "ACTIVE_CHAPTER_GATE"
STEERING_CANDIDATE_STALE = "STEERING_CANDIDATE_STALE"
CLOSEOUT_REGISTRY_DEBT = "CLOSEOUT_REGISTRY_DEBT"
MILESTONE_BLOCKED = "MILESTONE_BLOCKED"


def _norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _load_steering(repo: Path) -> dict[str, Any]:
    path = repo / STEERING_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_steering(repo: Path, data: dict[str, Any]) -> None:
    path = repo / STEERING_REL
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _plan_for_chapter(chapter_id: str) -> str:
    return f"docs/SOP/PHASE_PLANS/{chapter_id}_relay.json"


def queue_status_for_plan(repo: Path, plan_path: str) -> str:
    from scripts.ppe_queue import load_queue

    norm = _norm_plan(plan_path)
    try:
        queue = load_queue(repo)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return ""
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        item_plan = _norm_plan(str(item.get("planPath") or ""))
        if item_plan == norm:
            return str(item.get("status") or "").strip().upper()
    return ""


def is_chapter_fully_closed(repo: Path, chapter_id: str) -> bool:
    """Evidence COMPLETE and queue DONE (safe to prune registry / advance past candidate)."""
    from scripts.ppe_queue_health import chapter_marked_complete_in_repo

    plan_path = _plan_for_chapter(chapter_id)
    if not (repo / plan_path).is_file():
        return False
    if not chapter_marked_complete_in_repo(repo, plan_path):
        return False
    qstatus = queue_status_for_plan(repo, plan_path)
    if qstatus and qstatus != "DONE":
        return False
    return True


def is_steering_candidate_stale(repo: Path, *, candidate_id: str | None = None) -> bool:
    cid = str(candidate_id or _load_steering(repo).get("nextBuildCandidateId") or "").strip()
    if not cid:
        return False
    return is_chapter_fully_closed(repo, cid)


def resolve_next_build_candidate(repo: Path) -> str | None:
    """Derive next BUILD chapter: spine queue → READY queue row → non-stale steering."""
    repo = repo.resolve()
    steering = _load_steering(repo)
    registry = {
        str(x).strip()
        for x in (steering.get("closeoutOnlyChapterIds") or [])
        if str(x).strip()
    }

    spine = steering.get("spineQueueAfterCloseout") or []
    if isinstance(spine, list):
        for raw in spine:
            cid = str(raw or "").strip()
            if not cid:
                continue
            if cid in registry:
                continue
            if is_chapter_fully_closed(repo, cid):
                continue
            return cid

    try:
        from scripts.ppe_queue import load_queue

        queue = load_queue(repo)
        for item in queue.get("items") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("status") or "").upper() != "READY":
                continue
            plan_path = _norm_plan(str(item.get("planPath") or ""))
            if not plan_path:
                continue
            from scripts.ppe_chapter_coordination import plan_chapter_id

            cid = plan_chapter_id(plan_path)
            if cid in registry:
                continue
            if is_chapter_fully_closed(repo, cid):
                continue
            return cid
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    steering_id = str(steering.get("nextBuildCandidateId") or "").strip()
    if steering_id and not is_steering_candidate_stale(repo, candidate_id=steering_id):
        return steering_id
    return None


def assess_closeout_debt(repo: Path) -> dict[str, Any]:
    """Summarize registry debt vs active chapter gate."""
    from scripts.ppe_chapter_coordination import audit_closeout_spine, plan_chapter_id

    repo = repo.resolve()
    audit = audit_closeout_spine(repo)
    summary = audit.get("summary") or {}
    chapters = audit.get("chapters") or []
    steering = _load_steering(repo)

    active_plan = _norm_plan(str(summary.get("activePlanPath") or ""))
    active_chapter_id: str | None = None
    active_pending_slices: list[str] = []
    if active_plan:
        active_chapter_id = plan_chapter_id(active_plan)
        for ch in chapters:
            if _norm_plan(str(ch.get("planPath") or "")) == active_plan:
                active_pending_slices = list(ch.get("pendingEvidenceSlices") or [])
                break

    registry_stale = 0
    registry_actionable = 0
    for ch in chapters:
        status = str(ch.get("status") or "")
        cid = str(ch.get("chapterId") or "")
        if status == "complete":
            registry_stale += 1
            continue
        if status in ("closeout_pending", "marker_gap"):
            registry_actionable += 1
        elif status == "closeout_queued" and ch.get("pendingEvidenceSlices"):
            registry_actionable += 1

    steering_candidate = str(steering.get("nextBuildCandidateId") or "").strip() or None
    resolved_candidate = resolve_next_build_candidate(repo)
    steering_stale = bool(
        steering_candidate and is_steering_candidate_stale(repo, candidate_id=steering_candidate)
    )

    actionable_pending = len(active_pending_slices)
    has_active_gate = actionable_pending > 0 or any(
        str(ch.get("status") or "") in ("closeout_pending", "marker_gap")
        for ch in chapters
        if ch.get("isActiveManifest")
    )

    return {
        "registry_total": int(summary.get("registryCount") or 0),
        "registry_stale": registry_stale,
        "registry_actionable": registry_actionable,
        "active_chapter_id": active_chapter_id,
        "active_plan_path": active_plan or None,
        "active_pending_slices": active_pending_slices,
        "active_pending_count": actionable_pending,
        "has_active_gate": has_active_gate,
        "next_build_steering": steering_candidate,
        "next_build_resolved": resolved_candidate,
        "steering_stale": steering_stale,
        "spine_audit": audit,
    }


def advance_steering_candidate(repo: Path, *, apply: bool) -> dict[str, Any]:
    """Update nextBuildCandidateId when stale; prefer resolved spine/queue candidate."""
    repo = repo.resolve()
    steering = _load_steering(repo)
    if not steering:
        return {"applied": False, "reason": "no steering file"}

    current = str(steering.get("nextBuildCandidateId") or "").strip()
    resolved = resolve_next_build_candidate(repo)
    stale = bool(current and is_steering_candidate_stale(repo, candidate_id=current))

    if not stale and resolved == current:
        return {"applied": False, "reason": "candidate current", "nextBuildCandidateId": current}

    if not resolved:
        return {
            "applied": False,
            "reason": "no resolved candidate",
            "nextBuildCandidateId": current or None,
            "steering_stale": stale,
        }

    if resolved == current:
        return {"applied": False, "reason": "already resolved", "nextBuildCandidateId": current}

    out = {
        "applied": False,
        "previous": current or None,
        "nextBuildCandidateId": resolved,
        "steering_stale": stale,
    }
    if apply:
        steering["nextBuildCandidateId"] = resolved
        note = str(steering.get("nextBuildCandidateNote") or "").strip()
        if stale or not note:
            steering["nextBuildCandidateNote"] = "auto-advanced by ppe_milestone_gate (stale or spine)"
        hints = steering.get("docHints")
        if isinstance(hints, dict):
            nb = hints.get("nextBuildCandidate")
            if isinstance(nb, dict):
                nb["chapter_id"] = resolved
                nb["resolve_cmd"] = f"python scripts/resolve_sop.py --chapter {resolved} --json"
                hints["nextBuildCandidate"] = nb
                steering["docHints"] = hints
        _save_steering(repo, steering)
        out["applied"] = True
    return out


def prune_stale_closeout_registry(repo: Path, *, apply: bool) -> dict[str, Any]:
    """Remove registry rows where evidence is COMPLETE and queue is DONE."""
    from scripts.ppe_chapter_coordination import audit_closeout_spine
    from scripts.ppe_chapter_mode import prune_closeout_chapter

    repo = repo.resolve()
    audit = audit_closeout_spine(repo)
    pruned: list[str] = []
    skipped: list[dict[str, str]] = []

    for ch in audit.get("chapters") or []:
        if str(ch.get("status") or "") != "complete":
            continue
        cid = str(ch.get("chapterId") or "").strip()
        plan_path = _norm_plan(str(ch.get("planPath") or ""))
        if not cid or not plan_path:
            continue
        if not is_chapter_fully_closed(repo, cid):
            skipped.append({"chapterId": cid, "reason": "not fully closed"})
            continue
        if apply:
            if prune_closeout_chapter(repo, plan_path=plan_path):
                pruned.append(cid)
        else:
            pruned.append(cid)

    return {
        "applied": apply,
        "pruned": pruned,
        "pruned_count": len(pruned),
        "skipped": skipped,
    }


def reconcile_milestone_gate(repo: Path, *, apply: bool) -> dict[str, Any]:
    """Phase 2 batch: prune stale registry + advance steering candidate."""
    prune = prune_stale_closeout_registry(repo, apply=apply)
    advance = advance_steering_candidate(repo, apply=apply)
    debt = assess_closeout_debt(repo)
    return {
        "applied": apply,
        "prune": prune,
        "advance": advance,
        "debt": {
            "registry_total": debt.get("registry_total"),
            "registry_stale": debt.get("registry_stale"),
            "registry_actionable": debt.get("registry_actionable"),
            "next_build_resolved": debt.get("next_build_resolved"),
        },
    }


def milestone_gate_issues(repo: Path, debt: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Contradiction-style issues for pipeline health."""
    debt = debt or assess_closeout_debt(repo)
    issues: list[dict[str, Any]] = []

    active_id = debt.get("active_chapter_id")
    pending = debt.get("active_pending_slices") or []
    pending_count = int(debt.get("active_pending_count") or 0)

    if active_id and pending_count > 0:
        issues.append(
            {
                "code": ACTIVE_CHAPTER_GATE,
                "severity": "high" if pending_count > 2 else "medium",
                "message": (
                    f"Active chapter `{active_id}` — {pending_count} pending slice(s): "
                    f"{', '.join(str(s) for s in pending[:3])}"
                    + (f" (+{pending_count - 3} more)" if pending_count > 3 else "")
                ),
                "fix_class": "repair",
                "fix": "Finish relay closeout on VM (run_ppe_local / DESKTOP_CONTINUE) — do NOT re-BUILD product.",
                "commands": ["DESKTOP_CONTINUE.cmd --no-pause"],
            }
        )

    stale_count = int(debt.get("registry_stale") or 0)
    if stale_count > 0:
        issues.append(
            {
                "code": CLOSEOUT_REGISTRY_DEBT,
                "severity": "low" if not debt.get("has_active_gate") else "medium",
                "message": (
                    f"Closeout registry: {debt.get('registry_total', 0)} listed / "
                    f"{debt.get('registry_actionable', 0)} actionable / {stale_count} stale-complete"
                ),
                "fix_class": "repair",
                "fix": "python scripts/ppe_milestone_gate.py --reconcile --apply",
                "commands": ["python scripts/ppe_milestone_gate.py --reconcile --apply"],
            }
        )

    if debt.get("steering_stale"):
        resolved = debt.get("next_build_resolved") or "—"
        steering = debt.get("next_build_steering") or "—"
        issues.append(
            {
                "code": STEERING_CANDIDATE_STALE,
                "severity": "medium",
                "message": (
                    f"Steering nextBuildCandidate `{steering}` is COMPLETE — "
                    f"resolved next BUILD: `{resolved}`"
                ),
                "fix_class": "repair",
                "fix": "python scripts/ppe_milestone_gate.py --reconcile --apply",
                "commands": ["python scripts/ppe_milestone_gate.py --reconcile --apply"],
            }
        )

    if debt.get("has_active_gate") and active_id:
        issues.append(
            {
                "code": MILESTONE_BLOCKED,
                "severity": "medium",
                "message": (
                    f"Spine gate: `{active_id}` blocks next BUILD "
                    f"({pending_count} pending factory slice(s))."
                ),
                "fix_class": "repair",
                "fix": "Clear active chapter closeout before next BUILD.",
                "commands": ["DESKTOP_CONTINUE.cmd --no-pause"],
            }
        )

    return issues


def format_milestone_gate_lines(debt: dict[str, Any]) -> list[str]:
    """Human lines for OPERATOR_STATUS / founder report."""
    lines: list[str] = []
    active = debt.get("active_chapter_id")
    pending = int(debt.get("active_pending_count") or 0)
    if active and pending:
        lines.append(
            f"**Active gate:** `{active}` — {pending} pending slice(s)"
        )
    elif active:
        lines.append(f"**Active chapter:** `{active}` — factory finish in progress")

    total = int(debt.get("registry_total") or 0)
    stale = int(debt.get("registry_stale") or 0)
    actionable = int(debt.get("registry_actionable") or 0)
    if total:
        lines.append(
            f"**Registry debt:** {total} listed / {actionable} actionable / {stale} stale-complete"
        )

    if debt.get("steering_stale"):
        lines.append(
            f"**Steering drift:** candidate `{debt.get('next_build_steering')}` is COMPLETE "
            f"→ resolved `{debt.get('next_build_resolved')}`"
        )
    resolved = debt.get("next_build_resolved")
    if resolved and not debt.get("steering_stale"):
        lines.append(f"**Next BUILD (resolved):** `{resolved}`")
    return lines


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Milestone gate v2 — debt assess, reconcile, steering advance")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--reconcile", action="store_true", help="Prune stale registry + advance steering")
    ap.add_argument("--apply", action="store_true", help="Write steering/registry changes")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.reconcile:
        result = reconcile_milestone_gate(repo, apply=args.apply)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(json.dumps(result, indent=2))
        return 0

    debt = assess_closeout_debt(repo)
    payload = {"debt": debt, "issues": milestone_gate_issues(repo, debt)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for line in format_milestone_gate_lines(debt):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
