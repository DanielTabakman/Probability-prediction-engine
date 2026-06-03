"""Pre-flight guards for continuous auto-operator runs."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_context_bands import ESCALATE_LINE_THRESHOLD, WATCH_LINE_THRESHOLD, classify_line_count
from scripts.ppe_ide_build_starter import format_ide_build_resume
from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import _guards_config, guards_enabled, load_operator_config
from scripts.ppe_queue import mark_queue_item_done
from scripts.ppe_queue_health import chapter_marked_complete_in_repo
from scripts.ppe_slice_worker_mode import infer_slice_kind

GUARD_REPORT_REL = "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
GUARD_EXIT = 7
GUARD_SKIP_CHAPTER = 8


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
        "1. **Product slice:** BUILD in Cursor IDE (`docs/SOP/BUILD_PACKET_TEMPLATE.md`), "
        "commit on `buildBranch`, run `mark_ide_product_ready.cmd`, then `run_ppe_local.cmd`.\n"
        "2. **Otherwise:** fix the issue, then `run_ppe.cmd` or `run_ppe_auto_local.cmd`."
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


def run_continuous_guards(repo: Path, plan_path: str) -> int:
    """Return 0 run phase; GUARD_SKIP_CHAPTER (8) skip; GUARD_EXIT (7) stop."""
    if not guards_enabled(repo):
        return 0

    cfg = load_operator_config(repo)
    g = _guards_config(cfg)
    norm_plan = plan_path.replace("\\", "/").strip()

    if g.get("skipChapterIfEvidenceComplete", True) is not False:
        if chapter_marked_complete_in_repo(repo, norm_plan):
            print(f"ppe_operator_guards: skip chapter (evidence COMPLETE) {norm_plan}")
            _apply_skip_complete_chapter(repo, norm_plan)
            return GUARD_SKIP_CHAPTER

    plan = load_phase_plan(repo, norm_plan)
    slices = plan.get("slices") or []
    max_slices = g.get("maxPhaseSlices")
    if max_slices is not None:
        try:
            limit = int(max_slices)
            if limit > 0 and len(slices) > limit:
                detail = f"Phase plan has {len(slices)} slices (max {limit}). Split the chapter or raise maxPhaseSlices."
                return _guard_stop(repo, reason="TOO_MANY_SLICES", detail=detail, plan_path=norm_plan)
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
                return _guard_stop(
                    repo,
                    reason="CONTEXT_ESCALATE",
                    detail=detail,
                    plan_path=norm_plan,
                    resume="Shrink sprint spec or split chapter, then re-run.",
                )
            if watch_on and band == "WATCH":
                detail = (
                    f"Sprint spec {spec_rel} has {n} lines (>{WATCH_LINE_THRESHOLD} WATCH)."
                )
                return _guard_stop(
                    repo,
                    reason="CONTEXT_WATCH",
                    detail=detail,
                    plan_path=norm_plan,
                    resume="Review context band (WORKFLOW_CONTEXT_AUDIT_001.md) before continuous run.",
                )

    if g.get("blockProductUnderGlobalDeterministic", True) is False:
        return 0
    if not _skip_acp_active():
        return 0

    product_slices = _plan_product_slice_ids(repo, norm_plan)
    if not product_slices:
        return 0

    from scripts.ppe_ide_product_ready import marker_covers_product_slices

    if marker_covers_product_slices(repo, plan_path=norm_plan, product_slice_ids=product_slices):
        print(f"ppe_operator_guards: IDE product marker OK for {norm_plan}")
        return 0

    primary_slice = product_slices[0]
    ids = ", ".join(product_slices)
    detail = (
        f"Phase plan contains product slice(s) [{ids}] but PPE_SKIP_ACP=1 and no valid IDE_PRODUCT_READY marker. "
        "IDE BUILD, commit, then `mark_ide_product_ready.cmd <sliceId>`, then `run_ppe_local.cmd`."
    )
    resume = format_ide_build_resume(primary_slice, norm_plan)
    return _guard_stop(repo, reason="PRODUCT_BLOCKED", detail=detail, plan_path=norm_plan, resume=resume)
