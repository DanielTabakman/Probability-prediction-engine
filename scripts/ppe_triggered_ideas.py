"""Triggered ideas — park decisions until a chapter/plan makes them relevant.

Source: docs/SOP/TRIGGERED_IDEAS.json
Readable: docs/SOP/TRIGGERED_IDEAS.md (render-md)
Alert artifact: artifacts/control_plane/TRIGGERED_IDEAS_ALERT.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKLOG_REL = "docs/SOP/TRIGGERED_IDEAS.json"
BACKLOG_MD_REL = "docs/SOP/TRIGGERED_IDEAS.md"
ALERT_REL = "artifacts/control_plane/TRIGGERED_IDEAS_ALERT.json"
ARCHIVE_REL = "artifacts/logbook/triggered_ideas_archived.jsonl"

ACTIVE_STATUSES = frozenset({"parked", "surfaced"})
CLOSED_STATUSES = frozenset({"dismissed", "done"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def backlog_path(repo: Path) -> Path:
    return repo.resolve() / BACKLOG_REL


def load_backlog(repo: Path) -> dict[str, Any]:
    p = backlog_path(repo)
    if not p.is_file():
        return {"version": 1, "items": []}
    return json.loads(p.read_text(encoding="utf-8-sig"))


def save_backlog(repo: Path, backlog: dict[str, Any]) -> Path:
    p = backlog_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    return p


def _items(backlog: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in (backlog.get("items") or []) if isinstance(i, dict)]


def active_items(repo: Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in _items(load_backlog(repo)):
        st = str(item.get("status") or "parked").strip().lower()
        if st in ACTIVE_STATUSES:
            out.append(item)
    rank = {"high": 0, "medium": 1, "low": 2}
    out.sort(key=lambda i: (rank.get(str(i.get("priority") or "medium").lower(), 9), str(i.get("id") or "")))
    return out


def _slug_id(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", title.strip().lower()).strip("_")
    return slug[:64] or "idea"


def resolve_chapter_id(repo: Path, plan_path: str) -> str:
    norm = plan_path.replace("\\", "/").strip()
    try:
        from scripts.ppe_queue import load_queue

        for item in load_queue(repo).get("items") or []:
            if not isinstance(item, dict):
                continue
            if str(item.get("planPath") or "").replace("\\", "/").strip() != norm:
                continue
            cid = str(item.get("chapterId") or "").strip()
            if cid:
                return cid
    except FileNotFoundError:
        pass

    backlog_json = repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
    if backlog_json.is_file():
        try:
            data = json.loads(backlog_json.read_text(encoding="utf-8-sig"))
            for item in data.get("items") or []:
                if not isinstance(item, dict):
                    continue
                if str(item.get("planPath") or "").replace("\\", "/").strip() != norm:
                    continue
                cid = str(item.get("chapterId") or "").strip()
                if cid:
                    return cid
        except json.JSONDecodeError:
            pass

    stem = Path(norm).stem
    if stem.endswith("_relay"):
        return stem[: -len("_relay")]
    return stem


def _plan_context(repo: Path, plan_path: str) -> dict[str, str]:
    norm = plan_path.replace("\\", "/").strip()
    ctx = {"plan_path": norm, "chapter_id": resolve_chapter_id(repo, norm), "text": ""}
    parts: list[str] = [ctx["chapter_id"], norm]
    try:
        from scripts.ppe_manifest import load_phase_plan

        plan = load_phase_plan(repo, norm)
        parts.append(str(plan.get("name") or ""))
        for key in ("sprintSpecPath", "selectionRecord"):
            rel = str(plan.get(key) or "").strip()
            if rel:
                parts.append(rel)
                p = repo / rel.replace("\\", "/")
                if p.is_file():
                    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()[:120]
                    parts.append("\n".join(lines))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    ctx["text"] = "\n".join(parts).lower()
    return ctx


@dataclass
class TriggerMatch:
    item_id: str
    title: str
    summary: str
    reason: str


def _trigger_lists(item: dict[str, Any]) -> tuple[list[str], list[str], list[str], list[str]]:
    triggers = item.get("triggers") if isinstance(item.get("triggers"), dict) else {}
    chapter_ids = [str(x).strip() for x in (triggers.get("chapterIds") or []) if str(x).strip()]
    plan_paths = [str(x).replace("\\", "/").strip() for x in (triggers.get("planPaths") or []) if str(x).strip()]
    keywords = [str(x).strip().lower() for x in (triggers.get("keywords") or []) if str(x).strip()]
    not_for = [str(x).strip() for x in (item.get("notFor") or []) if str(x).strip()]
    return chapter_ids, plan_paths, keywords, not_for


def match_item(item: dict[str, Any], ctx: dict[str, str]) -> TriggerMatch | None:
    st = str(item.get("status") or "parked").strip().lower()
    if st not in ACTIVE_STATUSES:
        return None

    chapter_id = ctx["chapter_id"]
    plan_path = ctx["plan_path"]
    text = ctx["text"]

    chapter_ids, plan_paths, keywords, not_for = _trigger_lists(item)
    if chapter_id and chapter_id in not_for:
        return None
    if plan_path in not_for:
        return None

    reasons: list[str] = []
    if chapter_id and chapter_id in chapter_ids:
        reasons.append(f"chapterId={chapter_id}")
    if plan_path in plan_paths:
        reasons.append(f"planPath={plan_path}")
    for kw in keywords:
        if kw and kw in text:
            reasons.append(f"keyword={kw!r}")
            break

    if not reasons:
        return None

    iid = str(item.get("id") or "")
    return TriggerMatch(
        item_id=iid,
        title=str(item.get("title") or iid),
        summary=str(item.get("summary") or ""),
        reason="; ".join(reasons),
    )


def find_matches(repo: Path, *, plan_path: str, chapter_id: str | None = None) -> list[TriggerMatch]:
    ctx = _plan_context(repo, plan_path)
    if chapter_id:
        ctx["chapter_id"] = chapter_id
        ctx["text"] = f"{chapter_id}\n{ctx['text']}"
    matches: list[TriggerMatch] = []
    for item in _items(load_backlog(repo)):
        m = match_item(item, ctx)
        if m is not None:
            matches.append(m)
    return matches


def _mark_surfaced(repo: Path, item_ids: list[str]) -> None:
    if not item_ids:
        return
    backlog = load_backlog(repo)
    ids = set(item_ids)
    changed = False
    for item in _items(backlog):
        if str(item.get("id") or "") not in ids:
            continue
        if str(item.get("status") or "").lower() == "parked":
            item["status"] = "surfaced"
            item["surfacedAt"] = _utc_now()
            changed = True
    if changed:
        save_backlog(repo, backlog)


def write_alert(repo: Path, *, plan_path: str, chapter_id: str, matches: list[TriggerMatch]) -> Path | None:
    if not matches:
        alert = repo / ALERT_REL
        if alert.is_file():
            alert.unlink()
        return None
    payload = {
        "generated_at_utc": _utc_now(),
        "plan_path": plan_path.replace("\\", "/"),
        "chapter_id": chapter_id,
        "matches": [
            {
                "id": m.item_id,
                "title": m.title,
                "summary": m.summary,
                "reason": m.reason,
                "dismiss_cmd": f"python scripts/ppe_triggered_ideas.py dismiss {m.item_id}",
            }
            for m in matches
        ],
        "backlog_rel": BACKLOG_MD_REL,
    }
    out = repo / ALERT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def surface_for_plan(repo: Path, plan_path: str, *, chapter_id: str | None = None) -> list[TriggerMatch]:
    """Find matches, mark surfaced, write alert artifact, print operator lines."""
    matches = find_matches(repo, plan_path=plan_path, chapter_id=chapter_id)
    cid = chapter_id or resolve_chapter_id(repo, plan_path)
    if matches:
        _mark_surfaced(repo, [m.item_id for m in matches])
        write_alert(repo, plan_path=plan_path, chapter_id=cid, matches=matches)
        print("ppe_triggered_ideas: reconsider parked ideas for this chapter:")
        for m in matches:
            print(f"  - [{m.item_id}] {m.title} ({m.reason})")
            print(f"    dismiss: python scripts/ppe_triggered_ideas.py dismiss {m.item_id}")
    else:
        write_alert(repo, plan_path=plan_path, chapter_id=cid, matches=[])
    return matches


def render_markdown(repo: Path) -> str:
    backlog = load_backlog(repo)
    notes = str(backlog.get("notes") or "").strip()
    lines = [
        "# Triggered ideas",
        "",
        "**Purpose:** Park \"great idea, too early\" items with revisit triggers. "
        "They surface when a matching chapter enters SELECTION — dismiss when processed.",
        "",
        "| Command | Action |",
        "|---------|--------|",
        "| `triggered_ideas.cmd` | List active parked ideas |",
        "| `python scripts/ppe_triggered_ideas.py add ...` | Park a new idea |",
        "| `python scripts/ppe_triggered_ideas.py dismiss <id>` | Done — hide from active list |",
        "| `python scripts/ppe_triggered_ideas.py dismiss <id> --purge` | Remove + archive one line |",
        "",
        "**Machine source:** [`TRIGGERED_IDEAS.json`](TRIGGERED_IDEAS.json) · "
        "**Alert artifact:** `artifacts/control_plane/TRIGGERED_IDEAS_ALERT.json`",
        "",
    ]
    if notes:
        lines.extend([f"> {notes}", ""])

    active = active_items(repo)
    if active:
        lines.append("## Active (parked / surfaced)")
        lines.append("")
        for item in active:
            iid = str(item.get("id") or "")
            title = str(item.get("title") or iid)
            pri = str(item.get("priority") or "medium")
            st = str(item.get("status") or "parked")
            lines.append(f"### {title}")
            lines.append("")
            lines.append(f"- **id:** `{iid}` · **priority:** {pri} · **status:** {st}")
            if item.get("added"):
                lines.append(f"- **added:** {item.get('added')}")
            if item.get("surfacedAt"):
                lines.append(f"- **surfaced:** {item.get('surfacedAt')}")
            lines.append(f"- **summary:** {item.get('summary') or ''}")
            chapter_ids, plan_paths, keywords, not_for = _trigger_lists(item)
            if chapter_ids:
                lines.append(f"- **trigger chapterIds:** {', '.join(f'`{c}`' for c in chapter_ids)}")
            if plan_paths:
                lines.append(f"- **trigger planPaths:** {', '.join(f'`{p}`' for p in plan_paths)}")
            if keywords:
                lines.append(f"- **trigger keywords:** {', '.join(keywords)}")
            if not_for:
                lines.append(f"- **not for:** {', '.join(f'`{n}`' for n in not_for)}")
            lines.append("")
    else:
        lines.extend(["## Active (parked / surfaced)", "", "_None — head cleared._", ""])

    closed: list[dict[str, Any]] = []
    for item in _items(backlog):
        st = str(item.get("status") or "").strip().lower()
        if st in CLOSED_STATUSES:
            closed.append(item)
    if closed:
        lines.append("## Closed")
        lines.append("")
        for item in closed[-12:]:
            iid = str(item.get("id") or "")
            title = str(item.get("title") or iid)
            st = str(item.get("status") or "")
            closed_date = item.get("closed") or ""
            resolution = str(item.get("resolution") or "").strip()
            line = f"- **{title}** (`{iid}`) — {st}"
            if closed_date:
                line += f" · {closed_date}"
            if resolution:
                line += f" — {resolution}"
            lines.append(line)
        lines.append("")

    lines.extend(["## Changelog", "", f"| {_today()} | Auto-render from JSON |", ""])
    return "\n".join(lines)


def add_item(
    repo: Path,
    *,
    title: str,
    summary: str,
    idea_id: str = "",
    priority: str = "low",
    trigger_chapters: list[str] | None = None,
    trigger_plans: list[str] | None = None,
    trigger_keywords: list[str] | None = None,
    not_for: list[str] | None = None,
) -> Path:
    backlog = load_backlog(repo)
    items = list(backlog.get("items") or [])
    iid = (idea_id or _slug_id(title)).strip()
    for item in items:
        if isinstance(item, dict) and str(item.get("id") or "") == iid:
            raise SystemExit(f"id already exists: {iid}")
    row: dict[str, Any] = {
        "id": iid,
        "title": title.strip(),
        "summary": summary.strip(),
        "status": "parked",
        "priority": priority.strip().lower(),
        "added": _today(),
        "triggers": {
            "chapterIds": [x.strip() for x in (trigger_chapters or []) if x.strip()],
            "planPaths": [x.replace("\\", "/").strip() for x in (trigger_plans or []) if x.strip()],
            "keywords": [x.strip() for x in (trigger_keywords or []) if x.strip()],
        },
    }
    nf = [x.strip() for x in (not_for or []) if x.strip()]
    if nf:
        row["notFor"] = nf
    items.append(row)
    backlog["items"] = items
    save_backlog(repo, backlog)
    md_path = repo / BACKLOG_MD_REL
    md_path.write_text(render_markdown(repo), encoding="utf-8")
    return backlog_path(repo)


def close_item(
    repo: Path,
    idea_id: str,
    *,
    status: str,
    resolution: str = "",
    purge: bool = False,
) -> Path | None:
    backlog = load_backlog(repo)
    items = list(backlog.get("items") or [])
    idx = None
    row: dict[str, Any] | None = None
    for i, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("id") or "") == idea_id:
            idx = i
            row = item
            break
    if row is None:
        raise SystemExit(f"unknown id: {idea_id}")

    row["status"] = status
    row["closed"] = _today()
    if resolution.strip():
        row["resolution"] = resolution.strip()

    if purge:
        archive = repo / ARCHIVE_REL
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive_line = {
            "archived_at_utc": _utc_now(),
            "id": idea_id,
            "title": row.get("title"),
            "status": status,
            "resolution": row.get("resolution", ""),
        }
        with archive.open("a", encoding="utf-8") as f:
            f.write(json.dumps(archive_line, ensure_ascii=False) + "\n")
        items.pop(idx)
    else:
        items[idx] = row

    backlog["items"] = items
    save_backlog(repo, backlog)
    md_path = repo / BACKLOG_MD_REL
    md_path.write_text(render_markdown(repo), encoding="utf-8")
    return backlog_path(repo)


def cmd_status(repo: Path) -> int:
    items = active_items(repo)
    print(f"Triggered ideas: {len(items)} active")
    for item in items:
        pri = str(item.get("priority") or "medium").upper()
        st = str(item.get("status") or "parked")
        iid = str(item.get("id") or "")
        print(f"  [{pri}/{st}] {item.get('title') or iid} ({iid})")
    print(f"\nFull list: {BACKLOG_MD_REL}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Triggered ideas — park until relevant, dismiss when done")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="cmd")

    sub.add_parser("status", help="List active ideas")

    rm = sub.add_parser("render-md", help="Write TRIGGERED_IDEAS.md from JSON")
    rm.add_argument("--repo-root", type=Path, default=Path.cwd())

    ck = sub.add_parser("check", help="Check triggers for a plan (dry-run surface)")
    ck.add_argument("--plan", required=True, help="Phase plan path")
    ck.add_argument("--chapter-id", default="", help="Optional chapterId override")

    ad = sub.add_parser("add", help="Park a new idea")
    ad.add_argument("--title", required=True)
    ad.add_argument("--summary", required=True)
    ad.add_argument("--id", default="")
    ad.add_argument("--priority", default="low", choices=["high", "medium", "low"])
    ad.add_argument("--trigger-chapter", action="append", default=[], dest="trigger_chapters")
    ad.add_argument("--trigger-plan", action="append", default=[], dest="trigger_plans")
    ad.add_argument("--trigger-keyword", action="append", default=[], dest="trigger_keywords")
    ad.add_argument("--not-for", action="append", default=[], dest="not_for")

    ds = sub.add_parser("dismiss", help="Close idea (optional --purge to remove from JSON)")
    ds.add_argument("id")
    ds.add_argument("--reason", default="", help="Resolution note")
    ds.add_argument("--purge", action="store_true", help="Remove row and append to archive jsonl")

    dn = sub.add_parser("done", help="Mark idea processed into real work")
    dn.add_argument("id")
    dn.add_argument("--resolution", default="")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.cmd == "render-md":
        out = repo / BACKLOG_MD_REL
        out.write_text(render_markdown(repo), encoding="utf-8")
        print(f"ppe_triggered_ideas: wrote {out.relative_to(repo)}")
        return 0

    if args.cmd == "check":
        matches = surface_for_plan(
            repo,
            args.plan.replace("\\", "/"),
            chapter_id=args.chapter_id.strip() or None,
        )
        print(f"ppe_triggered_ideas: {len(matches)} match(es)")
        return 0

    if args.cmd == "add":
        path = add_item(
            repo,
            title=args.title,
            summary=args.summary,
            idea_id=args.id,
            priority=args.priority,
            trigger_chapters=args.trigger_chapters,
            trigger_plans=args.trigger_plans,
            trigger_keywords=args.trigger_keywords,
            not_for=args.not_for,
        )
        print(f"ppe_triggered_ideas: added -> {path.relative_to(repo)}")
        return 0

    if args.cmd == "dismiss":
        close_item(
            repo,
            args.id,
            status="dismissed",
            resolution=args.reason,
            purge=args.purge,
        )
        verb = "purged" if args.purge else "dismissed"
        print(f"ppe_triggered_ideas: {verb} {args.id}")
        return 0

    if args.cmd == "done":
        close_item(repo, args.id, status="done", resolution=args.resolution)
        print(f"ppe_triggered_ideas: done {args.id}")
        return 0

    if args.cmd == "status" or args.cmd is None:
        return cmd_status(repo)

    print(f"unknown command: {args.cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
