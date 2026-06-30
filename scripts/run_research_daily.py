"""Daily research pipeline — run collectors then eligible tests from registry."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research_archive_health import build_archive_health, write_archive_health  # noqa: E402
from scripts.research_pipeline_registry import collectors, tests  # noqa: E402

SUMMARY_REL = "artifacts/control_plane/RESEARCH_DAILY_LAST.json"


def _health_by_id(repo: Path) -> dict[str, dict[str, Any]]:
    payload = build_archive_health(repo)
    return {
        str(item.get("id") or ""): item
        for item in (payload.get("collectors") or [])
        if isinstance(item, dict)
    }


def _collector_ready(health: dict[str, dict[str, Any]], collector_ids: list[str]) -> bool:
    for cid in collector_ids:
        item = health.get(cid) or {}
        if not item.get("ready"):
            return False
    return True


def _min_days_for_test(test: dict[str, Any], health: dict[str, dict[str, Any]]) -> tuple[int, int]:
    reads = [str(x) for x in (test.get("reads_collectors") or [])]
    min_test = int(test.get("min_calendar_days") or 0)
    if not reads:
        return 0, min_test
    have = min(int((health.get(cid) or {}).get("calendar_days") or 0) for cid in reads)
    return have, min_test


def _run_cmd(repo: Path, rel_cmd: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    cmd_path = repo / rel_cmd
    if not cmd_path.is_file():
        return {"cmd": rel_cmd, "ok": False, "error": "missing cmd wrapper"}
    argv = ["cmd.exe", "/c", str(cmd_path)] + (extra_args or [])
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
    return {
        "cmd": rel_cmd,
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def _run_python(repo: Path, rel_script: str, extra_args: list[str] | None = None) -> dict[str, Any]:
    script = repo / rel_script
    if not script.is_file():
        return {"script": rel_script, "ok": False, "error": "missing script"}
    argv = [sys.executable, str(script)] + (extra_args or [])
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True)
    return {
        "script": rel_script,
        "ok": proc.returncode == 0,
        "exit_code": proc.returncode,
        "stderr_tail": (proc.stderr or "")[-500:],
    }


def run_research_daily(
    repo: Path,
    *,
    collect: bool = True,
    run_tests: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    health = _health_by_id(repo)
    results: dict[str, Any] = {
        "as_of_utc": datetime.now(tz=UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "collectors": [],
        "tests": [],
        "skipped_tests": [],
    }

    if collect and not dry_run:
        for spec in collectors(repo):
            cmd = str(spec.get("cmd") or "")
            if cmd:
                results["collectors"].append(_run_cmd(repo, cmd))
            else:
                script = str(spec.get("script") or "")
                results["collectors"].append(_run_python(repo, script))
        write_archive_health(repo)
        health = _health_by_id(repo)
    elif collect and dry_run:
        for spec in collectors(repo):
            results["collectors"].append({"id": spec.get("id"), "dry_run": True, "cmd": spec.get("cmd")})

    results["archive_health"] = list(health.values())

    if not run_tests:
        return results

    for test in tests(repo):
        test_id = str(test.get("id") or "")
        have, need = _min_days_for_test(test, health)
        reads = [str(x) for x in (test.get("reads_collectors") or [])]
        if have < need:
            results["skipped_tests"].append(
                {
                    "id": test_id,
                    "reason": f"archive {have}/{need} calendar days",
                    "reads_collectors": reads,
                }
            )
            continue
        if dry_run:
            results["tests"].append({"id": test_id, "dry_run": True})
            continue
        cmd = str(test.get("cmd") or "")
        extra = [str(a) for a in (test.get("run_args") or [])]
        if cmd:
            outcome = _run_cmd(repo, cmd, extra)
        else:
            outcome = _run_python(repo, str(test.get("script") or ""), extra)
        outcome["id"] = test_id
        fatal = bool(test.get("fatal"))
        if not outcome.get("ok") and fatal:
            results["tests"].append(outcome)
            results["failed_fatal"] = test_id
            break
        results["tests"].append(outcome)

    return results


def write_summary(repo: Path, summary: dict[str, Any]) -> Path:
    out = repo / SUMMARY_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run research collectors and eligible tests")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--no-collect", action="store_true")
    ap.add_argument("--no-tests", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true", help="Write RESEARCH_DAILY_LAST.json")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    summary = run_research_daily(
        repo,
        collect=not args.no_collect,
        run_tests=not args.no_tests,
        dry_run=args.dry_run,
    )
    if args.write or not args.dry_run:
        write_summary(repo, summary)
    if summary.get("failed_fatal"):
        print(f"run_research_daily: fatal test failed: {summary['failed_fatal']}", file=sys.stderr)
        return 1
    failed = [t for t in summary.get("tests") or [] if not t.get("ok") and not t.get("dry_run")]
    if failed:
        print(f"run_research_daily: {len(failed)} test(s) failed (non-fatal)", file=sys.stderr)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
