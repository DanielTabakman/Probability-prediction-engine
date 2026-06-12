"""Backlog runway analysis for operator planning and weekly digest."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scripts.ppe_propagate_queue import (
    _backlog_items,
    _blocked_with_plan_sorted,
    _best_queued_item,
    _plan_valid,
    backlog_path,
    load_backlog,
    normalize_backlog_priority,
)
from scripts.ppe_roadmap import norm_plan

DEFAULT_MIN_CHAPTERS = 2
DEFAULT_MIN_DAYS = 7.0
DEFAULT_MINUTES_PER_DAY = 240.0


def _runway_min_chapters() -> int:
    raw = os.environ.get("PPE_BACKLOG_RUNWAY_MIN_CHAPTERS", str(DEFAULT_MIN_CHAPTERS)).strip()
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_MIN_CHAPTERS


def _runway_min_days() -> float:
    raw = os.environ.get("PPE_BACKLOG_RUNWAY_MIN_DAYS", str(DEFAULT_MIN_DAYS)).strip()
    try:
        return max(1.0, float(raw))
    except ValueError:
        return DEFAULT_MIN_DAYS


def _minutes_per_day() -> float:
    raw = os.environ.get("PPE_BACKLOG_RUNWAY_MINUTES_PER_DAY", str(DEFAULT_MINUTES_PER_DAY)).strip()
    try:
        return max(60.0, float(raw))
    except ValueError:
        return DEFAULT_MINUTES_PER_DAY


def _backlog_item_status(item: dict[str, Any]) -> str:
    return str(item.get("status") or "").strip().lower()


def _active_backlog_chapter(backlog: dict[str, Any]) -> dict[str, Any] | None:
    for item in _backlog_items(backlog):
        if not isinstance(item, dict):
            continue
        if _backlog_item_status(item) in ("chartered", "queued"):
            return item
    return None


def estimate_plan_sus_minutes(repo: Path, plan_path: str) -> int:
    """Sum susMinutes from a phase plan (fallback hardMinutes, then default per slice)."""
    plan_fs = repo / norm_plan(plan_path)
    if not plan_fs.is_file():
        return 0
    try:
        data = json.loads(plan_fs.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return 0
    slices = data.get("slices") or []
    if not isinstance(slices, list):
        return 0
    total = 0
    for sl in slices:
        if not isinstance(sl, dict):
            continue
        try:
            sus = int(sl.get("susMinutes") or 0)
        except (TypeError, ValueError):
            sus = 0
        if sus <= 0:
            try:
                sus = int(sl.get("hardMinutes") or 0) // 2
            except (TypeError, ValueError):
                sus = 0
        if sus <= 0:
            sus = 60
        total += sus
    return total


@dataclass
class BacklogRunwayItem:
    chapter_id: str
    priority: str
    plan_path: str
    status: str
    estimated_days: float
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapterId": self.chapter_id,
            "priority": self.priority,
            "planPath": self.plan_path,
            "status": self.status,
            "estimatedDays": round(self.estimated_days, 1),
            "reason": self.reason,
        }


@dataclass
class BacklogRunwayReport:
    sufficient: bool
    promotable_count: int
    estimated_days: float
    min_chapters: int
    min_days: float
    active_chapter_id: str | None
    items: list[BacklogRunwayItem]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sufficient": self.sufficient,
            "promotableCount": self.promotable_count,
            "estimatedDays": round(self.estimated_days, 1),
            "minChapters": self.min_chapters,
            "minDays": self.min_days,
            "activeChapterId": self.active_chapter_id,
            "items": [item.to_dict() for item in self.items],
        }


def _promotable_items(repo: Path, backlog: dict[str, Any]) -> list[BacklogRunwayItem]:
    """Blocked rows with planPath plus any explicit queued row (priority order)."""
    minutes_per_day = _minutes_per_day()
    out: list[BacklogRunwayItem] = []
    seen_plans: set[str] = set()

    queued = _best_queued_item(backlog)
    if queued is not None:
        plan_path = norm_plan(str(queued.get("planPath") or ""))
        if plan_path and plan_path not in seen_plans:
            sus = estimate_plan_sus_minutes(repo, plan_path)
            out.append(
                BacklogRunwayItem(
                    chapter_id=str(queued.get("chapterId") or plan_path),
                    priority=normalize_backlog_priority(queued),
                    plan_path=plan_path,
                    status="queued",
                    estimated_days=sus / minutes_per_day,
                    reason=str(queued.get("reason") or "").strip(),
                )
            )
            seen_plans.add(plan_path)

    for _index, item, plan_path in _blocked_with_plan_sorted(backlog):
        if plan_path in seen_plans:
            continue
        ok, _err = _plan_valid(repo, plan_path)
        if not ok:
            continue
        sus = estimate_plan_sus_minutes(repo, plan_path)
        out.append(
            BacklogRunwayItem(
                chapter_id=str(item.get("chapterId") or plan_path),
                priority=normalize_backlog_priority(item),
                plan_path=plan_path,
                status="blocked",
                estimated_days=sus / minutes_per_day,
                reason=str(item.get("reason") or "").strip(),
            )
        )
        seen_plans.add(plan_path)
    return out


def analyze_backlog_runway(repo: Path) -> BacklogRunwayReport:
    repo = repo.resolve()
    min_chapters = _runway_min_chapters()
    min_days = _runway_min_days()

    if not backlog_path(repo).is_file():
        return BacklogRunwayReport(
            sufficient=False,
            promotable_count=0,
            estimated_days=0.0,
            min_chapters=min_chapters,
            min_days=min_days,
            active_chapter_id=None,
            items=[],
        )

    backlog = load_backlog(repo)
    active = _active_backlog_chapter(backlog)
    items = _promotable_items(repo, backlog)
    estimated_days = sum(item.estimated_days for item in items)
    sufficient = len(items) >= min_chapters and estimated_days >= min_days

    return BacklogRunwayReport(
        sufficient=sufficient,
        promotable_count=len(items),
        estimated_days=estimated_days,
        min_chapters=min_chapters,
        min_days=min_days,
        active_chapter_id=str(active.get("chapterId") or "").strip() or None if active else None,
        items=items,
    )


def _short_reason(reason: str, *, max_len: int = 72) -> str:
    text = reason.strip()
    if not text:
        return ""
    text = text.removeprefix("[").strip()
    if "]" in text[:12]:
        text = text.split("]", 1)[-1].strip()
    if len(text) > max_len:
        return text[: max_len - 3].rstrip() + "..."
    return text


def build_backlog_runway_markdown(report: BacklogRunwayReport) -> list[str]:
    lines = ["### Backlog runway", ""]
    if report.active_chapter_id:
        lines.append(f"- **Active chapter:** `{report.active_chapter_id}` (in flight — not counted below).")

    status = "**OK**" if report.sufficient else "**LOW — add backlog rows**"
    lines.append(
        f"- **Runway:** {status} — {report.promotable_count} promotable chapter(s), "
        f"~{report.estimated_days:.1f} estimated day(s) "
        f"(target ≥{report.min_chapters} chapters and ≥{report.min_days:.0f} days)."
    )

    if not report.items:
        lines.extend(
            [
                "- No promotable backlog rows with `planPath`. Append to "
                "[`PHASE_CHAPTER_BACKLOG.json`](../SOP/PHASE_CHAPTER_BACKLOG.json) "
                "(see [`BACKLOG_OPERATOR.md`](../SOP/BACKLOG_OPERATOR.md)).",
                "",
            ]
        )
        return lines

    lines.append("- **Upcoming (priority order):**")
    for item in report.items[:8]:
        reason = _short_reason(item.reason)
        suffix = f" — {reason}" if reason else ""
        lines.append(
            f"  - **{item.priority}** · `{item.chapter_id}` "
            f"(~{item.estimated_days:.1f}d){suffix}"
        )
    if len(report.items) > 8:
        lines.append(f"  - … +{len(report.items) - 8} more")
    if not report.sufficient:
        lines.append(
            "- **Action:** add `blocked` rows with `planPath` to "
            "[`PHASE_CHAPTER_BACKLOG.json`](../SOP/PHASE_CHAPTER_BACKLOG.json)."
        )
    lines.append("")
    return lines


def build_backlog_runway_phone(report: BacklogRunwayReport) -> list[str]:
    lines: list[str] = []
    if report.sufficient:
        lines.append(
            f"Backlog OK: {report.promotable_count} chapter(s), "
            f"~{report.estimated_days:.0f} est. days ahead."
        )
    else:
        lines.append(
            f"Backlog LOW: {report.promotable_count} chapter(s), "
            f"~{report.estimated_days:.0f} est. days (want ≥{report.min_chapters} "
            f"chapters / ≥{report.min_days:.0f} days). Add rows to PHASE_CHAPTER_BACKLOG.json."
        )
    if report.active_chapter_id:
        lines.append(f"Active now: {report.active_chapter_id}.")

    shown = report.items[:4]
    if shown:
        parts = []
        for item in shown:
            label = item.chapter_id.replace("_", " ")
            parts.append(f"{item.priority}: {label}")
        lines.append("Next up: " + "; ".join(parts) + ".")
    return lines
