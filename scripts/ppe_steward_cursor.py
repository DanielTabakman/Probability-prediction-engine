"""Cursor SDK steward — charter next roadmap chapter when the queue is idle (local runtime)."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from scripts.ppe_manifest import load_manifest
from scripts.ppe_roadmap import (
    ROADMAP_REL,
    _first_pending_with_valid_plan,
    _plan_valid,
    load_roadmap,
    norm_plan,
    roadmap_enabled,
    roadmap_path,
    save_roadmap,
    sync_roadmap_to_queue,
)
from scripts.ppe_queue import load_queue, upsert_queue_item

PROPOSAL_REL = "artifacts/steward/last_proposal.json"
BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
FRONTIER_REL = "docs/SOP/MVP1_FRONTIER.md"
INTEGRATED_REL = "docs/SOP/PPE_INTEGRATED_STATUS.md"

ALLOWED_WRITE_PREFIXES = (
    "docs/SOP/PHASE_PLANS/",
    "docs/SOP/PHASE_SELECTION_ROADMAP.json",
    "docs/SOP/SPRINT_",
    "docs/SOP/MVP1_",
    "docs/SOP/DEPLOY_",
    "docs/SOP/POST_",
    "artifacts/steward/",
)

FORBIDDEN_WRITE_PREFIXES = (
    "src/",
    "docs/VISION/",
    "docs/SOP/PPE_MASTER",
    ".env",
)


def steward_enabled(repo_root: Path | None = None) -> bool:
    if repo_root is not None:
        from scripts.ppe_operator_config import steward_charter_enabled

        return steward_charter_enabled(repo_root.resolve())
    env = os.environ.get("PPE_AUTO_STEWARD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    return False


def _manifest_idle(repo: Path) -> tuple[bool, str]:
    try:
        manifest = load_manifest(repo)
    except Exception as e:
        return False, str(e)
    status = str(manifest.get("status") or "").strip().upper()
    if status not in ("COMPLETE", ""):
        return False, f"manifest status {status}"
    if str(manifest.get("phasePlanPath") or "").strip():
        return False, "manifest has phasePlanPath"
    return True, ""


def needs_steward_charter(repo_root: Path) -> tuple[bool, str]:
    """True when auto-run should try to charter the next chapter."""
    repo = repo_root.resolve()
    if not steward_enabled(repo):
        return False, "PPE_AUTO_STEWARD disabled"
    if not roadmap_enabled(repo):
        return False, "roadmap disabled or missing"
    ok, reason = _manifest_idle(repo)
    if not ok:
        return False, reason

    queue = load_queue(repo)
    if any(
        isinstance(it, dict) and str(it.get("status") or "").upper() == "READY"
        for it in (queue.get("items") or [])
    ):
        return False, "queue has READY"

    if not roadmap_path(repo).is_file():
        return True, "no roadmap file yet"

    roadmap = load_roadmap(repo)
    if _first_pending_with_valid_plan(repo, roadmap) is not None:
        return False, "roadmap has valid pending"

    pending_any = any(
        isinstance(it, dict) and str(it.get("status") or "").strip().lower() == "pending"
        for it in (roadmap.get("items") or [])
    )
    if pending_any:
        return False, "roadmap has pending without valid plan (fix manually or delete row)"

    return True, "idle; no chartered next chapter"


def _read_tail(path: Path, max_chars: int = 6000) -> str:
    if not path.is_file():
        return f"(missing {path})"
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 80] + "\n\n...(truncated)...\n"


def build_steward_prompt(repo_root: Path) -> str:
    repo = repo_root.resolve()
    proposal_path = (repo / PROPOSAL_REL).replace("\\", "/")
    parts = [
        "You are the PPE **steward** (SELECTION only). Do not implement product code.",
        "",
        "Read these repo files for context:",
        f"- {BRIEF_REL}",
        f"- {FRONTIER_REL}",
        f"- {INTEGRATED_REL}",
        f"- {ROADMAP_REL}",
        "",
        "Task: propose the **next evidence-only relay chapter** suitable for deterministic",
        "worker mode (Control + Smoke + Closeout slices). Do not open new product surfaces.",
        "",
        "You MAY create or update files only under:",
        "- docs/SOP/PHASE_PLANS/*.json",
        "- docs/SOP/SPRINT_*.md",
        "- docs/SOP/*_SELECTION.md",
        "- docs/SOP/MVP1_*_EVIDENCE_STATUS.md",
        f"- {proposal_path}",
        "",
        "You MUST NOT edit src/, docs/VISION/, or PPE_MASTER canon.",
        "",
        "Write a single JSON file at:",
        f"  {proposal_path}",
        "",
        "Schema (strict):",
        json.dumps(
            {
                "chapterId": "snake_case_id",
                "chapterTitle": "human title",
                "planPath": "docs/SOP/PHASE_PLANS/<name>_relay.json",
                "sprintSpecPath": "docs/SOP/SPRINT_<NAME>.md",
                "selectionRecord": "docs/SOP/<NAME>_SELECTION.md",
                "evidenceDoc": "docs/SOP/MVP1_<NAME>_EVIDENCE_STATUS.md",
                "workerMode": "deterministic",
                "reason": "one line why this chapter is next",
                "scaffold": True,
            },
            indent=2,
        ),
        "",
        "If scaffold is true, also create the phase plan (3 slices: Control, Smoke, Closeout),",
        "sprint spec, selection doc, and evidence status stub matching existing relay chapters.",
        "Use baselineBranch main and EVIDENCE-PLANE slices.",
        "",
        "Context excerpts:",
        "--- AGENT_CONTINUITY_BRIEF ---",
        _read_tail(repo / BRIEF_REL, 4000),
        "--- MVP1_FRONTIER (head) ---",
        _read_tail(repo / FRONTIER_REL, 3500),
    ]
    return "\n".join(parts)


def _extract_json_blob(text: str) -> dict[str, Any] | None:
    text = text.strip()
    if not text:
        return None
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def load_proposal(repo_root: Path) -> tuple[dict[str, Any] | None, str]:
    p = repo_root.resolve() / PROPOSAL_REL
    if not p.is_file():
        return None, "proposal file missing"
    try:
        data = json.loads(p.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}"
    if not isinstance(data, dict):
        return None, "proposal must be an object"
    return data, ""


def validate_proposal(repo_root: Path, proposal: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("chapterId", "planPath", "reason"):
        if not str(proposal.get(key) or "").strip():
            errors.append(f"missing {key}")
    plan = norm_plan(str(proposal.get("planPath") or ""))
    if plan and not plan.startswith("docs/SOP/PHASE_PLANS/"):
        errors.append("planPath must be under docs/SOP/PHASE_PLANS/")
    wm = str(proposal.get("workerMode") or "deterministic").strip().lower()
    if wm not in ("deterministic", "acp", "local-agent"):
        errors.append(f"invalid workerMode: {wm}")
    if wm != "deterministic" and not os.environ.get("PPE_STEWARD_ALLOW_PRODUCT"):
        errors.append("only workerMode deterministic allowed without PPE_STEWARD_ALLOW_PRODUCT=1")
    return errors


def _slug_from_chapter(chapter_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", chapter_id).strip("_").upper()


def scaffold_chapter_files(repo_root: Path, proposal: dict[str, Any]) -> list[str]:
    """Create minimal relay chapter artifacts from proposal. Returns paths written."""
    repo = repo_root.resolve()
    chapter_id = str(proposal.get("chapterId") or "chapter").strip()
    slug = _slug_from_chapter(chapter_id)
    plan_path = norm_plan(str(proposal.get("planPath") or f"docs/SOP/PHASE_PLANS/{chapter_id}_relay.json"))
    sprint = norm_plan(
        str(proposal.get("sprintSpecPath") or f"docs/SOP/SPRINT_{slug}.md")
    )
    selection = norm_plan(
        str(proposal.get("selectionRecord") or f"docs/SOP/{slug}_SELECTION.md")
    )
    evidence = norm_plan(
        str(proposal.get("evidenceDoc") or f"docs/SOP/MVP1_{slug}_EVIDENCE_STATUS.md")
    )
    title = str(proposal.get("chapterTitle") or chapter_id).strip()
    tag = "".join(part[:1].upper() + part[1:] for part in chapter_id.split("_") if part)[:24] or "Chapter"

    plan = {
        "name": title,
        "baselineBranch": "main",
        "sprintSpecPath": sprint,
        "selectionRecord": selection,
        "slices": [
            {
                "sliceId": f"MVP1-{tag}-Control-Slice001",
                "sprintSpecPath": sprint,
                "buildBranch": f"build/auto/MVP1-{tag}-Control-Slice001-{chapter_id[:16]}",
                "declaredPlane": "EVIDENCE-PLANE",
                "susMinutes": 15,
                "hardMinutes": 30,
                "maxAttempts": 1,
            },
            {
                "sliceId": f"MVP1-{tag}-Smoke-Slice002",
                "sprintSpecPath": sprint,
                "buildBranch": f"build/auto/MVP1-{tag}-Smoke-Slice002-{chapter_id[:16]}",
                "declaredPlane": "EVIDENCE-PLANE",
                "susMinutes": 30,
                "hardMinutes": 90,
                "maxAttempts": 2,
            },
            {
                "sliceId": f"MVP1-{tag}-Closeout-Slice003",
                "sprintSpecPath": sprint,
                "buildBranch": f"build/auto/MVP1-{tag}-Closeout-Slice003-{chapter_id[:16]}",
                "declaredPlane": "EVIDENCE-PLANE",
                "susMinutes": 15,
                "hardMinutes": 30,
                "maxAttempts": 1,
                "closeout": {
                    "chapterId": chapter_id,
                    "chapterTitle": title,
                    "chapterStatus": "COMPLETE",
                    "closedDate": "TBD",
                    "evidenceDoc": evidence,
                    "sprintSpec": sprint,
                    "selectionOutcomeDoc": selection,
                    "nextSelectionDoc": FRONTIER_REL,
                    "carryDocs": [evidence],
                },
            },
        ],
    }

    written: list[str] = []
    plan_fs = repo / plan_path
    plan_fs.parent.mkdir(parents=True, exist_ok=True)
    if not plan_fs.is_file():
        plan_fs.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        written.append(plan_path)

    sprint_fs = repo / sprint
    if not sprint_fs.is_file():
        sprint_fs.write_text(
            f"# {title} — relay sprint spec\n\n"
            f"**SELECTION:** [`{Path(selection).name}`]({Path(selection).name})\n\n"
            "## Sprint intent\n\n"
            f"Evidence-only chapter `{chapter_id}` (deterministic worker).\n\n"
            "## Acceptance\n\n"
            "1. `python -m pytest -q` green.\n"
            "2. Control closeout marks chapter **COMPLETE**.\n",
            encoding="utf-8",
        )
        written.append(sprint)

    sel_fs = repo / selection
    if not sel_fs.is_file():
        sel_fs.write_text(
            f"# SELECTION — {title}\n\n"
            f"Chartered by Cursor steward (`ppe_steward_cursor.py`).\n\n"
            f"**Phase plan:** [`{Path(plan_path).name}`]({plan_path})\n",
            encoding="utf-8",
        )
        written.append(selection)

    ev_fs = repo / evidence
    if not ev_fs.is_file():
        ev_fs.write_text(
            f"# {title} — evidence status\n\n"
            f"**Chapter:** `{chapter_id}`  \n"
            "**Status:** **IN_PROGRESS**\n",
            encoding="utf-8",
        )
        written.append(evidence)

    return written


def apply_proposal(repo_root: Path, proposal: dict[str, Any], *, apply: bool) -> dict[str, Any]:
    repo = repo_root.resolve()
    errors = validate_proposal(repo, proposal)
    if errors:
        return {"applied": False, "errors": errors}

    plan_path = norm_plan(str(proposal["planPath"]))
    if str(proposal.get("scaffold", True)).lower() not in ("0", "false", "no"):
        if apply:
            scaffold_chapter_files(repo, proposal)

    ok_plan, plan_err = _plan_valid(repo, plan_path)
    if not ok_plan:
        return {"applied": False, "errors": [plan_err]}

    if not apply:
        return {
            "applied": True,
            "dry_run": True,
            "planPath": plan_path,
            "reason": "would append roadmap pending",
        }

    if roadmap_path(repo).is_file():
        roadmap = load_roadmap(repo)
    else:
        roadmap = {
            "version": 1,
            "notes": "Ordered chapters; steward + auto-SELECTION.",
            "items": [],
        }

    items = roadmap.setdefault("items", [])
    if not isinstance(items, list):
        items = []
        roadmap["items"] = items

    if any(norm_plan(str(it.get("planPath") or "")) == plan_path for it in items if isinstance(it, dict)):
        return {"applied": False, "errors": [f"roadmap already has {plan_path}"]}

    row = {
        "planPath": plan_path,
        "status": "pending",
        "reason": str(proposal.get("reason") or "steward charter"),
        "workerMode": str(proposal.get("workerMode") or "deterministic"),
    }
    sel_prep = str(proposal.get("selectionRecord") or "").strip()
    if sel_prep:
        row["selectionPrep"] = sel_prep
    items.append(row)
    save_roadmap(repo, roadmap)
    sync_roadmap_to_queue(repo, apply=True)
    upsert_queue_item(
        repo,
        plan_path=plan_path,
        status="PLANNED",
        reason=row["reason"],
        workerMode=row.get("workerMode"),
        selectionPrep=sel_prep,
    )
    return {"applied": True, "planPath": plan_path, "roadmap_status": "pending"}


def run_steward_agent_local(repo_root: Path, *, prompt: str) -> dict[str, Any]:
    """Invoke Cursor SDK local agent (requires cursor-sdk + CURSOR_API_KEY)."""
    api_key = (
        os.environ.get("CURSOR_API_KEY")
        or os.environ.get("CURSOR_AUTH_TOKEN")
        or ""
    ).strip()
    if not api_key:
        return {"ran": False, "reason": "missing CURSOR_API_KEY"}

    try:
        from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
    except ImportError:
        return {
            "ran": False,
            "reason": "cursor-sdk not installed (pip install cursor-sdk)",
        }

    model = os.environ.get("PPE_STEWARD_MODEL", "composer-2.5").strip()
    repo = repo_root.resolve()
    proposal_file = repo / PROPOSAL_REL
    proposal_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = Agent.prompt(
            prompt,
            AgentOptions(
                api_key=api_key,
                model=model,
                local=LocalAgentOptions(cwd=str(repo)),
            ),
        )
    except Exception as e:
        return {"ran": False, "reason": f"Agent.prompt failed: {e}"}

    status = getattr(result, "status", None)
    body = getattr(result, "result", None) or ""
    out: dict[str, Any] = {
        "ran": True,
        "status": status,
        "result_head": str(body)[:500],
    }
    if status == "error":
        out["reason"] = "steward agent run status=error"
        return out

    proposal, perr = load_proposal(repo)
    if proposal is None:
        parsed = _extract_json_blob(str(body))
        if parsed:
            proposal_file.write_text(json.dumps(parsed, indent=2) + "\n", encoding="utf-8")
            proposal, perr = load_proposal(repo)
        if proposal is None:
            out["reason"] = f"no proposal file: {perr}"
            return out

    out["proposal"] = proposal
    return out


def maybe_run_steward_cursor(repo_root: Path, *, apply: bool) -> dict[str, Any]:
    """Hook entry: charter next chapter when idle. Called from prepare_selection_idle."""
    repo = repo_root.resolve()
    need, reason = needs_steward_charter(repo)
    if not need:
        return {"skipped": True, "reason": reason}

    if not apply:
        return {
            "skipped": False,
            "would_run": True,
            "reason": reason,
            "prompt_preview": build_steward_prompt(repo)[:400] + "...",
        }

    prompt = build_steward_prompt(repo)
    agent_out = run_steward_agent_local(repo, prompt=prompt)
    if not agent_out.get("ran"):
        return {"skipped": False, "chartered": False, "agent": agent_out, "reason": agent_out.get("reason")}

    proposal = agent_out.get("proposal")
    if not isinstance(proposal, dict):
        proposal, perr = load_proposal(repo)
        if proposal is None:
            return {
                "skipped": False,
                "chartered": False,
                "agent": agent_out,
                "reason": perr,
            }

    apply_out = apply_proposal(repo, proposal, apply=True)
    return {
        "skipped": False,
        "chartered": bool(apply_out.get("applied")),
        "agent": {k: v for k, v in agent_out.items() if k != "proposal"},
        "apply": apply_out,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description="PPE Cursor SDK steward (local)")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--check", action="store_true", help="Print whether steward would run")
    ap.add_argument("--proposal", type=Path, default=None, help="Apply existing proposal JSON")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    if args.check:
        need, reason = needs_steward_charter(repo)
        print(json.dumps({"needs_steward": need, "reason": reason}, indent=2))
        return 0

    if args.proposal:
        data = json.loads(args.proposal.read_text(encoding="utf-8-sig"))
        out = apply_proposal(repo, data, apply=args.apply)
        print(json.dumps(out, indent=2))
        return 0 if out.get("applied") else 1

    out = maybe_run_steward_cursor(repo, apply=args.apply)
    print(json.dumps(out, indent=2, default=str))
    if out.get("skipped"):
        return 0
    return 0 if out.get("chartered") else 1


if __name__ == "__main__":
    raise SystemExit(main())
