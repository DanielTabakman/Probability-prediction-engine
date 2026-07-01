"""Coordination synthesizer — deterministic proceed / repair / recovery / park verdict.

Runs chapter coordination, branch preflight, delegation, and blind-spot signals.
Canon: docs/SOP/CHAPTER_COORDINATION_V1.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

COORDINATION_CHECK_REL = "artifacts/control_plane/COORDINATION_CHECK.json"
COORDINATION_DOC = "docs/SOP/CHAPTER_COORDINATION_V1.md"
RECOVERY_DOC = "docs/SOP/RECOVERY_PROTOCOL.md"

VERDICT_PROCEED = "proceed"
VERDICT_REPAIR = "repair"
VERDICT_RECOVERY = "recovery"
VERDICT_PARK = "park"

AUTO_REPAIR_CODES = frozenset(
    {
        "PRODUCT_ON_MAIN_NO_MARKER",
        "CLOSEOUT_REGISTRY_MISSING",
        "QUEUE_ACTIVE_PRODUCT_DESYNC",
    }
)
NO_AUTO_REPAIR_CODES = frozenset({"FRONTIER_AHEAD_OF_EVIDENCE"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _delegation_tier(repo: Path) -> tuple[str, list[str]]:
    try:
        from scripts.ppe_delegation_envelope import classify_paths, current_branch, git_changed_paths

        paths = git_changed_paths(repo)
        if not paths:
            return "auto", []
        verdict = classify_paths(repo, paths, branch=current_branch(repo))
        return str(verdict.tier or "auto"), list(verdict.reasons or [])
    except Exception:
        return "auto", []


def assess_coordination_check(
    repo: Path,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return structured coordination verdict for agents and burst plan."""
    repo = repo.resolve()
    if status is None:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)

    chapter_issues: list[dict[str, Any]] = []
    try:
        from scripts.ppe_chapter_coordination import audit_repo

        plan_path = str(status.get("phase_plan_path") or "").strip() or None
        chapter_issues = audit_repo(repo, plan_path=plan_path)
    except Exception as exc:
        chapter_issues = [
            {
                "code": "AUDIT_ERROR",
                "severity": "high",
                "message": str(exc),
                "fix": "python scripts/ppe_chapter_coordination.py",
            }
        ]

    blind_spot_issues: list[dict[str, str]] = []
    try:
        from scripts.ppe_operator_blind_spots import assess_operator_blind_spots

        blind = assess_operator_blind_spots(repo, status, probe_ssh=False)
        for issue in blind.get("issues") or []:
            if not isinstance(issue, dict):
                continue
            iid = str(issue.get("id") or "")
            if iid.startswith("chapter_coordination") or iid in (
                "branch_preflight",
                "mixed_plane",
            ):
                blind_spot_issues.append(issue)
    except Exception:
        pass

    branch_pf = status.get("branch_preflight") if isinstance(status.get("branch_preflight"), dict) else {}
    blocks_relay = bool(branch_pf.get("blocks_relay"))
    branch_commands = [str(c) for c in branch_pf.get("commands") or []]

    delegation_tier, delegation_reasons = _delegation_tier(repo)
    delegation_hint = str(status.get("delegation_hint") or "").strip()

    repairable = [i for i in chapter_issues if str(i.get("code") or "") in AUTO_REPAIR_CODES]
    manual_only = [i for i in chapter_issues if str(i.get("code") or "") in NO_AUTO_REPAIR_CODES]
    high_chapter = [i for i in chapter_issues if str(i.get("severity") or "").lower() == "high"]

    commands: list[str] = []
    verdict = VERDICT_PROCEED
    summary_parts: list[str] = []

    if delegation_tier == "human_only":
        verdict = VERDICT_PARK
        summary_parts.append("human_only delegation on dirty tree")
        commands.append(
            "Operator decision required — or RECOVERY with PPE_DELEGATION_OVERRIDE=1 per COMMIT_POLICY.md"
        )
    elif blocks_relay or any("mixed_plane" in str(r).lower() for r in delegation_reasons):
        verdict = VERDICT_RECOVERY
        summary_parts.append("branch/tree or mixed-plane blocks relay")
        commands.append("python scripts/ppe_branch_recovery.py --plane control --ship")
        if branch_commands:
            commands.extend(branch_commands[:2])
    elif delegation_tier == "steward_packet" and delegation_hint:
        verdict = VERDICT_RECOVERY
        summary_parts.append("steward_packet — recovery pass only")
        commands.append("python scripts/ppe_branch_recovery.py --plane control --ship")

    if manual_only and verdict == VERDICT_PROCEED:
        verdict = VERDICT_PARK
        summary_parts.append("frontier ahead of evidence — manual doc alignment")
        for issue in manual_only[:2]:
            fix = str(issue.get("fix") or "").strip()
            if fix:
                commands.append(fix)

    if repairable and verdict in (VERDICT_PROCEED, VERDICT_REPAIR):
        verdict = VERDICT_REPAIR
        summary_parts.append(f"{len(repairable)} auto-repairable chapter issue(s)")
        for issue in repairable[:3]:
            fix = str(issue.get("fix") or "").strip()
            if fix and fix not in commands:
                commands.append(fix)

    if high_chapter and verdict == VERDICT_PROCEED and not repairable:
        verdict = VERDICT_PARK
        summary_parts.append("high-severity chapter coordination without safe repair")

    blocks_burst = verdict in (VERDICT_RECOVERY, VERDICT_PARK)
    blocks_build = blocks_relay or verdict in (VERDICT_RECOVERY, VERDICT_PARK)

    if verdict == VERDICT_PROCEED and blind_spot_issues:
        high_blind = [i for i in blind_spot_issues if str(i.get("severity") or "").lower() == "high"]
        if high_blind and not blocks_burst:
            summary_parts.append(f"{len(high_blind)} coordination blind spot(s) — review before burst")

    summary = "; ".join(summary_parts) if summary_parts else "coordination ok"

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "summary": summary,
        "blocks_burst": blocks_burst,
        "blocks_build": blocks_build,
        "operator_verdict": str(status.get("verdict") or ""),
        "chapter_mode": (status.get("chapter_mode") or {}).get("mode")
        if isinstance(status.get("chapter_mode"), dict)
        else None,
        "branch": branch_pf.get("branch") or None,
        "blocks_relay": blocks_relay,
        "delegation_tier": delegation_tier,
        "delegation_hint": delegation_hint or None,
        "chapter_issues": chapter_issues,
        "blind_spot_issues": blind_spot_issues,
        "commands": commands,
        "docs": [COORDINATION_DOC, RECOVERY_DOC],
        "agent": "@ppe-coordination-check",
    }


