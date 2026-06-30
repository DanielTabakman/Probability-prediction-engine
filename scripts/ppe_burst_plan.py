"""Adaptive burst plan — preflight sizing + dynamic worker/cycle cap for PPE burst mode."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_context_bands import max_burst_cycles
from scripts.ppe_context_preflight import run_preflight
from scripts.ppe_operator_status import (
    VERDICT_FIX_PLAN,
    VERDICT_IDE_BUILD,
    VERDICT_RUN_LOCAL,
    VERDICT_STALE_STATE,
    VERDICT_ERROR,
    prepare_operator_status,
)
from scripts.ppe_phase_plan_window import non_closeout_slices_pending

BURST_PLAN_REL = "artifacts/control_plane/BURST_PLAN.json"

WORKER_VERDICTS = frozenset({VERDICT_IDE_BUILD, VERDICT_RUN_LOCAL})
TRIAGE_VERDICTS = frozenset({VERDICT_FIX_PLAN, VERDICT_STALE_STATE, VERDICT_ERROR})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _resolve_product_slice(repo: Path, status: dict[str, Any]) -> str | None:
    plan_path = str(status.get("phase_plan_path") or "").strip()
    guard = status.get("guard") or {}
    reason = str(guard.get("reason") or "")
    if plan_path and reason == "PRODUCT_BLOCKED":
        try:
            from scripts.ppe_ide_product_ready import next_pending_product_slice

            sid = next_pending_product_slice(repo, plan_path=plan_path)
            if sid:
                return sid
        except ImportError:
            pass
    detail = str(guard.get("detail") or status.get("blocker") or "")
    left = detail.find("[")
    right = detail.find("]")
    if left >= 0 and right > left:
        ids = [s.strip() for s in detail[left + 1 : right].split(",") if s.strip()]
        if ids:
            return ids[0]
    return None


def compute_burst_plan(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    if status is None:
        status = prepare_operator_status(repo)

    verdict = str(status.get("verdict") or VERDICT_ERROR)
    plan_path = str(status.get("phase_plan_path") or "").strip() or None
    product_slice = _resolve_product_slice(repo, status)

    pending: list[str] = []
    if plan_path:
        pending = non_closeout_slices_pending(repo, plan_path)
    remaining = len(pending)

    preflight_summary: dict[str, Any] | None = None
    overall_band = "NORMAL"
    if plan_path:
        preflight = run_preflight(repo, phase_plan=plan_path, slice_id=product_slice)
        overall_band = str(preflight.get("overall_band") or "NORMAL")
        preflight_summary = {
            "overall_band": overall_band,
            "slice_count": preflight.get("slice_count"),
            "build_packet_band": (preflight.get("build_packet") or {}).get("band")
            if isinstance(preflight.get("build_packet"), dict)
            else None,
            "ide_starter_band": (preflight.get("ide_starter") or {}).get("band")
            if isinstance(preflight.get("ide_starter"), dict)
            else None,
            "advisory_actions": preflight.get("advisory_actions") or [],
        }

    use_director = verdict in WORKER_VERDICTS
    director_recommended = verdict in WORKER_VERDICTS | TRIAGE_VERDICTS

    band_cap = max_burst_cycles(overall_band, director=use_director or verdict in TRIAGE_VERDICTS)
    max_cycles = band_cap
    if remaining > 0:
        max_cycles = min(max_cycles, remaining)

    if verdict in TRIAGE_VERDICTS:
        max_cycles = min(max_cycles, 1)
        use_director = True

    burst_allowed = max_cycles > 0 and verdict not in ("RUN_AUTO", "SUPPLY_LOW")

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "phase_plan_path": plan_path,
        "product_slice": product_slice,
        "pending_slices": pending,
        "remaining_count": remaining,
        "preflight": preflight_summary,
        "overall_band": overall_band,
        "max_cycles": max_cycles,
        "use_director": use_director,
        "director_recommended": director_recommended,
        "burst_allowed": burst_allowed,
        "worker_verdicts_only": True,
        "prompt": format_burst_director_prompt(
            max_cycles=max_cycles,
            overall_band=overall_band,
            remaining=remaining,
            verdict=verdict,
            burst_allowed=burst_allowed,
        ),
    }


def format_burst_director_prompt(
    *,
    max_cycles: int,
    overall_band: str,
    remaining: int,
    verdict: str,
    burst_allowed: bool,
) -> str:
    if not burst_allowed:
        return (
            "@ppe-director Burst blocked (band=ESCALATE or max_cycles=0). "
            "Read artifacts/control_plane/BURST_PLAN.json. Triage only — do not chain BUILD workers."
        )
    return (
        f"@ppe-director Adaptive burst mode. max_workers={max_cycles} "
        f"(band={overall_band}, remaining_slices={remaining}, verdict={verdict}). "
        "Read artifacts/control_plane/BURST_PLAN.json first. "
        "Spawn ppe-build-worker / ppe-finish-worker only for IDE_BUILD and RUN_LOCAL. "
        "Triage verdicts: one ppe-triage-worker max. Terminal loop running."
    )


def write_burst_plan(repo: Path, plan: dict[str, Any]) -> Path:
    out = repo / BURST_PLAN_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return out


def refresh_burst_plan(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    """Compute adaptive burst plan and write BURST_PLAN.json (operator status parity)."""
    plan = compute_burst_plan(repo, status)
    write_burst_plan(repo, plan)
    return plan


def load_burst_plan(repo: Path) -> dict[str, Any] | None:
    path = repo / BURST_PLAN_REL
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    return data if isinstance(data, dict) else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compute adaptive PPE burst plan from operator status + preflight.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"Write {BURST_PLAN_REL}")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    plan = compute_burst_plan(repo)

    if args.write:
        path = write_burst_plan(repo, plan)
        if not args.json:
            print(f"ppe_burst_plan: wrote {path.relative_to(repo)}")

    if args.json:
        sys.stdout.write(json.dumps(plan, indent=2) + "\n")
    elif not args.write:
        print(f"ppe_burst_plan: verdict={plan['verdict']} max_cycles={plan['max_cycles']} band={plan['overall_band']}")
        print(f"  remaining_slices={plan['remaining_count']} use_director={plan['use_director']}")
        if not plan["burst_allowed"]:
            print("  burst_allowed=false — prefer single verdict or split slice")

    return 0 if plan.get("burst_allowed") else 2


if __name__ == "__main__":
    raise SystemExit(main())
