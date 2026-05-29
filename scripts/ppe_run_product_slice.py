"""Run one product slice via agent-cli (explicit Cursor spend; bypasses PPE_SKIP_ACP)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_manifest, load_phase_plan
from scripts.ppe_operator_guards import load_guards
from scripts.ppe_slice_worker_mode import infer_slice_kind


def _find_slice(plan: dict[str, Any], slice_id: str) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and str(sl.get("sliceId") or "").strip() == slice_id:
            return sl
    return None


def _resolve_plan_path(repo: Path, plan_arg: str | None) -> str:
    if plan_arg and str(plan_arg).strip():
        return str(plan_arg).strip().replace("\\", "/")
    manifest = load_manifest(repo)
    plan_path = str(manifest.get("phasePlanPath") or "").strip().replace("\\", "/")
    if not plan_path:
        raise ValueError(
            "no --plan and manifest phasePlanPath is empty; pass a phase plan path or set ACTIVE_PHASE_MANIFEST.json"
        )
    return plan_path


def validate_product_slice(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str,
    require_touch_set: bool | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (plan, slice_obj). Raises ValueError on preflight failure."""
    plan = load_phase_plan(repo, plan_path)
    sl = _find_slice(plan, slice_id)
    if sl is None:
        raise ValueError(f"slice {slice_id!r} not found in phase plan {plan_path}")

    kind = infer_slice_kind(slice_id, sl)
    plan_mode = str(sl.get("workerMode") or sl.get("worker") or "").strip().lower()
    if kind != "product" and plan_mode not in ("local-agent", "agent-cli", "agent"):
        raise ValueError(
            f"slice {slice_id!r} is not a product slice "
            f"(kind={kind!r}); set workerMode=local-agent on the slice or use a Product slice id"
        )

    if require_touch_set is None:
        require_touch_set = bool(load_guards(repo).get("requireTouchSetOnProductSlices", True))
    if require_touch_set:
        touch = sl.get("touchSet")
        if not isinstance(touch, list) or not touch:
            raise ValueError(f"product slice {slice_id!r} missing non-empty touchSet in phase plan")

    return plan, sl


def apply_product_slice_env() -> None:
    os.environ["PPE_OPERATOR_ENV_APPLIED"] = "1"
    os.environ["PPE_SKIP_ACP"] = "0"
    os.environ["PPE_WORKER_MODE"] = "local-agent"
    os.environ["PPE_RUN_KIND"] = "product_slice"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Run one product slice with agent-cli (bypasses auto-operator PPE_SKIP_ACP)",
    )
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", required=True)
    ap.add_argument("--plan", type=str, default=None, help="Phase plan path (default: manifest phasePlanPath)")
    ap.add_argument(
        "--no-require-touch-set",
        action="store_true",
        help="Skip touchSet preflight (not recommended)",
    )
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    slice_id = str(args.slice_id).strip()
    if not slice_id:
        print("ERROR: empty --slice-id", file=sys.stderr)
        return 2

    try:
        plan_path = _resolve_plan_path(repo, args.plan)
        validate_product_slice(
            repo,
            slice_id=slice_id,
            plan_path=plan_path,
            require_touch_set=not args.no_require_touch_set,
        )
    except (ValueError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    apply_product_slice_env()
    print(f"ppe_run_product_slice: slice={slice_id} plan={plan_path} worker=local-agent (agent-cli)")

    from scripts.ppe_run import main as ppe_run_main

    return ppe_run_main(
        [
            "--repo-root",
            str(repo),
            "--slice",
            slice_id,
            "--plan",
            plan_path,
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
