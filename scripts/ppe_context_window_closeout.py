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
SWEEP_REL = "artifacts/control_plane/CONTEXT_WINDOW_CLOSEOUT_SWEEP.json"
WHATS_NEXT_JSON_REL = "artifacts/control_plane/WHATS_NEXT.json"
WHATS_NEXT_MD_REL = "artifacts/control_plane/WHATS_NEXT.md"
SOP_CLOSEOUT = "docs/SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md"

NEVER_COMMIT_PREFIXES: tuple[str, ...] = (
    "artifacts/",
    "_worktrees/",
    ".pytest_cache/",
    "__pycache__/",
)
NEVER_COMMIT_EXACT: frozenset[str] = frozenset({".env", ".env.local"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _slug_id(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    return s.strip("_")[:64] or "item"


def _norm_path(path: str) -> str:
    p = path.replace("\\", "/").strip()
    if p.startswith("./"):
        return p[2:]
    return p


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=False,
    )


def _current_branch(repo: Path) -> str:
    proc = _git(repo, "branch", "--show-current")
    return (proc.stdout or "").strip() if proc.returncode == 0 else ""


def is_never_commit_path(path: str) -> bool:
    p = _norm_path(path)
    if p in NEVER_COMMIT_EXACT:
        return True
    if p.endswith((".sqlite", ".sqlite3", ".db")):
        return True
    low = p.lower()
    if "credentials" in low or low.endswith(".pem"):
        return True
    return any(p.startswith(prefix) for prefix in NEVER_COMMIT_PREFIXES)


def committable_dirty_paths(preflight: dict[str, Any]) -> list[str]:
    paths = preflight.get("modified_untracked_paths") or []
    if not isinstance(paths, list):
        return []
    out: list[str] = []
    for raw in paths:
        if not isinstance(raw, str):
            continue
        p = _norm_path(raw)
        if is_never_commit_path(p):
            continue
        try:
            from scripts.repo_layer_paths import is_preflight_dirty_exempt

            if is_preflight_dirty_exempt(p):
                continue
        except ImportError:
            pass
        out.append(p)
    return sorted(out)


def effective_working_tree_clean(preflight: dict[str, Any]) -> bool:
    return not committable_dirty_paths(preflight)


def _classify_path_plane(path: str) -> str:
    p = _norm_path(path)
    if p.startswith("docs/SOP/"):
        return "CONTROL-PLANE"
    if p.startswith("src/"):
        return "PRODUCT-PLANE"
    if p.startswith("tests/") or p.startswith("scripts/"):
        return "EVIDENCE-PLANE"
    return "SUSPICIOUS / UNKNOWN"


def infer_commit_plane(paths: list[str]) -> str:
    planes = {_classify_path_plane(p) for p in paths}
    core = sorted(p for p in planes if p != "SUSPICIOUS / UNKNOWN")
    if len(core) == 1:
        return core[0]
    if core:
        return "+".join(core)
    return "UNKNOWN"


def build_sweep_commit_message(
    *,
    chapter_id: str,
    plane: str,
    paths: list[str],
    override: str = "",
) -> str:
    if override.strip():
        return override.strip()
    chapter = chapter_id.strip() or "context-closeout"
    plane_bit = plane.replace(" ", "").lower()
    if len(paths) == 1:
        hint = Path(paths[0]).name
    elif paths:
        hint = f"{len(paths)} files"
    else:
        hint = "sweep"
    return f"{chapter}: context-closeout sweep {hint} ({plane_bit})"


def _run_pushable_gate(repo: Path, *, pre_push: bool = False) -> int:
    cmd = [sys.executable, str(repo / "scripts" / "run_pushable_gate.py"), "--repo-root", str(repo)]
    if pre_push:
        cmd.append("--pre-push")
    return subprocess.run(cmd, cwd=repo, check=False).returncode


def _ahead_count(repo: Path) -> int:
    proc = _git(repo, "rev-list", "--count", "@{upstream}..HEAD")
    if proc.returncode == 0:
        try:
            return int((proc.stdout or "0").strip() or "0")
        except ValueError:
            pass
    branch = _current_branch(repo)
    if branch:
        proc = _git(repo, "rev-list", "--count", f"origin/{branch}..HEAD")
        if proc.returncode == 0:
            try:
                return int((proc.stdout or "0").strip() or "0")
            except ValueError:
                pass
    return 0


def _ensure_pr(repo: Path, *, branch: str, title: str, body: str) -> str | None:
    try:
        from scripts.ppe_operator_git_sync import _open_pr
    except ImportError:
        return None
    return _open_pr(repo, head=branch, title=title, body=body)


def run_operational_sweep(
    repo: Path,
    *,
    dry_run: bool = False,
    open_pr: bool = True,
    commit_message: str = "",
    chapter_id: str = "",
) -> dict[str, Any]:
    """Gate+commit ship-now dirty paths, push feature branches, fail closed on remainder."""
    repo = repo.resolve()
    result: dict[str, Any] = {
        "dry_run": dry_run,
        "ok": True,
        "safe_to_switch": True,
        "committed": False,
        "commit_message": None,
        "pushed": False,
        "pr_url": None,
        "park_reason": None,
        "park_paths": [],
        "blockers": [],
        "actions": [],
    }

    if not dry_run:
        fetch = _git(repo, "fetch", "origin")
        if fetch.returncode != 0:
            result["actions"].append(
                {
                    "action": "fetch",
                    "ok": False,
                    "error": (fetch.stderr or fetch.stdout or "git fetch failed").strip(),
                }
            )

    preflight = _run_json_script(repo, "scripts/frontier_preflight.py") or {}
    branch = str(preflight.get("branch") or _current_branch(repo) or "")
    paths = committable_dirty_paths(preflight)

    if branch == "main" and effective_working_tree_clean(preflight):
        pull_action: dict[str, Any] = {"action": "pull_main"}
        if dry_run:
            pull_action["dry_run"] = True
            pull_action["skipped"] = False
        else:
            from scripts.ppe_operator_git_sync import pull_main

            pull_action.update(pull_main(repo))
        result["actions"].append(pull_action)
        if not pull_action.get("ok", True) and not pull_action.get("skipped"):
            result["blockers"].append(
                f"pull failed: {pull_action.get('error') or pull_action.get('reason') or 'unknown'}"
            )

    if paths:
        if branch in ("main", "master"):
            result["park_paths"] = paths
            result["park_reason"] = "on main; execution work must use a feature branch"
            result["blockers"].append(result["park_reason"])
        elif not preflight.get("build_allowed"):
            blocker = str(preflight.get("blocker") or "preflight blocked auto-commit")
            result["park_paths"] = paths
            result["park_reason"] = blocker
            result["blockers"].append(f"park: {blocker}")
        else:
            plane = infer_commit_plane(paths)
            msg = build_sweep_commit_message(
                chapter_id=chapter_id,
                plane=plane,
                paths=paths,
                override=commit_message,
            )
            commit_action: dict[str, Any] = {
                "action": "commit",
                "paths": paths,
                "message": msg,
            }
            if dry_run:
                commit_action["dry_run"] = True
                result["actions"].append(commit_action)
            else:
                for p in paths:
                    add = _git(repo, "add", "--", p)
                    if add.returncode != 0:
                        commit_action["ok"] = False
                        commit_action["error"] = (add.stderr or add.stdout or "git add failed").strip()
                        result["actions"].append(commit_action)
                        result["blockers"].append(commit_action["error"])
                        break
                else:
                    gate_rc = _run_pushable_gate(repo, pre_push=False)
                    if gate_rc != 0:
                        commit_action["ok"] = False
                        commit_action["error"] = "pushable gate failed before commit"
                        result["blockers"].append(commit_action["error"])
                    else:
                        commit = _git(repo, "commit", "-m", msg)
                        commit_action["ok"] = commit.returncode == 0
                        if commit.returncode == 0:
                            result["committed"] = True
                            result["commit_message"] = msg
                        else:
                            commit_action["error"] = (commit.stderr or commit.stdout or "git commit failed").strip()
                            result["blockers"].append(commit_action["error"])
                    result["actions"].append(commit_action)

    if branch and branch not in ("main", "master", "HEAD"):
        ahead = _ahead_count(repo)
        if ahead > 0:
            push_action: dict[str, Any] = {"action": "push", "branch": branch, "ahead": ahead}
            if dry_run:
                push_action["dry_run"] = True
                result["actions"].append(push_action)
            else:
                gate_rc = _run_pushable_gate(repo, pre_push=True)
                if gate_rc != 0:
                    push_action["ok"] = False
                    push_action["error"] = "pre-push gate failed"
                    result["blockers"].append(push_action["error"])
                else:
                    push = _git(repo, "push", "-u", "origin", "HEAD")
                    push_action["ok"] = push.returncode == 0
                    if push.returncode == 0:
                        result["pushed"] = True
                        if open_pr:
                            pr_url = _ensure_pr(
                                repo,
                                branch=branch,
                                title=f"context-closeout: {branch}",
                                body="Auto-published by context window closeout sweep.",
                            )
                            if pr_url:
                                result["pr_url"] = pr_url
                                push_action["pr_url"] = pr_url
                    else:
                        push_action["error"] = (push.stderr or push.stdout or "git push failed").strip()
                        result["blockers"].append(push_action["error"])
                result["actions"].append(push_action)
    elif _ahead_count(repo) > 0 and branch in ("main", "master"):
        result["blockers"].append("unpushed commits on main — open PR manually (main is PR-only)")

    post = _run_json_script(repo, "scripts/frontier_preflight.py") or preflight
    dirty_remain = committable_dirty_paths(post)
    ahead_remain = _ahead_count(repo)
    if dirty_remain:
        result["safe_to_switch"] = False
        result["park_paths"] = dirty_remain
        if not result["park_reason"]:
            result["park_reason"] = "dirty working tree after sweep"
        result["blockers"].append(f"dirty: {len(dirty_remain)} committable path(s) remain")
    if ahead_remain > 0:
        result["safe_to_switch"] = False
        result["blockers"].append(f"unpushed: {ahead_remain} commit(s) ahead of upstream")
    blocker_text = str(post.get("blocker") or preflight.get("blocker") or "")
    if "unmerged" in blocker_text.lower() or "conflict" in blocker_text.lower():
        result["safe_to_switch"] = False
        result["blockers"].append("unmerged / conflicted paths present")

    result["ok"] = not result["blockers"]
    return result


def write_sweep_artifact(repo: Path, sweep: dict[str, Any]) -> Path:
    repo = repo.resolve()
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = repo / SWEEP_REL
    path.write_text(json.dumps(sweep, indent=2) + "\n", encoding="utf-8")
    return path


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


def collect_snapshot(repo: Path, *, sweep: dict[str, Any] | None = None) -> dict[str, Any]:
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
    payload: dict[str, Any] = {
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
    if sweep is not None:
        payload["sweep"] = sweep
    return payload


def _checklist_line(done: bool, label: str) -> str:
    return f"- [{'x' if done else ' '}] {label}"


def render_draft_markdown(repo: Path, snapshot: dict[str, Any]) -> str:
    pf = snapshot.get("preflight") if isinstance(snapshot.get("preflight"), dict) else {}
    sweep = snapshot.get("sweep") if isinstance(snapshot.get("sweep"), dict) else {}
    branch = str(pf.get("branch") or "?")
    wt = str(pf.get("working_tree") or "?")
    upstream = str(pf.get("upstream") or "?")
    stash = pf.get("stash_entries")
    by_plane = pf.get("files_by_plane") if isinstance(pf.get("files_by_plane"), dict) else {}
    manifest = snapshot.get("manifest") if isinstance(snapshot.get("manifest"), dict) else {}
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    prs = snapshot.get("open_prs") if isinstance(snapshot.get("open_prs"), list) else []
    ms = snapshot.get("manifest_summary") if isinstance(snapshot.get("manifest_summary"), dict) else {}

    tree_clean = effective_working_tree_clean(pf) if pf else wt == "clean"
    if sweep:
        tree_clean = tree_clean and not sweep.get("park_paths")
    unpushed_done = bool(sweep.get("pushed")) if sweep else False
    ahead_remain = _ahead_count(repo) if sweep else None
    if sweep and ahead_remain == 0:
        unpushed_done = True

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
    lines.append(_checklist_line(tree_clean, "Working tree clean or explicitly PARKED"))
    lines.append(
        _checklist_line(
            unpushed_done or (ahead_remain == 0 if ahead_remain is not None else False),
            "Unpushed commits pushed (feature branches)",
        )
    )
    lines.append(_checklist_line(False, "`main` pulled / ff-only current"))
    lines.append(_checklist_line(len(prs) == 0, f"Open PRs reviewed ({len(prs)} listed below)"))
    lines.append(_checklist_line(bool(sweep), "Operator / relay threads reconciled"))
    lines.append("")

    if sweep:
        lines.extend(
            [
                "### Auto sweep result",
                "",
                f"- **safe_to_switch:** {sweep.get('safe_to_switch')}",
                f"- **committed:** {sweep.get('committed')}",
                f"- **pushed:** {sweep.get('pushed')}",
            ]
        )
        if sweep.get("commit_message"):
            lines.append(f"- **commit:** `{sweep.get('commit_message')}`")
        if sweep.get("pr_url"):
            lines.append(f"- **pr:** {sweep.get('pr_url')}")
        if sweep.get("park_reason"):
            lines.append(f"- **park:** {sweep.get('park_reason')}")
        if sweep.get("blockers"):
            lines.append("- **blockers:**")
            for b in sweep.get("blockers") or []:
                lines.append(f"  - {b}")
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
            "| Bucket | Item | Action / destination |",
            "|--------|------|----------------------|",
            "| ship_now | <!-- AGENT_FILL --> | |",
            "| operator_next | <!-- AGENT_FILL --> | |",
            "| build_backlog | <!-- AGENT_FILL --> | `PHASE_CHAPTER_BACKLOG.json` |",
            "| human_backlog | <!-- AGENT_FILL --> | `HUMAN_STEWARD_BACKLOG.json` |",
            "| park | <!-- AGENT_FILL --> | branch/stash name |",
            "| drop | <!-- AGENT_FILL --> | reason |",
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


def write_artifacts(repo: Path, snapshot: dict[str, Any]) -> tuple[Path, Path]:
    repo = repo.resolve()
    out_dir = repo / "artifacts" / "control_plane"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = repo / SNAPSHOT_REL
    md_path = repo / DRAFT_REL
    json_path.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_draft_markdown(repo, snapshot), encoding="utf-8")
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


def infer_whats_next(snapshot: dict[str, Any]) -> str:
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    cmds = op.get("commands") or []
    if cmds:
        return f"Operator: `{cmds[0]}`"
    verdict = str(op.get("verdict") or "").strip()
    if verdict:
        return f"Check operator verdict `{verdict}` and `docs/SOP/AGENT_CONTINUITY_BRIEF.md`."
    return "Read `docs/SOP/AGENT_CONTINUITY_BRIEF.md` and ask what's next."


def build_closeout_record(
    snapshot: dict[str, Any],
    *,
    thread_role: str = "steward",
    whats_next: str = "",
    safe_to_switch: bool = True,
    slices_closed_in_thread: int = 0,
    triage_counts: dict[str, int] | None = None,
    notes: str = "",
) -> dict[str, Any]:
    pf = snapshot.get("preflight") if isinstance(snapshot.get("preflight"), dict) else {}
    op = snapshot.get("operator") if isinstance(snapshot.get("operator"), dict) else {}
    closed_at = str(snapshot.get("generated_at_utc") or _utc_now())
    next_line = whats_next.strip() or infer_whats_next(snapshot)
    return {
        "event": "context_window_closeout",
        "closeout_id": str(uuid.uuid4()),
        "closed_at": closed_at,
        "thread_role": thread_role.strip().lower() or "steward",
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
    closed = str(record.get("closed_at") or "?")
    role = str(record.get("thread_role") or "steward")
    chapter = str(record.get("chapter_id") or "(none)")
    line = str(record.get("whats_next") or infer_whats_next({}))
    safe = "yes" if record.get("safe_to_switch_agents") else "no"
    return "\n".join(
        [
            "# What's next",
            "",
            f"**Last context closeout:** {closed} · **thread:** {role} · **chapter:** `{chapter}` · **safe to switch:** {safe}",
            "",
            line,
            "",
            "_New Cursor chat: ask **what's next?** — agent reads this file + `AGENT_CONTINUITY_BRIEF.md`._",
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
    thread_role: str = "steward",
    whats_next: str = "",
    safe_to_switch: bool = True,
    slices_closed_in_thread: int = 0,
    triage_counts: dict[str, int] | None = None,
    notes: str = "",
    promote: bool = True,
) -> dict[str, Any]:
    record = build_closeout_record(
        snapshot,
        thread_role=thread_role,
        whats_next=whats_next,
        safe_to_switch=safe_to_switch,
        slices_closed_in_thread=slices_closed_in_thread,
        triage_counts=triage_counts,
        notes=notes,
    )
    append_closeout_record(repo, record)
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
        help="Render + append context_windows.jsonl + promote WHATS_NEXT (use at thread closeout)",
    )
    ap.add_argument("--json", action="store_true", help="Print snapshot JSON to stdout")
    ap.add_argument("--thread-role", default="steward", help="steward | ide_build | recovery | exploratory")
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
    ap.add_argument(
        "--sweep",
        action="store_true",
        help="Operational sweep: gate+commit ship-now, push feature branch, then --record",
    )
    ap.add_argument(
        "--sweep-dry-run",
        action="store_true",
        help="Report sweep actions without git commit/push",
    )
    ap.add_argument("--sweep-commit-message", default="", help="Override auto sweep commit message")
    ap.add_argument("--sweep-no-pr", action="store_true", help="Do not open PR after push")
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

    if args.sweep:
        args.record = True
        args.render = True
    if args.sweep_dry_run:
        args.render = True

    sweep_result: dict[str, Any] | None = None
    if args.sweep or args.sweep_dry_run:
        pre = collect_snapshot(repo)
        chapter_id = _chapter_from_snapshot(pre)
        sweep_result = run_operational_sweep(
            repo,
            dry_run=args.sweep_dry_run,
            open_pr=not args.sweep_no_pr,
            commit_message=args.sweep_commit_message,
            chapter_id=chapter_id,
        )
        if not args.sweep_dry_run:
            write_sweep_artifact(repo, sweep_result)
        print(f"ppe_context_window_closeout: sweep safe_to_switch={sweep_result.get('safe_to_switch')}")
        if sweep_result.get("blockers"):
            for blocker in sweep_result["blockers"]:
                print(f"ppe_context_window_closeout: sweep blocker: {blocker}")

    snapshot = collect_snapshot(repo, sweep=sweep_result)
    if args.json:
        print(json.dumps(snapshot, indent=2))
        return 0
    if args.render or args.record:
        json_path, md_path = write_artifacts(repo, snapshot)
        print(f"ppe_context_window_closeout: wrote {json_path.relative_to(repo)}")
        print(f"ppe_context_window_closeout: wrote {md_path.relative_to(repo)}")
        if sweep_result and not args.sweep_dry_run:
            print(f"ppe_context_window_closeout: wrote {SWEEP_REL}")
        if args.record:
            safe = args.safe_to_switch == "yes"
            if sweep_result is not None:
                safe = bool(sweep_result.get("safe_to_switch"))
            record = record_context_closeout(
                repo,
                snapshot,
                thread_role=args.thread_role,
                whats_next=args.whats_next,
                safe_to_switch=safe,
                slices_closed_in_thread=args.slices_closed,
                notes=args.notes,
                promote=not args.no_promote,
            )
            jsonl = _metrics_dir(repo) / CONTEXT_WINDOWS_FILE
            print(f"ppe_context_window_closeout: appended {jsonl.relative_to(repo)}")
            if not args.no_promote:
                print(f"ppe_context_window_closeout: promoted {WHATS_NEXT_MD_REL}")
            print(f"ppe_context_window_closeout: whats_next={record.get('whats_next')}")
        if sweep_result and not sweep_result.get("ok") and args.sweep and not args.sweep_dry_run:
            return 1
        return 0

    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