def write_coordination_check(repo: Path, payload: dict[str, Any]) -> Path:
    out = repo / COORDINATION_CHECK_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def format_status_lines(payload: dict[str, Any]) -> list[str]:
    """Lines for OPERATOR_STATUS.md coordination section."""
    verdict = str(payload.get("verdict") or VERDICT_PROCEED)
    summary = str(payload.get("summary") or "coordination ok")
    lines = [f"**Coordination:** `{verdict}` — {summary}"]
    if payload.get("blocks_burst"):
        lines.append(
            "  → Burst blocked — `@ppe-coordination-check` or "
            "`python scripts/ppe_coordination_check.py --write` before BUILD"
        )
    elif verdict == VERDICT_REPAIR:
        lines.append("  → Safe repair available — run commands in COORDINATION_CHECK.json")
    for cmd in (payload.get("commands") or [])[:2]:
        lines.append(f"  → `{cmd}`")
    return lines


def format_agent_prompt(payload: dict[str, Any]) -> str:
    verdict = str(payload.get("verdict") or VERDICT_PROCEED)
    lines = [
        "@ppe-coordination-check",
        f"Verdict: {verdict} — {payload.get('summary') or ''}",
        f"Read {COORDINATION_CHECK_REL} and {COORDINATION_DOC}.",
        "Return: (1) one-line verdict (2) root cause (3) numbered commands (4) proceed/recovery/park.",
    ]
    for cmd in payload.get("commands") or []:
        lines.append(f"  → {cmd}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Coordination synthesizer — proceed/repair/recovery/park.")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help=f"Write {COORDINATION_CHECK_REL}")
    ap.add_argument("--prompt", action="store_true", help="Print agent handoff prompt")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    payload = assess_coordination_check(repo)

    if args.write:
        path = write_coordination_check(repo, payload)
        if not args.json and not args.prompt:
            print(f"ppe_coordination_check: wrote {path.relative_to(repo)}")

    if args.prompt:
        print(format_agent_prompt(payload))
    elif args.json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    elif not args.write:
        print(
            f"ppe_coordination_check: verdict={payload['verdict']} "
            f"blocks_burst={payload['blocks_burst']} — {payload['summary']}"
        )
        for cmd in payload.get("commands") or []:
            print(f"  → {cmd}")

    if payload["verdict"] == VERDICT_PROCEED:
        return 0
    if payload["verdict"] == VERDICT_REPAIR:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
