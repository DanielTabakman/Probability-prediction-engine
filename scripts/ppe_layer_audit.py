"""Audit working tree or diff against repo layer scope."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from scripts.repo_layer_paths import (
    LayerScope,
    audit_git_diff,
    audit_git_dirty,
    format_build_packet_layer_block,
    resolve_slice_layer_scope,
    scope_for_active_manifest,
)


def _load_scope_from_args(repo: Path, args: argparse.Namespace) -> LayerScope:
    if args.layer_preset:
        from scripts.repo_layer_paths import load_presets, scope_from_preset

        presets = load_presets(repo)
        return scope_from_preset(presets, args.layer_preset)
    if args.envelope:
        data = json.loads(Path(args.envelope).read_text(encoding="utf-8-sig"))
        scope = LayerScope.from_envelope(data.get("repo_layer"))
        if scope is None:
            raise SystemExit("envelope missing repo_layer block")
        return scope
    if args.manifest:
        scope = scope_for_active_manifest(repo)
        if scope is None:
            raise SystemExit("no layer scope from active manifest / phase plan")
        return scope
    if args.slice_id:
        from scripts.ppe_manifest import load_phase_plan

        plan_path = args.phase_plan
        if not plan_path:
            raise SystemExit("--phase-plan required with --slice-id")
        plan = load_phase_plan(repo, plan_path)
        from scripts.repo_layer_paths import find_slice_in_plan

        sl = find_slice_in_plan(plan, args.slice_id)
        if sl is None:
            raise SystemExit(f"slice_id not in plan: {args.slice_id}")
        return resolve_slice_layer_scope(
            repo,
            slice_obj=sl,
            slice_id=args.slice_id,
            declared_plane=str(sl.get("declaredPlane") or args.declared_plane or "EVIDENCE-PLANE"),
        )
    raise SystemExit("specify --layer-preset, --envelope, --manifest, or --slice-id + --phase-plan")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit paths against repo layer scope.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--print-packet-block", action="store_true")
    ap.add_argument("--layer-preset", type=str, default=None)
    ap.add_argument("--envelope", type=Path, default=None)
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--slice-id", type=str, default=None)
    ap.add_argument("--phase-plan", type=str, default=None)
    ap.add_argument("--declared-plane", type=str, default="EVIDENCE-PLANE")
    ap.add_argument("--dirty", action="store_true", help="Audit git status porcelain paths")
    ap.add_argument(
        "--diff",
        type=str,
        default=None,
        metavar="BASE_REF",
        help="Audit git diff name-only vs base (default HEAD when omitted with --dirty)",
    )
    ap.add_argument("--base-ref", type=str, default="origin/main")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    scope = _load_scope_from_args(repo, args)

    if args.print_packet_block:
        print(format_build_packet_layer_block(scope))
        return 0

    violations: list[str] = []
    if args.dirty:
        violations.extend(audit_git_dirty(repo, scope))
    if args.diff is not None:
        base = args.diff if args.diff else args.base_ref
        violations.extend(audit_git_diff(repo, scope, base_ref=base))

    if not args.dirty and args.diff is None:
        ap.error("specify --dirty and/or --diff")

    result = {
        "ok": not violations,
        "layer_preset": scope.layer_preset,
        "layer": scope.layer,
        "violations": violations,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    if violations:
        for v in violations:
            print(f"ERROR: {v}", file=sys.stderr)
        print(
            f"layer audit failed: preset={scope.layer_preset!r} "
            f"({len(violations)} path violation(s))",
            file=sys.stderr,
        )
        return 1

    print(f"OK: layer audit passed (preset={scope.layer_preset!r})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
