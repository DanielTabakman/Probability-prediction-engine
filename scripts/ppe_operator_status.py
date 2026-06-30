"""Operator status: verdict + next commands before auto-loop or IDE BUILD."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_auto_select import choose_next_plan
from scripts.ppe_ide_build_starter import format_ide_build_resume, starter_path
from scripts.ppe_operator_hint import PPE_GO_HINT, append_ppe_go_hint
from scripts.ppe_manifest import load_manifest, resolve_summary
from scripts.ppe_operator_guards import (
    GUARD_EXIT,
    GUARD_SKIP_CHAPTER,
    GuardResult,
    evaluate_continuous_guards,
)
from scripts.ppe_preflight import run_preflight
from scripts.ppe_propagate_queue import (
    backlog_path,
    load_backlog,
    promote_first_blocked_with_plan,
)
from scripts.ppe_queue import load_queue
from scripts.ppe_thread_roles import infer_suggest_thread_rotate

STATUS_REPORT_REL = "artifacts/orchestrator/OPERATOR_STATUS.md"
NOTIFY_REL = "artifacts/control_plane/OPERATOR_STATUS_NOTIFY.json"

VERDICT_RUN_AUTO = "RUN_AUTO"
VERDICT_RUN_LOCAL = "RUN_LOCAL"
VERDICT_IDE_BUILD = "IDE_BUILD"
VERDICT_FIX_PLAN = "FIX_PLAN"
VERDICT_SUPPLY_LOW = "SUPPLY_LOW"
VERDICT_STALE_STATE = "STALE_STATE"
VERDICT_ERROR = "ERROR"

STOP_VERDICTS = frozenset({VERDICT_IDE_BUILD, VERDICT_FIX_PLAN, VERDICT_STALE_STATE, VERDICT_ERROR})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _backlog_counts(repo: Path) -> dict[str, int]:
    counts = {"queued": 0, "blocked": 0, "chartered": 0, "done": 0, "other": 0}
    if not backlog_path(repo).is_file():
        return counts
    backlog = load_backlog(repo)
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        st = str(item.get("status") or "").strip().lower()
        if st in counts:
            counts[st] += 1
        else:
            counts["other"] += 1
    return counts


def _queue_ready_count(repo: Path) -> int:
    queue = load_queue(repo)
    return sum(
        1
        for item in (queue.get("items") or [])
        if isinstance(item, dict) and str(item.get("status") or "").upper() == "READY"
    )


def _analyze_supply(repo: Path) -> dict[str, Any]:
    counts = _backlog_counts(repo)
    promote = promote_first_blocked_with_plan(repo, apply=False)
    return {
        "backlog": counts,
        "queue_ready": _queue_ready_count(repo),
        "next_promotable_blocked": promote if promote.get("promoted") else None,
        "promote_reason": promote.get("reason"),
    }


def _stale_running(repo: Path, *, manifest_status: str) -> bool:
    if manifest_status != "RUNNING":
        return False
    active = repo / "artifacts" / "orchestrator" / "ACTIVE_RUN.json"
    return not active.is_file()


def _primary_product_slice(plan_path: str, guard: GuardResult) -> str | None:
    if guard.reason != "PRODUCT_BLOCKED" or not guard.detail:
        return None
    left = guard.detail.find("[")
    right = guard.detail.find("]")
    if left < 0 or right <= left:
        return None
    ids = [s.strip() for s in guard.detail[left + 1 : right].split(",") if s.strip()]
    return ids[0] if ids else None


def _commands_for_verdict(
    *,
    verdict: str,
    plan_path: str | None,
    product_slice: str | None,
) -> list[str]:
    if verdict == VERDICT_IDE_BUILD:
        return [PPE_GO_HINT]
    if verdict == VERDICT_RUN_LOCAL:
        return [PPE_GO_HINT]
    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        return [PPE_GO_HINT]
    if verdict == VERDICT_RUN_AUTO:
        return ["run_ppe_auto_local_loop.cmd"]
    if verdict == VERDICT_SUPPLY_LOW:
        return [
            "Add status=queued rows to docs/SOP/PHASE_CHAPTER_BACKLOG.json",
            "run_ppe_auto_local_loop.cmd  (will idle-sleep until work appears)",
        ]
    if verdict == VERDICT_STALE_STATE:
        return [
            "Inspect artifacts/orchestrator/LAST_RUN_REPORT.md",
            "If no slice is running: set manifest status READY or run run_ppe_local.cmd",
        ]
    if verdict == VERDICT_FIX_PLAN:
        return ["Fix phase plan or sprint spec, then run_ppe_operator.cmd again"]
    return []


def _avoid_commands(verdict: str) -> list[str]:
    if verdict == VERDICT_IDE_BUILD:
        return ["run_ppe_auto_local_loop.cmd  (will hit PRODUCT_BLOCKED)"]
    if verdict == VERDICT_RUN_LOCAL:
        return ["run_ppe_auto_local_loop.cmd  (use run_ppe_local.cmd once first)"]
    if verdict == VERDICT_FIX_PLAN:
        return ["run_ppe_auto_local_loop.cmd"]
    return []


def _maybe_heal_idle_queue(repo: Path) -> dict[str, Any]:
    """When manifest is idle, repair roadmap drift and bootstrap the next READY row."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return {}
    out: dict[str, Any] = {}
    try:
        manifest = load_manifest(repo)
    except Exception:
        return out

    status = str(manifest.get("status") or "").strip().upper()
    if status not in ("COMPLETE", ""):
        return out
    if str(manifest.get("phasePlanPath") or "").strip():
        return out
    if _queue_ready_count(repo) > 0:
        return out

    from scripts.ppe_queue_health import repair_roadmap

    roadmap_fixes, _ = repair_roadmap(repo, apply=True)
    if roadmap_fixes:
        out["roadmap_repair"] = roadmap_fixes

    try:
        from scripts.ppe_propagate_queue import maybe_propagate_queue

        prop = maybe_propagate_queue(repo, apply=True)
        if prop.get("propagated") or prop.get("roadmap_repair") or prop.get("chartered_promote"):
            out["propagate"] = prop
    except Exception as exc:
        out["propagate_error"] = str(exc)

    if _queue_ready_count(repo) == 0:
        try:
            from scripts.ppe_roadmap import bootstrap_next_ready

            boot = bootstrap_next_ready(repo, apply=True)
            if boot.get("bootstrapped"):
                out["bootstrap"] = boot
        except Exception as exc:
            out["bootstrap_error"] = str(exc)

    if _queue_ready_count(repo) > 0:
        try:
            manifest = load_manifest(repo)
        except Exception:
            manifest = {}
        if not str(manifest.get("phasePlanPath") or "").strip():
            try:
                from scripts.ppe_auto_select import run_auto_select

                out["auto_select_exit"] = run_auto_select(
                    repo,
                    apply=True,
                    select_only=False,
                    mark_done=False,
                    force=False,
                )
            except Exception as exc:
                out["auto_select_error"] = str(exc)

    return out


