"""Today's build plan, blocker forecast, and business playbook lines for digests."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

from scripts.ppe_phone_status import _extract_slice_id, _next_step
from scripts.ppe_slice_worker_mode import infer_slice_kind


def _starter_hint(repo: Path, slice_id: str) -> str:
    starter = repo / "artifacts" / "orchestrator" / f"IDE_BUILD_STARTER_{slice_id}.md"
    if starter.is_file():
        return f"Starter ready: {starter.name}"
    return "Run generate_ide_build_starter.cmd when loop stops"


def _auto_build_hint(repo: Path) -> str | None:
    try:
        from scripts.ppe_ide_handoff import ide_handoff_enabled
        from scripts.ppe_operator_config import auto_remote_build_enabled
    except ImportError:
        return None
    if auto_remote_build_enabled(repo) or ide_handoff_enabled(repo):
        return (
            "Auto-build may start IDE BUILD on the desktop when the loop hits a product gate — "
            "or get ahead early with ppe_go.cmd."
        )
    return None


def forecast_blockers(repo: Path, status: dict[str, Any]) -> list[str]:
    """What may stop the loop today — act before it happens."""
    repo = repo.resolve()
    verdict = str(status.get("verdict") or "")
    plan_path = str(status.get("phase_plan_path") or "").strip()
    blocker = str(status.get("blocker") or "").strip()
    lines: list[str] = []

    if verdict == "IDE_BUILD":
        sid = _extract_slice_id(blocker) or "product slice"
        lines.append(f"Blocked now: IDE BUILD for {sid}.")
        lines.append(f"Do now: ppe_go.cmd or phone build — {_starter_hint(repo, sid)}")
        return lines

    if verdict == "RUN_LOCAL":
        lines.append("Blocked now: finish step (IDE marker present).")
        lines.append("Do now: run_ppe_local.cmd once on desktop — loop cannot advance until then.")
        return lines

    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        lines.append(f"Blocked now: {verdict}.")
        if blocker:
            lines.append(blocker[:200])
        lines.append("Do now: ppe_go.cmd or phone fix — loop will not make progress.")
        return lines

    if verdict == "SUPPLY_LOW":
        lines.append("Loop may idle: no READY chapter in queue.")
        lines.append("Do now: add backlog row or steward charter — otherwise no relay work today.")
        return lines

    if not plan_path:
        lines.append("No active phase plan — loop runs but may have nothing to relay.")
        return lines

    try:
        from scripts.ppe_ide_product_ready import next_pending_product_slice
        from scripts.ppe_phase_plan_window import active_slice_window, completed_slice_ids
        from scripts.ppe_operator_guards import _plan_product_slice_ids

        batch = active_slice_window(repo, plan_path)
        batch_ids = [str(sl.get("sliceId") or "").strip() for sl in batch]
        batch_ids = [sid for sid in batch_ids if sid]
        product_ids = set(_plan_product_slice_ids(repo, plan_path))
        next_product = next_pending_product_slice(repo, plan_path=plan_path)

        unattended = [sid for sid in batch_ids if sid not in product_ids]
        if unattended:
            preview = ", ".join(unattended[:3])
            if len(unattended) > 3:
                preview += f" (+{len(unattended) - 3} more)"
            lines.append(f"Should run unattended: {preview}")

        if next_product and next_product in batch_ids:
            lines.append(f"Will block today: IDE BUILD for {next_product} when relay reaches it.")
            lines.append(f"Get ahead: {_starter_hint(repo, next_product)} — do IDE BUILD before loop stops.")
        elif next_product:
            done = completed_slice_ids(repo, plan_path)
            remaining = [sid for sid in batch_ids if sid not in done]
            if remaining and not any(sid in product_ids for sid in remaining):
                lines.append("Today's batch looks relay-only (no product IDE gate in this batch).")
            else:
                lines.append(
                    f"Next IDE gate: {next_product} (after current batch or later in chapter)."
                )
        elif product_ids:
            lines.append("All product slices IDE-marked for this plan — finish/closeout may be next.")

        marker_path = repo / "artifacts" / "orchestrator" / "IDE_PRODUCT_READY.json"
        if marker_path.is_file() and verdict == "RUN_AUTO":
            try:
                import json

                marker = json.loads(marker_path.read_text(encoding="utf-8-sig"))
                marker_plan = str(marker.get("phasePlanPath") or "").replace("\\", "/")
                if marker_plan and marker_plan == plan_path.replace("\\", "/"):
                    lines.append("Watch: IDE marker exists — if loop stops, run_ppe_local may be needed.")
            except (OSError, json.JSONDecodeError):
                pass
    except (ImportError, FileNotFoundError, OSError, ValueError):
        lines.append("Could not read slice batch — send status from phone for detail.")

    hint = _auto_build_hint(repo)
    if hint and verdict == "RUN_AUTO":
        lines.append(hint)

    if not lines:
        lines.append("Nothing obvious blocking — keep loop running 24/7.")
    return lines


def build_plan_lines(repo: Path, status: dict[str, Any]) -> list[str]:
    """What the factory intends to run today."""
    repo = repo.resolve()
    lines: list[str] = []
    chapter = str(status.get("chapter_name") or "").strip()
    plan_path = str(status.get("phase_plan_path") or "").strip()
    verdict = str(status.get("verdict") or "")
    manifest = str(status.get("manifest_status") or "").strip()

    if chapter:
        lines.append(f"Chapter: {chapter}")
    elif plan_path:
        short = Path(plan_path).stem.replace("_relay", "").replace("_", " ")
        lines.append(f"Plan: {short}")

    if plan_path:
        try:
            from scripts.ppe_phase_plan_window import (
                active_slice_window,
                completed_slice_ids,
                plan_slice_count,
            )

            batch = active_slice_window(repo, plan_path)
            total = plan_slice_count(repo, plan_path)
            done = len(completed_slice_ids(repo, plan_path))
            batch_ids = [str(sl.get("sliceId") or "").strip() for sl in batch]
            batch_ids = [sid for sid in batch_ids if sid]
            if batch_ids:
                parts = []
                for sl in batch[:5]:
                    sid = str(sl.get("sliceId") or "").strip()
                    if not sid:
                        continue
                    kind = infer_slice_kind(sid, sl)
                    parts.append(f"{sid} ({kind})")
                preview = ", ".join(parts)
                if len(batch_ids) > 5:
                    preview += f" (+{len(batch_ids) - 5} more)"
                lines.append(f"Relay batch today: {preview}")
            if total:
                lines.append(f"Chapter progress: {done}/{total} slices done")
        except (ImportError, FileNotFoundError, OSError, ValueError):
            pass

    if manifest:
        lines.append(f"Manifest: {manifest}")

    if verdict == "RUN_AUTO":
        lines.append("Expectation: auto-loop runs relay batches until an IDE or fix gate.")
    elif verdict == "RUN_LOCAL":
        lines.append("Expectation: waiting on you for run_ppe_local finish.")
    elif verdict == "IDE_BUILD":
        lines.append("Expectation: stopped until IDE BUILD completes.")
    elif verdict == "SUPPLY_LOW":
        supply = status.get("supply") or {}
        next_promo = supply.get("next_promotable_blocked")
        if isinstance(next_promo, dict) and next_promo.get("chapterId"):
            lines.append(f"After closeout: {next_promo.get('chapterId')}")
        else:
            lines.append("Expectation: idle until new chapter is queued.")

    if not lines:
        lines.append("No active chapter — add work to backlog or run steward charter.")

    return lines


def business_playbook_lines(repo: Path, *, ref: date | None = None) -> list[str]:
    """Human business-development moves from steward scoreboard / validation playbook."""
    try:
        from scripts.ppe_steward_scoreboard import (
            build_plan_context,
            build_scoreboard,
            resolve_nudge_slot,
        )
    except ImportError:
        return ["Steward scoreboard unavailable."]

    sb = build_scoreboard(repo, ref=ref)
    slot = resolve_nudge_slot("auto", ref=ref) or "monday"
    ctx = build_plan_context(sb, slot)

    lines = [
        ctx["phase_label"],
        f"Score: {sb['sessions_logged']}/{sb['sessions_target']} tester sessions "
        f"({sb['sessions_this_week']} this week) · Report: {sb['validation_report_status']}",
        f"This week: {ctx['this_week_goal']}",
    ]
    for move in ctx["moves_today"][:3]:
        lines.append(move)

    actions = sb.get("next_actions") or []
    for action in actions[:2]:
        if action not in lines:
            lines.append(action)

    return lines


def operator_today_lines(repo: Path, status: dict[str, Any]) -> list[str]:
    """Single-line operator action if loop needs attention right now."""
    from scripts.ppe_desktop_operator_stack import stack_status

    blocker = str(status.get("blocker") or "")
    slice_id = _extract_slice_id(blocker)
    stack = stack_status()
    return [_next_step(status, slice_id=slice_id, stack=stack)]


def build_morning_title(status: dict[str, Any], forecast: list[str]) -> str:
    """Short lock-screen title from verdict and blocker forecast."""
    verdict = str(status.get("verdict") or "")
    blocker = str(status.get("blocker") or "")

    if verdict == "IDE_BUILD":
        sid = _extract_slice_id(blocker) or "slice"
        return _clip_title(f"PPE: IDE BUILD now — {sid}")
    if verdict == "RUN_LOCAL":
        return "PPE: finish step needed (run_ppe_local)"
    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        return _clip_title(f"PPE: {verdict} — needs you")

    for line in forecast:
        if line.startswith("Will block today:"):
            rest = line.removeprefix("Will block today: ").split(" when relay")[0]
            return _clip_title(f"PPE: IDE likely today — {rest}")
        if line.startswith("Blocked now:"):
            return _clip_title(f"PPE: {line.removeprefix('Blocked now: ')}")

    chapter = str(status.get("chapter_name") or "").strip()
    if chapter:
        short = chapter.split("(")[0].strip()[:36]
        return _clip_title(f"PPE: {short} — loop OK")
    if verdict == "SUPPLY_LOW":
        return "PPE: queue idle — add chapter"
    return "PPE morning report"


def _clip_title(text: str, *, limit: int = 88) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def build_week_factory_lines(repo: Path) -> list[str]:
    """Build-factory outlook for weekly digest (chapter + IDE gates this week)."""
    try:
        from scripts.ppe_operator_status import collect_operator_status
    except ImportError:
        return ["Operator status unavailable."]

    status = collect_operator_status(repo.resolve())
    lines = build_plan_lines(repo, status)[:5]
    for line in forecast_blockers(repo, status):
        if any(
            key in line
            for key in (
                "Will block",
                "Next IDE gate",
                "Blocked now",
                "Should run unattended",
                "All product slices",
            )
        ):
            if line not in lines:
                lines.append(line)
    hint = _auto_build_hint(repo)
    if hint and hint not in lines:
        lines.append(hint)
    return lines[:8]
