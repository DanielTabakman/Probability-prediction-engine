"""Human-operator scoreboard: tester sessions, validation report, next actions."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from scripts.ppe_focus_gate import validation_report_status

REALITY_CHECKS_REL = "docs/SOP/VALIDATION_REALITY_CHECKS.md"
COMMERCIAL_OPS_REL = "docs/SOP/COMMERCIAL_OPS_COMPLETION.md"
DEMO_SCRIPT_REL = "docs/SOP/DEMO_OPERATOR_SCRIPT.md"
SESSION_TARGET = 10
MSOS_P8_SECTION = "## MSOS P8 friends-first tester metrics"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

NudgeSlot = Literal["monday", "thursday", "auto"]


@dataclass(frozen=True)
class MsosP8Session:
    session_date: str
    profile: str
    comprehension: str
    thesis_confirm: str
    return_monitor: str
    paid_interest: str
    notes: str


def repo_root() -> Path:
    return Path.cwd().resolve()


def reality_checks_path(repo: Path) -> Path:
    return repo / REALITY_CHECKS_REL


def parse_msos_p8_sessions(text: str) -> list[MsosP8Session]:
    idx = text.find(MSOS_P8_SECTION)
    if idx < 0:
        return []
    section = text[idx:]
    sessions: list[MsosP8Session] = []
    in_table = False
    for line in section.splitlines():
        if line.startswith("| Date |"):
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            break
        if re.match(r"^\|\s*-+", line):
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 6:
            continue
        session_date = cols[0]
        if not DATE_RE.match(session_date):
            continue
        sessions.append(
            MsosP8Session(
                session_date=session_date,
                profile=cols[1],
                comprehension=cols[2],
                thesis_confirm=cols[3],
                return_monitor=cols[4],
                paid_interest=cols[5],
                notes=cols[6] if len(cols) > 6 else "",
            )
        )
    return sessions


def _parse_iso(d: str) -> date | None:
    try:
        return date.fromisoformat(d)
    except ValueError:
        return None


def sessions_this_week(sessions: list[MsosP8Session], *, ref: date | None = None) -> int:
    ref = ref or date.today()
    start = ref - timedelta(days=ref.weekday())
    end = start + timedelta(days=6)
    count = 0
    for s in sessions:
        d = _parse_iso(s.session_date)
        if d is not None and start <= d <= end:
            count += 1
    return count


def vps_cta_pending(repo: Path) -> bool:
    path = repo / COMMERCIAL_OPS_REL
    if not path.is_file():
        return True
    text = path.read_text(encoding="utf-8", errors="replace")
    if "steward follow-up" in text.lower():
        return True
    if re.search(r"VPS repo-root `.env`.*\|\s*\*\*steward", text, re.I):
        return True
    return "CTA row pending" in text


def build_scoreboard(repo: Path, *, ref: date | None = None) -> dict[str, Any]:
    ref = ref or date.today()
    rc_path = reality_checks_path(repo)
    text = rc_path.read_text(encoding="utf-8", errors="replace") if rc_path.is_file() else ""
    sessions = parse_msos_p8_sessions(text)
    logged = len(sessions)
    remaining = max(0, SESSION_TARGET - logged)
    report_status = validation_report_status(repo)
    week_count = sessions_this_week(sessions, ref=ref)
    paid_yes = sum(1 for s in sessions if s.paid_interest.strip().upper() == "Y")

    return {
        "sessions_logged": logged,
        "sessions_target": SESSION_TARGET,
        "sessions_remaining": remaining,
        "sessions_this_week": week_count,
        "paid_interest_yes": paid_yes,
        "validation_report_status": report_status,
        "vps_cta_pending": vps_cta_pending(repo),
        "reality_checks_path": REALITY_CHECKS_REL,
        "demo_script_path": DEMO_SCRIPT_REL,
        "week_of": (ref - timedelta(days=ref.weekday())).isoformat(),
        "next_actions": build_next_actions(
            logged=logged,
            remaining=remaining,
            week_count=week_count,
            report_status=report_status,
            vps_pending=vps_cta_pending(repo),
            paid_yes=paid_yes,
        ),
    }


def build_next_actions(
    *,
    logged: int,
    remaining: int,
    week_count: int,
    report_status: str,
    vps_pending: bool,
    paid_yes: int,
) -> list[str]:
    actions: list[str] = []

    if report_status == "COMPLETE" and remaining == 0:
        actions.append("Validation report COMPLETE — run steward SELECTION from report §4.")
        return actions

    if week_count == 0:
        actions.append(
            "Book 1 guided tester call this week (20–30 min). "
            "See docs/SOP/STEWARD_VALIDATION_GUIDE_V1.md Phase 2 — Monday outreach."
        )
    elif week_count < 2 and remaining > 0:
        actions.append(
            f"Log {max(0, 2 - week_count)} more session(s) this week "
            f"({logged}/{SESSION_TARGET} total logged)."
        )

    if remaining > 0:
        actions.append(
            f"Run demo: open {DEMO_SCRIPT_REL} (~5 min) on marketstructureos.com learn loop."
        )
        actions.append(
            f"After session: add one row in {REALITY_CHECKS_REL} "
            f"§ MSOS P8 — see STEWARD_VALIDATION_GUIDE_V1.md Phase 2 Thursday log."
        )
    elif report_status != "COMPLETE":
        actions.append(
            f"Sessions target met ({logged}/{SESSION_TARGET}). "
            f"Fill MSOS_P8_VALIDATION_REPORT_V1.md and set Status COMPLETE."
        )

    if report_status == "DRAFT" and logged >= 3:
        actions.append("Update validation report draft metrics from logged sessions.")

    if vps_pending and logged >= 1:
        actions.append(
            "VPS research-beta CTA still pending — set `.env` on VPS per COMMERCIAL_OPS_COMPLETION.md."
        )

    if paid_yes == 0 and logged >= 2:
        actions.append(
            "Paid interest still N — schedule one honest steward conversation (do not mark Y without it)."
        )

    if not actions:
        actions.append("Review OPERATING_CALENDAR_V1.md monthly steward checklist.")

    return actions


def format_scoreboard_text(scoreboard: dict[str, Any]) -> str:
    lines = [
        "PPE steward scoreboard",
        "",
        f"Tester sessions: {scoreboard['sessions_logged']}/{scoreboard['sessions_target']} "
        f"({scoreboard['sessions_remaining']} remaining)",
        f"This week (Mon–Sun): {scoreboard['sessions_this_week']} logged",
        f"Paid interest Y: {scoreboard['paid_interest_yes']}",
        f"Validation report: {scoreboard['validation_report_status']}",
        f"VPS research-beta CTA pending: {'yes' if scoreboard['vps_cta_pending'] else 'no'}",
        "",
        "Do next:",
    ]
    for i, action in enumerate(scoreboard.get("next_actions") or [], 1):
        lines.append(f"{i}. {action}")
    return "\n".join(lines)


def format_digest_commitment_lines(repo: Path) -> list[str]:
    sb = build_scoreboard(repo)
    lines = [
        "",
        "Your commitments",
        f"- Tester sessions: {sb['sessions_logged']}/{sb['sessions_target']} "
        f"({sb['sessions_this_week']} this week)",
        f"- Validation report: {sb['validation_report_status']}",
    ]
    actions = sb.get("next_actions") or []
    if actions:
        lines.append(f"- Next: {actions[0]}")
    return lines


def resolve_nudge_slot(slot: NudgeSlot, *, ref: date | None = None) -> str | None:
    ref = ref or date.today()
    if slot == "monday":
        return "monday"
    if slot == "thursday":
        return "thursday"
    weekday = ref.weekday()
    if weekday == 0:
        return "monday"
    if weekday == 3:
        return "thursday"
    return None


def build_nudge_message(scoreboard: dict[str, Any], slot: str) -> tuple[str, str]:
    logged = int(scoreboard["sessions_logged"])
    target = int(scoreboard["sessions_target"])
    week_count = int(scoreboard["sessions_this_week"])
    remaining = int(scoreboard["sessions_remaining"])
    actions = scoreboard.get("next_actions") or []

    if slot == "monday":
        title = f"PPE steward: plan outreach ({logged}/{target})"
        opener = (
            "Week start — book one real-world validation slot before Thursday."
            if week_count == 0
            else f"You logged {week_count} session(s) this week — aim for 2 total."
        )
    else:
        title = f"PPE steward: log or skip ({logged}/{target})"
        opener = (
            "Mid-week receipt — log a tester row or note why you skipped."
            if week_count == 0
            else f"This week: {week_count} session(s). Log notes while fresh."
        )

    lines = [opener, "", f"Score: {logged}/{target} sessions ({remaining} to gate unlock)"]
    lines.append(f"Report: {scoreboard['validation_report_status']}")
    lines.append("")
    lines.append("Do next:")
    for i, action in enumerate(actions[:4], 1):
        lines.append(f"{i}. {action}")
    lines.append("")
    lines.append(f"Receipt file: {REALITY_CHECKS_REL}")
    lines.append(f"Demo script: {DEMO_SCRIPT_REL}")
    lines.append("Full guide: docs/SOP/STEWARD_VALIDATION_GUIDE_V1.md")
    return title, "\n".join(lines)


def cmd_scoreboard(repo: Path, *, as_json: bool) -> int:
    sb = build_scoreboard(repo)
    if as_json:
        print(json.dumps(sb, indent=2))
    else:
        print(format_scoreboard_text(sb))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE steward scoreboard (human commitments)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Emit JSON scoreboard")
    args = ap.parse_args(argv)
    return cmd_scoreboard(args.repo_root.resolve(), as_json=args.json)


if __name__ == "__main__":
    raise SystemExit(main())