def collect_operator_status(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    idle_heal = _maybe_heal_idle_queue(repo)
    errors: list[str] = []
    try:
        summary = resolve_summary(repo)
    except Exception as exc:
        return {
            "verdict": VERDICT_ERROR,
            "exit_code": 1,
            "errors": [str(exc)],
            "commands": [],
            "avoid": [],
        }

    errors.extend(str(e) for e in summary.get("errors") or [])
    manifest_status = str(summary.get("status") or "").strip().upper()
    plan_path = str(summary.get("phase_plan_path") or "").strip() or None
    supply = _analyze_supply(repo)
    preflight = run_preflight(repo, allow_complete=True, allow_running=True, check_orchestrator=False)

    guard = GuardResult(exit_code=0, plan_path=plan_path or "")
    if plan_path:
        try:
            guard = evaluate_continuous_guards(repo, plan_path)
        except Exception as exc:
            errors.append(f"guard evaluation failed: {exc}")

    stale = _stale_running(repo, manifest_status=manifest_status)
    if stale:
        from scripts.ppe_active_run import heal_stale_running_manifest

        if heal_stale_running_manifest(repo):
            manifest_status = "READY"
            stale = False
            summary = resolve_summary(repo)
    product_slice: str | None = None
    if plan_path and guard.reason == "PRODUCT_BLOCKED":
        from scripts.ppe_ide_product_ready import next_pending_product_slice

        product_slice = next_pending_product_slice(repo, plan_path=plan_path)
    if not product_slice:
        product_slice = _primary_product_slice(plan_path or "", guard)

    verdict = VERDICT_RUN_AUTO
    exit_code = 0
    blocker: str | None = None

    if errors:
        verdict = VERDICT_ERROR
        exit_code = 1
        blocker = "; ".join(errors)
    elif stale:
        verdict = VERDICT_STALE_STATE
        exit_code = GUARD_EXIT
        blocker = "manifest RUNNING but artifacts/orchestrator/ACTIVE_RUN.json is missing"
    elif guard.exit_code == GUARD_EXIT:
        verdict = VERDICT_FIX_PLAN if guard.reason in ("CONTEXT_ESCALATE", "CONTEXT_WATCH", "TOO_MANY_SLICES") else VERDICT_IDE_BUILD
        if guard.reason == "PRODUCT_BLOCKED":
            verdict = VERDICT_IDE_BUILD
        exit_code = GUARD_EXIT
        blocker = guard.detail or guard.reason
    elif guard.exit_code == GUARD_SKIP_CHAPTER:
        verdict = VERDICT_RUN_AUTO
        blocker = guard.detail
    elif guard.reason == "IDE_MARKER_OK":
        verdict = VERDICT_RUN_LOCAL
        blocker = "IDE product marker present — finish chapter with run_ppe_local"
    elif manifest_status == "READY" and plan_path:
        verdict = VERDICT_RUN_AUTO
    elif manifest_status in ("COMPLETE", "") and not plan_path:
        _, select_reason = choose_next_plan(repo)
        if select_reason == "no READY items in queue" and not supply.get("next_promotable_blocked"):
            if supply["backlog"].get("queued", 0) == 0:
                verdict = VERDICT_SUPPLY_LOW
                blocker = "no READY queue item and no promotable blocked backlog chapter"
        else:
            verdict = VERDICT_SUPPLY_LOW
            blocker = select_reason
    elif manifest_status == "RUNNING":
        verdict = VERDICT_SUPPLY_LOW
        exit_code = 0
        blocker = "phase RUNNING — waiting for in-flight pass to finish"

    commands = _commands_for_verdict(verdict=verdict, plan_path=plan_path, product_slice=product_slice)
    avoid = _avoid_commands(verdict)
    rotate = infer_suggest_thread_rotate(
        verdict=verdict,
        manifest_status=manifest_status,
        plan_path=plan_path or "",
    )

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "exit_code": exit_code,
        "chapter_name": summary.get("chapter_name"),
        "manifest_status": manifest_status,
        "phase_plan_path": plan_path,
        "blocker": blocker,
        "guard": {
            "exit_code": guard.exit_code,
            "reason": guard.reason,
            "detail": guard.detail,
        },
        "supply": supply,
        "preflight_ok": preflight.get("ok"),
        "preflight_warnings": preflight.get("warnings") or [],
        "commands": commands,
        "avoid": avoid,
        "errors": errors,
        "idle_heal": idle_heal or None,
        **rotate,
    }


