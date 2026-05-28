"""Unified PPE run entry (full phase default). Invoked by run_ppe.cmd."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from scripts.ppe_auto_chain import chapter_is_complete, resume_incomplete_phase
from scripts.ppe_auto_select import run_auto_select
from scripts.ppe_google_docs_refresh import refresh_google_docs_on_queue_idle
from scripts.ppe_manifest import load_manifest, load_phase_plan, set_manifest_status
from scripts.ppe_preflight import run_preflight
from scripts.ppe_troubleshooter import (
    maybe_open_promotion_pr_for_blocked,
    maybe_recover_stop_for_review,
)
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


def _run_slice_impl(repo: Path, slice_id: str, plan_path: str) -> int:
    env = os.environ.copy()
    env["PPE_PHASE_PLAN"] = plan_path
    env["PYTHONPATH"] = str(repo)
    manifest = load_manifest(repo)
    sprint = str(manifest.get("sprintSpecPath") or "").strip()
    if not sprint:
        plan = load_phase_plan(repo, plan_path)
        sprint = str(plan.get("sprintSpecPath") or "docs/SOP/SPRINT_VALIDATION_CHAPTER.md")
    slice_cmd = repo / "run_slice.cmd"
    if not slice_cmd.is_file():
        print("ERROR: run_slice.cmd not found", file=sys.stderr)
        return 2
    return _run_cmd(
        ["cmd", "/c", str(slice_cmd), slice_id, sprint, "", plan_path],
        cwd=repo,
        env=env,
    )


def cmd_run_phase(repo: Path, plan_path: str, *, auto_resume: bool) -> int:
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

    try:
        set_manifest_status(repo, "RUNNING")
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

    phase_cmd = repo / "run_phase.cmd"
    if not phase_cmd.is_file():
        print("ERROR: run_phase.cmd not found", file=sys.stderr)
        return 2

    exit_code = _run_cmd(["cmd", "/c", str(phase_cmd), plan_path], cwd=repo, env=env)

    if auto_resume and exit_code != 0:
        recovered, resume_code = resume_incomplete_phase(
            repo,
            plan_path,
            run_slice=lambda sid: _run_slice_impl(repo, sid, plan_path),
        )
        if recovered and resume_code == 0:
            print("ppe_run: auto-resume recovered phase")
            exit_code = 0

    # Troubleshooter: auto-recover common STOP_FOR_REVIEW cases (promotion locks, closeout not applied).
    if auto_resume and exit_code == 20:
        try:
            recovered = maybe_recover_stop_for_review(
                repo=repo,
                plan_path=plan_path,
                run_slice=lambda sid: _run_slice_impl(repo, sid, plan_path),
            )
            if recovered:
                print("ppe_run: troubleshooter recovered STOP_FOR_REVIEW")
                exit_code = 0
        except Exception as e:
            print(f"WARN: troubleshooter failed: {e}")

    # If relay BLOCKED due to promotion drift, try opening a PR automatically.
    if auto_resume and exit_code == 40:
        try:
            url = maybe_open_promotion_pr_for_blocked(repo=repo)
            if url:
                print(f"ppe_run: opened promotion PR: {url}")
        except Exception as e:
            print(f"WARN: promotion PR open failed: {e}")

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


def _on_queue_idle(repo: Path, *, reason: str) -> None:
    """Best-effort MSOS Google Doc refresh when no READY queue chapter remains."""
    try:
        refresh_google_docs_on_queue_idle(repo, reason=reason)
    except Exception as e:
        print(f"ppe_run: WARN google docs idle refresh skipped: {e}")


def _try_select_next_chapter(repo: Path) -> tuple[bool, str]:
    """Auto-select after COMPLETE. Returns (selected, plan_path)."""
    sel_rc = run_auto_select(repo, apply=True, select_only=False, mark_done=False, force=False)
    if sel_rc != 0:
        return False, ""
    manifest = load_manifest(repo)
    plan_path = str(manifest.get("phasePlanPath") or "").strip()
    status = str(manifest.get("status") or "").strip().upper()
    if status == "READY" and plan_path:
        return True, plan_path
    return False, ""


def cmd_auto_chain_loop(
    repo: Path,
    *,
    max_chapters: int,
    auto_resume: bool,
    initial_plan: str | None = None,
) -> int:
    """Run phases until queue idle, failure, or max_chapters."""
    plan_path = initial_plan
    for chapter in range(1, max_chapters + 1):
        if not plan_path:
            selected, plan_path = _try_select_next_chapter(repo)
            if not selected:
                print("ppe_run: auto-chain idle (no READY queue chapter)")
                _on_queue_idle(repo, reason="auto-chain: no READY queue chapter")
                return 0
            print(f"ppe_run: auto-chain chapter {chapter}/{max_chapters} -> {plan_path}")

        exit_code = cmd_run_phase(repo, plan_path, auto_resume=auto_resume)
        if exit_code != 0:
            print(f"ppe_run: auto-chain stop (phase exit {exit_code})")
            return exit_code

        if not chapter_is_complete(repo, plan_path):
            print("ppe_run: auto-chain stop (chapter not complete after phase)")
            return exit_code

        plan_path = ""
        if chapter >= max_chapters:
            break

    print(f"ppe_run: auto-chain finished ({max_chapters} chapter slot(s))")
    _on_queue_idle(repo, reason="auto-chain: finished chapter slots")
    return 0


def cmd_run_slice(repo: Path, slice_id: str, plan_path: str, *, auto_chain: bool, auto_resume: bool) -> int:
    exit_code = _run_slice_impl(repo, slice_id, plan_path)
    if exit_code != 0 or not auto_chain:
        return exit_code
    if not chapter_is_complete(repo, plan_path):
        return exit_code
    selected, next_plan = _try_select_next_chapter(repo)
    if not selected:
        _on_queue_idle(repo, reason="slice closeout: no next READY chapter")
        return exit_code
    print(f"ppe_run: slice closeout complete; auto-chain -> {next_plan}")
    return cmd_run_phase(repo, next_plan, auto_resume=auto_resume)


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
        help="Auto-chain up to --continuous-max chapters (implies --auto-chain).",
    )
    ap.add_argument(
        "--continuous-max",
        type=int,
        default=5,
        help="Max chapters per --continuous / default auto-chain (default 5).",
    )
    ap.add_argument(
        "--auto-chain",
        action="store_true",
        default=None,
        help="After chapter COMPLETE, auto-select and run next READY queue chapter (default on).",
    )
    ap.add_argument(
        "--no-auto-chain",
        action="store_true",
        help="Do not start the next READY queue chapter after closeout.",
    )
    ap.add_argument(
        "--no-auto-resume",
        action="store_true",
        help="Do not auto-run remaining slices after a partial phase stop (e.g. BLOCKED).",
    )
    args = ap.parse_args(argv)

    repo = _repo_root(args.repo_root)

    env_chain = os.environ.get("PPE_AUTO_CHAIN", "").strip().lower()
    if args.no_auto_chain:
        auto_chain = False
    elif args.auto_chain:
        auto_chain = True
    elif env_chain in {"0", "false", "no"}:
        auto_chain = False
    else:
        auto_chain = True

    auto_resume = not args.no_auto_resume and os.environ.get("PPE_AUTO_RESUME", "").strip().lower() not in {
        "0",
        "false",
        "no",
    }

    if args.status:
        return cmd_status(repo)
    if args.dry_run:
        return cmd_dry_run(repo)

    max_chapters = max(1, args.continuous_max)
    if args.continuous:
        auto_chain = True
        return cmd_auto_chain_loop(repo, max_chapters=max_chapters, auto_resume=auto_resume)

    plan_path = args.plan
    if not plan_path:
        try:
            manifest = load_manifest(repo)
            plan_path = str(manifest.get("phasePlanPath") or "").strip()
        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    if args.slice:
        if not plan_path:
            print("ERROR: --slice requires phase plan in manifest or --plan", file=sys.stderr)
            return 1
        return cmd_run_slice(
            repo,
            args.slice,
            plan_path,
            auto_chain=auto_chain,
            auto_resume=auto_resume,
        )

    if not plan_path:
        if auto_chain:
            return cmd_auto_chain_loop(repo, max_chapters=1, auto_resume=auto_resume)
        print("ERROR: no phase plan (set ACTIVE_PHASE_MANIFEST.json or use --plan)", file=sys.stderr)
        return 1

    exit_code = cmd_run_phase(repo, plan_path, auto_resume=auto_resume)
    if exit_code != 0 or not auto_chain:
        return exit_code
    if not chapter_is_complete(repo, plan_path):
        return exit_code

    selected, next_plan = _try_select_next_chapter(repo)
    if not selected:
        _on_queue_idle(repo, reason="chapter complete: no next READY chapter")
        return exit_code
    print(f"ppe_run: chapter complete; auto-chain -> {next_plan}")
    return cmd_run_phase(repo, next_plan, auto_resume=auto_resume)


if __name__ == "__main__":
    raise SystemExit(main())
