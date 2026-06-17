"""Human steward backlog — policy/architecture topics outside the auto-loop.

Source: docs/SOP/HUMAN_STEWARD_BACKLOG.json
Readable: docs/SOP/HUMAN_STEWARD_BACKLOG.md (render-md)
Weekly ntfy: open high-priority titles appended to WEEKLY_DIGEST_NOTIFY payload.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKLOG_REL = "docs/SOP/HUMAN_STEWARD_BACKLOG.json"
BACKLOG_MD_REL = "docs/SOP/HUMAN_STEWARD_BACKLOG.md"
NOTIFY_SNIPPET_REL = "artifacts/control_plane/HUMAN_BACKLOG_NOTIFY.json"

OPEN_STATUSES = frozenset({"open", "in_progress"})
DONE_STATUSES = frozenset({"done", "deferred", "cancelled"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def backlog_path(repo: Path) -> Path:
    return repo.resolve() / BACKLOG_REL


def load_backlog(repo: Path) -> dict[str, Any]:
    p = backlog_path(repo)
    if not p.is_file():
        return {"version": 1, "items": []}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def _items(backlog: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in (backlog.get("items") or []) if isinstance(i, dict)]


def open_items(
    repo: Path,
    *,
    priority: str | None = None,
    include_in_progress: bool = True,
) -> list[dict[str, Any]]:
    statuses = set(OPEN_STATUSES if include_in_progress else {"open"})
    out: list[dict[str, Any]] = []
    for item in _items(load_backlog(repo)):
        st = str(item.get("status") or "open").strip().lower()
        if st not in statuses:
            continue
        if priority and str(item.get("priority") or "").strip().lower() != priority.lower():
            continue
        out.append(item)
    rank = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda i: (rank.get(str(i.get("priority") or "medium").lower(), 9), str(i.get("id") or "")))
    return out


def phone_snippet_lines(repo: Path, *, max_items: int = 3) -> list[str]:
    items = open_items(repo, priority="high")
    if not items:
        items = open_items(repo)[:max_items]
    else:
        items = items[:max_items]
    if not items:
        return []
    lines = ["Steward topics (human backlog)"]
    for item in items:
        pri = str(item.get("priority") or "medium").upper()
        title = str(item.get("title") or item.get("id") or "?")
        lines.append(f"- [{pri}] {title}")
    remaining = len(open_items(repo)) - len(items)
    if remaining > 0:
        lines.append(f"- +{remaining} more open — see HUMAN_STEWARD_BACKLOG.md")
    return lines


def render_markdown(repo: Path) -> str:
    backlog = load_backlog(repo)
    notes = str(backlog.get("notes") or "").strip()
    lines = [
        "# Human steward backlog",
        "",
        "**Purpose:** Policy and architecture topics too big for the auto-loop. "
        "Work through these deliberately — not via `PHASE_CHAPTER_BACKLOG.json`.",
        "",
        "| When | Action |",
        "|------|--------|",
        "| **Weekly** (Monday digest) | Scan open **high** items — ntfy lists top titles |",
        "| **Monthly** ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)) | Pick one item → `in_progress` |",
        "| **When done** | Set `status: done` + `closed` date in JSON; run `render-md` |",
        "",
        "**Machine source:** [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) · "
        "**Refresh this file:** `python scripts/ppe_human_backlog.py render-md`",
        "",
    ]
    if notes:
        lines.extend([f"> {notes}", ""])

    by_status: dict[str, list[dict[str, Any]]] = {}
    for item in _items(backlog):
        st = str(item.get("status") or "open").strip().lower()
        by_status.setdefault(st, []).append(item)

    order = ["in_progress", "open", "deferred", "done", "cancelled"]
    for status in order:
        bucket = by_status.pop(status, [])
        if not bucket:
            continue
        lines.append(f"## {status.replace('_', ' ').title()}")
        lines.append("")
        for item in bucket:
            iid = str(item.get("id") or "")
            title = str(item.get("title") or iid)
            pri = str(item.get("priority") or "medium")
            cat = str(item.get("category") or "")
            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"- **id:** `{iid}` · **priority:** {pri} · **category:** {cat}")
            if item.get("added"):
                lines.append(f"- **added:** {item.get('added')}")
            if item.get("closed"):
                lines.append(f"- **closed:** {item.get('closed')}")
            lines.append(f"- **summary:** {item.get('summary') or ''}")
            if item.get("policyQuestion"):
                lines.append(f"- **policy question:** {item.get('policyQuestion')}")
            if item.get("notes"):
                lines.append(f"- **notes:** {item.get('notes')}")
            lines.append("")

    for status, bucket in sorted(by_status.items()):
        lines.append(f"## {status.title()}")
        lines.append("")
        for item in bucket:
            lines.append(f"- {item.get('title') or item.get('id')}")
        lines.append("")

    lines.append("## Changelog")
    lines.append("")
    lines.append(f"| {datetime.now(timezone.utc).date().isoformat()} | Auto-render from JSON |")
    lines.append("")
    return "\n".join(lines)


def write_notify_snippet(repo: Path) -> Path | None:
    open_all = open_items(repo)
    if not open_all:
        return None
    payload = {
        "generated_at_utc": _utc_now(),
        "open_count": len(open_all),
        "high_open_count": len(open_items(repo, priority="high")),
        "open_ids": [str(i.get("id") or "") for i in open_all],
        "phone_lines": phone_snippet_lines(repo),
        "backlog_rel": BACKLOG_MD_REL,
    }
    out = repo / NOTIFY_SNIPPET_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def cmd_status(repo: Path) -> int:
    items = open_items(repo)
    high = [i for i in items if str(i.get("priority") or "").lower() == "high"]
    print(f"Human steward backlog: {len(items)} open ({len(high)} high)")
    for item in items:
        pri = str(item.get("priority") or "medium").upper()
        st = str(item.get("status") or "open")
        print(f"  [{pri}/{st}] {item.get('title') or item.get('id')}")
    print(f"\nFull list: {BACKLOG_MD_REL}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Human steward backlog (policy/architecture review)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--status", action="store_true", help="Print open items")
    ap.add_argument("--render-md", action="store_true", help="Write HUMAN_STEWARD_BACKLOG.md from JSON")
    ap.add_argument("--write-notify-snippet", action="store_true", help="Write artifacts/control_plane/HUMAN_BACKLOG_NOTIFY.json")
    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.render_md:
        out = repo / BACKLOG_MD_REL
        out.write_text(render_markdown(repo), encoding="utf-8")
        print(f"ppe_human_backlog: wrote {out.relative_to(repo)}")
        return 0
    if args.write_notify_snippet:
        path = write_notify_snippet(repo)
        if path is None:
            print("ppe_human_backlog: no open items — notify snippet skipped")
            return 0
        print(f"ppe_human_backlog: wrote {path.relative_to(repo)}")
        return 0
    if args.status:
        return cmd_status(repo)

    return cmd_status(repo)


if __name__ == "__main__":
    raise SystemExit(main())
