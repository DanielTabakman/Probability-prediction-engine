"""Pre-flight guards for continuous auto-operator runs."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import _guards_config, guards_enabled, load_operator_config
from scripts.ppe_slice_worker_mode import infer_slice_kind

GUARD_REPORT_REL = "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
GUARD_EXIT = 7


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _skip_acp_active() -> bool:
    return os.environ.get("PPE_SKIP_ACP", "").strip().lower() in ("1", "true", "yes", "on")


def _plan_has_product_slice(repo: Path, plan_path: str) -> list[str]:
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


def write_guard_report(repo: Path, *, reason: str, detail: str, plan_path: str) -> Path:
    out = repo / GUARD_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    body = f"""# Operator guard stop

**As-of:** {_utc_now()}
**Reason:** `{reason}`
**Phase plan:** `{plan_path}`

## Detail

{detail}

## Resume

1. **Product slice:** BUILD in Cursor IDE (see `docs/SOP/BUILD_PACKET_TEMPLATE.md`), commit on the plan `buildBranch`, then `run_ppe_local.cmd`.
2. **Otherwise:** fix the issue, then `run_ppe.cmd` or `run_ppe_auto_local.cmd` from repo root.
"""
    out.write_text(body, encoding="utf-8")
    return out


def run_continuous_guards(repo: Path, plan_path: str) -> int:
    """Return 0 if ok to run phase; GUARD_EXIT (7) if operator must intervene."""
    if not guards_enabled(repo):
        return 0

    cfg = load_operator_config(repo)
    g = _guards_config(cfg)
    if g.get("blockProductUnderGlobalDeterministic", True) is False:
        return 0
    if not _skip_acp_active():
        return 0

    product_slices = _plan_has_product_slice(repo, plan_path)
    if not product_slices:
        return 0

    ids = ", ".join(product_slices)
    detail = (
        f"Phase plan contains product slice(s) [{ids}] but PPE_SKIP_ACP=1 (deterministic relay). "
        "Continuous auto cannot implement product code. Use IDE BUILD + run_ppe_local.cmd, "
        "or run with PPE_OPERATOR_PROFILE=acp when API credits are available."
    )
    report = write_guard_report(repo, reason="PRODUCT_BLOCKED", detail=detail, plan_path=plan_path)
    print(f"ppe_operator_guards: stop ({GUARD_EXIT}) — {detail}")
    print(f"ppe_operator_guards: report={report}")
    return GUARD_EXIT