def prepare_operator_status(repo: Path) -> dict[str, Any]:
    """Apply operator config env, then collect status (CLI / handoff / burst parity)."""
    try:
        from scripts.ppe_operator_config import apply_operator_env

        apply_operator_env(repo)
    except Exception:
        pass
    return collect_operator_status(repo)


def _format_burst_summary(burst_plan: dict[str, Any] | None) -> list[str]:
    if not burst_plan:
        return []
    allowed = bool(burst_plan.get("burst_allowed"))
    lines = [
        "Burst: "
        f"max_workers={burst_plan.get('max_cycles')} "
        f"band={burst_plan.get('overall_band')} "
        f"remaining={burst_plan.get('remaining_count')} "
        f"allowed={'true' if allowed else 'false'}"
    ]
    if allowed and burst_plan.get("use_director"):
        lines.append(
            "Burst path: read artifacts/control_plane/BURST_PLAN.json → @ppe-director "
            "(adaptive burst default; ppe_go.cmd --single to opt out)"
        )
    elif not allowed:
        lines.append("Burst path: single verdict only — split slice or trim spec before chaining workers")
    return lines


def _format_human(
    status: dict[str, Any],
    repo: Path | None = None,
    *,
    burst_plan: dict[str, Any] | None = None,
) -> str:
    lines = [
        f"VERDICT: {status.get('verdict')}",
        "",
    ]
    if status.get("chapter_name"):
        lines.append(f"Chapter: {status['chapter_name']}")
    if status.get("manifest_status"):
        lines.append(f"Manifest: {status['manifest_status']}")
    if status.get("phase_plan_path"):
        lines.append(f"Plan: {status['phase_plan_path']}")
    if status.get("blocker"):
        lines.append(f"Blocker: {status['blocker']}")
    supply = status.get("supply") or {}
    backlog = supply.get("backlog") or {}
    lines.append(
        "Supply: "
        f"queued={backlog.get('queued', 0)} "
        f"blocked={backlog.get('blocked', 0)} "
        f"queue_READY={supply.get('queue_ready', 0)}"
    )
    try:
        from scripts.ppe_workflow_cost import operator_lane_line

        if repo is not None:
            lines.append(operator_lane_line(repo))
    except Exception:
        pass
    next_promo = supply.get("next_promotable_blocked")
    if isinstance(next_promo, dict) and next_promo.get("chapterId"):
        lines.append(f"Next after closeout: {next_promo.get('chapterId')} ({next_promo.get('planPath')})")
    elif supply.get("promote_reason") and status.get("verdict") == VERDICT_SUPPLY_LOW:
        lines.append(f"Promote: {supply.get('promote_reason')}")

    burst = burst_plan if burst_plan is not None else status.get("burst_plan")
    if isinstance(burst, dict):
        lines.extend(_format_burst_summary(burst))

    cmds = status.get("commands") or []
    if cmds:
        lines.extend(["", "Do this:"])
        for i, cmd in enumerate(cmds, 1):
            lines.append(f"  {i}. {cmd}")
    avoid = status.get("avoid") or []
    if avoid:
        lines.extend(["", "Do NOT run:"])
        for item in avoid:
            lines.append(f"  - {item}")
    warnings = status.get("preflight_warnings") or []
    if warnings:
        lines.extend(["", "Preflight warnings:"])
        for w in warnings:
            lines.append(f"  - {w}")
    errors = status.get("errors") or []
    if errors:
        lines.extend(["", "Errors:"])
        for e in errors:
            lines.append(f"  - {e}")
    if status.get("suggest_thread_rotate"):
        from scripts.ppe_thread_roles import THREAD_ROTATE_FOOTER

        lines.extend(
            [
                "",
                "Thread rotate (recommended)",
                f"Reason: {status.get('thread_rotate_reason')}",
                str(status.get("thread_rotate_message") or ""),
                THREAD_ROTATE_FOOTER,
            ]
        )
    return "\n".join(lines) + "\n"


