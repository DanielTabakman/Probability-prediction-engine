"""Read-only codebase health gate for local use and scheduled CI.

Runs queue audit, relay codebase_health_report, and control_plane_consistency_check.
Fails with exit code 1 when hard health criteria are not met.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.ppe_queue_health import run_queue_health

RELAY = ("scripts", "relay_runtime_v0.py")


def _latest_health_artifact(repo: Path, filename: str) -> Path | None:
    health_root = repo / "artifacts" / "health"
    if not health_root.is_dir():
        return None
    candidates = sorted(
        (p for p in health_root.glob(f"*/{filename}") if p.is_file()),
        key=lambda p: p.parent.name,
    )
    return candidates[-1] if candidates else None


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_relay_stage(repo: Path, job: str) -> int:
    cmd = [
        sys.executable,
        str(repo / RELAY[0] / RELAY[1]),
        "--repo-root",
        str(repo),
        "stage",
        job,
    ]
    print(f"+ {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=repo).returncode


def evaluate_queue(repo: Path) -> list[str]:
    result = run_queue_health(repo, apply=False)
    failures: list[str] = []
    if not result["ok"]:
        for issue in result["remaining_issues"]:
            failures.append(f"queue: {issue}")
    return failures


def evaluate_codebase_health_report(report: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    canonical = report.get("canonical_docs_present") or {}
    missing = [path for path, present in canonical.items() if not present]
    if missing:
        errors.extend(f"codebase_health: missing canonical doc {path}" for path in missing)

    unresolved = report.get("known_unresolved_items") or []
    if unresolved:
        warnings.extend(
            f"codebase_health: unresolved untracked path {path}" for path in unresolved[:10]
        )
        if len(unresolved) > 10:
            warnings.append(
                f"codebase_health: ... {len(unresolved) - 10} more unresolved untracked paths"
            )

    tree = report.get("tree_cleanliness") or {}
    for label, key in (("modified", "tracked_modified"), ("staged", "staged")):
        count = int(tree.get(key) or 0)
        if count:
            warnings.append(f"codebase_health: {count} tracked {label} file(s)")

    return errors, warnings


def evaluate_consistency_report(report: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    findings = report.get("findings") or []
    for finding in findings:
        severity = str(finding.get("severity") or "info")
        doc = finding.get("doc") or "?"
        locator = finding.get("locator") or "?"
        message = finding.get("message") or ""
        line = f"consistency: [{severity}] {doc} {locator}: {message}"
        if severity == "error":
            errors.append(line)
        elif severity == "warn":
            warnings.append(line)
        else:
            warnings.append(line)

    if not report.get("passed", False) and not errors:
        errors.append("consistency: report passed=false with no error findings")

    return errors, warnings


def run_gate(
    repo: Path,
    *,
    skip_relay: bool = False,
    skip_queue: bool = False,
) -> dict[str, Any]:
    repo = repo.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    artifacts: dict[str, str | None] = {
        "codebase_health_report": None,
        "control_plane_consistency_report": None,
    }

    if not skip_queue:
        errors.extend(evaluate_queue(repo))

    if not skip_relay:
        for job, artifact_name in (
            ("codebase_health_report", "codebase_health_report.json"),
            ("control_plane_consistency_check", "control_plane_consistency_report.json"),
        ):
            code = _run_relay_stage(repo, job)
            if code != 0:
                errors.append(f"relay stage {job} exited {code}")
                continue

            artifact = _latest_health_artifact(repo, artifact_name)
            if artifact is None:
                errors.append(f"missing artifact artifacts/health/*/{artifact_name}")
                continue

            artifacts[artifact_name.replace(".json", "")] = artifact.relative_to(repo).as_posix()
            report = _load_json(artifact)

            if artifact_name == "codebase_health_report.json":
                job_errors, job_warnings = evaluate_codebase_health_report(report)
            else:
                job_errors, job_warnings = evaluate_consistency_report(report)

            errors.extend(job_errors)
            warnings.extend(job_warnings)

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "artifacts": artifacts,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only codebase health gate")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Emit structured JSON summary")
    ap.add_argument("--skip-relay", action="store_true", help="Queue audit only (tests)")
    ap.add_argument("--skip-queue", action="store_true", help="Relay jobs only (tests)")
    args = ap.parse_args(argv)

    result = run_gate(
        args.repo_root,
        skip_relay=args.skip_relay,
        skip_queue=args.skip_queue,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=sys.stderr)
        for error in result["errors"]:
            print(f"FAIL: {error}", file=sys.stderr)
        if result["artifacts"]:
            for name, path in result["artifacts"].items():
                if path:
                    print(f"artifact: {name} -> {path}")
        if result["ok"]:
            print("codebase_health_gate: OK")
        else:
            print(f"codebase_health_gate: {len(result['errors'])} failure(s)", file=sys.stderr)

    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
