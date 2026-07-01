"""One-shot operator infrastructure doctor (autobuilder won't run these checks)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def run_operator_doctor(
    repo: Path,
    *,
    probe_ssh: bool = True,
    write_artifacts: bool = True,
) -> dict[str, Any]:
    repo = repo.resolve()
    report: dict[str, Any] = {"checks": []}

    try:
        from scripts.ppe_notify_push import bootstrap_operator_notify_env, ntfy_configured, notify_enabled

        bootstrap_operator_notify_env(repo)
        ntfy_ok = notify_enabled() and ntfy_configured()
        report["checks"].append({"id": "ntfy", "ok": ntfy_ok})
    except Exception as exc:
        report["checks"].append({"id": "ntfy", "ok": False, "error": str(exc)})

    try:
        from scripts.ppe_operator_blind_spots import _gh_auth_ok

        gh_ok, gh_err = _gh_auth_ok()
        report["checks"].append({"id": "gh_auth", "ok": gh_ok, "detail": gh_err or None})
    except Exception as exc:
        report["checks"].append({"id": "gh_auth", "ok": False, "error": str(exc)})

    if probe_ssh:
        try:
            from scripts.ppe_operator_vm_ssh import VM_SSH_HOST, ssh_vm

            ssh = ssh_vm("echo PPE_DOCTOR_OK", timeout=25)
            ok = bool(ssh.get("ok") and "PPE_DOCTOR_OK" in str(ssh.get("stdout") or ""))
            report["checks"].append(
                {
                    "id": "ssh_vm",
                    "ok": ok,
                    "host": VM_SSH_HOST,
                    "detail": (ssh.get("stderr") or ssh.get("stdout") or "")[:160] or None,
                }
            )
        except Exception as exc:
            report["checks"].append({"id": "ssh_vm", "ok": False, "error": str(exc)})

    try:
        from scripts.check_vm_host_health import collect_host_health, write_host_health

        host = collect_host_health(repo, via_ssh=probe_ssh)
        if write_artifacts:
            write_host_health(repo, host)
        report["vm_host_health"] = host
        report["checks"].append({"id": "vm_host_health", "ok": bool(host.get("healthy", True))})
    except Exception as exc:
        report["checks"].append({"id": "vm_host_health", "ok": False, "error": str(exc)})

    status: dict[str, Any] = {}
    try:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)
        report["verdict"] = status.get("verdict")
        report["chapter_mode"] = (status.get("chapter_mode") or {}).get("mode")
    except Exception as exc:
        report["status_error"] = str(exc)

    try:
        from scripts.ppe_operator_blind_spots import (
            assess_operator_blind_spots,
            write_blind_spots,
            write_operator_health,
        )

        blind = assess_operator_blind_spots(repo, status, probe_ssh=probe_ssh)
        if write_artifacts:
            write_blind_spots(repo, blind)
            write_operator_health(repo, blind)
        report["blind_spots"] = blind
    except Exception as exc:
        report["blind_spots_error"] = str(exc)

    try:
        from scripts.ppe_coordination_check import (
            assess_coordination_check,
            write_coordination_check,
        )

        coordination = assess_coordination_check(repo, status)
        if write_artifacts:
            write_coordination_check(repo, coordination)
        report["coordination_check"] = coordination
        report["checks"].append(
            {
                "id": "coordination",
                "ok": not coordination.get("blocks_burst"),
                "verdict": coordination.get("verdict"),
                "detail": coordination.get("summary"),
            }
        )
    except Exception as exc:
        report["coordination_check_error"] = str(exc)

    high = [
        i
        for i in (report.get("blind_spots") or {}).get("issues") or []
        if isinstance(i, dict) and i.get("severity") == "high"
    ]
    report["ok"] = not high and all(c.get("ok") for c in report.get("checks") or [] if isinstance(c, dict))
    return report


def format_doctor_report(report: dict[str, Any]) -> str:
    lines = ["PPE operator doctor", ""]
    verdict = report.get("verdict")
    mode = report.get("chapter_mode")
    if verdict:
        lines.append(f"Verdict: {verdict}" + (f"  mode={mode}" if mode else ""))
    blind = report.get("blind_spots") if isinstance(report.get("blind_spots"), dict) else {}
    line = blind.get("operator_health_line")
    if line:
        lines.append(str(line))
    coord = report.get("coordination_check") if isinstance(report.get("coordination_check"), dict) else {}
    if coord:
        lines.append(
            f"Coordination: {coord.get('verdict')} — {coord.get('summary')}"
        )
    lines.append("")
    for check in report.get("checks") or []:
        if not isinstance(check, dict):
            continue
        mark = "ok" if check.get("ok") else "FAIL"
        cid = check.get("id", "?")
        detail = check.get("detail") or check.get("error") or ""
        lines.append(f"  [{mark}] {cid}" + (f" — {detail}" if detail else ""))
    issues = blind.get("issues") or []
    if issues:
        lines.append("")
        lines.append("Blind spots:")
        for item in issues:
            if isinstance(item, dict):
                lines.append(f"  - [{item.get('severity')}] {item.get('message')}")
                fix = str(item.get("fix") or "").strip()
                if fix:
                    lines.append(f"      fix: {fix}")
    lines.append("")
    lines.append("OK" if report.get("ok") else "ACTION NEEDED")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Run operator infrastructure doctor (non-relay checks)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-ssh", action="store_true", help="Skip SSH probes (faster, offline)")
    ap.add_argument("--no-write", action="store_true", help="Do not write artifacts/control_plane/*")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    report = run_operator_doctor(
        repo,
        probe_ssh=not args.no_ssh,
        write_artifacts=not args.no_write,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_doctor_report(report))
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
