"""Loop hooks: workflow metrics + IDE BUILD starter generation in the auto-operator."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import load_operator_config
from scripts.ppe_slice_worker_mode import infer_slice_kind
from scripts.workflow_metrics_cli import (
    cmd_slice_close,
    cmd_summary,
    ensure_session_started,
    log_event,
)


def _efficiency_config(repo: Path) -> dict[str, Any]:
    cfg = load_operator_config(repo)
    raw = cfg.get("workflowEfficiency")
    if isinstance(raw, dict):
        return raw
    return {}


def efficiency_enabled(repo: Path) -> bool:
    we = _efficiency_config(repo)
    if we.get("enabled") is False:
        return False
    return we.get("enabled", True) is not False


def _flag(repo: Path, key: str, *, default: bool = True) -> bool:
    if not efficiency_enabled(repo):
        return False
    we = _efficiency_config(repo)
    val = we.get(key, default)
    return val is not False


def on_loop_start(repo: Path) -> None:
    if not _flag(repo, "trackMetrics", default=True):
        return
    sid = ensure_session_started(repo, notes="run_ppe_auto_local_loop")
    if sid:
        log_event(repo, "loop_start", session_id=sid, note="run_ppe_auto_local_loop.cmd")
        print(f"ppe_workflow_loop_hooks: metrics session {sid}")


def _closeout_slice_id(plan: dict[str, Any], plan_path: str) -> str:
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if sl.get("closeout") or (sid and "CLOSEOUT" in sid.upper()):
            return sid
    name = str(plan.get("name") or plan_path).strip()
    return f"chapter:{name}"


def _plan_has_product(plan: dict[str, Any]) -> bool:
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if sid and infer_slice_kind(sid, sl) == "product":
            return True
    return False


def on_guard_stop(
    repo: Path,
    *,
    reason: str,
    plan_path: str,
    detail: str = "",
    slice_id: str | None = None,
) -> str:
    """Run guard-stop hooks; return extra resume markdown (may be empty)."""
    extra: list[str] = []
    norm_plan = plan_path.replace("\\", "/").strip()

    if _flag(repo, "trackMetrics", default=True):
        ensure_session_started(repo, notes="auto loop")
        log_event(
            repo,
            "guard_stop",
            slice_id=slice_id,
            value_1=reason,
            value_2=norm_plan,
            note=detail[:500] if detail else "",
        )

    if reason == "PRODUCT_BLOCKED" and slice_id and _flag(repo, "autoGenerateIdeStarter", default=True):
        try:
            from scripts.ppe_ide_build_starter import starter_path, write_starter

            out = write_starter(repo, slice_id=slice_id, phase_plan=norm_plan)
            rel = starter_path(slice_id)
            extra.append(f"**IDE BUILD starter (auto-generated):** `{rel}`")
            extra.append(f"Open **new** Cursor thread; `@` `{rel}` only.")
            print(f"ppe_workflow_loop_hooks: wrote {out}")
        except Exception as exc:
            extra.append(f"WARN: could not auto-generate IDE starter: {exc}")

    if _flag(repo, "autoPreflight", default=False) and reason in ("CONTEXT_ESCALATE", "CONTEXT_WATCH"):
        try:
            from scripts.ppe_context_preflight import run_preflight

            report = run_preflight(repo, phase_plan=norm_plan, slice_id=slice_id)
            extra.append(f"**Context preflight:** overall `{report.get('overall_band')}`")
        except Exception as exc:
            extra.append(f"WARN: preflight skipped: {exc}")

    return "\n".join(extra)


def on_product_marked(repo: Path, *, slice_id: str, plan_path: str) -> None:
    if not _flag(repo, "trackMetrics", default=True):
        return
    ensure_session_started(repo, notes="auto loop")
    log_event(repo, "product_marked_ready", slice_id=slice_id, value_1=plan_path)
    cmd_slice_close(
        repo,
        slice_id=slice_id,
        size="M",
        roundtrips=1,
        notes="ide_product_ready marker",
    )


def on_chapter_complete(repo: Path, *, plan_path: str) -> None:
    if not _flag(repo, "trackMetrics", default=True):
        return
    norm_plan = plan_path.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    slice_id = _closeout_slice_id(plan, norm_plan)
    size = "M" if _plan_has_product(plan) else "S"
    ensure_session_started(repo, notes="auto loop")
    log_event(repo, "chapter_complete", slice_id=slice_id, value_1=norm_plan)
    cmd_slice_close(
        repo,
        slice_id=slice_id,
        size=size,
        roundtrips=0,
        notes="unattended chapter closeout",
    )
    if _flag(repo, "printSummaryOnChapterComplete", default=False):
        cmd_summary(repo, days=7)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Workflow efficiency loop hooks.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--loop-start", action="store_true", help="Call once when starting run_ppe_auto_local_loop")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if args.loop_start:
        on_loop_start(repo)
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
