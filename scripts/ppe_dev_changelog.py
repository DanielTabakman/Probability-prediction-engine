"""Rolling dev release changelog — dated sections from main merges and chapter closeouts."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

CHANGELOG_REL = "docs/RELEASES/DEV_CHANGELOG.md"
STATE_REL = "docs/RELEASES/.dev_changelog_state.json"

HEADER_LINES = [
    "# Dev changelog (rolling)",
    "",
    "Human-readable release notes for work that landed on `main`. "
    "Updated on merge, daily (UTC), and chapter closeout.",
    "",
]

QUIET_STUB = "_No merges to `main`._"
CHAPTER_CLOSED_PREFIX = "**Chapter closed:**"
SLICE_ID_RE = re.compile(r"\b(?:MSOS|MVP1)-[A-Za-z0-9]+-(?:Control|Product|Platform|Smoke|Witness|Closeout)-Slice\d+\b")
PATH_HINT_DIRS = ("apps/msos-web/", "src/viz/", "src/engine/", "scripts/", "docs/SOP/")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _utc_today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _run_git(repo: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} failed: {err}")
    return (proc.stdout or "").strip()


@dataclass
class ChangelogState:
    recorded_shas: list[str] = field(default_factory=list)
    last_main_sha: str = ""
    recorded_events: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "recorded_shas": list(self.recorded_shas),
            "last_main_sha": self.last_main_sha,
            "recorded_events": list(self.recorded_events),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ChangelogState:
        return cls(
            recorded_shas=[str(x) for x in (raw.get("recorded_shas") or [])],
            last_main_sha=str(raw.get("last_main_sha") or ""),
            recorded_events=[str(x) for x in (raw.get("recorded_events") or [])],
        )


@dataclass
class ParsedChangelog:
    sections: dict[str, list[str]]

    def to_markdown(self) -> str:
        lines = list(HEADER_LINES)
        for date in sorted(self.sections.keys(), reverse=True):
            lines.append(f"## {date}")
            lines.append("")
            bullets = self.sections[date]
            if bullets:
                lines.extend(bullets)
            else:
                lines.append(QUIET_STUB)
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"


def changelog_path(repo: Path) -> Path:
    return repo / CHANGELOG_REL


def state_path(repo: Path) -> Path:
    return repo / STATE_REL


def load_state(repo: Path) -> ChangelogState:
    p = state_path(repo)
    if not p.is_file():
        return ChangelogState()
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            return ChangelogState.from_dict(raw)
    except (json.JSONDecodeError, OSError):
        pass
    return ChangelogState()


def save_state(repo: Path, state: ChangelogState) -> None:
    p = state_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_changelog(text: str) -> ParsedChangelog:
    sections: dict[str, list[str]] = {}
    current_date: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current_date = line[3:].strip()
            sections.setdefault(current_date, [])
            continue
        if current_date is None:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped == QUIET_STUB:
            continue
        if stripped.startswith("- "):
            sections[current_date].append(stripped)
    return ParsedChangelog(sections=sections)


def load_changelog(repo: Path) -> ParsedChangelog:
    p = changelog_path(repo)
    if not p.is_file():
        return ParsedChangelog(sections={})
    return parse_changelog(p.read_text(encoding="utf-8"))


def save_changelog(repo: Path, parsed: ParsedChangelog) -> None:
    p = changelog_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(parsed.to_markdown(), encoding="utf-8")


def _resolve_main_ref(repo: Path) -> str:
    try:
        _run_git(repo, ["rev-parse", "--verify", "origin/main"])
        return "origin/main"
    except RuntimeError:
        return "main"


def _main_head(repo: Path) -> str:
    ref = _resolve_main_ref(repo)
    return _run_git(repo, ["rev-parse", ref])


def _commit_info(repo: Path, sha: str) -> tuple[str, str, str, str]:
    """Returns full_sha, short_sha, subject, date_utc (YYYY-MM-DD)."""
    fmt = "%H\t%h\t%s\t%cI"
    line = _run_git(repo, ["show", "-s", f"--format={fmt}", sha])
    parts = line.split("\t", 3)
    if len(parts) < 4:
        raise RuntimeError(f"unexpected git show format for {sha}: {line!r}")
    full_sha, short_sha, subject, committed = parts[0], parts[1], parts[2], parts[3]
    date_utc = committed[:10]
    return full_sha, short_sha, subject, date_utc


def _path_hint(repo: Path, sha: str) -> str:
    try:
        names = _run_git(repo, ["diff-tree", "--no-commit-id", "--name-only", "-r", sha])
    except RuntimeError:
        return ""
    if not names:
        return ""
    counts: dict[str, int] = {}
    for name in names.splitlines():
        norm = name.replace("\\", "/")
        for prefix in PATH_HINT_DIRS:
            if norm.startswith(prefix):
                counts[prefix] = counts.get(prefix, 0) + 1
                break
    if not counts:
        return ""
    top = max(counts, key=lambda k: counts[k])
    return top.rstrip("/")


def _chapter_title_from_plan(repo: Path, phase_plan: Path | str | None, slice_id: str) -> str | None:
    if not phase_plan:
        return None
    plan_path = Path(phase_plan)
    if not plan_path.is_absolute():
        plan_path = repo / plan_path
    if not plan_path.is_file():
        return None
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        if str(sl.get("sliceId") or "").strip() != slice_id:
            continue
        closeout = sl.get("closeout")
        if isinstance(closeout, dict):
            title = str(closeout.get("chapterTitle") or "").strip()
            if title:
                return title
    return None


def format_commit_bullet(
    repo: Path,
    *,
    full_sha: str,
    short_sha: str,
    subject: str,
    phase_plan: Path | str | None = None,
) -> str:
    subj = subject.strip()
    if subj.lower().startswith("control-closeout:"):
        slice_part = subj.split(":", 1)[1].strip()
        title = _chapter_title_from_plan(repo, phase_plan, slice_part) or slice_part
        return f"- {CHAPTER_CLOSED_PREFIX} {title} (`{slice_part}`)"

    hint = _path_hint(repo, full_sha)
    if SLICE_ID_RE.search(subj):
        line = f"- {subj}"
    else:
        line = f"- `{short_sha}` — {subj}"
    if hint:
        line += f" (`{hint}/`)"
    return line


def _list_commits(
    repo: Path,
    *,
    since_sha: str | None = None,
    since_days: int | None = None,
) -> list[str]:
    ref = _resolve_main_ref(repo)
    args = ["log", ref, "--format=%H", "--reverse"]
    if since_sha:
        args.append(f"{since_sha}..{ref}")
    elif since_days is not None:
        since_dt = datetime.now(timezone.utc) - timedelta(days=since_days)
        args.append(f"--since={since_dt.strftime('%Y-%m-%d')}")
    out = _run_git(repo, args)
    if not out:
        return []
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def _bullet_exists(parsed: ParsedChangelog, bullet: str) -> bool:
    needle = bullet.strip()
    for bullets in parsed.sections.values():
        if needle in bullets:
            return True
    return False


def _append_bullet(parsed: ParsedChangelog, date: str, bullet: str) -> None:
    if _bullet_exists(parsed, bullet):
        return
    parsed.sections.setdefault(date, [])
    parsed.sections[date].insert(0, bullet)


def process_commits(
    repo: Path,
    *,
    shas: list[str],
    state: ChangelogState,
    parsed: ParsedChangelog,
    phase_plan: Path | str | None = None,
) -> int:
    added = 0
    for sha in shas:
        if sha in state.recorded_shas:
            continue
        full_sha, short_sha, subject, date_utc = _commit_info(repo, sha)
        bullet = format_commit_bullet(
            repo,
            full_sha=full_sha,
            short_sha=short_sha,
            subject=subject,
            phase_plan=phase_plan,
        )
        if not _bullet_exists(parsed, bullet):
            _append_bullet(parsed, date_utc, bullet)
            added += 1
        state.recorded_shas.append(full_sha)
    if shas:
        state.last_main_sha = _main_head(repo)
    return added


def cmd_refresh(
    repo: Path,
    *,
    day: str | None = None,
    phase_plan: Path | str | None = None,
) -> int:
    repo = repo.resolve()
    state = load_state(repo)
    parsed = load_changelog(repo)

    since = state.last_main_sha or None
    if since:
        try:
            _run_git(repo, ["merge-base", "--is-ancestor", since, _resolve_main_ref(repo)])
        except RuntimeError:
            since = None

    new_shas = _list_commits(repo, since_sha=since)
    if not since and not state.recorded_shas:
        new_shas = _list_commits(repo, since_days=30)

    added = process_commits(repo, shas=new_shas, state=state, parsed=parsed, phase_plan=phase_plan)

    if day:
        parsed.sections.setdefault(day, [])

    save_changelog(repo, parsed)
    save_state(repo, state)
    print(f"ppe_dev_changelog: refresh added {added} commit bullet(s)")
    return 0


def cmd_backfill(repo: Path, *, days: int = 30) -> int:
    repo = repo.resolve()
    state = load_state(repo)
    parsed = load_changelog(repo)
    shas = _list_commits(repo, since_days=days)
    pending = [s for s in shas if s not in state.recorded_shas]
    added = process_commits(repo, shas=pending, state=state, parsed=parsed)
    save_changelog(repo, parsed)
    save_state(repo, state)
    print(f"ppe_dev_changelog: backfill added {added} commit bullet(s) over {days} days")
    return 0


def append_chapter_closed_event(
    repo: Path,
    *,
    slice_id: str,
    phase_plan: Path | str | None = None,
    title: str | None = None,
) -> int:
    repo = repo.resolve()
    event_key = f"chapter_closed:{slice_id}"
    state = load_state(repo)
    if event_key in state.recorded_events:
        print(f"ppe_dev_changelog: skip duplicate event {event_key}")
        return 0

    chapter_title = (title or "").strip() or _chapter_title_from_plan(repo, phase_plan, slice_id) or slice_id
    bullet = f"- {CHAPTER_CLOSED_PREFIX} {chapter_title} (`{slice_id}`)"

    parsed = load_changelog(repo)
    today = _utc_today()
    if not _bullet_exists(parsed, bullet):
        _append_bullet(parsed, today, bullet)
        save_changelog(repo, parsed)

    state.recorded_events.append(event_key)
    save_state(repo, state)
    print(f"ppe_dev_changelog: appended chapter_closed {slice_id}")
    return 0


def cmd_append_event(
    repo: Path,
    *,
    kind: str,
    slice_id: str,
    title: str = "",
    phase_plan: Path | str | None = None,
) -> int:
    if kind != "chapter_closed":
        print(f"ppe_dev_changelog: unknown event kind {kind!r}", file=sys.stderr)
        return 1
    return append_chapter_closed_event(
        repo,
        slice_id=slice_id,
        phase_plan=phase_plan,
        title=title or None,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Rolling dev release changelog")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_refresh = sub.add_parser("refresh", help="Append new origin/main commits since last recorded SHA")
    p_refresh.add_argument("--day", type=str, default=None, help="Ensure YYYY-MM-DD section (quiet stub if empty)")
    p_refresh.add_argument("--phase-plan", type=Path, default=None)

    p_backfill = sub.add_parser("backfill", help="Seed changelog from recent main history")
    p_backfill.add_argument("--days", type=int, default=30)

    p_event = sub.add_parser("append-event", help="Append a relay cycle event")
    p_event.add_argument("--kind", required=True)
    p_event.add_argument("--slice-id", required=True)
    p_event.add_argument("--title", default="")
    p_event.add_argument("--phase-plan", type=Path, default=None)

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "refresh":
        return cmd_refresh(repo, day=args.day, phase_plan=args.phase_plan)
    if args.command == "backfill":
        return cmd_backfill(repo, days=args.days)
    if args.command == "append-event":
        return cmd_append_event(
            repo,
            kind=args.kind,
            slice_id=args.slice_id,
            title=args.title,
            phase_plan=args.phase_plan,
        )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
