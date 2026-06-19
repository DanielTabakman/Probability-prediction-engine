"""Unified control plane — reconcile steering + route human work through the queue.

Canon: docs/SOP/CONTROL_PLANE_OPERATOR_V1.md

One read path after reconcile:
  artifacts/orchestrator/CONTROL_PLANE_STATUS.json

Human intake:
  ppe_request.cmd --chapter-id <id> --reason "..." [--apply]
  ppe_request.cmd --human --title "..." --summary "..." [--apply]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.ppe_manifest import MANIFEST_REL, load_manifest, validate_manifest
from scripts.ppe_propagate_queue import (
    backlog_path,
    load_backlog,
    maybe_propagate_queue,
    reconcile_closed_chapters,
)
from scripts.ppe_queue import QUEUE_REL, load_queue

CONTROL_PLANE_STATUS_REL = "artifacts/orchestrator/CONTROL_PLANE_STATUS.json"
CONTINUITY_BRIEF_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"

ACTION_NOW = "NOW"
ACTION_WAIT = "WAIT"
ACTION_QUEUE = "QUEUE"
ACTION_HUMAN = "HUMAN"
ACTION_ALREADY_QUEUED = "ALREADY_QUEUED"
ACTION_REJECT = "REJECT"

STOP_VERDICTS = frozenset({"IDE_BUILD", "RUN_LOCAL", "FIX_PLAN", "STALE_STATE", "ERROR"})


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm_plan(plan_path: str) -> str:
    return plan_path.replace("\\", "/").strip()


def _slug_id(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.strip().lower())
    return slug.strip("_") or "item"


def _queue_items(queue: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in (queue.get("items") or []) if isinstance(i, dict)]


def _backlog_items(backlog: dict[str, Any]) -> list[dict[str, Any]]:
    return [i for i in (backlog.get("items") or []) if isinstance(i, dict)]


def _first_ready_plan(queue: dict[str, Any]) -> str | None:
    for item in _queue_items(queue):
        if str(item.get("status") or "").upper() == "READY":
            plan = _norm_plan(str(item.get("planPath") or ""))
            if plan:
                return plan
    return None


def _find_backlog_row(
    backlog: dict[str, Any],
    *,
    chapter_id: str | None = None,
    plan_path: str | None = None,
) -> dict[str, Any] | None:
    cid = (chapter_id or "").strip()
    plan = _norm_plan(plan_path or "")
    for item in _backlog_items(backlog):
        item_cid = str(item.get("chapterId") or "").strip()
        item_plan = _norm_plan(str(item.get("planPath") or ""))
        if cid and item_cid == cid:
            return item
        if plan and item_plan == plan:
            return item
    return None


def _find_queue_row(queue: dict[str, Any], plan_path: str) -> dict[str, Any] | None:
    plan = _norm_plan(plan_path)
    for item in _queue_items(queue):
        if _norm_plan(str(item.get("planPath") or "")) == plan:
            return item
    return None


def _chapter_id_from_plan(plan_path: str) -> str:
    name = Path(plan_path).name
    if name.endswith("_relay.json"):
        return name[: -len("_relay.json")]
    return _slug_id(Path(plan_path).stem)


def resolve_chapter_ref(
    repo: Path,
    *,
    chapter_id: str | None = None,
    plan_path: str | None = None,
) -> dict[str, Any]:
    """Resolve chapter_id <-> plan_path from backlog or queue."""
    repo = repo.resolve()
    backlog = load_backlog(repo) if backlog_path(repo).is_file() else {"items": []}
    queue = load_queue(repo) if (repo / QUEUE_REL).is_file() else {"items": []}

    cid = (chapter_id or "").strip()
    plan = _norm_plan(plan_path or "")

    row = _find_backlog_row(backlog, chapter_id=cid or None, plan_path=plan or None)
    if row:
        cid = cid or str(row.get("chapterId") or "").strip()
        plan = plan or _norm_plan(str(row.get("planPath") or ""))

    if plan and not cid:
        cid = _chapter_id_from_plan(plan)
    if cid and not plan:
        row = _find_backlog_row(backlog, chapter_id=cid)
        if row:
            plan = _norm_plan(str(row.get("planPath") or ""))
        else:
            for item in _queue_items(queue):
                item_plan = _norm_plan(str(item.get("planPath") or ""))
                if item_plan and _chapter_id_from_plan(item_plan) == cid:
                    plan = item_plan
                    break

    queue_row = _find_queue_row(queue, plan) if plan else None
    backlog_row = _find_backlog_row(backlog, chapter_id=cid or None, plan_path=plan or None)

    return {
        "chapter_id": cid,
        "plan_path": plan,
        "backlog_row": backlog_row,
        "queue_row": queue_row,
        "has_plan": bool(plan),
    }


def _parse_evidence_status(repo: Path, plan_path: str) -> str | None:
    """Best-effort evidence doc status: COMPLETE | CHARTERED | IN PROGRESS | None."""
    backlog = load_backlog(repo) if backlog_path(repo).is_file() else {"items": []}
    row = _find_backlog_row(backlog, plan_path=plan_path)
    selection = str((row or {}).get("selectionRecord") or "").strip()
    candidates: list[Path] = []
    if selection:
        candidates.append(repo / selection.replace("\\", "/"))
    stem = _chapter_id_from_plan(plan_path).upper().replace("_", "_")
    for path in (repo / "docs" / "SOP").glob("*_EVIDENCE_STATUS.md"):
        if stem.replace("_", "") in path.name.upper().replace("_", ""):
            candidates.append(path)
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen or not path.is_file():
            continue
        seen.add(key)
        text = path.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\*\*Status:\*\*\s*\*\*([^*]+)\*\*", text, re.IGNORECASE)
        if m:
            return m.group(1).strip().upper()
    return None


def _continuity_brief_chapter_status(repo: Path) -> str | None:
    path = repo / CONTINUITY_BRIEF_REL
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"\|\s*Status\s*\|\s*([^|]+)\|", text, re.IGNORECASE)
    if m:
        return m.group(1).strip().upper()
    return None


def collect_alignment_findings(repo: Path) -> list[dict[str, Any]]:
    """Cross-check committed steering files; return structured findings."""
    repo = repo.resolve()
    findings: list[dict[str, Any]] = []

    try:
        manifest = load_manifest(repo)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        findings.append(
            {
                "severity": "error",
                "code": "manifest_invalid",
                "message": str(exc),
            }
        )
        return findings

    for err in validate_manifest(repo, manifest):
        findings.append(
            {
                "severity": "error",
                "code": "manifest_validation",
                "message": err,
            }
        )

    manifest_plan = _norm_plan(str(manifest.get("phasePlanPath") or ""))
    manifest_status = str(manifest.get("status") or "").strip().upper()

    try:
        queue = load_queue(repo)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        findings.append({"severity": "error", "code": "queue_invalid", "message": str(exc)})
        queue = {"items": []}

    ready_plan = _first_ready_plan(queue)
    if manifest_status in ("READY", "RUNNING") and manifest_plan and ready_plan and manifest_plan != ready_plan:
        findings.append(
            {
                "severity": "error",
                "code": "manifest_queue_mismatch",
                "message": f"manifest binds {manifest_plan!r} but first READY queue row is {ready_plan!r}",
            }
        )

    if manifest_plan:
        qrow = _find_queue_row(queue, manifest_plan)
        qst = str((qrow or {}).get("status") or "").upper()
        if manifest_status in ("READY", "RUNNING") and qrow and qst not in ("READY", "RUNNING", "PLANNED"):
            findings.append(
                {
                    "severity": "warn",
                    "code": "manifest_queue_status",
                    "message": f"manifest {manifest_status} but queue row is {qst}",
                }
            )

    backlog = load_backlog(repo) if backlog_path(repo).is_file() else {"items": []}
    chartered = [
        i
        for i in _backlog_items(backlog)
        if str(i.get("status") or "").lower() in ("chartered", "queued")
    ]
    if len(chartered) > 1:
        ids = [str(i.get("chapterId") or "?") for i in chartered]
        findings.append(
            {
                "severity": "warn",
                "code": "backlog_multiple_active",
                "message": f"multiple chartered/queued backlog rows: {', '.join(ids)}",
            }
        )

    if manifest_plan:
        brow = _find_backlog_row(backlog, plan_path=manifest_plan)
        if brow:
            bst = str(brow.get("status") or "").lower()
            if manifest_status in ("READY", "RUNNING") and bst == "done":
                findings.append(
                    {
                        "severity": "error",
                        "code": "backlog_done_manifest_active",
                        "message": f"backlog marks {brow.get('chapterId')} done but manifest still {manifest_status}",
                    }
                )

    brief_status = _continuity_brief_chapter_status(repo)
    if brief_status == "COMPLETE" and manifest_status in ("READY", "RUNNING") and manifest_plan:
        findings.append(
            {
                "severity": "warn",
                "code": "continuity_brief_stale",
                "message": "AGENT_CONTINUITY_BRIEF says COMPLETE but manifest still active — run reconcile after re-queue",
            }
        )

    if manifest_plan:
        evidence = _parse_evidence_status(repo, manifest_plan)
        if evidence and evidence not in ("COMPLETE",) and manifest_status == "COMPLETE":
            findings.append(
                {
                    "severity": "warn",
                    "code": "evidence_manifest_mismatch",
                    "message": f"evidence status {evidence} but manifest COMPLETE",
                }
            )
        if evidence == "COMPLETE" and manifest_status in ("READY", "RUNNING"):
            findings.append(
                {
                    "severity": "warn",
                    "code": "evidence_reopened",
                    "message": "evidence COMPLETE but manifest re-opened — intentional re-queue?",
                }
            )

    return findings


def _commands_for_verdict(verdict: str, *, plan_path: str | None = None) -> list[str]:
    if verdict == "IDE_BUILD":
        return ["DESKTOP_BUILD.cmd", "ppe_go.cmd"]
    if verdict == "RUN_LOCAL":
        return ["DESKTOP_CONTINUE.cmd", "run_ppe_local.cmd"]
    if verdict == "RUN_AUTO":
        return ["run_ppe.cmd", "run_ppe_auto_local_loop.cmd"]
    if verdict in STOP_VERDICTS:
        return ["ppe_autobuilder.cmd diagnose"]
    if plan_path:
        return ["run_ppe.cmd"]
    return ["ppe_autobuilder.cmd status --write"]


def _upsert_build_backlog(
    repo: Path,
    *,
    chapter_id: str,
    reason: str,
    plan_path: str = "",
    priority: str = "medium",
    focus_tier: str = "P2",
    urgent: bool = False,
    urgent_reason: str = "",
) -> dict[str, Any]:
    path = backlog_path(repo)
    if not path.is_file():
        raise FileNotFoundError(f"Missing {path.relative_to(repo)}")
    backlog = load_backlog(repo)
    items = list(backlog.get("items") or [])
    existing = _find_backlog_row(backlog, chapter_id=chapter_id)
    if existing:
        st = str(existing.get("status") or "").lower()
        if st in ("chartered", "queued", "blocked"):
            existing["reason"] = reason.strip()
            if plan_path:
                existing["planPath"] = _norm_plan(plan_path)
            existing["source"] = "ppe_request"
            if urgent:
                existing["urgent"] = True
                if urgent_reason.strip():
                    existing["urgentReason"] = urgent_reason.strip()
            path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
            return {"updated": True, "chapter_id": chapter_id, "status": st}
        return {"updated": False, "chapter_id": chapter_id, "status": st}

    row: dict[str, Any] = {
        "chapterId": chapter_id,
        "status": "blocked",
        "priority": priority.strip().lower(),
        "focusPlaybookTier": focus_tier.strip().upper(),
        "reason": reason.strip(),
        "canonRef": "docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md",
        "added": datetime.now(timezone.utc).date().isoformat(),
        "source": "ppe_request",
    }
    if plan_path:
        row["planPath"] = _norm_plan(plan_path)
    if urgent:
        row["urgent"] = True
        if urgent_reason.strip():
            row["urgentReason"] = urgent_reason.strip()
    items.append(row)
    backlog["items"] = items
    path.write_text(json.dumps(backlog, indent=2) + "\n", encoding="utf-8")
    return {"updated": True, "chapter_id": chapter_id, "status": "blocked"}


def route_build_request(
    repo: Path,
    *,
    chapter_id: str | None = None,
    plan_path: str | None = None,
    reason: str,
    priority: str = "medium",
    focus_tier: str = "P2",
    urgent: bool = False,
    urgent_reason: str = "",
    apply: bool = False,
) -> dict[str, Any]:
    """Decide NOW / WAIT / QUEUE for chapter work; optionally append backlog row."""
    repo = repo.resolve()
    ref = resolve_chapter_ref(repo, chapter_id=chapter_id, plan_path=plan_path)
    cid = str(ref.get("chapter_id") or "").strip()
    plan = str(ref.get("plan_path") or "").strip()
    if not cid:
        return {
            "action": ACTION_REJECT,
            "reason": "could not resolve chapter_id — pass --chapter-id or --plan-path",
            "apply": apply,
        }

    if not reason.strip():
        return {"action": ACTION_REJECT, "reason": "reason is required", "apply": apply}

    backlog_row = ref.get("backlog_row")
    plan = str(ref.get("plan_path") or "").strip()

    from scripts.ppe_autobuilder import collect_autobuilder_status
    from scripts.ppe_focus_gate import evaluate_focus_gate

    runtime = collect_autobuilder_status(repo)
    verdict = str(runtime.get("verdict") or "")
    manifest = load_manifest(repo)
    manifest_plan = _norm_plan(str(manifest.get("phasePlanPath") or ""))
    manifest_status = str(manifest.get("status") or "").strip().upper()
    active_chapter = str(runtime.get("operator", {}).get("chapter_name") or "")

    request_plan = _norm_plan(plan) if plan else ""

    if isinstance(backlog_row, dict):
        bst = str(backlog_row.get("status") or "").lower()
        if bst in ("chartered", "queued"):
            item_plan = _norm_plan(str(backlog_row.get("planPath") or ""))
            if item_plan and manifest_plan and item_plan != manifest_plan:
                return {
                    "action": ACTION_ALREADY_QUEUED,
                    "reason": f"chapter {cid!r} already {bst} in chapter backlog",
                    "chapter_id": cid,
                    "plan_path": plan,
                    "backlog_status": bst,
                    "apply": apply,
                }

    gate_reason: str | None = None
    if plan:
        gate = evaluate_focus_gate(repo, plan)
        if not gate.allowed and not urgent:
            gate_reason = gate.reason

    request_plan = _norm_plan(plan) if plan else ""

    # Matches active pipeline chapter → proceed (subject to verdict).
    if request_plan and manifest_plan and request_plan == manifest_plan:
        if verdict in STOP_VERDICTS:
            cmds = _commands_for_verdict(verdict, plan_path=request_plan)
            return {
                "action": ACTION_NOW,
                "reason": f"active chapter {cid} — verdict {verdict}",
                "chapter_id": cid,
                "plan_path": request_plan,
                "verdict": verdict,
                "commands": cmds,
                "apply": apply,
            }
        return {
            "action": ACTION_NOW,
            "reason": f"active chapter {cid} — relay may proceed",
            "chapter_id": cid,
            "plan_path": request_plan,
            "verdict": verdict,
            "commands": _commands_for_verdict(verdict or "RUN_AUTO", plan_path=request_plan),
            "apply": apply,
        }

    # Pipeline busy on a different chapter.
    if manifest_status == "RUNNING" and manifest_plan and request_plan != manifest_plan:
        result = {
            "action": ACTION_WAIT,
            "reason": f"pipeline RUNNING on {manifest_plan!r} — finish current chapter first",
            "chapter_id": cid,
            "plan_path": request_plan,
            "active_plan": manifest_plan,
            "active_chapter": active_chapter,
            "apply": apply,
        }
        if apply:
            result["backlog"] = _upsert_build_backlog(
                repo,
                chapter_id=cid,
                reason=reason,
                plan_path=request_plan,
                priority=priority,
                focus_tier=focus_tier,
                urgent=urgent,
                urgent_reason=urgent_reason,
            )
            result["action"] = ACTION_QUEUE
            result["reason"] = f"queued behind active chapter — {reason.strip()}"
        return result

    if manifest_status in ("READY", "RUNNING") and manifest_plan and request_plan and request_plan != manifest_plan:
        result = {
            "action": ACTION_QUEUE,
            "reason": f"pipeline committed to {manifest_plan!r} — queued {cid!r}",
            "chapter_id": cid,
            "plan_path": request_plan,
            "active_plan": manifest_plan,
            "apply": apply,
        }
        if gate_reason:
            result["focus_gate"] = gate_reason
        if apply:
            result["backlog"] = _upsert_build_backlog(
                repo,
                chapter_id=cid,
                reason=reason,
                plan_path=request_plan,
                priority=priority,
                focus_tier=focus_tier,
                urgent=urgent,
                urgent_reason=urgent_reason,
            )
        return result

    if verdict in STOP_VERDICTS and manifest_plan:
        result = {
            "action": ACTION_WAIT,
            "reason": f"operator verdict {verdict} — resolve before starting {cid!r}",
            "chapter_id": cid,
            "plan_path": request_plan,
            "verdict": verdict,
            "commands": _commands_for_verdict(verdict),
            "apply": apply,
        }
        if apply and request_plan:
            result["backlog"] = _upsert_build_backlog(
                repo,
                chapter_id=cid,
                reason=reason,
                plan_path=request_plan,
                priority=priority,
                focus_tier=focus_tier,
                urgent=urgent,
                urgent_reason=urgent_reason,
            )
            result["action"] = ACTION_QUEUE
        return result

    # Queue position: not READY yet in PHASE_QUEUE.
    if request_plan:
        queue = load_queue(repo)
        qrow = _find_queue_row(queue, request_plan)
        qst = str((qrow or {}).get("status") or "").upper()
        ready_plan = _first_ready_plan(queue)
        if qrow and qst == "PLANNED" and ready_plan and ready_plan != request_plan:
            result = {
                "action": ACTION_QUEUE,
                "reason": f"chapter PLANNED — waits behind READY {ready_plan!r}",
                "chapter_id": cid,
                "plan_path": request_plan,
                "queue_status": qst,
                "ahead_plan": ready_plan,
                "apply": apply,
            }
            if gate_reason:
                result["focus_gate"] = gate_reason
            if apply:
                result["backlog"] = _upsert_build_backlog(
                    repo,
                    chapter_id=cid,
                    reason=reason,
                    plan_path=request_plan,
                    priority=priority,
                    focus_tier=focus_tier,
                    urgent=urgent,
                    urgent_reason=urgent_reason,
                )
            return result

    # Idle or promotable — queue unless urgent NOW bootstrap applies.
    if gate_reason and not urgent:
        result = {
            "action": ACTION_QUEUE,
            "reason": f"focus gate: {gate_reason}",
            "chapter_id": cid,
            "plan_path": request_plan,
            "focus_gate": gate_reason,
            "apply": apply,
        }
        if apply:
            result["backlog"] = _upsert_build_backlog(
                repo,
                chapter_id=cid,
                reason=reason,
                plan_path=request_plan,
                priority=priority,
                focus_tier=focus_tier,
                urgent=urgent,
                urgent_reason=urgent_reason,
            )
        return result

    result = {
        "action": ACTION_QUEUE,
        "reason": "pipeline idle or promotable — added to chapter backlog (blocked until relay ready)",
        "chapter_id": cid,
        "plan_path": request_plan,
        "apply": apply,
    }
    if apply:
        result["backlog"] = _upsert_build_backlog(
            repo,
            chapter_id=cid,
            reason=reason,
            plan_path=request_plan,
            priority=priority,
            focus_tier=focus_tier,
            urgent=urgent,
            urgent_reason=urgent_reason,
        )
    return result


def route_human_request(
    repo: Path,
    *,
    title: str,
    summary: str,
    priority: str = "medium",
    category: str = "governance",
    policy_question: str = "",
    apply: bool = False,
) -> dict[str, Any]:
    """Policy/architecture topics — never auto-implement; human steward backlog."""
    from scripts.ppe_context_window_closeout import add_human_backlog_item

    if not title.strip() or not summary.strip():
        return {"action": ACTION_REJECT, "reason": "title and summary required", "apply": apply}
    if not apply:
        return {
            "action": ACTION_HUMAN,
            "reason": "policy topic — will append to HUMAN_STEWARD_BACKLOG on --apply",
            "title": title.strip(),
            "apply": apply,
        }
    path = add_human_backlog_item(
        repo,
        title=title,
        summary=summary,
        priority=priority,
        category=category,
        policy_question=policy_question,
    )
    return {
        "action": ACTION_HUMAN,
        "reason": "appended to human steward backlog",
        "title": title.strip(),
        "path": str(path.relative_to(repo)),
        "apply": apply,
    }


def build_control_plane_status(
    repo: Path,
    *,
    autobuilder: dict[str, Any],
    findings: list[dict[str, Any]],
    reconcile_steps: dict[str, Any],
) -> dict[str, Any]:
    manifest = load_manifest(repo)
    queue = load_queue(repo)
    backlog = load_backlog(repo) if backlog_path(repo).is_file() else {"items": []}
    manifest_plan = _norm_plan(str(manifest.get("phasePlanPath") or ""))

    errors = sum(1 for f in findings if f.get("severity") == "error")
    warnings = sum(1 for f in findings if f.get("severity") == "warn")

    return {
        "version": 1,
        "as_of": _utc_now(),
        "source_of_truth": {
            "committed_chapter": MANIFEST_REL,
            "queue": QUEUE_REL,
            "backlog": str(backlog_path(repo).relative_to(repo)),
            "runtime_verdict": "artifacts/orchestrator/AUTOBUILDER_STATUS.json",
            "human_read": CONTROL_PLANE_STATUS_REL,
        },
        "alignment": {
            "passed": errors == 0,
            "errors": errors,
            "warnings": warnings,
            "findings": findings,
        },
        "committed": {
            "manifest_status": str(manifest.get("status") or ""),
            "phase_plan_path": manifest_plan,
            "first_ready_queue_plan": _first_ready_plan(queue),
            "chartered_backlog": [
                str(i.get("chapterId") or "")
                for i in _backlog_items(backlog)
                if str(i.get("status") or "").lower() in ("chartered", "queued")
            ],
        },
        "reconcile": reconcile_steps,
        "verdict": autobuilder.get("verdict"),
        "phase": autobuilder.get("phase"),
        "recommended_action": autobuilder.get("recommended_action"),
        "operator": autobuilder.get("operator"),
        "commands": autobuilder.get("commands"),
        "runtime": autobuilder,
    }


def write_control_plane_status(repo: Path, status: dict[str, Any]) -> Path:
    path = repo / CONTROL_PLANE_STATUS_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    return path


def reconcile_control_plane(repo: Path, *, apply: bool = True) -> dict[str, Any]:
    """Sync backlog/queue, regenerate runtime status, write CONTROL_PLANE_STATUS.json."""
    repo = repo.resolve()
    steps: dict[str, Any] = {}

    if apply:
        steps["reconcile_closed"] = reconcile_closed_chapters(repo, apply=True)
        steps["propagate"] = maybe_propagate_queue(repo, apply=True)

    findings = collect_alignment_findings(repo)

    from scripts.ppe_autobuilder import collect_autobuilder_status, write_status_artifact
    from scripts.ppe_operator_status import collect_operator_status, write_status_report

    autobuilder = collect_autobuilder_status(repo)
    write_status_artifact(repo, autobuilder)
    operator = collect_operator_status(repo)
    write_status_report(repo, operator)

    snapshot = build_control_plane_status(
        repo,
        autobuilder=autobuilder,
        findings=findings,
        reconcile_steps=steps,
    )
    path = write_control_plane_status(repo, snapshot)
    snapshot["artifact"] = str(path.relative_to(repo))
    return snapshot


def format_route_brief(route: dict[str, Any]) -> str:
    action = route.get("action", "?")
    reason = route.get("reason", "")
    parts = [f"ACTION={action}", reason]
    if route.get("commands"):
        parts.append("commands=" + ", ".join(route["commands"]))
    if route.get("path"):
        parts.append(f"path={route['path']}")
    return " — ".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PPE control plane — reconcile + human request routing")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)

    p_rec = sub.add_parser("reconcile", help="Sync steering + write CONTROL_PLANE_STATUS.json")
    p_rec.add_argument("--dry-run", action="store_true", help="Check alignment only; do not sync or write")
    p_rec.add_argument("--json", action="store_true")

    p_req = sub.add_parser("request", help="Route human chapter work through the queue")
    p_req.add_argument("--chapter-id", default="", help="Snake_case chapter id")
    p_req.add_argument("--plan-path", default="", help="Relay plan path under docs/SOP/PHASE_PLANS/")
    p_req.add_argument("--reason", default="", help="Why this work matters")
    p_req.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    p_req.add_argument("--focus-tier", default="P2")
    p_req.add_argument("--urgent", action="store_true", help="Bypass focus gate when promoting")
    p_req.add_argument("--urgent-reason", default="")
    p_req.add_argument("--apply", action="store_true", help="Append to backlog when QUEUE/WAIT")
    p_req.add_argument("--json", action="store_true")

    p_hum = sub.add_parser("human", help="Route policy topic to human steward backlog")
    p_hum.add_argument("--title", required=True)
    p_hum.add_argument("--summary", required=True)
    p_hum.add_argument("--priority", default="medium", choices=["high", "medium", "low"])
    p_hum.add_argument("--category", default="governance")
    p_hum.add_argument("--policy-question", default="")
    p_hum.add_argument("--apply", action="store_true")
    p_hum.add_argument("--json", action="store_true")

    args = ap.parse_args(argv)
    repo = args.repo_root.resolve()

    if args.command == "reconcile":
        if args.dry_run:
            findings = collect_alignment_findings(repo)
            payload = {"alignment": {"findings": findings, "passed": not any(f.get("severity") == "error" for f in findings)}}
            if args.json:
                print(json.dumps(payload, indent=2))
            else:
                errs = sum(1 for f in findings if f.get("severity") == "error")
                warns = sum(1 for f in findings if f.get("severity") == "warn")
                print(f"ppe_control_plane: dry-run errors={errs} warnings={warns}")
                for f in findings[:8]:
                    print(f"  [{f.get('severity')}] {f.get('code')}: {f.get('message')}")
            return 1 if errs else 0
        snapshot = reconcile_control_plane(repo, apply=True)
        if args.json:
            print(json.dumps(snapshot, indent=2))
        else:
            align = snapshot.get("alignment") or {}
            print(
                f"ppe_control_plane: reconcile -> {snapshot.get('artifact')} "
                f"verdict={snapshot.get('verdict')} alignment_passed={align.get('passed')}"
            )
        return 0 if (snapshot.get("alignment") or {}).get("passed", True) else 1

    if args.command == "request":
        route = route_build_request(
            repo,
            chapter_id=args.chapter_id or None,
            plan_path=args.plan_path or None,
            reason=args.reason,
            priority=args.priority,
            focus_tier=args.focus_tier,
            urgent=args.urgent,
            urgent_reason=args.urgent_reason,
            apply=args.apply,
        )
        if args.json:
            print(json.dumps(route, indent=2))
        else:
            print(f"ppe_control_plane: {format_route_brief(route)}")
        return 0 if route.get("action") != ACTION_REJECT else 1

    if args.command == "human":
        route = route_human_request(
            repo,
            title=args.title,
            summary=args.summary,
            priority=args.priority,
            category=args.category,
            policy_question=args.policy_question,
            apply=args.apply,
        )
        if args.json:
            print(json.dumps(route, indent=2))
        else:
            print(f"ppe_control_plane: {format_route_brief(route)}")
        return 0 if route.get("action") != ACTION_REJECT else 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
