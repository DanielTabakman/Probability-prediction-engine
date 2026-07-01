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
            "number,headRefName,url,title",
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
        if mirror_health.get("alert"):
            issues.append(
                _issue(
                    "vm_mirror_stale",
                    severity="high",
                    message=str(mirror_health.get("agent_note") or "VM phase mirror stale or empty."),
                    fix="git pull origin main; wait for loop host mirror PR merge.",
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
    if mirror_prs:
        nums = ", ".join(f"#{p.get('number')}" for p in mirror_prs[:3])
        issues.append(
            _issue(
                "mirror_pr_pending",
                severity="medium",
                message=f"Open VM mirror PR(s) not merged: {nums}",
                fix="Merge or wait for automerge; then git pull origin main on desktop.",
            )
        )

    try:
        from scripts.check_vm_host_health import load_host_health

        host = load_host_health(repo)
        if host and host.get("alerts"):
            health["host_alerts"] = host.get("alerts")
            for alert in host.get("alerts") or []:
                issues.append(
                    _issue(
                        "vm_host_resources",
                        severity="high" if "critical" in str(alert) else "medium",
                        message=str(alert),
                        fix="Free disk/RAM on loop host; see VM_HOST_HEALTH.json.",
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
    if health.get("mirror_stale"):
        parts.append("mirror=stale")
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
