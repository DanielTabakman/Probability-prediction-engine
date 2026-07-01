"""Context window closeout — machine facts + draft report for retiring a Cursor chat.

Canon: docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_human_backlog import BACKLOG_REL as HUMAN_BACKLOG_REL
from scripts.ppe_human_backlog import load_backlog as load_human_backlog
from scripts.ppe_human_backlog import render_markdown as render_human_md
from scripts.ppe_manifest import load_manifest, resolve_summary
from scripts.ppe_propagate_queue import backlog_path, load_backlog as load_chapter_backlog
from scripts.workflow_metrics_cli import (
    CONTEXT_WINDOWS_FILE,
    _append_jsonl,
    _metrics_dir,
    read_context_windows,
)

DRAFT_REL = "artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT_DRAFT.md"
SNAPSHOT_REL = "artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT.json"
WHATS_NEXT_JSON_REL = "artifacts/control_plane/WHATS_NEXT.json"
WHATS_NEXT_MD_REL = "artifacts/control_plane/WHATS_NEXT.md"
SOP_CLOSEOUT = "docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug_id(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    return s.strip("_")[:64] or "item"


def _run_json_script(repo: Path, rel_script: str) -> dict[str, Any] | None:
    script = repo / rel_script.replace("\\", "/")
    if not script.is_file():
        return None
    proc = subprocess.run(
        [sys.executable, str(script), "--json"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1) or not proc.stdout.strip():
        return None
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None


def _git_head(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _gh_open_prs(repo: Path) -> list[dict[str, str]]:
    try:
        proc = subprocess.run(
            ["gh", "pr", "list", "--json", "number,title,state,headRefName,url,isDraft"],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return []
    if proc.returncode != 0 or not proc.stdout.strip():
        return []
    try:
        rows = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return []
    out: list[dict[str, str]] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        out.append(
            {
                "number": str(row.get("number") or ""),
                "title": str(row.get("title") or ""),
                "state": str(row.get("state") or ""),
                "branch": str(row.get("headRefName") or ""),
                "url": str(row.get("url") or ""),
                "draft": str(bool(row.get("isDraft"))).lower(),
            }
        )
    return out


def _operator_verdict(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_operator_status import collect_operator_status

        return collect_operator_status(repo)
    except Exception as exc:
        return {"verdict": "UNKNOWN", "errors": [str(exc)]}


def collect_snapshot(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    preflight = _run_json_script(repo, "scripts/frontier_preflight.py") or {}
    manifest: dict[str, Any] = {}
    try:
        manifest = load_manifest(repo)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    summary: dict[str, Any] = {}
    try:
        summary = resolve_summary(repo)
    except Exception:
        pass
    operator = _operator_verdict(repo)
    chapter_backlog = load_chapter_backlog(repo) if backlog_path(repo).is_file() else {"items": []}
    human_backlog = load_human_backlog(repo)
    open_human = [
        i
        for i in (human_backlog.get("items") or [])
        if isinstance(i, dict)
        and str(i.get("status") or "open").lower() in ("open", "in_progress")
    ]
    blocked_chapters = [
        i
        for i in (chapter_backlog.get("items") or [])
        if isinstance(i, dict) and str(i.get("status") or "").lower() == "blocked"
    ]
    return {
        "generated_at_utc": _utc_now(),
        "head": _git_head(repo),
        "preflight": preflight,
        "manifest": {
            "status": manifest.get("status"),
            "phasePlanPath": manifest.get("phasePlanPath"),
            "sprintSpecPath": manifest.get("sprintSpecPath"),
        },
        "manifest_summary": {
            "chapter_id": summary.get("chapter_id") or summary.get("chapterId"),
            "plan_path": summary.get("plan_path") or summary.get("planPath"),
        },
        "operator": {
            "verdict": operator.get("verdict"),
            "commands": operator.get("commands") or [],
            "avoid": operator.get("avoid") or [],
            "errors": operator.get("errors") or [],
        },
        "open_prs": _gh_open_prs(repo),
        "backlog_counts": {
            "chapter_blocked": len(blocked_chapters),
            "human_open": len(open_human),
        },
        "canon": SOP_CLOSEOUT,
    }


def _checklist_line(done: bool, label: str) -> str:
    return f"- [{'x' if done else ' '}] {label}"


def render_draft_markdown(
    repo: Path,
    snapshot: dict[str, Any],
    *,
    ship_report: dict[str, Any] | None = None,
) -> str:
    pf = snapshot.get("preflight") if isinstance(snapshot.get("preflight"), dict) else {}
    branch = str(pf.get("branch") or "?")
    wt = str(pf.get("working_tree") or "?")
    upstream = str(pf.get("upstream") or "?")
    stash = pf.get("stash_entries")
    by_plane = pf.get("files_by_plane") if isinstance(pf.get("files_by_plane"), dict) else {}
    manifest = snapshot.get("manifest") if isinstance(snapshot.get("manifest"), dict) else {}
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    prs = snapshot.get("open_prs") if isinstance(snapshot.get("open_prs"), list) else []
    ms = snapshot.get("manifest_summary") if isinstance(snapshot.get("manifest_summary"), dict) else {}

    lines = [
        "# Context window closeout (draft)",
        "",
        f"**Generated:** {snapshot.get('generated_at_utc')} · **HEAD:** `{snapshot.get('head') or '?'}`",
        "",
        f"**Canon:** [`{SOP_CLOSEOUT}`]({SOP_CLOSEOUT})",
        "",
        "> Complete all `<!-- AGENT_FILL -->` sections, then use **Next thread** from the SOP.",
        "",
        "## Machine facts",
        "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Branch | `{branch}` |",
        f"| Working tree | **{wt}** |",
        f"| Upstream | {upstream} |",
        f"| Stash entries | {stash} |",
        f"| Manifest status | `{manifest.get('status')}` |",
        f"| Active plan | `{manifest.get('phasePlanPath') or '(none)'}` |",
        f"| Chapter (summary) | `{ms.get('chapter_id') or '?'}` |",
        f"| Operator verdict | **{op.get('verdict')}** |",
        f"| Chapter backlog (blocked) | {snapshot.get('backlog_counts', {}).get('chapter_blocked', '?')} |",
        f"| Human backlog (open) | {snapshot.get('backlog_counts', {}).get('human_open', '?')} |",
        "",
        "### Dirty files by plane",
        "",
    ]
    if by_plane:
        for plane in ("CONTROL-PLANE", "PRODUCT-PLANE", "EVIDENCE-PLANE", "SUSPICIOUS / UNKNOWN"):
            files = by_plane.get(plane) or []
            if not files:
                continue
            lines.append(f"**{plane}** ({len(files)}):")
            for p in files:
                lines.append(f"- `{p}`")
            lines.append("")
    else:
        lines.append("_(none reported)_")
        lines.append("")

    if op.get("commands"):
        lines.extend(["### Operator commands (suggested)", ""])
        for c in op.get("commands") or []:
            lines.append(f"- `{c}`")
        lines.append("")
    if op.get("avoid"):
        lines.extend(["### Operator avoid", ""])
        for c in op.get("avoid") or []:
            lines.append(f"- `{c}`")
        lines.append("")

    lines.extend(["## Operational sweep", ""])
    tree_clean = wt == "clean"
    ship = ship_report if isinstance(ship_report, dict) else {}
    ship_ok = ship.get("ok") is True and not ship.get("blocked")
    parked = ship.get("parked") if isinstance(ship.get("parked"), list) else []
    if ship:
        tree_clean = tree_clean or (ship_ok and not parked)
    pushed_ok = any(
        isinstance(s, dict)
        and s.get("step") in ("publish", "publish_ahead")
        and s.get("ok") is True
        for s in (ship.get("steps") or [])
    )
    prs_reviewed = len(prs) == 0 or pushed_ok or ship_ok
    lines.append(_checklist_line(tree_clean or bool(parked), "Working tree clean or explicitly PARKED"))
    lines.append(_checklist_line(pushed_ok or tree_clean, "Unpushed commits pushed (feature branches)"))
    lines.append(_checklist_line(False, "`main` pulled / ff-only current"))
    lines.append(_checklist_line(prs_reviewed, f"Open PRs reviewed ({len(prs)} listed below)"))
    lines.append(_checklist_line(ship_ok, "Auto-ship sweep (gate → commit → push → PR)"))
    lines.append(_checklist_line(False, "Operator / relay threads reconciled"))
    if ship:
        lines.extend(["", "### Auto-ship sweep", ""])
        lines.append(f"- **ok:** `{ship.get('ok')}` · **blocked:** `{ship.get('blocked')}`")
        if parked:
            lines.append(f"- **parked paths:** {len(parked)} (mixed-plane or gate failure)")
        for row in ship.get("steps") or []:
            if not isinstance(row, dict):
                continue
            detail = row.get("detail") or row.get("reason") or row.get("pr_url") or ""
            lines.append(f"- `{row.get('step')}` — ok={row.get('ok')} {detail}".rstrip())
        lines.append("")

    if prs:
        lines.extend(["### Open pull requests", ""])
        for pr in prs:
            if not isinstance(pr, dict):
                continue
            draft = " draft" if pr.get("draft") == "true" else ""
            lines.append(
                f"- #{pr.get('number')} `{pr.get('branch')}`{draft} — {pr.get('title')} ({pr.get('url')})"
            )
        lines.append("")

    lines.extend(
        [
            "## Window meta",
            "",
            "<!-- AGENT_FILL: Thread role (steward / IDE BUILD / recovery / exploratory) -->",
            "",
            "<!-- AGENT_FILL: Optimization target at start → at end -->",
            "",
            "### What happened",
            "",
            "<!-- AGENT_FILL: bullets — commits, PRs, docs, decisions (verify against git) -->",
            "",
            "### Why / how it arose",
            "",
            "<!-- AGENT_FILL: trigger, scope creep, operator event, bug, etc. -->",
            "",
            "### Threads inventory",
            "",
            "| Topic | Started | Finished | Abandoned | Next owner |",
            "|-------|---------|----------|-----------|------------|",
            "| <!-- AGENT_FILL --> | | | | |",
            "",
            "### Window ledger (optional)",
            "",
            "`Ledger — Roundtrips: _ | Raw copy-pastes: _ | Slices closed: _ | Active slice: _ | Next step: _`",
            "",
            "## Follow-up triage",
            "",
            "| Bucket | Item | Lane | Action / destination |",
            "|--------|------|------|----------------------|",
            "| ship_now | <!-- AGENT_FILL --> | control_plane | |",
            "| operator_next | <!-- AGENT_FILL --> | relay | operator thread |",
            "| build_backlog | <!-- AGENT_FILL --> | control_plane | `PHASE_CHAPTER_BACKLOG.json` |",
            "| human_backlog | <!-- AGENT_FILL --> | human | `HUMAN_STEWARD_BACKLOG.json` |",
            "| park | <!-- AGENT_FILL --> | mixed | branch/stash name |",
            "| drop | <!-- AGENT_FILL --> | — | reason |",
            "",
            "## AGENT CONTINUITY",
            "",
            "```text",
            "AGENT CONTINUITY",
            "- Safe to switch agents? <!-- YES/NO -->",
            "- Exact reason:",
            "- If YES: exact handoff payload required:",
            "- If NO: what must finish in-repo first:",
            "```",
            "",
            "## Next thread",
            "",
            "<!-- AGENT_FILL: @-mentions for the *next* Cursor thread only -->",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_artifacts(
    repo: Path,
    snapshot: dict[str, Any],
    *,
    ship_report: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / SNAPSHOT_REL
    md_path = repo / DRAFT_REL
    payload = dict(snapshot)
    if ship_report is not None:
        payload["ship_report"] = ship_report
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_draft_markdown(repo, snapshot, ship_report=ship_report), encoding="utf-8")
    return json_path, md_path


def _chapter_from_snapshot(snapshot: dict[str, Any]) -> str:
    ms = snapshot.get("manifest_summary") if isinstance(snapshot.get("manifest_summary"), dict) else {}
    cid = ms.get("chapter_id") or ms.get("chapterId")
    if cid:
        return str(cid).strip()
    manifest = snapshot.get("manifest") if isinstance(snapshot.get("manifest"), dict) else {}
    plan = str(manifest.get("phasePlanPath") or "").strip().replace("\\", "/")
    if not plan:
        return ""
    stem = Path(plan).stem
    if stem.endswith("_relay"):
        return stem[: -len("_relay")]
    return stem


def infer_whats_next(snapshot: dict[str, Any], *, ship_report: dict[str, Any] | None = None) -> str:
    from scripts.ppe_thread_roles import infer_next_thread_role, suggested_opener_for_role

    ship = ship_report if isinstance(ship_report, dict) else snapshot.get("ship_report")
    if isinstance(ship, dict):
        if ship.get("blocked"):
            return "Recovery: finish parked closeout ship (see CONTEXT_WINDOW_CLOSEOUT_DRAFT.md) or open a recovery thread."
        if ship.get("ok") and any(
            isinstance(s, dict) and s.get("step") in ("publish", "publish_ahead") and s.get("ok")
            for s in (ship.get("steps") or [])
        ):
            return "Shipped — CI auto-merges when green. Open operator thread and ask what's next?"
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    closing_role = str(snapshot.get("closeout_thread_role") or "operator")
    next_role = infer_next_thread_role(
        closing_role=closing_role,
        operator_verdict=str(op.get("verdict") or ""),
    )
    opener = suggested_opener_for_role(next_role)
    cmds = op.get("commands") or []
    if cmds:
        return f"Next thread role: **{next_role}**. Opener: `{opener}` · Operator: `{cmds[0]}`"
    verdict = str(op.get("verdict") or "").strip()
    if verdict:
        return f"Next thread role: **{next_role}**. Opener: `{opener}` · Verdict `{verdict}` — see `AGENT_CONTINUITY_BRIEF.md`."
    return f"Next thread role: **{next_role}**. Opener: `{opener}` · Read `AGENT_CONTINUITY_BRIEF.md`."


def build_closeout_record(
    snapshot: dict[str, Any],
    *,
    thread_role: str = "operator",
    whats_next: str = "",
    safe_to_switch: bool = True,
    slices_closed_in_thread: int = 0,
    triage_counts: dict[str, int] | None = None,
    notes: str = "",
    ship_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    from scripts.ppe_thread_roles import infer_next_thread_role, normalize_thread_role, suggested_opener_for_role

    pf = snapshot.get("preflight") if isinstance(snapshot.get("preflight"), dict) else {}
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    closed_at = str(snapshot.get("generated_at_utc") or _utc_now())
    ship = ship_report if isinstance(ship_report, dict) else snapshot.get("ship_report")
    role_norm = normalize_thread_role(thread_role)
    snap_for_infer = {**snapshot, "closeout_thread_role": role_norm}
    next_line = whats_next.strip() or infer_whats_next(snap_for_infer, ship_report=ship if isinstance(ship, dict) else None)
    next_role = infer_next_thread_role(
        closing_role=role_norm,
        operator_verdict=str(op.get("verdict") or ""),
    )
    if isinstance(ship, dict) and ship.get("blocked"):
        safe_to_switch = False
    return {
        "event": "context_window_closeout",
        "closeout_id": str(uuid.uuid4()),
        "closed_at": closed_at,
        "thread_role": role_norm,
        "next_thread_role": next_role,
        "suggested_opener": suggested_opener_for_role(next_role),
        "chapter_id": _chapter_from_snapshot(snapshot),
        "head": snapshot.get("head"),
        "branch": pf.get("branch"),
        "working_tree": pf.get("working_tree"),
        "operator_verdict": op.get("verdict"),
        "whats_next": next_line,
        "safe_to_switch_agents": bool(safe_to_switch),
        "slices_closed_in_thread": int(slices_closed_in_thread),
        "triage_counts": dict(triage_counts or {}),
        "notes": notes.strip(),
        "ship_ok": None if not isinstance(ship, dict) else ship.get("ok"),
        "ship_blocked": None if not isinstance(ship, dict) else ship.get("blocked"),
    }


def append_closeout_record(repo: Path, record: dict[str, Any]) -> Path:
    repo = repo.resolve()
    path = _metrics_dir(repo) / CONTEXT_WINDOWS_FILE
    _append_jsonl(path, record)
    return path


def latest_closeout_record(repo: Path) -> dict[str, Any] | None:
    rows = read_context_windows(repo)
    return rows[-1] if rows else None


def render_whats_next_markdown(record: dict[str, Any]) -> str:
    from scripts.ppe_thread_roles import normalize_thread_role, suggested_opener_for_role

    closed = str(record.get("closed_at") or "?")
    role = normalize_thread_role(str(record.get("thread_role") or "operator"))
    next_role = normalize_thread_role(str(record.get("next_thread_role") or role))
    opener = str(record.get("suggested_opener") or suggested_opener_for_role(next_role))
    chapter = str(record.get("chapter_id") or "(none)")
    line = str(record.get("whats_next") or infer_whats_next({}))
    safe = "yes" if record.get("safe_to_switch_agents") else "no"
    return "\n".join(
        [
            "# What's next",
            "",
            f"**Last context closeout:** {closed} · **closed as:** {role} · **chapter:** `{chapter}` · **safe to switch:** {safe}",
            "",
            f"**Next thread role:** `{next_role}`",
            f"**Suggested opener:** {opener}",
            "",
            line,
            "",
            "_Operator relay: open operator thread and ask **what's next?** Charter work: use **Charter thread** opener in `docs/SOP/THREAD_STARTERS_V1.md`._",
            "",
        ]
    )


def promote_whats_next(repo: Path, record: dict[str, Any]) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / WHATS_NEXT_JSON_REL
    md_path = repo / WHATS_NEXT_MD_REL
    payload = {
        "generated_at_utc": _utc_now(),
        "source": "context_window_closeout",
        "closeout_id": record.get("closeout_id"),
        "closed_at": record.get("closed_at"),
        "thread_role": record.get("thread_role"),
        "next_thread_role": record.get("next_thread_role"),
        "suggested_opener": record.get("suggested_opener"),
        "chapter_id": record.get("chapter_id"),
        "whats_next": record.get("whats_next"),
        "safe_to_switch_agents": record.get("safe_to_switch_agents"),
        "operator_verdict": record.get("operator_verdict"),
    }
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_whats_next_markdown(record), encoding="utf-8")
    return json_path, md_path


def record_context_closeout(
    repo: Path,
    snapshot: dict[str, Any],
    *,
    thread_role: str = "operator",
    whats_next: str = "",
    safe_to_switch: bool = True,
    slices_closed_in_thread: int = 0,
    triage_counts: dict[str, int] | None = None,
    notes: str = "",
    promote: bool = True,
    ship_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    record = build_closeout_record(
        snapshot,
        thread_role=thread_role,
        whats_next=whats_next,
        safe_to_switch=safe_to_switch,
        slices_closed_in_thread=slices_closed_in_thread,
        triage_counts=triage_counts,
        notes=notes,
        ship_report=ship_report,
    )
    append_closeout_record(repo, record)
    try:
        from scripts.ppe_tracking_hub import record_context_closeout_event

        record_context_closeout_event(repo, record)
    except Exception:
        pass
    if promote:
        promote_whats_next(repo, record)
    try:
        from scripts.active_product_direction import sync_product_direction

        record["product_direction_sync"] = sync_product_direction(repo)
    except Exception as exc:
        record["product_direction_sync"] = {"error": str(exc)}
    return record


def load_whats_next_markdown(repo: Path) -> str | None:
    path = repo / WHATS_NEXT_MD_REL
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8").strip()
    return text or None


def add_build_backlog_item(
    repo: Path,
    *,
    chapter_id: str,
    reason: str,
    priority: str = "medium",
    focus_tier: str = "P2",
) -> Path:
    repo = repo.resolve()
    path = backlog_path(repo)
    if not path.is_file():
        raise SystemExit(f"Missing {path.relative_to(repo)}")
    backlog = load_chapter_backlog(repo)
    items = list(backlog.get("items") or [])
    cid = chapter_id.strip()
    for item in items:
        if isinstance(item, dict) and str(item.get("chapterId") or "") == cid:
            raise SystemExit(f"chapterId already exists: {cid}")
    items.append(
        {
            "chapterId": cid,
            "status": "blocked",
            "priority": priority.strip().lower(),
            "focusPlaybookTier": focus_tier.strip().upper(),
            "reason": reason.strip(),
            "canonRef": "docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md",
            "added": datetime.now(timezone.utc).date().isoformat(),
            "source": "context_window_closeout",
        }
    )
    backlog["items"] = items
    path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    return path


def add_triggered_idea_item(
    repo: Path,
    *,
    title: str,
    summary: str,
    priority: str = "low",
    idea_id: str = "",
    trigger_chapters: list[str] | None = None,
    trigger_keywords: list[str] | None = None,
    not_for: list[str] | None = None,
) -> Path:
    from scripts.ppe_triggered_ideas import add_item

    return add_item(
        repo,
        title=title,
        summary=summary,
        idea_id=idea_id,
        priority=priority,
        trigger_chapters=trigger_chapters,
        trigger_keywords=trigger_keywords,
        not_for=not_for,
    )


def add_human_backlog_item(
    repo: Path,
    *,
    title: str,
    summary: str,
    priority: str = "medium",
    category: str = "governance",
    policy_question: str = "",
) -> Path:
    repo = repo.resolve()
    path = repo / HUMAN_BACKLOG_REL
    backlog = load_human_backlog(repo)
    items = list(backlog.get("items") or [])
    iid = _slug_id(title)
    for item in items:
        if isinstance(item, dict) and str(item.get("id") or "") == iid:
            raise SystemExit(f"id already exists: {iid}")
    row: dict[str, Any] = {
        "id": iid,
        "title": title.strip(),
        "status": "open",
        "priority": priority.strip().lower(),
        "category": category.strip().lower(),
        "summary": summary.strip(),
        "added": datetime.now(timezone.utc).date().isoformat(),
        "source": "context_window_closeout",
    }
    if policy_question.strip():
        row["policyQuestion"] = policy_question.strip()
    items.append(row)
    backlog["items"] = items
    path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    md_path = repo / "docs/SOP/HUMAN_STEWARD_BACKLOG.md"
    md_path.write_text(render_human_md(repo), encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Context window closeout gather + backlog helpers")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--render", action="store_true", help="Write JSON snapshot + draft markdown")
    ap.add_argument(
        "--record",
        action="store_true",
        help="Render + auto-ship + append context_windows.jsonl + promote WHATS_NEXT",
    )
    ap.add_argument(
        "--ship",
        action="store_true",
        help="Run operational sweep (gate → commit → push → PR) before render/record",
    )
    ap.add_argument(
        "--no-ship",
        action="store_true",
        help="Skip auto-ship even with --record (triage-only closeout)",
    )
    ap.add_argument("--ship-dry-run", action="store_true", help="Preview auto-ship without git mutations")
    ap.add_argument("--json", action="store_true", help="Print snapshot JSON to stdout")
    ap.add_argument(
        "--thread-role",
        default="operator",
        help="operator | charter | ide_build | recovery | explore (legacy: steward→charter, exploratory→charter)",
    )
    ap.add_argument("--whats-next", default="", help="One-line next action (default: infer from operator verdict)")
    ap.add_argument(
        "--safe-to-switch",
        choices=("yes", "no"),
        default="yes",
        help="AGENT CONTINUITY safe to switch agents",
    )
    ap.add_argument("--slices-closed", type=int, default=0, help="Slices closed in this Cursor thread")
    ap.add_argument("--notes", default="", help="Optional closeout notes")
    ap.add_argument("--no-promote", action="store_true", help="Skip writing WHATS_NEXT artifacts")
    sub = ap.add_subparsers(dest="cmd")

    ab = sub.add_parser("add-build", help="Append blocked row to PHASE_CHAPTER_BACKLOG.json")
    ab.add_argument("--chapter-id", required=True)
    ab.add_argument("--reason", required=True)
    ab.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    ab.add_argument("--focus-tier", default="P2")

    ah = sub.add_parser("add-human", help="Append open row to HUMAN_STEWARD_BACKLOG.json")
    ah.add_argument("--title", required=True)
    ah.add_argument("--summary", required=True)
    ah.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    ah.add_argument("--category", default="governance")
    ah.add_argument("--policy-question", default="")

    at = sub.add_parser("add-triggered", help="Park idea in TRIGGERED_IDEAS.json (revisit when chapter matches)")
    at.add_argument("--title", required=True)
    at.add_argument("--summary", required=True)
    at.add_argument("--id", default="")
    at.add_argument("--priority", default="low", choices=["high", "medium", "low"])
    at.add_argument("--trigger-chapter", action="append", default=[], dest="trigger_chapters")
    at.add_argument("--trigger-keyword", action="append", default=[], dest="trigger_keywords")
    at.add_argument("--not-for", action="append", default=[], dest="not_for")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.cmd == "add-build":
        path = add_build_backlog_item(
            repo,
            chapter_id=args.chapter_id,
            reason=args.reason,
            priority=args.priority,
            focus_tier=args.focus_tier,
        )
        print(f"ppe_context_window_closeout: appended build backlog -> {path.relative_to(repo)}")
        return 0
    if args.cmd == "add-human":
        path = add_human_backlog_item(
            repo,
            title=args.title,
            summary=args.summary,
            priority=args.priority,
            category=args.category,
            policy_question=args.policy_question,
        )
        print(f"ppe_context_window_closeout: appended human backlog -> {path.relative_to(repo)}")
        return 0
    if args.cmd == "add-triggered":
        path = add_triggered_idea_item(
            repo,
            title=args.title,
            summary=args.summary,
            priority=args.priority,
            idea_id=args.id,
            trigger_chapters=args.trigger_chapters,
            trigger_keywords=args.trigger_keywords,
            not_for=args.not_for,
        )
        print(f"ppe_context_window_closeout: appended triggered idea -> {path.relative_to(repo)}")
        return 0

    snapshot = collect_snapshot(repo)
    ship_report: dict[str, Any] | None = None
    do_ship = args.ship or (args.record and not args.no_ship)
    if do_ship:
        from scripts.ppe_context_closeout_ship import run_operational_sweep

        ship_report = run_operational_sweep(repo, dry_run=args.ship_dry_run)
        if not args.ship_dry_run:
            snapshot = collect_snapshot(repo)
        if ship_report.get("ok"):
            print("ppe_context_window_closeout: auto-ship ok")
        elif ship_report.get("blocked"):
            print("ppe_context_window_closeout: auto-ship blocked — see draft report", file=sys.stderr)
        else:
            print("ppe_context_window_closeout: auto-ship incomplete", file=sys.stderr)

    if args.json:
        payload = dict(snapshot)
        if ship_report is not None:
            payload["ship_report"] = ship_report
        print(json.dumps(payload, indent=2))
        return 0 if not ship_report or ship_report.get("ok") else 1
    if args.render or args.record:
        json_path, md_path = write_artifacts(repo, snapshot, ship_report=ship_report)
        print(f"ppe_context_window_closeout: wrote {json_path.relative_to(repo)}")
        print(f"ppe_context_window_closeout: wrote {md_path.relative_to(repo)}")
        if args.record:
            safe = args.safe_to_switch == "yes" and not (ship_report and ship_report.get("blocked"))
            record = record_context_closeout(
                repo,
                snapshot,
                thread_role=args.thread_role,
                whats_next=args.whats_next,
                safe_to_switch=safe,
                slices_closed_in_thread=args.slices_closed,
                notes=args.notes,
                promote=not args.no_promote,
                ship_report=ship_report,
            )
            jsonl = _metrics_dir(repo) / CONTEXT_WINDOWS_FILE
            print(f"ppe_context_window_closeout: appended {jsonl.relative_to(repo)}")
            if not args.no_promote:
                print(f"ppe_context_window_closeout: promoted {WHATS_NEXT_MD_REL}")
            print(f"ppe_context_window_closeout: whats_next={record.get('whats_next')}")
        exit_code = 0 if not ship_report or ship_report.get("ok") else 1
        return exit_code

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
