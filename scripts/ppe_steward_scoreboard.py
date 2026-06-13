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
GUIDE_REL = "docs/SOP/STEWARD_VALIDATION_GUIDE_V1.md"
SESSION_TARGET = 10
NORTH_STAR = (
    "See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds."
)
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

    sb: dict[str, Any] = {
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
        "plan_phase": "",
        "next_actions": build_next_actions(
            logged=logged,
            remaining=remaining,
            week_count=week_count,
            report_status=report_status,
            vps_pending=vps_cta_pending(repo),
            paid_yes=paid_yes,
        ),
    }
    sb["plan_phase"] = resolve_plan_phase(sb)
    return sb


def resolve_plan_phase(scoreboard: dict[str, Any]) -> str:
    logged = int(scoreboard.get("sessions_logged") or 0)
    target = int(scoreboard.get("sessions_target") or SESSION_TARGET)
    report = str(scoreboard.get("validation_report_status") or "DRAFT")
    if report == "COMPLETE":
        return "complete"
    if logged >= target:
        return "finish_report"
    if logged >= 3:
        return "weekly_and_draft"
    if logged == 0:
        return "start"
    return "weekly_loop"


def _phase_label(phase: str) -> str:
    return {
        "start": "Phase 0-1: first outreach (setup + solo rehearsal)",
        "weekly_loop": "Phase 2: weekly tester loop",
        "weekly_and_draft": "Phase 2-3: sessions + draft validation report",
        "finish_report": "Phase 4: complete validation report",
        "complete": "Done: steward SELECTION from report",
    }.get(phase, phase)


def build_plan_context(scoreboard: dict[str, Any], slot: str) -> dict[str, Any]:
    """Why / goals / outcomes for steward nudges and walkthrough."""
    logged = int(scoreboard["sessions_logged"])
    target = int(scoreboard["sessions_target"])
    remaining = int(scoreboard["sessions_remaining"])
    week_count = int(scoreboard["sessions_this_week"])
    phase = str(scoreboard.get("plan_phase") or resolve_plan_phase(scoreboard))

    shared_why = (
        "Agents can ship code; only you can prove traders want the wedge. "
        f"The build gate stays closed until {target} logged sessions + validation report COMPLETE."
    )
    shared_outcome = (
        "Unlock the next chartered chapter, know if the 15-second story lands, "
        "and avoid building platform surface nobody asked for."
    )

    if slot == "monday":
        weekly_goal = (
            "Book one 20–30 min guided demo before Thursday."
            if week_count == 0
            else f"Add {max(0, 2 - week_count)} more session(s) this week ({week_count} so far)."
        )
        moves = [
            "Pick one name from your outreach list (BTC options / quant-curious).",
            "Send a short text — ask for 20–30 min this week, honest feedback.",
            "Calendar hold when they reply; link marketstructureos.com.",
        ]
        if phase == "start":
            moves.insert(
                0,
                "If you have not yet: solo-run DEMO_OPERATOR_SCRIPT once (~5 min).",
            )
        why_today = (
            "Monday ping — validation is a calendar problem. "
            "No outreach text = no session = score stays 0/10."
        )
    else:
        weekly_goal = (
            "Log one MSOS P8 row or an honest skip reason — 5 minutes."
            if week_count == 0
            else f"Capture session {week_count} notes in VALIDATION_REALITY_CHECKS while fresh."
        )
        moves = [
            f"Open {REALITY_CHECKS_REL} § MSOS P8.",
            "Add one dated row (comprehension / return Y/N) OR note: Skipped week — reason.",
            "Run ppe_steward_scoreboard.py — confirm count moved.",
        ]
        why_today = (
            "Thursday ping — no repo row means the session did not count for the company. "
            "This is the receipt that opens the gate."
        )

    return {
        "phase": phase,
        "phase_label": _phase_label(phase),
        "north_star": NORTH_STAR,
        "why_plan": shared_why,
        "why_today": why_today,
        "what_you_get": shared_outcome,
        "this_week_goal": weekly_goal,
        "moves_today": moves,
        "score_line": f"{logged}/{target} sessions ({remaining} to gate)",
        "report_status": scoreboard["validation_report_status"],
    }


