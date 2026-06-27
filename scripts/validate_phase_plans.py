"""Validate phase plan JSON against PHASE_PLAN_SLICE_SCHEMA."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.ppe_manifest import (
    load_manifest,
    load_phase_plan,
    manifest_path,
    validate_phase_plan,
)


def _plan_paths(repo: Path, *, all_plans: bool, phase_plan: str | None) -> list[Path]:
    if phase_plan:
        p = Path(phase_plan)
        if not p.is_absolute():
            p = repo / p
        return [p]
    if all_plans:
        sop = repo / "docs" / "SOP" / "PHASE_PLANS"
        return sorted(sop.glob("*_relay.json"))
    return []


def _check_verify_nodes(repo: Path, plan: dict, plan_rel: str) -> list[str]:
    warnings: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "")
        for item in sl.get("acceptance") or []:
            if not isinstance(item, dict):
                continue
            verify = str(item.get("verify") or "").strip()
            if not verify.startswith("tests/"):
                continue
            test_file = verify.split("::", 1)[0]
            if not (repo / test_file).is_file():
                warnings.append(f"{sid}: acceptance verify path missing: {test_file}")
    return warnings


def validate_plans(
    repo: Path,
    *,
    paths: list[Path],
    strict: bool,
    check_test_names: bool,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in paths:
        rel = str(path.relative_to(repo)).replace("\\", "/")
        try:
            plan = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as e:
            errors.append(f"{rel}: invalid JSON: {e}")
            continue
        for msg in validate_phase_plan(plan, strict_agent_schema=strict):
            errors.append(f"{rel}: {msg}")
        if check_test_names:
            warnings.extend(_check_verify_nodes(repo, plan, rel))
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate phase plan slice schema.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--phase-plan", default=None, help="Single plan path (repo-relative)")
    ap.add_argument("--manifest", action="store_true", help="Validate ACTIVE_PHASE_MANIFEST plan")
    ap.add_argument("--all", action="store_true", help="All docs/SOP/PHASE_PLANS/*_relay.json")
    ap.add_argument(
        "--strict",
        action="store_true",
        help="Require touchSet on PRODUCT-PLANE slices (agent schema)",
    )
    ap.add_argument(
        "--check-test-names",
        action="store_true",
        help="Warn when acceptance verify pytest paths are missing (advisory)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    paths: list[Path] = []

    if args.manifest:
        if not manifest_path(repo).is_file():
            print("validate_phase_plans: manifest missing", file=sys.stderr)
            return 1
        manifest = load_manifest(repo)
        plan_rel = str(manifest.get("phasePlanPath") or "").strip()
        if not plan_rel:
            print("validate_phase_plans: manifest has empty phasePlanPath", file=sys.stderr)
            return 1
        paths.append(repo / plan_rel.replace("\\", "/"))
        if not args.strict:
            args.strict = str(manifest.get("status") or "").strip() in ("READY", "RUNNING")

    paths.extend(_plan_paths(repo, all_plans=args.all, phase_plan=args.phase_plan))

    if not paths:
        ap.error("Specify --phase-plan, --manifest, or --all")

    errors, warnings = validate_plans(
        repo,
        paths=paths,
        strict=args.strict,
        check_test_names=args.check_test_names,
    )

    if args.json:
        payload = {"errors": errors, "warnings": warnings, "plans_checked": len(paths)}
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        print(f"validate_phase_plans: checked {len(paths)} plan(s)")
        for w in warnings:
            print(f"  warn: {w}")
        for e in errors:
            print(f"  error: {e}")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
