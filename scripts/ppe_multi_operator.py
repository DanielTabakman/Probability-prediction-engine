"""Aggregate autobuilder status across multiple operator instances (multi-clone hosts)."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MULTI_STATUS_REL = "artifacts/orchestrator/MULTI_OPERATOR_STATUS.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def collect_multi_operator_status(coordinator_repo: Path) -> dict[str, Any]:
    """Status snapshot for each enabled instance."""
    from scripts.ppe_operator_instance import list_enabled_instances, resolve_instance_for_repo

    coordinator_repo = coordinator_repo.resolve()
    instances = list_enabled_instances(coordinator_repo)
    rows: list[dict[str, Any]] = []
    for inst in instances:
        root = Path(str(inst.get("repoRoot") or coordinator_repo))
        row: dict[str, Any] = {
            "id": inst.get("id"),
            "label": inst.get("label"),
            "repoRoot": str(root),
            "reachable": root.is_dir(),
        }
        if not root.is_dir():
            row["error"] = "repo root missing"
            rows.append(row)
            continue
        try:
            from scripts.ppe_autobuilder import collect_autobuilder_status

            status = collect_autobuilder_status(root)
            row.update(
                {
                    "phase": status.get("phase"),
                    "verdict": status.get("verdict"),
                    "recommended_action": status.get("recommended_action"),
                    "active_plan": (status.get("operator") or {}).get("phase_plan_path"),
                    "next_after_closeout": (status.get("propagation_preview") or {}).get("next_plan_path"),
                    "stack_ok": (status.get("stack") or {}).get("stack_ok"),
                }
            )
        except Exception as exc:
            row["error"] = str(exc)
        rows.append(row)

    return {
        "version": 1,
        "as_of": _utc_now(),
        "coordinator": resolve_instance_for_repo(coordinator_repo),
        "instance_count": len(rows),
        "instances": rows,
    }


def write_multi_status(coordinator_repo: Path, data: dict[str, Any] | None = None) -> Path:
    coordinator_repo = coordinator_repo.resolve()
    payload = data if data is not None else collect_multi_operator_status(coordinator_repo)
    path = (coordinator_repo / MULTI_STATUS_REL).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def ensure_all_stacks(coordinator_repo: Path) -> dict[str, Any]:
    """Call autobuilder ensure on each reachable instance."""
    from scripts.ppe_autobuilder import action_ensure
    from scripts.ppe_operator_instance import list_enabled_instances

    results: list[dict[str, Any]] = []
    for inst in list_enabled_instances(coordinator_repo):
        root = Path(str(inst.get("repoRoot") or ""))
        if not root.is_dir():
            results.append({"id": inst.get("id"), "error": "missing repo"})
            continue
        try:
            out = action_ensure(root)
            results.append({"id": inst.get("id"), **out})
        except Exception as exc:
            results.append({"id": inst.get("id"), "error": str(exc)})
    return {"ensured": results}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Multi-operator coordinator status")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Coordinator repo (instances config host)")
    sub = ap.add_subparsers(dest="command", required=True)
    p_status = sub.add_parser("status", help="Collect status for all instances")
    p_status.add_argument("--json", action="store_true")
    p_status.add_argument("--write", action="store_true", help=f"Write {MULTI_STATUS_REL}")
    sub.add_parser("ensure", help="Ensure headless stack on each instance")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "ensure":
        out = ensure_all_stacks(repo)
        print(json.dumps(out, indent=2))
        return 0

    data = collect_multi_operator_status(repo)
    if args.write or not args.json:
        path = write_multi_status(repo, data)
        if not args.json:
            print(f"ppe_multi_operator: wrote {path}")
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        for row in data.get("instances") or []:
            print(
                f"  {row.get('id')}: phase={row.get('phase')} verdict={row.get('verdict')} "
                f"stack_ok={row.get('stack_ok')}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