def format_plan_walkthrough(scoreboard: dict[str, Any], *, slot: str | None = None) -> str:
    """Full plan review for operator — run anytime to agree with the plan."""
    phase = str(scoreboard.get("plan_phase") or resolve_plan_phase(scoreboard))
    lines = [
        "PPE steward plan walkthrough",
        "",
        f"Where you are: {_phase_label(phase)}",
        f"Score: {scoreboard['sessions_logged']}/{scoreboard['sessions_target']} sessions",
        f"Report: {scoreboard['validation_report_status']}",
        "",
        "North star",
        NORTH_STAR,
        "",
        "Why this plan exists",
        build_plan_context(scoreboard, "monday")["why_plan"],
        "",
        "What you are trying to get out of it",
        "- Proof traders understand implied + disagreement in ~15 seconds",
        "- Return intent (would they open it again?)",
        "- Honest paid-interest signal before widening scope",
        "- Evidence to unlock next SELECTION (not agent guesswork)",
        "",
    ]
    for day_slot, label in (("monday", "Monday 13:00 — outreach"), ("thursday", "Thursday 20:00 — receipt")):
        if slot and slot != day_slot:
            continue
        ctx = build_plan_context(scoreboard, day_slot)
        lines.extend(
            [
                label,
                f"Why: {ctx['why_today']}",
                f"This week: {ctx['this_week_goal']}",
                "Your moves:",
            ]
        )
        for i, move in enumerate(ctx["moves_today"], 1):
            lines.append(f"  {i}. {move}")
        lines.append("")

    lines.extend(
        [
            "Full step-by-step",
            GUIDE_REL,
            "",
            "Agree? Execute Monday/Thursday moves. Skip only with logged reason.",
        ]
    )
    return "\n".join(lines)


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
    phase = str(scoreboard.get("plan_phase") or resolve_plan_phase(scoreboard))
    lines = [
        "PPE steward scoreboard",
        "",
        f"Plan phase: {_phase_label(phase)}",
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
    lines.append("")
    lines.append("Full plan: python scripts/ppe_steward_scoreboard.py --walkthrough")
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
    actions = scoreboard.get("next_actions") or []
    ctx = build_plan_context(scoreboard, slot)
    phase = ctx["phase_label"]

    if slot == "monday":
        title = f"PPE steward Mon: outreach ({logged}/{target})"
    else:
        title = f"PPE steward Thu: log receipt ({logged}/{target})"

    lines = [
        phase,
        "",
        "Why this ping",
        ctx["why_today"],
        "",
        "Why the plan",
        ctx["why_plan"],
        "",
        "What you get out of it",
        ctx["what_you_get"],
        "",
        "This week",
        ctx["this_week_goal"],
        "",
        "Your moves now",
    ]
    for i, move in enumerate(ctx["moves_today"], 1):
        lines.append(f"{i}. {move}")

    lines.extend(
        [
            "",
            f"Score: {ctx['score_line']} · Report: {ctx['report_status']}",
            "",
            "Also on deck:",
        ]
    )
    for i, action in enumerate(actions[:3], 1):
        lines.append(f"- {action}")

    lines.extend(["", "Walkthrough: python scripts/ppe_steward_scoreboard.py --walkthrough", GUIDE_REL])
    body = "\n".join(lines)
    if len(body) > 3800:
        body = body[:3797] + "..."
    return title, body


def cmd_scoreboard(repo: Path, *, as_json: bool, walkthrough: bool = False) -> int:
    sb = build_scoreboard(repo)
    if walkthrough:
        print(format_plan_walkthrough(sb))
        return 0
    if as_json:
        print(json.dumps(sb, indent=2))
    else:
        print(format_scoreboard_text(sb))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE steward scoreboard (human commitments)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true", help="Emit JSON scoreboard")
    ap.add_argument(
        "--walkthrough",
        action="store_true",
        help="Print full plan (why, goals, Mon/Thu moves) for operator review",
    )
    args = ap.parse_args(argv)
    return cmd_scoreboard(args.repo_root.resolve(), as_json=args.json, walkthrough=args.walkthrough)


if __name__ == "__main__":
    raise SystemExit(main())
