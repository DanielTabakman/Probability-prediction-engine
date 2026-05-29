"""Operator guardrails for continuous PPE runs (context, product/deterministic, queue health)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import load_operator_config
from scripts.ppe_queue_health import chapter_marked_complete_in_repo
from scripts.ppe_slice_worker_mode import infer_slice_kind, resolve_worker_mode

OPERATOR_GUARD_EXIT = 7

DEFAULT_GUARDS: dict[str, Any] = {
    "enabled": True,
    "stopOnContextEscalate": True,
    "stopOnContextWatch": False,
    "maxPhaseSlices": 6,
    "blockProductUnderGlobalDeterministic": True,
    "requireTouchSetOnProductSlices": True,
    "skipChapterIfEvidenceComplete": True,
    "maxConsecutivePhaseFailures": 2,
    "runQueueHealthBeforeChapter": True,
}


@dataclass
class GuardVerdict:
    ok: bool
    stop: bool
    skip_chapter: bool
    code: str
    message: str
    details: dict[str, Any] = field(default_factory=dict)


def guards_enabled(repo_root: Path) -> bool:
    env = os.environ.get("PPE_OPERATOR_GUARDS", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    cfg = load_operator_config(repo_root)
    if not cfg.get("enabled"):
        return False
    g = cfg.get("guards")
    if isinstance(g, dict) and g.get("enabled") is False:
        return False
    return True


def load_guards(repo_root: Path) -> dict[str, Any]:
    cfg = load_operator_config(repo_root)
    raw = cfg.get("guards")
    merged = dict(DEFAULT_GUARDS)
    if isinstance(raw, dict):
        merged.update(raw)
    return merged


def sprint_context_band(repo_root: Path, sprint_spec_rel: str | None) -> str:
    """NORMAL | WATCH | ESCALATE — mirrors write_last_run_report heuristic."""
    rel = str(sprint_spec_rel or "").strip().replace("\\", "/")
    if not rel:
        return "NORMAL"
    p = repo_root / rel
    if not p.is_file():
        return "NORMAL"
    line_count = len(p.read_text(encoding="utf-8", errors="replace").splitlines())
    if line_count > 400:
        return "ESCALATE"
    if line_count > 200:
        return "WATCH"
    return "NORMAL"


def _global_deterministic() -> bool:
    wm = (os.environ.get("PPE_WORKER_MODE") or "").strip().lower()
    if wm in ("deterministic", "deterministic-worker", "local"):
        return True
    return os.environ.get("PPE_SKIP_ACP", "").strip().lower() in ("1", "true", "yes", "on")


def assess_phase_plan(
    repo_root: Path,
    plan_path: str,
    *,
    guards: dict[str, Any] | None = None,
) -> GuardVerdict:
    """Validate a phase plan before relay; used by continuous mode and steward."""
    repo = repo_root.resolve()
    g = guards if guards is not None else load_guards(repo)
    norm = str(plan_path or "").replace("\\", "/").strip()
    if not norm:
        return GuardVerdict(False, True, False, "PLAN_MISSING", "empty phase plan path")

    try:
        plan = load_phase_plan(repo, norm)
    except (FileNotFoundError, json.JSONDecodeError, OSError) as e:
        return GuardVerdict(False, True, False, "PLAN_INVALID", f"cannot load phase plan: {e}")

    slices = [sl for sl in (plan.get("slices") or []) if isinstance(sl, dict)]
    max_slices = int(g.get("maxPhaseSlices") or 6)
    if len(slices) > max_slices:
        return GuardVerdict(
            False,
            True,
            False,
            "TOO_MANY_SLICES",
            f"phase plan has {len(slices)} slices (max {max_slices})",
            {"sliceCount": len(slices), "maxPhaseSlices": max_slices},
        )

    sprint_default = str(plan.get("sprintSpecPath") or "")
    bands: dict[str, str] = {}
    for rel in {sprint_default, *(str(sl.get("sprintSpecPath") or "") for sl in slices)}:
        rel = rel.strip()
        if not rel:
            continue
        bands[rel] = sprint_context_band(repo, rel)

    if g.get("stopOnContextEscalate") and any(b == "ESCALATE" for b in bands.values()):
        bad = [k for k, v in bands.items() if v == "ESCALATE"]
        return GuardVerdict(
            False,
            True,
            False,
            "CONTEXT_ESCALATE",
            "sprint spec too large for unattended auto-run (>400 lines); shrink or split chapter",
            {"sprintSpecs": bad, "bands": bands},
        )
    if g.get("stopOnContextWatch") and any(b == "WATCH" for b in bands.values()):
        bad = [k for k, v in bands.items() if v == "WATCH"]
        return GuardVerdict(
            False,
            True,
            False,
            "CONTEXT_WATCH",
            "sprint spec in WATCH band (>200 lines); manual BUILD preferred",
            {"sprintSpecs": bad, "bands": bands},
        )

    block_product = bool(g.get("blockProductUnderGlobalDeterministic", True))
    require_touch = bool(g.get("requireTouchSetOnProductSlices", True))
    product_slices: list[str] = []

    for sl in slices:
        slice_id = str(sl.get("sliceId") or "").strip()
        kind = infer_slice_kind(slice_id, sl)
        if kind != "product":
            continue
        product_slices.append(slice_id)
        mode = resolve_worker_mode(slice_id=slice_id, slice_obj=sl)
        if block_product and _global_deterministic() and mode == "deterministic":
            return GuardVerdict(
                False,
                True,
                False,
                "PRODUCT_BLOCKED",
                (
                    f"product slice {slice_id} would run deterministic-only "
                    "(SCOPE_AMBIGUITY); set workerMode=local-agent on the slice or unset PPE_WORKER_MODE"
                ),
                {"sliceId": slice_id, "resolvedWorkerMode": mode},
            )
        touch = sl.get("touchSet")
        if require_touch and (not isinstance(touch, list) or not touch):
            return GuardVerdict(
                False,
                True,
                False,
                "PRODUCT_NO_TOUCH_SET",
                f"product slice {slice_id} missing non-empty touchSet",
                {"sliceId": slice_id},
            )

    return GuardVerdict(
        True,
        False,
        False,
        "OK",
        "plan passed operator guards",
        {"productSlices": product_slices, "contextBands": bands},
    )


def assess_before_continuous_chapter(repo_root: Path, plan_path: str) -> GuardVerdict:
    """Pre-flight for one continuous chapter (skip stale COMPLETE, else assess plan)."""
    repo = repo_root.resolve()
    g = load_guards(repo)
    if g.get("skipChapterIfEvidenceComplete") and chapter_marked_complete_in_repo(repo, plan_path):
        return GuardVerdict(
            True,
            False,
            True,
            "SKIP_ALREADY_COMPLETE",
            "chapter evidence already COMPLETE; repair queue / skip relay",
            {"planPath": plan_path},
        )
    return assess_phase_plan(repo, plan_path, guards=g)


def write_guard_report(repo_root: Path, verdict: GuardVerdict) -> Path:
    repo = repo_root.resolve()
    out_dir = repo / "artifacts" / "orchestrator"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "OPERATOR_GUARD_REPORT.md"
    lines = [
        "# PPE operator guard report",
        "",
        f"- **code**: `{verdict.code}`",
        f"- **stop**: `{verdict.stop}`",
        f"- **skip_chapter**: `{verdict.skip_chapter}`",
        f"- **message**: {verdict.message}",
        "",
        "## details",
        "",
        "```json",
        json.dumps(verdict.details, indent=2),
        "```",
        "",
        "Resume: fix the issue, then `run_ppe.cmd` or `run_ppe_auto.cmd` from repo root.",
        "For CONTEXT_ESCALATE, prefer a new thread with `docs/SOP/AGENT_CONTINUITY_BRIEF.md` only.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
