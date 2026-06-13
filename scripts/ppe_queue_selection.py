"""Evaluate whether a queue/roadmap chapter can be selected; skip blockers and continue."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from scripts.ppe_manifest import load_phase_plan, validate_phase_plan
from scripts.ppe_queue_health import chapter_marked_complete_in_repo

ROADMAP_REL = "docs/SOP/PHASE_SELECTION_ROADMAP.json"
BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"


def norm_plan(path: str) -> str:
    return str(path or "").replace("\\", "/").strip()


def _load_json(repo: Path, rel: str) -> dict[str, Any] | None:
    p = repo / rel.replace("\\", "/")
    if not p.is_file():
        return None
    import json

    return json.loads(p.read_text(encoding="utf-8-sig"))


def backlog_item_for_plan(repo: Path, plan_path: str) -> dict[str, Any] | None:
    norm = norm_plan(plan_path)
    backlog = _load_json(repo, BACKLOG_REL)
    if not backlog:
        return None
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        if norm_plan(str(item.get("planPath") or "")) == norm:
            return item
    return None


def chapter_id_for_plan(repo: Path, plan_path: str) -> str:
    item = backlog_item_for_plan(repo, plan_path)
    if item:
        cid = str(item.get("chapterId") or "").strip()
        if cid:
            return cid
    plan_fs = repo / norm_plan(plan_path)
    if plan_fs.is_file():
        try:
            plan = load_phase_plan(repo, plan_path)
            for sl in plan.get("slices") or []:
                if not isinstance(sl, dict):
                    continue
                closeout = sl.get("closeout")
                if isinstance(closeout, dict):
                    cid = str(closeout.get("chapterId") or "").strip()
                    if cid:
                        return cid
        except Exception:
            pass
    return norm_plan(plan_path).split("/")[-1].replace("_relay.json", "").replace(".json", "")


def roadmap_status_for_plan(repo: Path, plan_path: str) -> str:
    norm = norm_plan(plan_path)
    roadmap = _load_json(repo, ROADMAP_REL)
    if not roadmap:
        return ""
    for item in roadmap.get("items") or []:
        if not isinstance(item, dict):
            continue
        if norm_plan(str(item.get("planPath") or "")) == norm:
            return str(item.get("status") or "").strip().lower()
    return ""


def anchor_plan_for_chapter(repo: Path, plan_path: str) -> str:
    """Return queueAfterPlanPath from backlog row, if any."""
    item = backlog_item_for_plan(repo, plan_path)
    if not item:
        return ""
    return norm_plan(str(item.get("queueAfterPlanPath") or ""))


def anchor_chapter_complete(repo: Path, anchor_plan: str) -> bool:
    if not anchor_plan:
        return True
    status = roadmap_status_for_plan(repo, anchor_plan)
    if status == "done":
        return True
    return chapter_marked_complete_in_repo(repo, anchor_plan)


def plan_validation_errors(repo: Path, plan_path: str) -> list[str]:
    rel = norm_plan(plan_path)
    if not rel:
        return ["empty planPath"]
    fs = repo / rel
    if not fs.is_file():
        return [f"plan not found: {rel}"]
    try:
        plan = load_phase_plan(repo, rel)
    except Exception as e:
        return [f"plan JSON invalid: {e}"]
    return list(validate_phase_plan(plan))


def selection_blockers(repo: Path, plan_path: str) -> list[str]:
    """Return human-readable reasons this chapter cannot be selected (empty = ok)."""
    blockers: list[str] = []

    errors = plan_validation_errors(repo, plan_path)
    if errors:
        blockers.extend(errors)
        return blockers

    if chapter_marked_complete_in_repo(repo, plan_path):
        blockers.append("evidence COMPLETE (finalize, do not select)")
        return blockers

    anchor = anchor_plan_for_chapter(repo, plan_path)
    if anchor and not anchor_chapter_complete(repo, anchor):
        blockers.append(f"waiting for anchor {anchor} to complete")

    try:
        from scripts.ppe_operator_guards import (
            GUARD_EXIT,
            GUARD_SKIP_CHAPTER,
            evaluate_selection_guards,
        )

        guard = evaluate_selection_guards(repo, plan_path)
        if guard is not None and guard.exit_code in (GUARD_EXIT, GUARD_SKIP_CHAPTER):
            blockers.append(guard.detail)
    except FileNotFoundError:
        pass

    try:
        from scripts.ppe_focus_gate import evaluate_focus_gate

        focus = evaluate_focus_gate(repo, plan_path)
        if not focus.allowed:
            blockers.append(f"focus gate — {focus.reason}")
    except ImportError:
        pass

    return blockers


@dataclass
class SkippedChapter:
    plan_path: str
    chapter_id: str
    reasons: list[str] = field(default_factory=list)

    @property
    def reason(self) -> str:
        return "; ".join(self.reasons)


@dataclass
class QueueSelectionResult:
    plan_path: str | None
    reason: str
    skipped: list[SkippedChapter] = field(default_factory=list)


def choose_next_selectable(
    repo: Path,
    items: list[Any],
    *,
    status: Literal["READY", "pending"] = "READY",
) -> QueueSelectionResult:
    """First selectable chapter in queue order; collect skipped rows with reasons."""
    want = status.upper()
    if want == "PENDING":
        want = "pending"

    skipped: list[SkippedChapter] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        item_status = str(item.get("status") or "").strip()
        if want == "READY":
            if item_status.upper() != "READY":
                continue
        else:
            if item_status.lower() != "pending":
                continue

        plan_path = norm_plan(str(item.get("planPath") or ""))
        if not plan_path:
            continue

        chapter_id = chapter_id_for_plan(repo, plan_path)
        blockers = selection_blockers(repo, plan_path)

        if blockers and blockers == ["evidence COMPLETE (finalize, do not select)"]:
            skipped.append(SkippedChapter(plan_path, chapter_id, blockers))
            continue

        if blockers:
            skipped.append(SkippedChapter(plan_path, chapter_id, blockers))
            continue

        reason = str(item.get("reason") or "").strip() or f"queue item {i} {status}"
        try:
            from scripts.ppe_focus_gate import evaluate_focus_gate

            focus = evaluate_focus_gate(repo, plan_path)
            if focus.urgent_bypass:
                reason = f"{reason} (urgent bypass)"
        except ImportError:
            pass
        return QueueSelectionResult(plan_path=plan_path, reason=reason, skipped=skipped)

    if skipped:
        detail = "; ".join(f"{s.chapter_id}: {s.reason}" for s in skipped)
        return QueueSelectionResult(
            plan_path=None,
            reason=f"no selectable {status} item; skipped: {detail}",
            skipped=skipped,
        )
    return QueueSelectionResult(
        plan_path=None,
        reason=f"no {status} items in queue",
        skipped=skipped,
    )