def _format_brief(status: dict[str, Any]) -> str:
    verdict = status.get("verdict", VERDICT_ERROR)
    exit_code = status.get("exit_code", 1)
    plan = status.get("phase_plan_path") or ""
    return f"VERDICT={verdict} exit={exit_code} plan={plan}"


def write_status_report(repo: Path, status: dict[str, Any], *, sync_burst: bool = True) -> Path:
    out = repo / STATUS_REPORT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    burst_plan: dict[str, Any] | None = None
    if sync_burst:
        try:
            from scripts.ppe_burst_plan import refresh_burst_plan

            burst_plan = refresh_burst_plan(repo, status)
            status["burst_plan"] = burst_plan
        except Exception:
            pass
    whats_next_block = ""
    try:
        from scripts.ppe_context_window_closeout import load_whats_next_markdown

        wn = load_whats_next_markdown(repo)
        if wn:
            # Inject body only (skip duplicate H1 if present).
            body_lines = wn.splitlines()
            if body_lines and body_lines[0].startswith("# "):
                body_lines = body_lines[2:] if len(body_lines) > 2 and not body_lines[1].strip() else body_lines[1:]
            whats_next_block = "\n## What's next (last context closeout)\n\n" + "\n".join(body_lines).strip() + "\n"
    except ImportError:
        pass
    body = f"""# Operator status

**As-of:** {status.get("as_of")}
**Verdict:** `{status.get("verdict")}`

{_format_human(status, repo, burst_plan=burst_plan)}
{whats_next_block}"""
    out.write_text(body, encoding="utf-8")
    try:
        from scripts.ppe_operator_compass import sync_compass

        sync_compass(repo, status=status, patch_map=True)
    except Exception:
        pass
    return out


