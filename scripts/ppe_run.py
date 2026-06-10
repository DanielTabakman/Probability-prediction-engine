"""Unified PPE run entry (full phase default). Invoked by run_ppe.cmd."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.ppe_auto_select import choose_next_plan, run_auto_select
from scripts.ppe_manifest import load_manifest, load_phase_plan, save_manifest, set_manifest_status
from scripts.ppe_preflight import run_preflight
from scripts.resolve_active_phase import main as resolve_main


def _repo_root(explicit: Path | None) -> Path:
    return (explicit or Path.cwd()).resolve()


def _windows_cmdline(argv: list[str]) -> str:
    """Build a cmd.exe command line (list2cmdline over-escapes for cmd /c on some paths)."""
    parts: list[str] = []
    for arg in argv:
        if arg == "":
            parts.append('""')
        elif any(c in arg for c in " \t"):
            parts.append(f'"{arg}"')
        else:
            parts.append(arg)
    return " ".join(parts)


def _run_cmd(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> int:
    # Windows: avoid cmd /c argv splitting on repo paths with spaces (use shell=True).
    if sys.platform == "win32" and len(cmd) >= 3 and cmd[0].lower() == "cmd" and cmd[1].lower() == "/c":
        line = _windows_cmdline(cmd[2:])
        print(f"ppe_run: {line}")
        return subprocess.run(line, shell=True, cwd=cwd, env=env).returncode
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
    return 0 if pf["ok"] else 1 if rc == 0 else rc


def cmd_run_phase(repo: Path, plan_path: str) -> int:
    env = os.environ.copy()
    env["PPE_PHASE_PLAN"] = plan_path
    env["PYTHONPATH"] = str(repo)
    if not env.get("PPE_WORKER_MODE") and env.get("PPE_SKIP_ACP", "").lower() in ("1", "true", "yes"):
        env["PPE_WORKER_MODE"] = "deterministic"
    skip_orchestrator = env.get("PPE_SKIP_ACP", "").lower() in ("1", "true", "yes") or (
        env.get("PPE_WORKER_MODE") or ""
    ).strip().lower() in ("deterministic", "local")
    pf = run_preflight(repo, check_orchestrator=not skip_orchestrator)
    if not pf["ok"]:
        for e in pf["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    for w in pf.get("warnings") or []:
        print(f"WARN: {w}")

    try:
        set_manifest_status(repo, "RUNNING")
        manifest = load_manifest(repo)
        wm = str(manifest.get("workerMode") or "").strip().lower()
        if wm and not env.get("PPE_WORKER_MODE"):
            env["PPE_WORKER_MODE"] = wm
            if wm == "deterministic":
                env.setdefault("PPE_SKIP_ACP", "1")
    except Exception as e:
        print(f"WARN: could not set manifest RUNNING: {e}")

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

    worker_mode = (env.get("PPE_WORKER_MODE") or "").strip().lower()
    if worker_mode in ("deterministic", "local") or env.get("PPE_SKIP_ACP", "").lower() in (
        "1",
        "true",
        "yes",
    ):
        exit_code = subprocess.run(
            [sys.executable, str(repo / "scripts" / "ppe_relay_phase.py"), "--repo-root", str(repo), "--plan", plan_path],
            cwd=repo,
            env=env,
        ).returncode
    else:
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
        try:
            from scripts.ui_smoke_diagnose import diagnose_stop_for_review, format_diagnosis

            diagnosis = diagnose_stop_for_review(repo_root=repo, exit_code=exit_code, relay=None)
            if diagnosis:
                print("")
                print("ppe_run: smoke auto-diagnosis")
                print(format_diagnosis(diagnosis))
        except Exception as e:
            print(f"WARN: smoke auto-diagnosis skipped: {e}")

    report_path = repo / "artifacts" / "orchestrator" / "LAST_RUN_REPORT.md"
    print("")
    print(f"ppe_run: exit_code={exit_code}")
    print(f"ppe_run: report={report_path}")
    if report_path.is_file():
        ritual = "Open a NEW Cursor thread; load only docs/SOP/AGENT_CONTINUITY_BRIEF.md"
        print(f"ppe_run: {ritual}")
    return exit_code


def _idle_hydrate_and_select(repo: Path) -> bool:
    """Re-run backlog propagate + steward + bootstrap; select READY if one appears."""
    from scripts.ppe_roadmap import prepare_selection_idle

    prep = prepare_selection_idle(repo, apply=True)
    print(f"ppe_run: idle hydrate {json.dumps(prep)}")
    plan_path, reason = choose_next_plan(repo)
    if not plan_path:
        return False
    plan = load_phase_plan(repo, plan_path)
    manifest = load_manifest(repo)
    manifest["phasePlanPath"] = plan_path
    manifest["sprintSpecPath"] = str(plan.get("sprintSpecPath") or manifest.get("sprintSpecPath") or "").strip()
    manifest["selectionRecord"] = str(plan.get("selectionRecord") or manifest.get("selectionRecord") or "").strip()
    manifest["status"] = "READY"
    manifest["notes"] = f"idle hydrate selected: {reason}"
    save_manifest(repo, manifest)
    return True


def cmd_continuous(repo: Path, *, max_chapters: int = 20) -> int:
    """Run phases back-to-back until queue empty, failure, or max_chapters."""
    for chapter in range(1, max_chapters + 1):
        print(f"ppe_run: continuous chapter {chapter}/{max_chapters}")
        sel_rc = run_auto_select(repo, apply=True, select_only=False, mark_done=False, force=False)
        if sel_rc != 0:
            print(f"ppe_run: continuous stop (auto-select exit {sel_rc})")
            return sel_rc

        try:
            manifest = load_manifest(repo)
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        plan_path = str(manifest.get("phasePlanPath") or "").strip()
        status = str(manifest.get("status") or "").strip().upper()
        if status != "READY" or not plan_path:
            if _idle_hydrate_and_select(repo):
                manifest = load_manifest(repo)
                plan_path = str(manifest.get("phasePlanPath") or "").strip()
                status = str(manifest.get("status") or "").strip().upper()
            if status != "READY" or not plan_path:
                print("ppe_run: continuous idle (no READY manifest / empty plan)")
                return 0

        try:
            from scripts.ppe_operator_config import operator_enabled
            from scripts.ppe_operator_guards import run_continuous_guards

            if operator_enabled(repo):
                from scripts.ppe_operator_guards import GUARD_SKIP_CHAPTER

                guard_rc = run_continuous_guards(repo, plan_path)
                if guard_rc == GUARD_SKIP_CHAPTER:
                    print("ppe_run: continuous skip chapter (guard)")
                    continue
                if guard_rc != 0:
                    return guard_rc
        except Exception as exc:
            print(f"WARN: continuous guards skipped: {exc}")

        exit_code = cmd_run_phase(repo, plan_path)
        if exit_code != 0:
            try:
                manifest = load_manifest(repo)
                if str(manifest.get("status") or "").strip().upper() == "COMPLETE":
                    print("ppe_run: continuous continue (phase exit non-zero but manifest COMPLETE)")
                    continue
            except Exception:
                pass
            print(f"ppe_run: continuous stop (phase exit {exit_code})")
            return exit_code

        manifest = load_manifest(repo)
        if str(manifest.get("status") or "").strip().upper() != "COMPLETE":
            print("ppe_run: continuous stop (phase ended without COMPLETE manifest)")
            return exit_code

    print(f"ppe_run: continuous stop (reached max chapters {max_chapters})")
    return 0


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
    ap.add_argument(
        "--continuous",
        action="store_true",
        help="After each chapter COMPLETE, auto-select and run next READY queue item (max 5).",
    )
    ap.add_argument(
        "--continuous-max",
        type=int,
        default=20,
        help="Max chapters per --continuous invocation (default 20).",
    )
    args = ap.parse_args(argv)

    repo = _repo_root(args.repo_root)

    if args.status:
        return cmd_status(repo)
    if args.dry_run:
        return cmd_dry_run(repo)
    if args.continuous:
        if args.slice:
            print("ERROR: --continuous cannot be used with --slice", file=sys.stderr)
            return 2
        return cmd_continuous(repo, max_chapters=max(1, args.continuous_max))

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
