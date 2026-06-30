"""Program-level operator queue — human labels, slice counts, time estimates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROGRAM_QUEUE_REL = "config/operator_program_queue.yaml"
PHASE_QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"
TIER1_MANIFEST_REL = "config/assets_tier1_manifest.yaml"

RELAY_BUSY_VERDICTS = frozenset({"RUN_LOCAL", "IDE_BUILD", "RUN_AUTO", "FIX_PLAN", "STALE_STATE", "ERROR"})
MANIFEST_COMPLETE = frozenset({"complete", "done"})
SPINE_CHAPTER_TOKENS = ("trader_review", "dist_download", "cross_venue_strategy", "distribution_timeseries")


def relay_is_busy(status: dict[str, Any]) -> bool:
    return str(status.get("verdict") or "") in RELAY_BUSY_VERDICTS


def _load_yaml_chapters(repo: Path, manifest_rel: str) -> list[dict[str, Any]]:
    path = repo / manifest_rel
    if not path.is_file():
        return []
    try:
        import yaml
    except ImportError:
        return []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    chapters = data.get("chapters") or {}
    return [
        {"chapter_id": chapter_id, **row}
        for chapter_id, row in chapters.items()
        if isinstance(row, dict)
    ]


def _load_phase_queue_items(repo: Path) -> list[dict[str, Any]]:
    path = repo / PHASE_QUEUE_REL
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return [item for item in (data.get("items") or []) if isinstance(item, dict)]


def _load_program_queue_config(repo: Path) -> list[dict[str, Any]]:
    path = repo / PROGRAM_QUEUE_REL
    if not path.is_file():
        return []
    try:
        import yaml
    except ImportError:
        return []
    programs = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("programs") or []
    return [p for p in programs if isinstance(p, dict)]


def format_est_hours(slices: int, hours_per_slice: int) -> str:
    if slices <= 0:
        return "—"
    total = slices * hours_per_slice
    if slices == 1:
        return f"~{total}h"
    lo = max(1, total - hours_per_slice)
    hi = total + hours_per_slice
    return f"~{lo}–{hi}h"


def _count_manifest_slices(repo: Path, program: dict[str, Any]) -> int:
    manifest_rel = str(program.get("manifest") or TIER1_MANIFEST_REL)
    wave = str(program.get("manifest_wave") or "").strip() or None
    count = 0
    for chapter in _load_yaml_chapters(repo, manifest_rel):
        st = str(chapter.get("status") or "").strip().lower()
        if st in MANIFEST_COMPLETE:
            continue
        if wave and str(chapter.get("wave") or "") != wave:
            continue
        count += 1
    return count


def _count_phase_queue_slices(repo: Path, program: dict[str, Any]) -> int:
    pq = program.get("phase_queue") if isinstance(program.get("phase_queue"), dict) else {}
    suffix = str(pq.get("spine_program_suffix") or "").strip()
    count = 0
    for item in _load_phase_queue_items(repo):
        if str(item.get("status") or "").upper() == "DONE":
            continue
        if suffix and suffix not in str(item.get("spineProgram") or ""):
            continue
        count += 1
    return count


def program_slices_remaining(repo: Path, program: dict[str, Any]) -> int:
    if program.get("manifest"):
        return _count_manifest_slices(repo, program)
    if program.get("phase_queue"):
        return _count_phase_queue_slices(repo, program)
    return 0


def build_program_queue(repo: Path, status: dict[str, Any]) -> list[dict[str, Any]]:
    busy = relay_is_busy(status)
    active_chapter = str(status.get("chapter_name") or "").lower()
    out: list[dict[str, Any]] = []
    for program in _load_program_queue_config(repo):
        pid = str(program.get("id") or "")
        slices = program_slices_remaining(repo, program)
        if slices <= 0:
            continue
        hours = int(program.get("hours_per_slice") or 3)
        how = str(program.get("operator_phrase") or program.get("operator_hint") or "").strip()
        doc = str(program.get("doc") or "").strip()
        why_parts: list[str] = []
        if how:
            why_parts.append(f'"{how}"' if " " in how else how)
        if doc:
            why_parts.append(doc)
        if busy:
            why_parts.append(
                "parallel — pick when you have bandwidth"
                if program.get("parallel")
                else "wait for relay idle"
            )
        elif program.get("parallel"):
            why_parts.append("optional parallel track")
        in_closeout = busy and bool(program.get("phase_queue")) and any(
            tok in active_chapter for tok in SPINE_CHAPTER_TOKENS
        )
        out.append(
            {
                "id": f"program_{pid}",
                "label": str(program.get("label") or pid),
                "slices_remaining": slices,
                "est_hours": format_est_hours(slices, hours),
                "why": " · ".join(why_parts) or "See program doc",
                "source": "program_queue",
                "priority": int(program.get("priority") or 99),
                "parallel": bool(program.get("parallel")),
                "in_closeout": in_closeout,
            }
        )
    out.sort(key=lambda row: (row["priority"], row["label"]))
    return out


def program_do_now(repo: Path, status: dict[str, Any]) -> list[dict[str, str]]:
    if relay_is_busy(status):
        return []
    programs = build_program_queue(repo, status)
    if not programs:
        return []
    primary = next((p for p in programs if not p.get("parallel")), programs[0])
    slices = int(primary["slices_remaining"])
    est = str(primary["est_hours"])
    title = f"{primary['label']} — {slices} slice{'s' if slices != 1 else ''} ({est})"
    return [{"id": str(primary["id"]), "title": title, "why": str(primary.get("why") or ""), "source": "program_queue"}]
