"""Diagnose IDE BUILD automation wiring — which part is broken."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_ide_build_automation_trigger import (
    TRIGGER_REL,
    load_trigger,
    post_automation_webhook,
    trigger_path,
)

HEALTH_JSON_REL = "artifacts/orchestrator/IDE_BUILD_AUTOMATION_HEALTH.json"
HEALTH_MD_REL = "artifacts/orchestrator/IDE_BUILD_AUTOMATION_HEALTH.md"
LAST_ERROR_REL = "artifacts/orchestrator/IDE_BUILD_AUTOMATION_LAST_ERROR.json"
CURSOR_LOCAL_CMD = "ppe_operator_cursor.local.cmd"

# Exit: 0 all OK | 1 wiring broken | 2 quota/capacity only (retry later)
EXIT_OK = 0
EXIT_BROKEN = 1
EXIT_QUOTA_ONLY = 2


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _check(name: str, *, ok: bool, code: str, detail: str, fix: str, severity: str = "error") -> dict[str, Any]:
    return {
        "name": name,
        "ok": ok,
        "code": code,
        "detail": detail,
        "fix": fix,
        "severity": severity,
    }


def classify_webhook_failure(result: dict[str, Any]) -> str:
    if result.get("skipped"):
        return "WEBHOOK_NOT_CONFIGURED"
    if result.get("ok"):
        return "OK"
    detail = str(result.get("detail") or result.get("error") or "").lower()
    err = str(result.get("error") or "").lower()
    if "resource_exhausted" in detail or "resource_exhausted" in err:
        return "WEBHOOK_QUOTA_EXHAUSTED"
    if "401" in err or "403" in err or "unauthorized" in detail:
        return "WEBHOOK_AUTH_FAILED"
    if "404" in err:
        return "WEBHOOK_URL_NOT_FOUND"
    if "network" in detail or "timed out" in detail or "getaddrinfo" in detail:
        return "WEBHOOK_NETWORK_ERROR"
    return "WEBHOOK_HTTP_ERROR"


def run_health_checks(repo: Path, *, ping_webhook: bool = True) -> dict[str, Any]:
    repo = repo.resolve()
    checks: list[dict[str, Any]] = []

    url = os.environ.get("PPE_CURSOR_AUTOMATION_WEBHOOK_URL", "").strip()
    key = os.environ.get("PPE_CURSOR_AUTOMATION_WEBHOOK_KEY", "").strip()
    local_cmd = repo / CURSOR_LOCAL_CMD

    checks.append(
        _check(
            "cursor_local_cmd",
            ok=local_cmd.is_file(),
            code="MISSING_CURSOR_LOCAL_CMD" if not local_cmd.is_file() else "OK",
            detail=f"{CURSOR_LOCAL_CMD} {'present' if local_cmd.is_file() else 'missing'}",
            fix=f"Copy ppe_operator_cursor.local.cmd.example → {CURSOR_LOCAL_CMD} with webhook URL + key",
            severity="error" if not local_cmd.is_file() else "info",
        )
    )
    checks.append(
        _check(
            "webhook_url_env",
            ok=bool(url),
            code="MISSING_WEBHOOK_URL" if not url else "OK",
            detail="PPE_CURSOR_AUTOMATION_WEBHOOK_URL set" if url else "PPE_CURSOR_AUTOMATION_WEBHOOK_URL unset",
            fix=f"Set in {CURSOR_LOCAL_CMD} (see ppe_operator_cursor.local.cmd.example)",
        )
    )
    checks.append(
        _check(
            "webhook_key_env",
            ok=bool(key),
            code="MISSING_WEBHOOK_KEY" if not key else "OK",
            detail="PPE_CURSOR_AUTOMATION_WEBHOOK_KEY set" if key else "PPE_CURSOR_AUTOMATION_WEBHOOK_KEY unset",
            fix=f"Set Bearer key in {CURSOR_LOCAL_CMD}",
        )
    )

    try:
        from scripts.ppe_ide_handoff import ide_handoff_enabled

        handoff_on = ide_handoff_enabled(repo)
    except ImportError:
        handoff_on = True
    checks.append(
        _check(
            "ide_handoff",
            ok=handoff_on,
            code="IDE_HANDOFF_DISABLED" if not handoff_on else "OK",
            detail="IDE handoff enabled" if handoff_on else "IDE handoff disabled",
            fix="Set PPE_IDE_HANDOFF=1 or ideHandoff.enabled in PPE_AUTO_OPERATOR.local.json",
        )
    )

    try:
        from scripts.ppe_post_build_watcher import post_build_watcher_enabled

        watcher_on = post_build_watcher_enabled(repo)
    except ImportError:
        watcher_on = True
    checks.append(
        _check(
            "post_build_watcher",
            ok=watcher_on,
            code="POST_BUILD_WATCHER_DISABLED" if not watcher_on else "OK",
            detail="post-build watcher enabled" if watcher_on else "post-build watcher disabled",
            fix="ideHandoff.postBuildWatcher: true in PPE_AUTO_OPERATOR.local.json",
            severity="warning" if not watcher_on else "info",
        )
    )

    trigger_ok = False
    trigger_detail = ""
    try:
        tp = trigger_path(repo)
        tp.parent.mkdir(parents=True, exist_ok=True)
        trigger_ok = tp.parent.is_dir() and os.access(tp.parent, os.W_OK)
        trigger_detail = str(tp.relative_to(repo)).replace("\\", "/")
    except OSError as exc:
        trigger_detail = str(exc)
    checks.append(
        _check(
            "trigger_file",
            ok=trigger_ok,
            code="TRIGGER_NOT_WRITABLE" if not trigger_ok else "OK",
            detail=f"{TRIGGER_REL} writable" if trigger_ok else f"cannot write {TRIGGER_REL}: {trigger_detail}",
            fix="Ensure .cursor/ exists and is writable in repo root",
        )
    )

    trigger_data = load_trigger(repo)
    if trigger_data.get("status") == "pending":
        checks.append(
            _check(
                "trigger_pending",
                ok=True,
                code="TRIGGER_PENDING_SLICE",
                detail=f"pending slice {trigger_data.get('sliceId')!r} — automation should run when quota allows",
                fix="Wait for Cursor quota or run BUILD manually from starter",
                severity="info",
            )
        )

    webhook_result: dict[str, Any] = {"skipped": True}
    if ping_webhook and url:
        webhook_result = post_automation_webhook(
            repo,
            {"event": "ppe_health_ping", "note": "ignore unless slice pending"},
        )
        wh_code = classify_webhook_failure(webhook_result)
        wh_ok = wh_code == "OK"
        wh_severity = "error"
        wh_fix = "Check URL and Bearer key in ppe_operator_cursor.local.cmd"
        if wh_code == "WEBHOOK_QUOTA_EXHAUSTED":
            wh_severity = "quota"
            wh_fix = "Cursor background composer quota exhausted — retry after billing cycle or add credits"
        elif wh_code == "WEBHOOK_NOT_CONFIGURED":
            wh_ok = False
        checks.append(
            _check(
                "webhook_ping",
                ok=wh_ok,
                code=wh_code,
                detail=json.dumps(webhook_result, ensure_ascii=False),
                fix=wh_fix,
                severity=wh_severity,
            )
        )
    elif ping_webhook:
        checks.append(
            _check(
                "webhook_ping",
                ok=False,
                code="WEBHOOK_NOT_CONFIGURED",
                detail="skipped ping — URL not set",
                fix=f"Configure {CURSOR_LOCAL_CMD}",
            )
        )

    broken = [c for c in checks if not c["ok"] and c["severity"] == "error"]
    quota_only = (
        not broken
        and any(c["code"] == "WEBHOOK_QUOTA_EXHAUSTED" for c in checks)
    )
    warnings = [c for c in checks if not c["ok"] and c["severity"] == "warning"]

    if broken:
        verdict = "BROKEN"
        exit_code = EXIT_BROKEN
        blocker = broken[0]["code"]
        summary = f"Wiring broken: {blocker} — {broken[0]['fix']}"
    elif quota_only:
        verdict = "QUOTA_BLOCKED"
        exit_code = EXIT_QUOTA_ONLY
        blocker = "WEBHOOK_QUOTA_EXHAUSTED"
        summary = "Wiring OK; Cursor quota blocks cloud BUILD until capacity returns"
    elif warnings:
        verdict = "OK_WITH_WARNINGS"
        exit_code = EXIT_OK
        blocker = None
        summary = "Wiring OK with warnings — see report"
    else:
        verdict = "OK"
        exit_code = EXIT_OK
        blocker = None
        summary = "IDE BUILD automation wiring OK"

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "exit_code": exit_code,
        "blocker": blocker,
        "summary": summary,
        "checks": checks,
        "webhook_ping": webhook_result,
        "will_work_when_quota_returns": verdict in ("OK", "QUOTA_BLOCKED", "OK_WITH_WARNINGS"),
    }


def write_last_error(repo: Path, *, context: str, failure: dict[str, Any]) -> Path:
    repo = repo.resolve()
    path = repo / LAST_ERROR_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    code = classify_webhook_failure(failure) if "error" in failure or "skipped" in failure else str(
        failure.get("code") or "UNKNOWN"
    )
    body = {
        "as_of": _utc_now(),
        "context": context,
        "code": code,
        "failure": failure,
        "fix_hint": _fix_for_code(code),
    }
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return path


def _fix_for_code(code: str) -> str:
    fixes = {
        "WEBHOOK_QUOTA_EXHAUSTED": "Wait for Cursor quota reset or add credits; use manual BUILD (@ starter) meanwhile",
        "WEBHOOK_AUTH_FAILED": "Rotate webhook key in Cursor Automations; update ppe_operator_cursor.local.cmd",
        "WEBHOOK_URL_NOT_FOUND": "Recreate automation webhook URL; update ppe_operator_cursor.local.cmd",
        "WEBHOOK_NOT_CONFIGURED": "Copy ppe_operator_cursor.local.cmd.example and set URL + key",
        "MISSING_WEBHOOK_URL": "Set PPE_CURSOR_AUTOMATION_WEBHOOK_URL in ppe_operator_cursor.local.cmd",
        "MISSING_WEBHOOK_KEY": "Set PPE_CURSOR_AUTOMATION_WEBHOOK_KEY in ppe_operator_cursor.local.cmd",
        "IDE_HANDOFF_DISABLED": "Enable ideHandoff in PPE_AUTO_OPERATOR.local.json",
        "TRIGGER_NOT_WRITABLE": "Fix .cursor/ directory permissions",
    }
    return fixes.get(code, "Run: check_ide_build_automation.cmd — paste blocker code to steward thread")


def format_health_md(report: dict[str, Any]) -> str:
    lines = [
        "# IDE BUILD automation health",
        "",
        f"**As-of:** {report['as_of']}",
        f"**Verdict:** `{report['verdict']}`",
        f"**Summary:** {report['summary']}",
        "",
    ]
    if report.get("blocker"):
        lines.append(f"**Blocker code:** `{report['blocker']}`")
        lines.append("")
    lines.extend(
        [
            "## Will it work?",
            "",
            f"- **When quota returns:** {'yes' if report.get('will_work_when_quota_returns') else 'no — fix wiring first'}",
            "- **Cloud automation:** BUILD + commit on build branch (starter in webhook payload)",
            "- **Local loop:** `mark_ide_product_ready` + `run_ppe_local` via post-build watcher or `finish_ide_build.cmd`",
            "- **Manual fallback:** `@` starter in new Agent thread",
            "",
            "## Checks",
            "",
            "| OK | Code | Detail | Fix |",
            "|----|------|--------|-----|",
        ]
    )
    for c in report.get("checks") or []:
        mark = "yes" if c["ok"] else "no"
        lines.append(f"| {mark} | `{c['code']}` | {c['detail'][:120]} | {c['fix'][:80]} |")
    lines.extend(
        [
            "",
            "## Commands",
            "",
            "```bat",
            "check_ide_build_automation.cmd",
            "open_ide_handoff.cmd",
            "finish_ide_build.cmd",
            "```",
            "",
            f"Last handoff error: `{LAST_ERROR_REL}`",
        ]
    )
    return "\n".join(lines) + "\n"


def write_health_report(repo: Path, report: dict[str, Any]) -> tuple[Path, Path]:
    repo = repo.resolve()
    json_path = repo / HEALTH_JSON_REL
    md_path = repo / HEALTH_MD_REL
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(format_health_md(report), encoding="utf-8")
    return json_path, md_path


def main() -> int:
    ap = argparse.ArgumentParser(description="IDE BUILD automation health check")
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--no-ping", action="store_true", help="Skip webhook HTTP ping")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo = args.repo_root.resolve()

    report = run_health_checks(repo, ping_webhook=not args.no_ping)
    json_path, md_path = write_health_report(repo, report)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"ppe_ide_build_automation_health: {report['verdict']} — {report['summary']}")
        print(f"ppe_ide_build_automation_health: wrote {md_path}")

    return int(report["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
