"""Weekly human-readable digest from DEV_CHANGELOG + frontier steering."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Literal

from scripts.ppe_dev_changelog import CHAPTER_CLOSED_PREFIX, QUIET_STUB, load_changelog

DIGEST_REL = "docs/RELEASES/WEEKLY_DIGEST.md"
STATE_REL = "docs/RELEASES/.weekly_digest_state.json"
NOTIFY_REL = "artifacts/control_plane/WEEKLY_DIGEST_NOTIFY.json"
MSOS_FRONTIER_REL = "docs/SOP/MSOS_FRONTIER.md"
MVP1_FRONTIER_REL = "docs/SOP/MVP1_FRONTIER.md"

HEADER_LINES = [
    "# Weekly digest (rolling)",
    "",
    "Monday-morning summaries (UTC). Each section covers the prior Monday–Sunday week.",
    "Receipt detail: [`DEV_CHANGELOG.md`](DEV_CHANGELOG.md).",
    "",
]

BulletKind = Literal["product", "ops", "skip"]

OPS_PATTERNS = (
    re.compile(r"control-plane:", re.I),
    re.compile(r"\bcontrol:", re.I),
    re.compile(r"\bOps:", re.I),
    re.compile(r"\bSELECTION\b", re.I),
    re.compile(r"charter witness", re.I),
    re.compile(r"PHASE_QUEUE", re.I),
    re.compile(r"fix\(tests\):", re.I),
    re.compile(r"merge-to-push-gate", re.I),
    re.compile(r"Workflow-efficiency", re.I),
    re.compile(r"integrate repo layer map", re.I),
    re.compile(r"^ci:", re.I),
)

PRODUCT_PATH_HINTS = ("apps/msos-web/", "src/viz/", "src/engine/")


@dataclass
class WeeklyDigestState:
    recorded_weeks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"recorded_weeks": list(self.recorded_weeks)}

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> WeeklyDigestState:
        return WeeklyDigestState(recorded_weeks=[str(x) for x in (raw.get("recorded_weeks") or [])])


@dataclass
class WeekSection:
    week_monday: str
    in_short: str
    product_lines: list[str]
    ops_summary: str
    whats_next_lines: list[str]
    merge_count: int
    receipt_anchor: str
    friction_lines: list[str] = field(default_factory=list)

    def to_markdown(self) -> list[str]:
        mon = date.fromisoformat(self.week_monday)
        sun = mon + timedelta(days=6)
        lines = [
            f"## Week of {self.week_monday} (Mon–Sun UTC)",
            "",
            f"**In short:** {self.in_short}",
            "",
            "### What shipped (product)",
        ]
        if self.product_lines:
            lines.extend(self.product_lines)
        else:
            lines.append("- Nothing user-visible merged to `main` this week.")
        lines.append("")
        lines.append("### Behind the scenes")
        lines.append(f"- {self.ops_summary}")
        lines.append("")
        if self.friction_lines:
            lines.append("### Workflow friction")
            lines.extend(self.friction_lines)
            lines.append("")
        lines.append("### What's next")
        if self.whats_next_lines:
            lines.extend(self.whats_next_lines)
        else:
            lines.append("- See [`MSOS_FRONTIER.md`](../SOP/MSOS_FRONTIER.md) for live steering.")
        lines.append("")
        lines.append("### Receipt")
        lines.append(
            f"- {self.merge_count} merge(s) to `main` — "
            f"detail in [DEV_CHANGELOG.md](DEV_CHANGELOG.md#{self.receipt_anchor})."
        )
        lines.append("")
        return lines


def digest_path(repo: Path) -> Path:
    return repo / DIGEST_REL


def notify_payload_path(repo: Path) -> Path:
    return repo / NOTIFY_REL


_MONTH_ABBR = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
_GITHUB_REMOTE_RE = re.compile(
    r"^(?:https://github\.com/|git@github\.com:)([^/]+)/([^/.]+?)(?:\.git)?$"
)


def format_week_range(week_monday: str) -> str:
    mon = date.fromisoformat(week_monday)
    sun = mon + timedelta(days=6)
    if mon.month == sun.month:
        return f"{_MONTH_ABBR[mon.month - 1]} {mon.day}-{sun.day}"
    return f"{_MONTH_ABBR[mon.month - 1]} {mon.day}-{_MONTH_ABBR[sun.month - 1]} {sun.day}"


def _repo_is_public_on_github(repo: Path) -> bool:
    try:
        proc = subprocess.run(
            ["gh", "repo", "view", "--json", "isPrivate"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if proc.returncode != 0:
        return False
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return False
    return not bool(data.get("isPrivate"))


def resolve_digest_click_url(repo: Path, *, branch: str = "main") -> str | None:
    if not _repo_is_public_on_github(repo):
        return None
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    match = _GITHUB_REMOTE_RE.match((proc.stdout or "").strip())
    if not match:
        return None
    rel = DIGEST_REL.replace("\\", "/")
    return f"https://github.com/{match.group(1)}/{match.group(2)}/blob/{branch}/{rel}"


def _phone_product_line(raw: str) -> str:
    text = raw.strip()
    match = re.match(r"\*\*(.+?)\*\*:?\s*(.*)", text)
    if not match:
        return re.sub(r"`", "", text).strip()
    label = match.group(1).strip().rstrip(":")
    for prefix in (
        "MSOS website — ",
        "MSOS program — ",
        "PPE implied lab (Streamlit): ",
        "MVP1 engine / lab: ",
        "MSOS design: ",
    ):
        if label.startswith(prefix):
            label = label[len(prefix) :]
            break
    rest = re.sub(r"`", "", match.group(2)).strip().rstrip(".")
    if rest:
        short_rest = rest.split("—", 1)[0].strip()
        if len(short_rest) > 72:
            short_rest = short_rest[:69].rstrip() + "..."
        return f"{label}: {short_rest}" if short_rest else label
    return label


def _user_facing_ship(raw: str) -> str:
    lower = raw.lower()
    if "homepage" in lower and "p2" in lower:
        return "MSOS now has a public homepage you can share"
    if "command center" in lower and "p3" in lower:
        return "Signed-in Command Center shell is live (preview data)"
    if "stack decision" in lower or (re.search(r"\bp1\b", lower) and "streamlit" in lower):
        return "Website + PPE lab fit is documented and locked in"
    if "storyboard" in lower:
        return "UI storyboards landed for upcoming design chapters"
    if "trust" in lower or "disagreement" in lower:
        return "PPE lab trust and disagreement views got sharper"
    if "onboarding" in lower:
        return "PPE lab onboarding is clearer and easier to follow"
    if "smoke witness" in lower:
        return "PPE lab picked up stronger automated UI checks"
    if CHAPTER_CLOSED_PREFIX in raw:
        title = raw.split(CHAPTER_CLOSED_PREFIX, 1)[-1].split("(`", 1)[0].strip()
        if title:
            return f"Chapter wrapped: {title}"
    return _phone_product_line(raw)


def _phone_next_line(raw: str) -> str:
    text = re.sub(r"\*\*", "", raw)
    text = re.sub(r"`", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def _user_facing_next(raw: str) -> str:
    lower = raw.lower()
    if "active build chapter" in lower:
        match = re.search(r"MSOS P\d[^—\n*]*", raw, re.I)
        if match:
            label = re.sub(r"\*+", "", match.group(0)).strip()
            return f"Building next: {label}"
    if "next slice" in lower and "evidence" in lower:
        return "Next up: Command Center evidence charter"
    if "mvp1 track" in lower:
        return "MVP1 lab still has active slices in flight"
    return _phone_next_line(raw)


def build_phone_digest_notify(section: dict[str, Any]) -> dict[str, str]:
    week = str(section["week_monday"])
    merge_count = int(section.get("merge_count") or 0)
    product_lines = [str(x) for x in (section.get("product_lines") or [])]
    ops_summary = str(section.get("ops_summary") or "").strip()
    whats_next = [str(x) for x in (section.get("whats_next_lines") or [])]
    week_range = format_week_range(week)
    product_count = len(product_lines)

    if product_count >= 4:
        opener = f"Strong week. {product_count} user-facing changes just landed."
    elif product_count == 3:
        opener = "Good momentum - three updates you'll actually notice."
    elif product_count == 2:
        opener = "Two solid wins shipped this week."
    elif product_count == 1:
        opener = "One meaningful update went live."
    else:
        opener = "Quiet product week - the build factory kept humming."

    lines = [opener, "", "What's different for you"]
    if product_lines:
        shown: list[str] = []
        for line in product_lines[:3]:
            item = _user_facing_ship(line)
            if item not in shown:
                shown.append(item)
        for item in shown:
            lines.append(f"- {item}")
        extra = product_count - len(shown)
        if extra > 0:
            lines.append(f"- +{extra} more ship(s) this week")
    else:
        lines.append("- No user-visible surface changes merged to main")
    lines.append("")

    if ops_summary:
        ops = ops_summary.lstrip("- ").strip()
        ops = re.sub(r"— omitted from product bullets above\.?", "", ops).strip()
        match = re.search(r"(\d+)\s+control-plane", ops, re.I)
        if match:
            lines.extend(["Behind the curtain", f"{match.group(1)} planning and CI merges kept automation moving.", ""])
        else:
            lines.extend(["Behind the curtain", ops, ""])

    if whats_next:
        lines.append("On deck")
        for raw in whats_next[:2]:
            lines.append(f"- {_user_facing_next(raw)}")
        lines.append("")

    friction = [str(x) for x in (section.get("friction_lines") or [])]
    if friction:
        lines.append("Workflow watch")
        for raw in friction[:2]:
            text = raw.lstrip("- ").strip()
            if text:
                lines.append(f"- {text}")
        lines.append("")

    if section.get("click_url"):
        lines.append(f"{merge_count} merges to main. Tap for the long read on GitHub.")
    else:
        lines.append(f"{merge_count} merges to main. You're caught up - details are above.")

    body = "\n".join(lines).strip()
    if len(body) > 3500:
        body = body[:3497] + "..."
    return {"phone_title": f"This week in PPE - {week_range}", "phone_body": body}


def parse_latest_week_summary(text: str) -> dict[str, Any] | None:
    """Return summary for the newest ## Week of section in WEEKLY_DIGEST.md."""
    week_monday: str | None = None
    in_short: str | None = None
    merge_count = 0
    in_first_week = False
    current_section: str | None = None
    product_lines: list[str] = []
    ops_summary = ""
    whats_next_lines: list[str] = []
    friction_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## Week of "):
            if week_monday is not None:
                break
            week_monday = line.split("## Week of ", 1)[1].split(" ", 1)[0].strip()
            in_first_week = True
            current_section = None
            continue
        if not in_first_week:
            continue
        if line.startswith("## "):
            break
        if line.startswith("### What shipped"):
            current_section = "product"
            continue
        if line.startswith("### Behind the scenes"):
            current_section = "ops"
            continue
        if line.startswith("### What's next"):
            current_section = "next"
            continue
        if line.startswith("### Workflow friction"):
            current_section = "friction"
            continue
        if line.startswith("### "):
            current_section = None
            continue

        stripped = line.strip()
        if stripped.startswith("**In short:**"):
            in_short = stripped.split("**In short:**", 1)[1].strip()
        elif current_section == "product" and stripped.startswith("- "):
            product_lines.append(stripped[2:])
        elif current_section == "ops" and stripped.startswith("- ") and not ops_summary:
            ops_summary = stripped[2:]
        elif current_section == "next" and stripped.startswith("- "):
            whats_next_lines.append(stripped[2:])
        elif current_section == "friction" and stripped.startswith("- "):
            friction_lines.append(stripped)
        elif stripped.startswith("- ") and "merge(s) to `main`" in stripped:
            match = re.search(r"(\d+)\s+merge\(s\)", stripped)
            if match:
                merge_count = int(match.group(1))

    if week_monday and in_short:
        return {
            "week_monday": week_monday,
            "in_short": in_short,
            "merge_count": merge_count,
            "digest_rel": DIGEST_REL,
            "product_lines": product_lines,
            "ops_summary": ops_summary,
            "whats_next_lines": whats_next_lines,
            "friction_lines": friction_lines,
        }
    return None


