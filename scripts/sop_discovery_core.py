"""SOP / chapter doc discovery — shared index + resolve logic.

Canon: docs/SOP/AGENT_ROUTING_V1.md
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.ppe_control_plane import resolve_chapter_ref
from scripts.ppe_manifest import load_phase_plan
from scripts.ppe_queue import QUEUE_REL, load_queue

CHAPTER_DOC_INDEX_REL = "docs/SOP/CHAPTER_DOC_INDEX.json"
ROUTING_CANON_REL = "docs/SOP/AGENT_ROUTING_V1.md"

DO_NOT_LOAD: tuple[str, ...] = (
    "docs/SOP/CURRENT_FRONTIER.md",
    "docs/CURRENT_FRONTIER.md",
    "docs/Frontier_Steward_Handoff.md",
    "docs/SOP/MANAGER_LOOP.md",
    "docs/SOP/WORKER_LOOP.md",
    "docs/CONTROL_PLANE/PROMPTS/WORKER_LAUNCH_PROMPT.md",
)

# module_id → program doc (analytical modules)
MODULE_PROGRAM_DOCS: dict[str, str] = {
    "implied_distribution": "docs/SOP/MVP1_FRONTIER.md",
    "options_horizon": "docs/SOP/OPTIONS_HORIZON_PROGRAM_V1.md",
    "forward_consistency": "docs/SOP/FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md",
    "expression_planner": "docs/SOP/MVP1_FRONTIER.md",
    "cross_venue_event_gap": "docs/SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md",
    "exposure_menu": "docs/SOP/EXPOSURE_MENU_PROGRAM_V1.md",
    "workflow": "docs/SOP/TRADER_LEARNING_SPINE_PROGRAM_V1.md",
}

# topic phrase (substring match, lowercased) → routing bundle
TOPIC_ROUTES: list[dict[str, Any]] = [
    {
        "id": "asset_enable",
        "match": (
            "add asset",
            "enable asset",
            "hook up asset",
            "get sol down",
            "discover asset",
            "asset source",
        ),
        "sop": "docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md",
        "load_always": ["docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md"],
        "load_on_demand": ["docs/SOP/ASSET_ENABLEMENT_RUNBOOK_V1.md"],
        "cursor_rule": ".cursor/rules/asset-auto-discovery.mdc",
        "next_action": "run_discover_asset_data_source",
        "agent_steps": [
            "python scripts/discover_asset_data_source.py --asset <ID> --json",
            "Execute next_action from JSON; do not ask which exchange.",
        ],
    },
    {
        "id": "asset_batch",
        "match": (
            "asset batch",
            "tier-1 batch",
            "tier-2 batch",
            "finish tier-1",
            "batch wave",
        ),
        "sop": "docs/SOP/ASSET_BATCH_EXPANSION_POLICY_V1.md",
        "load_always": [
            "docs/SOP/ASSET_BATCH_EXPANSION_POLICY_V1.md",
            "docs/SOP/PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md",
        ],
        "load_on_demand": ["docs/SOP/PPE_MULTI_ASSET_META_INFRA_PROGRAM_V1.md"],
        "cursor_rule": ".cursor/rules/asset-auto-discovery.mdc",
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "trader_spine",
        "match": (
            "trader learning",
            "learning spine",
            "post-mortem",
            "review loop",
            "trader workflow",
        ),
        "sop": "docs/SOP/TRADER_LEARNING_SPINE_PROGRAM_V1.md",
        "load_always": ["docs/SOP/TRADER_LEARNING_SPINE_PROGRAM_V1.md"],
        "load_on_demand": ["docs/SOP/UX_EXECUTION_BACKLOG_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "ux_execution",
        "match": ("ux backlog", "ux execution", "ux charter", "ux design"),
        "sop": "docs/SOP/UX_EXECUTION_BACKLOG_V1.md",
        "load_always": [
            "docs/SOP/UX_EXECUTION_BACKLOG_V1.md",
            "docs/SOP/MSOS_UX_DESIGN_PHILOSOPHY_V1.md",
        ],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "options_horizon",
        "match": ("options horizon", "horizon chart", "horizon replay"),
        "sop": "docs/SOP/OPTIONS_HORIZON_PROGRAM_V1.md",
        "load_always": ["docs/SOP/OPTIONS_HORIZON_PROGRAM_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "exposure_menu",
        "match": ("exposure menu", "exposure path"),
        "sop": "docs/SOP/EXPOSURE_MENU_PROGRAM_V1.md",
        "load_always": ["docs/SOP/EXPOSURE_MENU_PROGRAM_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "forward_consistency",
        "match": ("forward consistency", "consistency radar"),
        "sop": "docs/SOP/FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md",
        "load_always": ["docs/SOP/FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "cross_venue",
        "match": ("cross venue", "cross-venue", "polymarket scan"),
        "sop": "docs/SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md",
        "load_always": ["docs/SOP/MVP1_CROSS_VENUE_QUANT_PROGRAM_V1.md"],
        "load_on_demand": ["docs/SOP/RESEARCH_PIPELINE_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "tradeable_universe",
        "match": ("tradeable universe", "asset catalog", "tier-1 manifest"),
        "sop": "docs/SOP/PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md",
        "load_always": ["docs/SOP/PPE_TRADEABLE_UNIVERSE_PROGRAM_V1.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "operator_relay",
        "match": ("what's next", "operator thread", "relay", "autobuilder", "run_ppe"),
        "sop": "docs/SOP/AGENT_ROUTING_V1.md",
        "load_always": [
            "artifacts/orchestrator/OPERATOR_STATUS.md",
            "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
        ],
        "load_on_demand": ["docs/SOP/AGENT_ROUTING_V1.md"],
        "next_action": "operator_thread_burst_or_single",
    },
    {
        "id": "commit_gate",
        "match": ("commit", "pushable gate", "pytest gate", "commit policy"),
        "sop": "docs/SOP/COMMIT_POLICY.md",
        "load_always": ["docs/SOP/COMMIT_POLICY.md"],
        "load_on_demand": ["docs/SOP/TESTING_TIERS_V1.md"],
        "next_action": "load_on_demand_only",
    },
    {
        "id": "deploy",
        "match": ("deploy", "vps", "cloudflare access", "production"),
        "sop": "docs/SOP/PRODUCTION_DEPLOY_PROTOCOL.md",
        "load_always": ["docs/SOP/PRODUCTION_DEPLOY_PROTOCOL.md"],
        "load_on_demand": ["docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md"],
        "next_action": "load_on_demand_only",
    },
    {
        "id": "research_pipeline",
        "match": ("research pipeline", "collector ops", "archive health"),
        "sop": "docs/SOP/RESEARCH_PIPELINE_V1.md",
        "load_always": ["docs/SOP/RESEARCH_PIPELINE_V1.md"],
        "load_on_demand": ["config/research_pipeline_registry.json"],
        "next_action": "charter_thread_load_program",
    },
]


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _norm(path: str) -> str:
    return path.replace("\\", "/").strip()


def _chapter_id_from_plan(plan_path: str) -> str:
    name = Path(plan_path).name
    if name.endswith("_relay.json"):
        return name[: -len("_relay.json")]
    stem = Path(plan_path).stem
    return re.sub(r"[^a-z0-9]+", "_", stem.strip().lower()).strip("_")


def _closeout_from_plan(plan: dict[str, Any]) -> dict[str, Any] | None:
    for sl in plan.get("slices") or []:
        if isinstance(sl, dict) and isinstance(sl.get("closeout"), dict):
            return sl["closeout"]
    return None


def _infer_evidence_doc(repo: Path, chapter_id: str) -> str | None:
    cid_norm = chapter_id.upper().replace("-", "_")
    sop_dir = repo / "docs" / "SOP"
    for path in sorted(sop_dir.glob("*_EVIDENCE_STATUS.md")):
        stem = path.stem.upper().replace("-", "_")
        if cid_norm.replace("_", "") in stem.replace("_", ""):
            return _norm(str(path.relative_to(repo)))
    return None


def _infer_selection_doc(repo: Path, chapter_id: str, plan: dict[str, Any]) -> str | None:
    sel = _norm(str(plan.get("selectionRecord") or ""))
    if sel and (repo / sel).is_file():
        return sel
    cid = chapter_id.upper()
    for path in sorted((repo / "docs" / "SOP").glob("POST_*_SELECTION*.md")):
        if cid.replace("_", "") in path.stem.upper().replace("_", ""):
            return _norm(str(path.relative_to(repo)))
    return None


def chapter_doc_bundle(repo: Path, *, chapter_id: str, plan_path: str) -> dict[str, Any]:
    """Build doc bundle for one relay chapter."""
    repo = repo.resolve()
    plan_rel = _norm(plan_path)
    plan = load_phase_plan(repo, plan_rel)
    closeout = _closeout_from_plan(plan) or {}

    sprint = _norm(
        str(closeout.get("sprintSpec") or plan.get("sprintSpecPath") or "")
    )
    selection = _norm(
        str(
            closeout.get("selectionOutcomeDoc")
            or plan.get("selectionRecord")
            or _infer_selection_doc(repo, chapter_id, plan)
            or ""
        )
    )
    evidence = _norm(
        str(closeout.get("evidenceDoc") or _infer_evidence_doc(repo, chapter_id) or "")
    )
    next_selection = _norm(str(closeout.get("nextSelectionDoc") or ""))
    carry = [
        _norm(str(p))
        for p in (closeout.get("carryDocs") or [])
        if str(p).strip()
    ]

    program_doc: str | None = None
    for mod_id, prog in MODULE_PROGRAM_DOCS.items():
        if mod_id.replace("_", "") in chapter_id.replace("_", ""):
            program_doc = prog
            break

    queue_status: str | None = None
    if (repo / QUEUE_REL).is_file():
        queue = load_queue(repo)
        for item in queue.get("items") or []:
            if not isinstance(item, dict):
                continue
            if _norm(str(item.get("planPath") or "")) == plan_rel:
                queue_status = str(item.get("status") or "").strip().upper()
                break

    load_always = [p for p in (program_doc, selection) if p]
    load_for_build = [p for p in (sprint, plan_rel) if p]
    load_on_demand = [p for p in (evidence, next_selection, *carry) if p]

    return {
        "chapter_id": chapter_id,
        "plan_path": plan_rel,
        "program_doc": program_doc,
        "selection": selection or None,
        "sprint": sprint or None,
        "evidence": evidence or None,
        "next_selection": next_selection or None,
        "carry_docs": carry,
        "queue_status": queue_status,
        "load_always": load_always,
        "load_for_build": load_for_build,
        "load_on_demand": load_on_demand,
        "do_not_load": list(DO_NOT_LOAD),
    }


def scan_chapter_plans(repo: Path) -> list[dict[str, Any]]:
    repo = repo.resolve()
    plans_dir = repo / "docs" / "SOP" / "PHASE_PLANS"
    if not plans_dir.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(plans_dir.glob("*_relay.json")):
        plan_rel = _norm(str(path.relative_to(repo)))
        chapter_id = _chapter_id_from_plan(plan_rel)
        try:
            rows.append(chapter_doc_bundle(repo, chapter_id=chapter_id, plan_path=plan_rel))
        except (OSError, json.JSONDecodeError, KeyError):
            continue
    return rows


def build_chapter_doc_index(repo: Path) -> dict[str, Any]:
    chapters = scan_chapter_plans(repo)
    by_id = {row["chapter_id"]: row for row in chapters if row.get("chapter_id")}
    return {
        "version": 1,
        "generated_at": _utc_now(),
        "canon": ROUTING_CANON_REL,
        "resolve_cmd": "python scripts/resolve_sop.py --chapter <id> --json",
        "chapter_count": len(chapters),
        "chapters": chapters,
        "by_chapter_id": by_id,
        "topic_route_ids": [r["id"] for r in TOPIC_ROUTES],
        "module_program_docs": MODULE_PROGRAM_DOCS,
    }


def write_chapter_doc_index(repo: Path) -> Path:
    repo = repo.resolve()
    data = build_chapter_doc_index(repo)
    out = repo / CHAPTER_DOC_INDEX_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _match_topic(topic: str) -> dict[str, Any] | None:
    needle = topic.strip().lower()
    if not needle:
        return None
    best: dict[str, Any] | None = None
    best_score = 0
    for route in TOPIC_ROUTES:
        for phrase in route.get("match") or ():
            p = str(phrase).lower()
            if p in needle or needle in p:
                score = len(p)
                if score > best_score:
                    best_score = score
                    best = route
    return best


def resolve_by_topic(topic: str) -> dict[str, Any]:
    route = _match_topic(topic)
    if route is None:
        return {
            "ok": False,
            "topic": topic,
            "next_action": "grep_or_ask_steward",
            "sop": ROUTING_CANON_REL,
            "load_always": [ROUTING_CANON_REL],
            "load_on_demand": ["docs/SOP/PPE_MODULE_REGISTRY_V1.md"],
            "do_not_load": list(DO_NOT_LOAD),
            "agent_steps": [
                "Retry with --chapter <chapter_id> if you know the relay chapter.",
                "Or load docs/SOP/PPE_MODULE_REGISTRY_V1.md and pick the program doc.",
            ],
        }
    return {
        "ok": True,
        "topic": topic,
        "topic_route_id": route["id"],
        "sop": route["sop"],
        "load_always": list(route.get("load_always") or []),
        "load_for_build": list(route.get("load_for_build") or []),
        "load_on_demand": list(route.get("load_on_demand") or []),
        "cursor_rule": route.get("cursor_rule"),
        "next_action": route.get("next_action"),
        "agent_steps": list(route.get("agent_steps") or []),
        "do_not_load": list(DO_NOT_LOAD),
    }


def resolve_by_module(repo: Path, module_id: str) -> dict[str, Any]:
    mid = module_id.strip().lower().replace("-", "_")
    program = MODULE_PROGRAM_DOCS.get(mid)
    if not program:
        return {
            "ok": False,
            "module_id": mid,
            "next_action": "unknown_module",
            "sop": ROUTING_CANON_REL,
            "load_always": ["docs/SOP/PPE_MODULE_REGISTRY_V1.md"],
            "do_not_load": list(DO_NOT_LOAD),
        }

    # Find active chapter for module if any
    chapter_match: dict[str, Any] | None = None
    for row in scan_chapter_plans(repo):
        cid = str(row.get("chapter_id") or "")
        if mid.replace("_", "") in cid.replace("_", ""):
            if row.get("queue_status") in (None, "READY", "RUNNING", "PLANNED"):
                chapter_match = row
                break

    out: dict[str, Any] = {
        "ok": True,
        "module_id": mid,
        "sop": program,
        "program_doc": program,
        "load_always": [program],
        "load_on_demand": ["docs/SOP/PPE_MODULE_REGISTRY_V1.md"],
        "next_action": "charter_thread_load_program",
        "do_not_load": list(DO_NOT_LOAD),
    }
    if chapter_match:
        out["chapter_id"] = chapter_match.get("chapter_id")
        out["load_for_build"] = chapter_match.get("load_for_build")
        out["load_on_demand"] = list(
            dict.fromkeys(
                (out.get("load_on_demand") or [])
                + (chapter_match.get("load_on_demand") or [])
            )
        )
    return out


def resolve_by_chapter(repo: Path, *, chapter_id: str | None = None, plan_path: str | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    ref = resolve_chapter_ref(repo, chapter_id=chapter_id, plan_path=plan_path)
    cid = str(ref.get("chapter_id") or "").strip()
    plan = str(ref.get("plan_path") or "").strip()
    if not cid or not plan:
        return {
            "ok": False,
            "chapter_id": cid or None,
            "plan_path": plan or None,
            "next_action": "chapter_not_found",
            "sop": ROUTING_CANON_REL,
            "load_always": [ROUTING_CANON_REL, "docs/SOP/CHAPTER_DOC_INDEX.json"],
            "do_not_load": list(DO_NOT_LOAD),
            "agent_steps": [
                "python scripts/generate_chapter_doc_index.py --write",
                "List chapters: jq '.chapters[].chapter_id' docs/SOP/CHAPTER_DOC_INDEX.json",
            ],
        }

    bundle = chapter_doc_bundle(repo, chapter_id=cid, plan_path=plan)
    queue_row = ref.get("queue_row") if isinstance(ref.get("queue_row"), dict) else {}
    return {
        "ok": True,
        "chapter_id": cid,
        "plan_path": plan,
        "queue_status": bundle.get("queue_status"),
        "selection_prep": _norm(str(queue_row.get("selectionPrep") or "")) or None,
        "sop": bundle.get("program_doc") or bundle.get("selection") or ROUTING_CANON_REL,
        "program_doc": bundle.get("program_doc"),
        "load_always": bundle.get("load_always") or [],
        "load_for_build": bundle.get("load_for_build") or [],
        "load_on_demand": bundle.get("load_on_demand") or [],
        "next_action": "ide_build_starter_if_blocked_else_relay",
        "do_not_load": list(DO_NOT_LOAD),
        "agent_steps": [
            f"Charter/SELECTION: load program + selection only.",
            f"IDE BUILD: @artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md only.",
            f"generate_ide_build_starter.cmd <sliceId> {plan}",
        ],
    }
