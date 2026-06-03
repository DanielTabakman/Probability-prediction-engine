"""Advisory context preflight before IDE BUILD or continuous run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_build_packet import build_packet_text
from scripts.ppe_context_bands import (
    advisory_actions,
    classify_line_count,
    file_line_count,
    score_build_packet,
    worst_band,
)
from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_operator_config import _guards_config, load_operator_config


def _plan_sprint_spec_paths(plan: dict) -> list[str]:
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


def run_preflight(
    repo: Path,
    *,
    phase_plan: str,
    slice_id: str | None = None,
) -> dict[str, object]:
    norm_plan = phase_plan.replace("\\", "/").strip()
    plan = load_phase_plan(repo, norm_plan)
    slices = plan.get("slices") or []

    cfg = load_operator_config(repo)
    g = _guards_config(cfg)
    max_slices = g.get("maxPhaseSlices")

    spec_reports: list[dict[str, object]] = []
    bands: list[str] = []
    for spec_rel in _plan_sprint_spec_paths(plan):
        n = file_line_count(repo, spec_rel)
        if n is None:
            spec_reports.append({"path": spec_rel, "missing": True})
            continue
        band = classify_line_count(n)
        bands.append(band)
        spec_reports.append({"path": spec_rel, "line_count": n, "band": band})

    slice_count = len(slices)
    slice_band = "NORMAL"
    if max_slices is not None:
        try:
            limit = int(max_slices)
            if limit > 0 and slice_count > limit:
                slice_band = "ESCALATE"
                bands.append("ESCALATE")
        except (TypeError, ValueError):
            pass

    packet_report: dict[str, object] | None = None
    if slice_id:
        text = build_packet_text(repo, slice_id=slice_id, phase_plan=norm_plan)
        packet_report = score_build_packet(text)
        bands.append(str(packet_report["band"]))

    overall = worst_band(*bands) if bands else "NORMAL"
    return {
        "phase_plan": norm_plan,
        "slice_count": slice_count,
        "max_phase_slices": max_slices,
        "slice_count_band": slice_band,
        "sprint_specs": spec_reports,
        "build_packet": packet_report,
        "overall_band": overall,
        "advisory_actions": advisory_actions(overall),
    }


def _print_report(report: dict[str, object]) -> None:
    print(f"ppe_context_preflight: plan={report['phase_plan']}")
    print(f"  slices: {report['slice_count']} (max configured: {report['max_phase_slices']})")
    if report.get("slice_count_band") == "ESCALATE":
        print("  slice_count: ESCALATE (> configured maxPhaseSlices)")

    for spec in report.get("sprint_specs") or []:
        if not isinstance(spec, dict):
            continue
        if spec.get("missing"):
            print(f"  sprint_spec: {spec['path']} MISSING")
            continue
        print(f"  sprint_spec: {spec['path']} — {spec['band']} ({spec['line_count']} lines)")

    bp = report.get("build_packet")
    if isinstance(bp, dict):
        print(f"  build_packet: {bp.get('band')} ({bp.get('line_count')} lines)")

    print(f"  overall (advisory): {report['overall_band']}")
    for action in report.get("advisory_actions") or []:
        print(f"    - {action}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Advisory context preflight for phase plans.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--phase-plan", required=True)
    ap.add_argument("--slice-id", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when overall band is ESCALATE (default: advisory exit 0)",
    )
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    report = run_preflight(repo, phase_plan=args.phase_plan, slice_id=args.slice_id)

    if args.json:
        sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        _print_report(report)

    if args.strict and report.get("overall_band") == "ESCALATE":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
