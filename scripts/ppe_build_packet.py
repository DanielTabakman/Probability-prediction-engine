"""Generate slim BUILD packets (paths only) for IDE / relay handoff."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.ppe_context_bands import score_build_packet
from scripts.ppe_manifest import load_manifest, load_phase_plan
from scripts.ppe_slice_worker_mode import infer_slice_kind
from scripts.repo_layer_paths import (
    find_slice_in_plan,
    format_build_packet_layer_block,
    resolve_slice_layer_scope,
)

BUILD_PACKET_DIR = "artifacts/orchestrator"
CONTINUITY_BRIEF = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"


def _git_head(repo: Path) -> str | None:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return (proc.stdout or "").strip() or None


def build_packet_text(repo: Path, *, slice_id: str, phase_plan: str) -> str:
    norm_plan = phase_plan.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    sl = find_slice_in_plan(plan, slice_id)
    if sl is None:
        raise SystemExit(f"slice_id not in plan: {slice_id}")

    declared_plane = str(sl.get("declaredPlane") or "EVIDENCE-PLANE")
    scope = resolve_slice_layer_scope(
        repo,
        slice_obj=sl,
        slice_id=slice_id,
        declared_plane=declared_plane,
    )
    layer_block = format_build_packet_layer_block(scope)
    sprint = str(sl.get("sprintSpecPath") or plan.get("sprintSpecPath") or "").strip()
    build_branch = str(sl.get("buildBranch") or f"build/auto/{slice_id}").strip()
    baseline = str(plan.get("baselineBranch") or "main").strip()

    parts = [
        "EXECUTION STEP: BUILD",
        f"PLANE: {declared_plane}",
        layer_block,
        f"SLICE_ID: {slice_id}",
        f"PHASE_PLAN: {norm_plan}",
    ]
    if sprint:
        parts.append(f"SPRINT_SPEC: {sprint}")
    selection = str(plan.get("selectionRecord") or plan.get("selectionOutcomeDoc") or "").strip()
    if selection:
        parts.append(f"SELECTION: {selection}")
    parts.extend(
        [
            f"CONTINUITY_BRIEF: {CONTINUITY_BRIEF}",
            f"BASELINE_BRANCH: {baseline}",
            f"BUILD_BRANCH: {build_branch}",
        ]
    )
    return "\n".join(parts) + "\n"


def build_packet_path(slice_id: str) -> str:
    safe = slice_id.replace("/", "_").replace("\\", "_")
    return f"{BUILD_PACKET_DIR}/BUILD_PACKET_{safe}.txt"


def first_product_slice_id(repo: Path, phase_plan: str) -> str | None:
    plan = load_phase_plan(repo, phase_plan)
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        slice_id = str(sl.get("sliceId") or "").strip()
        if slice_id and infer_slice_kind(slice_id, sl) == "product":
            return slice_id
    return None


def resolve_from_manifest(repo: Path) -> tuple[str, str]:
    manifest = load_manifest(repo)
    plan_path = str(manifest.get("phasePlanPath") or "").strip()
    if not plan_path:
        raise SystemExit("manifest phasePlanPath is empty")
    slice_id = first_product_slice_id(repo, plan_path)
    if not slice_id:
        raise SystemExit("no product slice in active phase plan")
    return slice_id, plan_path


def write_build_packet(
    repo: Path,
    *,
    slice_id: str,
    phase_plan: str,
    stdout_only: bool = False,
) -> Path | None:
    text = build_packet_text(repo, slice_id=slice_id, phase_plan=phase_plan)
    if stdout_only:
        sys.stdout.write(text)
        return None
    out = repo / build_packet_path(slice_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate slim BUILD packet for a slice.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--slice-id", type=str, default=None)
    ap.add_argument("--phase-plan", type=str, default=None)
    ap.add_argument("--manifest", action="store_true", help="Use active manifest + first product slice")
    ap.add_argument("--stdout", action="store_true", help="Print packet to stdout only")
    ap.add_argument("--score", action="store_true", help="Print context band after generation")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.manifest:
        slice_id, phase_plan = resolve_from_manifest(repo)
    else:
        if not args.slice_id or not args.phase_plan:
            ap.error("--slice-id and --phase-plan required unless --manifest")
        slice_id = args.slice_id
        phase_plan = args.phase_plan

    text = build_packet_text(repo, slice_id=slice_id, phase_plan=phase_plan)
    if args.stdout:
        sys.stdout.write(text)
    else:
        out = write_build_packet(repo, slice_id=slice_id, phase_plan=phase_plan)
        print(f"ppe_build_packet: wrote {out}")

    if args.score:
        scored = score_build_packet(text)
        print(f"ppe_build_packet: band={scored['band']} lines={scored['line_count']}")
        for action in scored.get("advisory_actions") or []:
            print(f"  - {action}")

    head = _git_head(repo)
    if head:
        print(f"ppe_build_packet: HEAD={head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
