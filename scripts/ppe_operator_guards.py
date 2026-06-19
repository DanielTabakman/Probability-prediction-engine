"""Pre-flight guards for continuous auto-operator runs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_context_bands import ESCALATE_LINE_THRESHOLD, WATCH_LINE_THRESHOLD, classify_line_count
from scripts.ppe_ide_build_starter import format_ide_build_resume
from scripts.ppe_operator_hint import PPE_GO_HINT
from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import _guards_config, guards_enabled, load_operator_config
from scripts.ppe_phase_plan_window import (
    effective_slice_count_for_guard,
    phase_slice_batching_enabled,
)
from scripts.ppe_queue import mark_queue_item_done
from scripts.ppe_queue_health import chapter_marked_complete_in_repo
from scripts.ppe_slice_worker_mode import infer_slice_kind

GUARD_REPORT_REL = "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
GUARD_EXIT = 7
GUARD_SKIP_CHAPTER = 8

STRIPE_BILLING_PLAN = "docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json"
STRIPE_OPERATOR_PREREQ_ID = "stripe_operator_prereq"


@dataclass
class GuardResult:
    exit_code: int = 0
    reason: str = ""
    detail: str = ""
    plan_path: str = ""


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _skip_acp_active() -> bool:
    return os.environ.get("PPE_SKIP_ACP", "").strip().lower() in ("1", "true", "yes", "on")


def _plan_product_slice_ids(repo: Path, plan_path: str) -> list[str]:
    plan = load_phase_plan(repo, plan_path)
    product_ids: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        slice_id = str(sl.get("sliceId") or "").strip()
        if not slice_id:
            continue
        if infer_slice_kind(slice_id, sl) == "product":
            product_ids.append(slice_id)
    return product_ids


def _plan_sprint_spec_paths(repo: Path, plan_path: str) -> list[str]:
    plan = load_phase_plan(repo, plan_path)
    paths: list[str] = []
    default = str(plan.get("sprintSpecPath") or "").strip()
    if default:
        paths.append(default)
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sp = str(sl.get("sprintSpecPath") or "").strip()
        if sp and sp not in paths:
            paths.append(sp)
    return paths


def _sprint_spec_line_count(repo: Path, rel_path: str) -> int | None:
    p = repo / rel_path.replace("\\", "/")
    if not p.is_file():
        return None
    return len(p.read_text(encoding="utf-8", errors="replace").splitlines())


def write_guard_report(
    repo: Path,
    *,
    reason: str,
    detail: str,
    plan_path: str,
    resume: str | None = None,
) -> Path:
    out = repo / GUARD_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    resume_block = resume or (
        f"1. **You:** `{PPE_GO_HINT}`\n"
        "2. **Director** handles BUILD, commit, mark ready, and `run_ppe_local`.\n"
        "3. **Otherwise:** fix the issue, then `ppe_go.cmd` or `run_ppe_operator.cmd`."
    )
    body = f"""# Operator guard stop

**As-of:** {_utc_now()}
**Reason:** `{reason}`
**Phase plan:** `{plan_path}`

## Detail

{detail}

## Resume

