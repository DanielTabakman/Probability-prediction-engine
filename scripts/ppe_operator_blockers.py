"""Generate artifacts/orchestrator/BLOCKERS.md for triage workers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

BLOCKERS_REL = "artifacts/orchestrator/BLOCKERS.md"
GUARD_REPORT_REL = "artifacts/orchestrator/OPERATOR_GUARD_REPORT.md"
LAST_RUN_REL = "artifacts/orchestrator/LAST_RUN_REPORT.md"


def _read_head(path: Path, *, max_lines: int = 12) -> str | None:
    if not path.is_file():
        return None
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return None
    excerpt = "\n".join(lines[:max_lines])
    if len(lines) > max_lines:
        excerpt += f"\n\n_(truncated — {len(lines)} lines total)_"
    return excerpt


def _latest_relay_decision(repo: Path) -> tuple[str | None, str | None]:
    runs = repo / "artifacts" / "relay" / "runs"
    if not runs.is_dir():
        return None, None
    candidates = [p for p in runs.iterdir() if p.is_dir() and (p / "decision.json").is_file()]
    if not candidates:
        return None, None
    latest = max(candidates, key=lambda p: p.stat().st_mtime)
    rel = latest.relative_to(repo).as_posix()
    try:
        import json

        data = json.loads((latest / "decision.json").read_text(encoding="utf-8-sig"))
        decision = str(data.get("decision") or "").strip() or None
    except (OSError, json.JSONDecodeError, ValueError):
        decision = None
    return rel, decision


def build_blockers_payload(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    inbox = status.get("inbox") or {}
    guard_excerpt = _read_head(repo / GUARD_REPORT_REL)
    last_run_excerpt = _read_head(repo / LAST_RUN_REL)
    relay_dir, relay_decision = _latest_relay_decision(repo)
    return {
        "as_of": status.get("as_of"),
        "verdict": status.get("verdict"),
        "blocker": status.get("blocker"),
        "inbox": inbox,
        "guard_report_excerpt": guard_excerpt,
        "last_run_excerpt": last_run_excerpt,
        "relay_run_dir": relay_dir,
        "relay_decision": relay_decision,
        "suggested_worker": inbox.get("agent"),
    }


def format_blockers_md(payload: dict[str, Any]) -> str:
    inbox = payload.get("inbox") or {}
    lines = [
        "# Operator blockers",
        "",
        f"**As-of:** {payload.get('as_of')}",
        f"**Verdict:** `{payload.get('verdict')}`",
        "",
        "## Inbox",
        "",
        f"- **Owner:** {inbox.get('owner')} ({inbox.get('agent')})",
    ]
    if inbox.get("active_slice_id"):
        lines.append(f"- **Active slice:** `{inbox.get('active_slice_id')}`")
    if inbox.get("blocker") or payload.get("blocker"):
        lines.append(f"- **Blocker:** {inbox.get('blocker') or payload.get('blocker')}")
    if inbox.get("next_command"):
        lines.append(f"- **Next:** `{inbox.get('next_command')}`")
    if inbox.get("stale_active_slice"):
        lines.append("- **Warning:** active IDE slice checkout is stale (>24h)")

    lines.extend(["", "## Suggested worker", "", f"`{payload.get('suggested_worker') or '@ppe-triage-worker'}`", ""])

    if payload.get("relay_decision"):
        lines.extend(
            [
                "## Relay",
                "",
                f"- **Decision:** `{payload.get('relay_decision')}`",
                f"- **Run dir:** `{payload.get('relay_run_dir')}`",
                "",
            ]
        )

    if payload.get("guard_report_excerpt"):
        lines.extend(["## Guard report (excerpt)", "", "```text", payload["guard_report_excerpt"], "```", ""])

    if payload.get("last_run_excerpt"):
        lines.extend(["## Last run (excerpt)", "", "```text", payload["last_run_excerpt"], "```", ""])

    lines.extend(
        [
            "## Read order (triage)",
            "",
            "1. This file",
            "2. `artifacts/orchestrator/OPERATOR_STATUS.md`",
            "3. Full `OPERATOR_GUARD_REPORT.md` or `LAST_RUN_REPORT.md` only if needed",
            "",
        ]
    )
    return "\n".join(lines)


def write_blockers_report(repo: Path, status: dict[str, Any]) -> Path:
    payload = build_blockers_payload(repo, status)
    out = repo / BLOCKERS_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(format_blockers_md(payload), encoding="utf-8")
    return out
