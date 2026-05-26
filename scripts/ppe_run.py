"""Unified PPE run entry (full phase default). Invoked by run_ppe.cmd."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from scripts.ppe_agent_healthcheck import run_agent_healthcheck
from scripts.ppe_git_network import local_git_only_enabled
from scripts.ppe_manifest import load_manifest, set_manifest_status
from scripts.ppe_preflight import run_preflight
from scripts.resolve_active_phase import main as resolve_main


def _repo_root(explicit: Path | None) -> Path:
    return (explicit or Path.cwd()).resolve()


def _run_cmd(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> int:
    print(f"ppe_run: {' '.join(cmd)}")
    return subprocess.run(cmd, cwd=cwd, env=env).returncode


def cmd_status(repo: Path) -> int:
    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    if active.is_file():
        print(f"ACTIVE_RUN: {active.read_text(encoding='utf-8')[:500]}")
    else:
        print("ACTIVE_RUN: none")
    last = repo / "artifacts" / "orchestrator" / "LAST_RUN_REPORT.md"
    if last.is_file():
        print(f"LAST_RUN_REPORT: {last}")
        print(last.read_text(encoding="utf-8")[:1200])
    return resolve_main(["--repo-root", str(repo)])


def cmd_dry_run(repo: Path) -> int:
    rc = resolve_main(["--repo-root", str(repo)])
    pf = run_preflight(repo)
    for w in pf.get("warnings") or []:
        print(f"WARN: {w}")
    for e in pf.get("errors") or []:
        print(f"ERROR: {e}", file=sys.stderr)
    if os.environ.get("PPE_SKIP_AGENT_CHECK", "").strip().lower() not in ("1", "true", "yes"):
        print("ppe_run: would run ppe_agent_healthcheck")
    if local_git_only_enabled():
        print("ppe_run: PPE_LOCAL_GIT_ONLY=1 (local commit/promotion; no git push)")
    return 0 if pf["ok"] else 1 if rc == 0 else rc


def _agent_health_gate(repo: Path) -> int:
    if os.environ.get("PPE_SKIP_AGENT_CHECK", "").strip().lower() in ("1", "true", "yes"):
        print("WARN: PPE_SKIP_AGENT_CHECK set — skipping Cursor Agent health gate")
        return 0
    hc = run_agent_healthcheck(repo)
    for w in hc.get("warnings") or []:
        print(f"WARN: {w}")
    for e in hc.get("errors") or []:
        print(f"ERROR: {e}", file=sys.stderr)
    return 0 if hc["ok"] else 1


def cmd_run_phase(repo: Path, plan_path: str) -> int:
    env = os.environ.copy()
    env["PPE_PHASE_PLAN"] = plan_path
    env["PYTHONPATH"] = str(repo)
    pf = run_preflight(repo)
    if not pf["ok"]:
        for e in pf["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    for w in pf.get("warnings") or []:
        print(f"WARN: {w}")

    agent_rc = _agent_health_gate(repo)
    if agent_rc != 0:
        return agent_rc

    if local_git_only_enabled():
        print(
            "WARN: PPE_LOCAL_GIT_ONLY=1 — commits/promotion are local only; "
            "git push and PR are deferred until an unrestricted network."
        )

    try:
        set_manifest_status(repo, "RUNNING")
    except Exception as e:
        print(f"WARN: could not set manifest RUNNING: {e}")

    refresh = repo / "scripts" / "google_docs_refresh.py"
    if refresh.is_file():
        refresh_env = env.copy()
        refresh_env["PYTHONPATH"] = str(repo)
        refresh_proc = subprocess.run(
            [
                sys.executable,
                str(refresh),
                "--repo-root",
                str(repo),
                "--trigger",
                "cycle-start",
            ],
            cwd=repo,
            env=refresh_env,
        )
        if refresh_proc.returncode != 0:
            print(
                f"WARN: google_docs_refresh (cycle-start) exit {refresh_proc.returncode}; "
                "continuing phase run"
            )

    log = repo / "scripts" / "log_event.py"
    if log.is_file():
        subprocess.run(
            [
                sys.executable,
                str(log),
                "--event-type",
                "run_ppe.start",
                "--summary",
                f"Start phase {plan_path}",
                "--actor",
                "wrapper",
                "--ref",
                "kind=cmd,path=run_ppe.cmd",
            ],
            cwd=repo,
            check=False,
        )

    phase_cmd = repo / "run_phase.cmd"
    if not phase_cmd.is_file():
        print("ERROR: run_phase.cmd not found", file=sys.stderr)
        return 2

    exit_code = _run_cmd(["cmd", "/c", str(phase_cmd), plan_path], cwd=repo, env=env)

    if log.is_file():
        subprocess.run(
            [
                sys.executable,
                str(log),
                "--event-type",
                "run_ppe.end",
                "--summary",
                f"End phase {plan_path} exit_code={exit_code}",
                "--actor",
                "wrapper",
            ],
            cwd=repo,
            check=False,
        )

    if exit_code != 0:
        try:
            manifest = load_manifest(repo)
            if manifest.get("status") == "RUNNING":
                set_manifest_status(repo, "READY")
        except Exception:
            pass

    report_path = repo / "artifacts" / "orchestrator" / "LAST_RUN_REPORT.md"
    print("")
    print(f"ppe_run: exit_code={exit_code}")
    print(f"ppe_run: report={report_path}")
    if report_path.is_file():
        ritual = "Open a NEW Cursor thread; load only docs/SOP/AGENT_CONTINUITY_BRIEF.md"
        print(f"ppe_run: {ritual}")
    return exit_code


def cmd_run_slice(repo: Path, slice_id: str, plan_path: str) -> int:
    env = os.environ.copy()
    env["PPE_PHASE_PLAN"] = plan_path
    manifest = load_manifest(repo)
    sprint = str(manifest.get("sprintSpecPath") or "docs/SOP/SPRINT_VALIDATION_CHAPTER.md")
    slice_cmd = repo / "run_slice.cmd"
    if not slice_cmd.is_file():
        print("ERROR: run_slice.cmd not found", file=sys.stderr)
        return 2
    return _run_cmd(
        ["cmd", "/c", str(slice_cmd), slice_id, sprint, "", plan_path],
        cwd=repo,
        env=env,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE unified run")
    ap.add_argument("--repo-root", type=Path, default=None)
    ap.add_argument("--plan", type=str, default=None, help="Override phase plan path")
    ap.add_argument("--slice", type=str, default=None, help="Run single slice (escape hatch)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--status", action="store_true")
    args = ap.parse_args(argv)

    repo = _repo_root(args.repo_root)

    if args.status:
        return cmd_status(repo)
    if args.dry_run:
        return cmd_dry_run(repo)

    plan_path = args.plan
    if not plan_path:
        try:
            manifest = load_manifest(repo)
            plan_path = str(manifest.get("phasePlanPath") or "").strip()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
    if not plan_path:
        print("ERROR: no phase plan (set ACTIVE_PHASE_MANIFEST.json or use --plan)", file=sys.stderr)
        return 1

    if args.slice:
        return cmd_run_slice(repo, args.slice, plan_path)
    return cmd_run_phase(repo, plan_path)


if __name__ == "__main__":
    raise SystemExit(main())