{resume_block}
"""
    out.write_text(body, encoding="utf-8")
    return out


def _guard_stop(repo: Path, *, reason: str, detail: str, plan_path: str, resume: str | None = None) -> int:
    report = write_guard_report(repo, reason=reason, detail=detail, plan_path=plan_path, resume=resume)
    print(f"ppe_operator_guards: stop ({GUARD_EXIT}) — {detail}")
    print(f"ppe_operator_guards: report={report}")
    return GUARD_EXIT


def _apply_skip_complete_chapter(repo: Path, plan_path: str) -> None:
    norm = plan_path.replace("\\", "/").strip()
    mark_queue_item_done(
        repo,
        plan_path=norm,
        done_reason="operator guard: chapter evidence already COMPLETE in repo",
    )
    try:
        from scripts.ppe_manifest import clear_manifest_plan_path, load_manifest, save_manifest

        manifest = load_manifest(repo)
        manifest["status"] = "COMPLETE"
        manifest["notes"] = "skipped by operator guard (evidence COMPLETE)"
        save_manifest(repo, manifest)
        clear_manifest_plan_path(repo, note="Guard skip: evidence already COMPLETE.")
    except Exception as exc:
        print(f"WARN: manifest update on guard skip: {exc}")


def _stripe_build_deferred_guard(repo: Path, plan_path: str) -> GuardResult | None:
    """Block Stripe auto-SELECTION while operator prereqs or demo gate are open."""
    norm_plan = plan_path.replace("\\", "/").strip()
    if norm_plan != STRIPE_BILLING_PLAN:
        return None
    try:
        from scripts.ppe_human_backlog import load_backlog

        for item in load_backlog(repo).get("items") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("id") or "") != STRIPE_OPERATOR_PREREQ_ID:
                continue
            status = str(item.get("status") or "open").strip().lower()
            if status in ("open", "in_progress"):
                return GuardResult(
                    exit_code=GUARD_SKIP_CHAPTER,
                    reason="STRIPE_BUILD_DEFERRED",
                    detail=(
                        "Stripe BUILD deferred — close HUMAN_STEWARD_BACKLOG "
                        f"{STRIPE_OPERATOR_PREREQ_ID} after E2E demo on production"
                    ),
                    plan_path=norm_plan,
                )
    except FileNotFoundError:
        pass
    return None


def evaluate_selection_guards(repo: Path, plan_path: str) -> GuardResult | None:
    """Pre-SELECTION checks: block auto-select when plan config violates guard limits."""
    norm_plan = plan_path.replace("\\", "/").strip()
    if not guards_enabled(repo):
        return None

    stripe_guard = _stripe_build_deferred_guard(repo, norm_plan)
    if stripe_guard is not None:
        return stripe_guard

    cfg = load_operator_config(repo)
    g = _guards_config(cfg)

    if g.get("skipChapterIfEvidenceComplete", True) is not False:
        if chapter_marked_complete_in_repo(repo, norm_plan):
            return GuardResult(
                exit_code=GUARD_SKIP_CHAPTER,
                reason="SKIP_CHAPTER_EVIDENCE_COMPLETE",
                detail=f"evidence COMPLETE for {norm_plan}",
                plan_path=norm_plan,
            )

    plan = load_phase_plan(repo, norm_plan)
    slices = plan.get("slices") or []
    max_slices = g.get("maxPhaseSlices")
    if max_slices is not None and not phase_slice_batching_enabled(repo):
        try:
            limit = int(max_slices)
            if limit > 0 and len(slices) > limit:
                detail = (
                    f"Phase plan has {len(slices)} slices (max {limit}). "
                    "Split the chapter or raise maxPhaseSlices before SELECTION."
                )
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="TOO_MANY_SLICES",
                    detail=detail,
                    plan_path=norm_plan,
                )
        except (TypeError, ValueError):
            pass

    if g.get("stopOnContextEscalate", True) is not False or g.get("stopOnContextWatch") is True:
        watch_on = g.get("stopOnContextWatch") is True
        for spec_rel in _plan_sprint_spec_paths(repo, norm_plan):
            n = _sprint_spec_line_count(repo, spec_rel)
            if n is None:
                continue
            band = classify_line_count(n)
            if g.get("stopOnContextEscalate", True) is not False and band == "ESCALATE":
                detail = (
                    f"Sprint spec {spec_rel} has {n} lines "
                    f"(>{ESCALATE_LINE_THRESHOLD} ESCALATE). Shrink or split before SELECTION."
                )
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="CONTEXT_ESCALATE",
                    detail=detail,
                    plan_path=norm_plan,
                )
            if watch_on and band == "WATCH":
                detail = f"Sprint spec {spec_rel} has {n} lines (>{WATCH_LINE_THRESHOLD} WATCH)."
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="CONTEXT_WATCH",
                    detail=detail,
                    plan_path=norm_plan,
                )
    return None


def evaluate_continuous_guards(repo: Path, plan_path: str) -> GuardResult:
    """Dry-run guards for operator status (no queue/manifest writes)."""
    norm_plan = plan_path.replace("\\", "/").strip()
    if not guards_enabled(repo):
        return GuardResult(exit_code=0, plan_path=norm_plan)

    cfg = load_operator_config(repo)
    g = _guards_config(cfg)

    if g.get("skipChapterIfEvidenceComplete", True) is not False:
        if chapter_marked_complete_in_repo(repo, norm_plan):
            return GuardResult(
                exit_code=GUARD_SKIP_CHAPTER,
                reason="SKIP_CHAPTER_EVIDENCE_COMPLETE",
                detail=f"evidence COMPLETE for {norm_plan}",
                plan_path=norm_plan,
            )

    plan = load_phase_plan(repo, norm_plan)
    max_slices = g.get("maxPhaseSlices")
    if max_slices is not None and not phase_slice_batching_enabled(repo):
        slices = plan.get("slices") or []
        try:
            limit = int(max_slices)
            if limit > 0 and len(slices) > limit:
                detail = f"Phase plan has {len(slices)} slices (max {limit}). Split the chapter or raise maxPhaseSlices."
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="TOO_MANY_SLICES",
                    detail=detail,
                    plan_path=norm_plan,
                )
        except (TypeError, ValueError):
            pass
    elif max_slices is not None and phase_slice_batching_enabled(repo):
        try:
            limit = int(max_slices)
            effective = effective_slice_count_for_guard(repo, norm_plan)
            if limit > 0 and effective > limit:
                detail = (
                    f"Active slice batch has {effective} slices (max {limit}). "
                    "This should not happen — check phase slice progress state."
                )
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="TOO_MANY_SLICES",
                    detail=detail,
                    plan_path=norm_plan,
                )
        except (TypeError, ValueError):
            pass

    if g.get("stopOnContextEscalate", True) is not False or g.get("stopOnContextWatch") is True:
        watch_on = g.get("stopOnContextWatch") is True
        for spec_rel in _plan_sprint_spec_paths(repo, norm_plan):
            n = _sprint_spec_line_count(repo, spec_rel)
            if n is None:
                continue
            band = classify_line_count(n)
            if g.get("stopOnContextEscalate", True) is not False and band == "ESCALATE":
                detail = (
                    f"Sprint spec {spec_rel} has {n} lines "
                    f"(>{ESCALATE_LINE_THRESHOLD} ESCALATE). Shrink or split before unattended run."
                )
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="CONTEXT_ESCALATE",
                    detail=detail,
                    plan_path=norm_plan,
                )
            if watch_on and band == "WATCH":
                detail = f"Sprint spec {spec_rel} has {n} lines (>{WATCH_LINE_THRESHOLD} WATCH)."
                return GuardResult(
                    exit_code=GUARD_EXIT,
                    reason="CONTEXT_WATCH",
                    detail=detail,
                    plan_path=norm_plan,
                )

    if g.get("blockProductUnderGlobalDeterministic", True) is False:
        return GuardResult(exit_code=0, plan_path=norm_plan)
    if not _skip_acp_active():
        return GuardResult(exit_code=0, plan_path=norm_plan)

    product_slices = _plan_product_slice_ids(repo, norm_plan)
    if not product_slices:
        return GuardResult(exit_code=0, plan_path=norm_plan)

    from scripts.ppe_ide_product_ready import next_pending_product_slice

    next_sid = next_pending_product_slice(repo, plan_path=norm_plan)
    if next_sid is None:
        return GuardResult(
            exit_code=0,
            reason="IDE_MARKER_OK",
            detail="All product slices marked in IDE_PRODUCT_READY",
            plan_path=norm_plan,
        )

    detail = (
        f"Next product slice [{next_sid}] needs IDE BUILD (PPE_SKIP_ACP=1, not in IDE_PRODUCT_READY). "
        f"{PPE_GO_HINT}"
    )
    return GuardResult(
        exit_code=GUARD_EXIT,
        reason="PRODUCT_BLOCKED",
        detail=detail,
        plan_path=norm_plan,
    )


def run_continuous_guards(repo: Path, plan_path: str) -> int:
    """Return 0 run phase; GUARD_SKIP_CHAPTER (8) skip; GUARD_EXIT (7) stop."""
    result = evaluate_continuous_guards(repo, plan_path)
    norm_plan = plan_path.replace("\\", "/").strip()

    if result.exit_code == GUARD_SKIP_CHAPTER:
        print(f"ppe_operator_guards: skip chapter (evidence COMPLETE) {norm_plan}")
        _apply_skip_complete_chapter(repo, norm_plan)
        return GUARD_SKIP_CHAPTER

    if result.exit_code == GUARD_EXIT:
        resume = None
        if result.reason == "PRODUCT_BLOCKED":
            from scripts.ppe_ide_product_ready import next_pending_product_slice

            next_sid = next_pending_product_slice(repo, plan_path=norm_plan)
            if next_sid:
                resume = format_ide_build_resume(next_sid, norm_plan)
        return _guard_stop(
            repo,
            reason=result.reason,
            detail=result.detail,
            plan_path=norm_plan,
            resume=resume,
        )

    if result.reason == "IDE_MARKER_OK":
        print(f"ppe_operator_guards: IDE product marker OK for {norm_plan}")

    return 0