def cmd_write_notify_payload(repo: Path) -> int:
    repo = repo.resolve()
    p = digest_path(repo)
    if not p.is_file():
        print("ppe_weekly_digest: notify payload skipped (no digest file)", file=sys.stderr)
        return 1
    summary = parse_latest_week_summary(p.read_text(encoding="utf-8"))
    if not summary:
        print("ppe_weekly_digest: notify payload skipped (no week section)", file=sys.stderr)
        return 1
    summary["generated_at_utc"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    click_url = resolve_digest_click_url(repo)
    if click_url:
        summary["click_url"] = click_url
    summary.update(build_phone_digest_notify(summary))
    try:
        from scripts.ppe_human_backlog import (
            open_items,
            phone_snippet_lines,
            render_markdown,
            write_notify_snippet,
        )

        (repo / "docs/SOP/HUMAN_STEWARD_BACKLOG.md").write_text(
            render_markdown(repo), encoding="utf-8"
        )
        write_notify_snippet(repo)
        snippet = phone_snippet_lines(repo)
        if snippet:
            summary["human_backlog_open"] = len(open_items(repo))
            body = str(summary.get("phone_body") or "").strip()
            summary["phone_body"] = f"{body}\n\n" + "\n".join(snippet) if body else "\n".join(snippet)
    except ImportError:
        pass
    out = notify_payload_path(repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ppe_weekly_digest: wrote {out}")
    return 0


def state_path(repo: Path) -> Path:
    return repo / STATE_REL


def load_state(repo: Path) -> WeeklyDigestState:
    p = state_path(repo)
    if not p.is_file():
        return WeeklyDigestState()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return WeeklyDigestState.from_dict(raw)
    except (json.JSONDecodeError, OSError):
        pass
    return WeeklyDigestState()


def save_state(repo: Path, state: WeeklyDigestState) -> None:
    p = state_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def monday_of_week(d: date) -> date:
    return d - timedelta(days=d.weekday())


def last_completed_week_monday(ref: datetime | None = None) -> date:
    ref = ref or datetime.now(timezone.utc)
    this_monday = monday_of_week(ref.date())
    return this_monday - timedelta(days=7)


def week_dates(week_monday: date) -> list[str]:
    return [(week_monday + timedelta(days=i)).isoformat() for i in range(7)]


def _bullet_body(bullet: str) -> str:
    return bullet[2:].strip() if bullet.startswith("- ") else bullet.strip()


def classify_bullet(bullet: str) -> BulletKind:
    body = _bullet_body(bullet)
    if not body or body == QUIET_STUB:
        return "skip"
    if CHAPTER_CLOSED_PREFIX in body:
        return "product"
    for pat in OPS_PATTERNS:
        if pat.search(body):
            if any(h in body for h in PRODUCT_PATH_HINTS):
                return "product"
            if re.search(r"\bMSOS P[0-9]\b", body, re.I) and re.search(
                r"homepage|Command Center|Product-Slice", body, re.I
            ):
                return "product"
            return "ops"
    if any(h in body for h in PRODUCT_PATH_HINTS):
        return "product"
    if re.search(r"\bMSOS P[0-9]\b", body, re.I):
        return "product"
    if re.search(r"\bMVP1\b", body, re.I) and re.search(
        r"Product-Slice|trust|review|onboarding|disagreement|smoke witness", body, re.I
    ):
        return "product"
    if re.search(r"storyboard", body, re.I):
        return "product"
    return "ops"


def _strip_technical_tail(body: str) -> str:
    body = re.sub(r"\s*\(`[^`]+/`\)\s*$", "", body)
    body = re.sub(r"\s*\(#[0-9]+\)\s*", " ", body)
    body = re.sub(r"^`[0-9a-f]+`\s*—\s*", "", body)
    return body.strip()


def humanize_product_bullet(bullet: str) -> str:
    body = _strip_technical_tail(_bullet_body(bullet))
    if CHAPTER_CLOSED_PREFIX in body:
        rest = body.split(CHAPTER_CLOSED_PREFIX, 1)[1].strip()
        title = rest.split("(`", 1)[0].strip()
        return f"- **Chapter complete:** {title}."

    lower = body.lower()
    if "msos p2" in lower and "homepage" in lower:
        return (
            "- **MSOS website — homepage (P2):** Public marketing homepage and platform wiring "
            "landed on `main`."
        )
    if "msos p3" in lower and "command center" in lower:
        return (
            "- **MSOS website — Command Center (P3):** Authenticated workspace shell and overview "
            "page (fixture/preview data) landed on `main`."
        )
    if "msos p1" in lower and ("routing" in lower or "adr" in lower):
        return (
            "- **MSOS program — stack decision (P1):** Documented how the Next.js site and "
            "Streamlit PPE app fit together (no PPE math changes)."
        )
    if "storyboard" in lower:
        return "- **MSOS design:** Storyboard assets installed in-repo for upcoming UI chapters."
    if "src/viz/" in bullet or ("mvp1" in lower and "trust" in lower):
        return "- **PPE implied lab (Streamlit):** Trust or UI work shipped in the MVP1 lab."
    if "apps/msos-web/" in bullet:
        cleaned = body.split("(")[0].strip().rstrip(".")
        return f"- **MSOS website:** {cleaned}."
    if re.search(r"\bMVP1\b", body, re.I):
        cleaned = body.split("(")[0].strip().rstrip(".")
        if len(cleaned) >= 12:
            return f"- **MVP1 engine / lab:** {cleaned}."
    cleaned = body.split("(")[0].strip().rstrip(".")
    if len(cleaned) < 12 or cleaned.lower() in {"feat", "feat."}:
        return ""
    return f"- {cleaned}."


def _dedupe_lines(lines: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for ln in lines:
        key = ln.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(ln)
    return out


def collect_week_bullets(repo: Path, week_monday: date) -> tuple[list[str], int]:
    parsed = load_changelog(repo)
    all_bullets: list[str] = []
    for day in week_dates(week_monday):
        all_bullets.extend(parsed.sections.get(day, []))
    return all_bullets, len(all_bullets)


def build_in_short(product_human: list[str]) -> str:
    if not product_human:
        return "No user-visible product changes merged to `main` this week."
    texts = [ln.lstrip("- ").split(":**", 1)[-1].strip().rstrip(".") for ln in product_human[:2]]
    if len(texts) == 1:
        return f"This week: {texts[0]}."
    return f"This week: {texts[0]} Also: {texts[1]}."


def build_ops_summary(ops_count: int, total: int) -> str:
    if ops_count == 0 and total == 0:
        return "No merges to `main` recorded in the dev changelog for this week."
    if ops_count == 0:
        return "No separate automation or planning-only merges called out."
    return (
        f"{ops_count} control-plane / planning merge(s) (charters, SELECTION, CI, operator tooling) "
        "— omitted from product bullets above."
    )


def _read_text(repo: Path, rel: str) -> str:
    p = repo / rel
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")


def extract_whats_next(repo: Path) -> list[str]:
    lines: list[str] = []
    msos = _read_text(repo, MSOS_FRONTIER_REL)
    for ln in msos.splitlines():
        s = ln.strip()
        if s.startswith("- **Active BUILD chapter:**"):
            lines.append(f"- {s[2:].strip()}")
        if "**NEXT**" in s and "|" in s and "Slice" in s:
            cols = [c.strip() for c in s.strip("|").split("|")]
            if len(cols) >= 3:
                lines.append(f"- **Next slice:** {cols[2]} ({cols[1].strip()})")
            break

    mvp1 = _read_text(repo, MVP1_FRONTIER_REL)
    mvp1_active = False
    for ln in mvp1.splitlines():
        if "| **OPEN** |" in ln or "| **NEXT** |" in ln:
            mvp1_active = True
            break
    if mvp1_active:
        lines.append("- **MVP1 track:** active slices in [`MVP1_FRONTIER.md`](../SOP/MVP1_FRONTIER.md).")
    return lines[:4]


def build_week_section(repo: Path, week_monday: date) -> WeekSection:
    from scripts.ppe_workflow_radar import load_radar_friction_lines

    bullets, total = collect_week_bullets(repo, week_monday)
    product_raw: list[str] = []
    ops_count = 0
    for b in bullets:
        kind = classify_bullet(b)
        if kind == "product":
            product_raw.append(b)
        elif kind == "ops":
            ops_count += 1

    product_human = _dedupe_lines(
        [h for b in product_raw for h in [humanize_product_bullet(b)] if h]
    )
    anchor = week_monday.isoformat()
    for day in reversed(week_dates(week_monday)):
        if load_changelog(repo).sections.get(day):
            anchor = day
            break

    return WeekSection(
        week_monday=week_monday.isoformat(),
        in_short=build_in_short(product_human),
        product_lines=product_human,
        ops_summary=build_ops_summary(ops_count, total),
        whats_next_lines=extract_whats_next(repo),
        merge_count=total,
        receipt_anchor=anchor,
        friction_lines=load_radar_friction_lines(repo, week_monday),
    )


def render_digest(sections: dict[str, WeekSection]) -> str:
    lines = list(HEADER_LINES)
    for week_key in sorted(sections.keys(), reverse=True):
        lines.extend(sections[week_key].to_markdown())
    return "\n".join(lines).rstrip() + "\n"


def _rebuild_sections(repo: Path, week_ids: list[str]) -> dict[str, WeekSection]:
    sections: dict[str, WeekSection] = {}
    for wid in week_ids:
        sections[wid] = build_week_section(repo, date.fromisoformat(wid))
    return sections


def cmd_generate(repo: Path, *, week_monday: date | None = None, force: bool = False) -> int:
    repo = repo.resolve()
    state = load_state(repo)
    target = week_monday or last_completed_week_monday()
    week_id = target.isoformat()

    if week_id in state.recorded_weeks and not force:
        print(f"ppe_weekly_digest: skip (already recorded {week_id})")
        return 0

    if week_id not in state.recorded_weeks:
        state.recorded_weeks.append(week_id)

    all_week_ids = sorted(set(state.recorded_weeks), reverse=True)
    sections = _rebuild_sections(repo, all_week_ids)

    digest_path(repo).parent.mkdir(parents=True, exist_ok=True)
    digest_path(repo).write_text(render_digest(sections), encoding="utf-8")
    save_state(repo, state)
    print(f"ppe_weekly_digest: wrote week of {week_id}")
    return 0


def cmd_backfill(repo: Path, *, weeks: int = 4) -> int:
    repo = repo.resolve()
    state = load_state(repo)
    ref_monday = last_completed_week_monday()
    new_ids: list[str] = []
    for i in range(weeks):
        wm = monday_of_week(ref_monday - timedelta(days=7 * i))
        new_ids.append(wm.isoformat())

    for wid in new_ids:
        if wid not in state.recorded_weeks:
            state.recorded_weeks.append(wid)

    all_week_ids = sorted(set(state.recorded_weeks), reverse=True)
    sections = _rebuild_sections(repo, all_week_ids)

    digest_path(repo).parent.mkdir(parents=True, exist_ok=True)
    digest_path(repo).write_text(render_digest(sections), encoding="utf-8")
    save_state(repo, state)
    print(f"ppe_weekly_digest: backfill wrote {len(all_week_ids)} week(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Weekly human-readable digest")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate digest for last completed week (Mon–Sun UTC)")
    p_gen.add_argument("--week", type=str, default=None, help="Week Monday YYYY-MM-DD")
    p_gen.add_argument("--force", action="store_true")

    p_back = sub.add_parser("backfill", help="Seed recent completed weeks")
    p_back.add_argument("--weeks", type=int, default=4)

    sub.add_parser("write-notify-payload", help="Write JSON for Windows toast notifier")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "generate":
        week: date | None = None
        if args.week:
            week = monday_of_week(date.fromisoformat(args.week))
        return cmd_generate(repo, week_monday=week, force=args.force)
    if args.command == "backfill":
        return cmd_backfill(repo, weeks=args.weeks)
    if args.command == "write-notify-payload":
        return cmd_write_notify_payload(repo)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