def _write_notify_payload(repo: Path, status: dict[str, Any]) -> Path:
    out = repo / NOTIFY_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    verdict = str(status.get("verdict") or "")
    body = append_ppe_go_hint(str(status.get("blocker") or _format_brief(status)), verdict, repo=repo)
    payload = {
        "as_of": status.get("as_of"),
        "verdict": status.get("verdict"),
        "exit_code": status.get("exit_code"),
        "title": f"PPE operator: {status.get('verdict')}",
        "body": body,
    }
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def _maybe_auto_remote_build(repo: Path, status: dict[str, Any]) -> dict[str, Any] | None:
    """CLI build or IDE handoff when loop hits IDE_BUILD guard stop."""
    if str(status.get("verdict") or "") != VERDICT_IDE_BUILD:
        return None
    try:
        from scripts.ppe_ide_handoff import ide_handoff_enabled, respond_to_ide_build
        from scripts.ppe_operator_config import auto_remote_build_enabled
        from scripts.ppe_remote_build_agent import read_build_lock
    except ImportError:
        return None
    if not auto_remote_build_enabled(repo) and not ide_handoff_enabled(repo):
        return None
    if read_build_lock(repo):
        return None
    return respond_to_ide_build(
        repo,
        source="loop-guard",
        note="auto-triggered by operator loop on IDE_BUILD guard stop",
    )


def _notify_mobile(repo: Path, *, status: dict[str, Any] | None = None) -> None:
    auto_build = _maybe_auto_remote_build(repo, status or {}) if status else None
    push = repo / "scripts" / "ppe_notify_push.py"
    if not push.is_file():
        return
    if auto_build and auto_build.get("started"):
        if auto_build.get("notified"):
            return
        mode = str(auto_build.get("mode") or auto_build.get("action") or "build")
        if mode == "ide_handoff":
            title = f"PPE IDE handoff: {auto_build.get('slice_id') or 'IDE_BUILD'}"
            body = append_ppe_go_hint(
                str(auto_build.get("message") or "IDE BUILD ready."),
                VERDICT_IDE_BUILD,
                repo=repo,
            )
        else:
            title = f"PPE auto-build started: {auto_build.get('slice_id') or 'IDE_BUILD'}"
            body = str(auto_build.get("message") or "Agent CLI running on desktop.")
        subprocess.run(
            [
                sys.executable,
                str(push),
                "--title",
                title,
                "--body",
                body,
                "--verdict",
                VERDICT_IDE_BUILD,
            ],
            cwd=repo,
            check=False,
        )
        return
    payload = repo / NOTIFY_REL
    if not payload.is_file():
        return
    subprocess.run(
        [sys.executable, str(push), "--payload", str(payload)],
        cwd=repo,
        check=False,
    )


def _notify_windows(repo: Path, *, status: dict[str, Any]) -> None:
    ps = repo / "scripts" / "notify_operator_status.ps1"
    if ps.is_file():
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ps),
                "-RepoRoot",
                str(repo),
            ],
            cwd=repo,
            check=False,
        )
    _notify_mobile(repo, status=status)


def _configure_stdio_utf8() -> None:
    """Avoid UnicodeEncodeError on Windows cp1252 consoles (e.g. arrows in PPE_GO_HINT)."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def main(argv: list[str] | None = None) -> int:
    _configure_stdio_utf8()
    ap = argparse.ArgumentParser(description="PPE operator status and next-command verdict")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Print JSON only")
    ap.add_argument("--brief", action="store_true", help="One-line verdict for loop wrappers")
    ap.add_argument("--notify", action="store_true", help="Windows toast when verdict needs attention")
    ap.add_argument("--no-write", action="store_true", help="Do not write OPERATOR_STATUS.md")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    status = prepare_operator_status(repo)

    if not args.no_write:
        report = write_status_report(repo, status)
        if not args.brief and not args.json:
            print(f"ppe_operator_status: report={report}")

    if args.json:
        print(json.dumps(status, indent=2))
    elif args.brief:
        print(_format_brief(status))
    else:
        print(_format_human(status, repo), end="")

    if args.notify and status.get("verdict") in STOP_VERDICTS:
        from scripts.ppe_guard_notify_dedup import record_guard_notify, should_skip_guard_notify

        if should_skip_guard_notify(repo, status):
            if not args.brief and not args.json:
                print("ppe_operator_status: guard notify skipped (dedup cooldown)")
        else:
            _write_notify_payload(repo, status)
            _notify_windows(repo, status=status)
            record_guard_notify(repo, status)

    return int(status.get("exit_code") or 0)


if __name__ == "__main__":
    raise SystemExit(main())
