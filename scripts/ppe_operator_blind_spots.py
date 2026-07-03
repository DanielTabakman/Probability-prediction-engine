"""Operator blind spots — issues autobuilder / what's-next won't surface."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.ppe_operator_git_sync import VM_MIRROR_PUBLISH_PREFIX, _gh_available, _gh_json

BLIND_SPOTS_REL = "artifacts/control_plane/OPERATOR_BLIND_SPOTS.json"
HEALTH_REL = "artifacts/control_plane/OPERATOR_HEALTH.json"
MIRROR_PR_ESCALATE_SECONDS = 900
MIRROR_PR_NOTIFY_STATE_REL = "artifacts/control_plane/VM_MIRROR_PR_STALE_NOTIFY.json"


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _pr_age_seconds(pr: dict[str, Any]) -> float | None:
    created = _parse_utc(str(pr.get("createdAt") or ""))
    if created is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - created).total_seconds())


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _issue(
    issue_id: str,
    *,
    severity: str,
    message: str,
    fix: str = "",
) -> dict[str, str]:
    return {"id": issue_id, "severity": severity, "message": message, "fix": fix}


def _gh_auth_ok() -> tuple[bool, str]:
    if not _gh_available():
        return False, "gh CLI not installed"
    try:
        proc = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, "gh auth status failed"
    if proc.returncode == 0:
        return True, ""
    return False, (proc.stderr or proc.stdout or "not logged in").strip()[:160]


def _open_vm_mirror_prs(repo: Path) -> list[dict[str, Any]]:
    if not _gh_available():
        return []
    prs = _gh_json(
        repo,
        [
            "gh",
            "pr",
            "list",
            "--base",
            "main",
            "--state",
            "open",
            "--json",
            "number,headRefName,url,title,createdAt",
            "--limit",
            "20",
        ],
    )
    if not isinstance(prs, list):
        return []
    out: list[dict[str, Any]] = []
    for pr in prs:
        if not isinstance(pr, dict):
            continue
        head = str(pr.get("headRefName") or "")
        if head.startswith(VM_MIRROR_PUBLISH_PREFIX):
            out.append(pr)
    return out


def _maybe_notify_stale_mirror_prs(repo: Path, stale_prs: list[dict[str, Any]]) -> bool:
    if not stale_prs:
        return False
    nums = sorted(int(p["number"]) for p in stale_prs if p.get("number") is not None)
    if not nums:
        return False
    fp = ",".join(str(n) for n in nums)
    state_path = repo / MIRROR_PR_NOTIFY_STATE_REL
    prior: dict[str, Any] = {}
    if state_path.is_file():
        try:
            prior = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior = {}
    if fp == str(prior.get("fingerprint") or ""):
        return False
    urls = [str(p.get("url") or "") for p in stale_prs[:3] if p.get("url")]
    title = f"PPE VM mirror PR stuck ({len(stale_prs)} open >15m)"
    body = "Merge or automerge mirror PRs so desktop git pull sees fresh phase.\n" + "\n".join(urls)
    try:
        from scripts.ppe_notify_push import ntfy_topic_stuck, send_ntfy_to_topic

        sent = send_ntfy_to_topic(
            ntfy_topic_stuck(),
            title=title,
            body=body,
            priority="high",
            tags=["mirror", "pr", "warning"],
        )
    except Exception:
        return False
    if sent:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(
            json.dumps({"fingerprint": fp, "notified_at": _utc_now(), "pr_numbers": nums}, indent=2) + "\n",
            encoding="utf-8",
        )
    return sent


def assess_operator_blind_spots(
    repo: Path,
    status: dict[str, Any] | None = None,
    *,
    probe_ssh: bool = False,
) -> dict[str, Any]:
    """Return blind-spot issues the relay verdict does not cover."""
    repo = repo.resolve()
    status = status or {}
    issues: list[dict[str, str]] = []
    health: dict[str, Any] = {}

    try:
        from scripts.ppe_notify_push import bootstrap_operator_notify_env, ntfy_configured, notify_enabled

        bootstrap_operator_notify_env(repo)
        ntfy_ok = notify_enabled() and ntfy_configured()
        health["ntfy_ok"] = ntfy_ok
        if not ntfy_ok:
            issues.append(
                _issue(
                    "ntfy_unconfigured",
                    severity="medium",
                    message="Mobile ntfy not configured — stuck/mirror alerts won't reach phone.",
                    fix="Copy ppe_operator_notify.local.cmd.example → set PPE_NTFY_TOPIC (+ PPE_NTFY_TOPIC_STUCK).",
                )
            )
    except Exception:
        health["ntfy_ok"] = None

    gh_ok, gh_err = _gh_auth_ok()
    health["gh_ok"] = gh_ok
    if not gh_ok:
        issues.append(
            _issue(
                "gh_auth",
                severity="high",
                message=f"GitHub CLI auth missing — mirror PRs won't open/merge. ({gh_err})",
                fix="Run `gh auth login` on desktop and loop host.",
            )
        )

    loop_ok = False
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        loop_ok = bool(loop_host_start_allowed()[0])
        health["loop_host"] = loop_ok
    except Exception:
        health["loop_host"] = None

    if not loop_ok:
        ssh_ok = None
        if probe_ssh:
            try:
                from scripts.ppe_operator_vm_ssh import VM_SSH_HOST, ssh_vm

                ssh = ssh_vm("echo PPE_OK", timeout=20)
                ssh_ok = bool(ssh.get("ok") and "PPE_OK" in str(ssh.get("stdout") or ""))
                health["ssh_ok"] = ssh_ok
                health["ssh_host"] = VM_SSH_HOST
                if not ssh_ok:
                    err = (ssh.get("stderr") or ssh.get("error") or "connection failed").strip()[:120]
                    issues.append(
                        _issue(
                            "ssh_vm",
                            severity="high",
                            message=f"Desktop cannot SSH to VM ({VM_SSH_HOST}): {err}",
                            fix="Run scripts/setup_ppe_vm_cursor_ssh.ps1; set PPE_VM_SSH_HOST=ppe-vm.",
                        )
                    )
                else:
                    try:
                        from scripts.ppe_ntfy_commands import commands_enabled

                        if commands_enabled():
                            from scripts.ppe_operator_vm_ssh import VM_REPO, ssh_vm

                            heal = ssh_vm(
                                f"cd /d {VM_REPO} && call call_ppe_operator_local.cmd && "
                                f"set PYTHONPATH=%CD% && "
                                f"python scripts/ppe_headless_stack_supervisor.py --repo-root . --ensure",
                                timeout=90,
                            )
                            stdout = str(heal.get("stdout") or "")
                            start = stdout.find("{")
                            vm_ntfy = None
                            if start >= 0:
                                try:
                                    blob = json.loads(stdout[start:])
                                    vm_ntfy = bool(blob.get("ntfy_listen_running"))
                                    health["vm_ntfy_listen"] = vm_ntfy
                                except json.JSONDecodeError:
                                    pass
                            if vm_ntfy is False:
                                issues.append(
                                    _issue(
                                        "vm_ntfy_listener_down",
                                        severity="high",
                                        message="VM phone-command listener (ppe_ntfy_listen) is not running — status/build from phone will not reply.",
                                        fix="On VM: run_ppe_headless_stack.cmd --ensure or ppe_ntfy_phone_diag.cmd --heal-vm from desktop.",
                                    )
                                )
                    except Exception:
                        pass
            except Exception as exc:
                health["ssh_ok"] = False
                issues.append(
                    _issue(
                        "ssh_vm",
                        severity="high",
                        message=f"SSH probe failed: {exc}",
                        fix="Run scripts/setup_ppe_vm_cursor_ssh.ps1.",
                    )
                )
        else:
            cache = None
            try:
                from scripts.ppe_operator_vm_ssh import load_vm_status_cache

                cache = load_vm_status_cache(repo)
            except Exception:
                pass
            if not cache or not cache.get("ok"):
                issues.append(
                    _issue(
                        "ssh_vm_unverified",
                        severity="medium",
                        message="VM SSH not verified this pass — mirror preferred over SSH.",
                        fix="If DESKTOP_CONTINUE fails: run setup_ppe_vm_cursor_ssh.ps1 once.",
                    )
                )

    mirror_health = status.get("vm_mirror_health") if isinstance(status.get("vm_mirror_health"), dict) else None
    if mirror_health:
        health["mirror_populated"] = mirror_health.get("populated")
        health["mirror_stale"] = mirror_health.get("stale")
        health["mirror_untrusted"] = mirror_health.get("untrusted")
        health["mirror_heartbeat_overdue"] = mirror_health.get("heartbeat_overdue")
        if mirror_health.get("untrusted") and mirror_health.get("alert"):
            issues.append(
                _issue(
                    "vm_mirror_stale",
                    severity="high",
                    message=str(mirror_health.get("agent_note") or "VM phase mirror stale or empty."),
                    fix="git pull origin main; wait for loop host mirror PR merge.",
                )
            )
        elif mirror_health.get("heartbeat_overdue") and mirror_health.get("alert"):
            issues.append(
                _issue(
                    "vm_mirror_heartbeat_overdue",
                    severity="medium",
                    message=str(mirror_health.get("agent_note") or "VM in-flight mirror heartbeat overdue."),
                    fix="git pull origin main; VM loop republishes every ~10m during in-flight.",
                )
            )

    branch_pf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else None
    if branch_pf and branch_pf.get("blocks_relay"):
        health["branch_blocks_relay"] = True
        for reason in branch_pf.get("reasons") or []:
            issues.append(
                _issue(
                    "branch_preflight",
                    severity="high",
                    message=str(reason),
                    fix="git checkout main && git pull; stash/commit product WIP before relay.",
                )
            )

    warnings = status.get("preflight_warnings") or []
    actionable_warnings = [
        w
        for w in warnings
        if not str(w).startswith("repo layer scope:")
    ]
    if actionable_warnings:
        health["preflight_warnings"] = len(actionable_warnings)
        issues.append(
            _issue(
                "mixed_plane",
                severity="high",
                message=f"{len(actionable_warnings)} preflight warning(s) — dirty tree or branch mismatch.",
                fix="See docs/SOP/RECOVERY_PROTOCOL.md before relay.",
            )
        )

    mirror_prs = _open_vm_mirror_prs(repo) if gh_ok else []
    health["open_mirror_prs"] = len(mirror_prs)
    stale_mirror_prs = [
        p
        for p in mirror_prs
        if (_pr_age_seconds(p) or 0.0) > float(MIRROR_PR_ESCALATE_SECONDS)
    ]
    if mirror_prs:
        nums = ", ".join(f"#{p.get('number')}" for p in mirror_prs[:3])
        severity = "high" if stale_mirror_prs else "medium"
        age_note = ""
        if stale_mirror_prs:
            oldest_m = int(max(_pr_age_seconds(p) or 0 for p in stale_mirror_prs) // 60)
            age_note = f" (oldest {oldest_m}m)"
        issues.append(
            _issue(
                "mirror_pr_pending",
                severity=severity,
                message=f"Open VM mirror PR(s) not merged: {nums}{age_note}",
                fix="Merge or wait for automerge; then git pull origin main on desktop.",
            )
        )
        if stale_mirror_prs:
            _maybe_notify_stale_mirror_prs(repo, stale_mirror_prs)

    try:
        from scripts.check_vm_host_health import host_health_is_fresh, load_host_health

        host = load_host_health(repo)
        if host and host_health_is_fresh(host) and host.get("alerts"):
            health["host_alerts"] = host.get("alerts")
            for alert in host.get("alerts") or []:
                issues.append(
                    _issue(
                        "vm_host_resources",
                        severity="high" if "critical" in str(alert) else "medium",
                        message=str(alert),
                        fix="Free disk/RAM on loop host; run scripts/ppe_doctor.cmd.",
                    )
                )
        elif host and not host_health_is_fresh(host):
            health["host_health_stale"] = True
    except Exception:
        pass

    try:
        from scripts.ppe_chapter_coordination import audit_repo, format_warning_lines

        coord_issues = audit_repo(repo)
        if coord_issues:
            health["coordination_issues"] = len(coord_issues)
            for issue in coord_issues[:4]:
                issues.append(
                    _issue(
                        f"chapter_coordination_{issue.get('code', 'unknown')}".lower(),
                        severity=str(issue.get("severity") or "high"),
                        message=str(issue.get("message") or "Chapter coordination desync"),
                        fix=str(issue.get("fix") or f"See docs/SOP/CHAPTER_COORDINATION_V1.md"),
                    )
                )
            if len(coord_issues) > 4:
                extra = format_warning_lines(coord_issues[4:], max_lines=2)
                issues.append(
                    _issue(
                        "chapter_coordination_more",
                        severity="medium",
                        message=f"{len(coord_issues) - 4} more coordination issue(s)",
                        fix="; ".join(extra) if extra else "python scripts/ppe_chapter_coordination.py",
                    )
                )
    except Exception:
        pass

    try:
        from scripts.ppe_gh_auth_expiry import assess_gh_auth_expiry, format_gh_expiry_line

        gh_exp = assess_gh_auth_expiry()
        health["gh_expiry"] = gh_exp
        if gh_exp.get("needs_reauth"):
            issues.append(
                _issue(
                    "gh_auth_expired",
                    severity="high",
                    message="GitHub CLI auth missing or expired.",
                    fix="Run gh auth login on desktop and loop host.",
                )
            )
        elif gh_exp.get("warn_expiry"):
            line = format_gh_expiry_line(gh_exp)
            if line:
                issues.append(
                    _issue(
                        "gh_auth_expiring",
                        severity="medium",
                        message=line,
                        fix="Run gh auth login before token expires.",
                    )
                )
    except Exception:
        pass

    high = sum(1 for i in issues if i.get("severity") == "high")
    medium = sum(1 for i in issues if i.get("severity") == "medium")
    summary = "ok"
    if issues:
        summary = f"{len(issues)} blind spot(s): high={high} medium={medium}"

    return {
        "as_of": _utc_now(),
        "issues": issues,
        "health": health,
        "summary": summary,
        "operator_health_line": _format_health_line(health, issues),
    }


def _format_health_line(health: dict[str, Any], issues: list[dict[str, str]]) -> str:
    parts = [
        f"gh={'ok' if health.get('gh_ok') else 'fail'}",
        f"ntfy={'ok' if health.get('ntfy_ok') else 'off'}",
    ]
    if health.get("ssh_ok") is not None:
        parts.append(f"ssh={'ok' if health.get('ssh_ok') else 'fail'}")
    if health.get("mirror_untrusted") or health.get("mirror_stale"):
        parts.append("mirror=stale")
    elif health.get("mirror_heartbeat_overdue"):
        parts.append("mirror=heartbeat_overdue")
    elif health.get("mirror_populated"):
        parts.append("mirror=ok")
    if health.get("open_mirror_prs"):
        parts.append(f"mirror_prs={health['open_mirror_prs']}")
    if issues:
        parts.append(f"spots={len(issues)}")
    return "health: " + " ".join(parts)


def write_blind_spots(repo: Path, payload: dict[str, Any]) -> Path:
    path = (repo / BLIND_SPOTS_REL).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def write_operator_health(repo: Path, payload: dict[str, Any]) -> Path:
    path = (repo / HEALTH_REL).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    compact = {
        "as_of": payload.get("as_of"),
        "summary": payload.get("summary"),
        "line": payload.get("operator_health_line"),
        "health": payload.get("health"),
        "issue_count": len(payload.get("issues") or []),
    }
    path.write_text(json.dumps(compact, indent=2) + "\n", encoding="utf-8")
    return path


def format_blind_spot_lines(payload: dict[str, Any], *, max_items: int = 5) -> list[str]:
    issues = payload.get("issues") or []
    if not issues:
        return []
    lines = ["", "**Blind spots (autobuilder won't catch):**"]
    line = payload.get("operator_health_line")
    if line:
        lines.append(f"  `{line}`")
    for item in issues[:max_items]:
        if isinstance(item, dict):
            lines.append(f"  - [{item.get('severity', '?')}] {item.get('message')}")
    extra = len(issues) - max_items
    if extra > 0:
        lines.append(f"  - …and {extra} more (see OPERATOR_BLIND_SPOTS.json)")
    return lines
