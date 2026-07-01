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
PROGRAM_DOC_INDEX_REL = "docs/SOP/PROGRAM_DOC_INDEX.json"
ARCHIVE_INDEX_REL = "docs/SOP/ARCHIVE_INDEX.md"
ROUTING_CANON_REL = "docs/SOP/AGENT_ROUTING_V1.md"
STEERING_REL = "docs/SOP/AGENT_STEERING_V1.json"

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
    "implied_distribution": "docs/SOP/IMPLIED_DISTRIBUTION_PROGRAM_V1.md",
    "options_horizon": "docs/SOP/OPTIONS_HORIZON_PROGRAM_V1.md",
    "forward_consistency": "docs/SOP/FORWARD_CONSISTENCY_RADAR_PROGRAM_V1.md",
    "expression_planner": "docs/SOP/EXPRESSION_PLANNER_PROGRAM_V1.md",
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
    {
        "id": "steward_selection",
        "match": ("steward", "selection", "closeout", "selection outcome", "selection prep"),
        "sop": "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
        "load_always": [
            "docs/SOP/PHASE_CHAPTER_BACKLOG.json",
            "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json",
        ],
        "load_on_demand": ["docs/SOP/PHASE_SELECTION_ROADMAP.json"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "module_registry",
        "match": ("module registry", "module map", "ppe module", "tier-1 module"),
        "sop": "docs/SOP/PPE_MODULE_REGISTRY_V1.md",
        "load_always": ["docs/SOP/PPE_MODULE_REGISTRY_V1.md"],
        "load_on_demand": ["docs/SOP/CHAPTER_DOC_INDEX.json"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "enablement",
        "match": ("enablement", "enable runbook", "asset enablement", "enable asset batch"),
        "sop": "docs/SOP/ASSET_ENABLEMENT_RUNBOOK_V1.md",
        "load_always": [
            "docs/SOP/ASSET_ENABLEMENT_RUNBOOK_V1.md",
            "docs/SOP/ASSET_DATA_SOURCE_DISCOVERY_V1.md",
        ],
        "cursor_rule": ".cursor/rules/asset-auto-discovery.mdc",
        "next_action": "run_discover_asset_data_source",
    },
    {
        "id": "msos_web",
        "match": ("msos web", "msos website", "strategy lab", "feedback beta", "feedback instrumentation"),
        "sop": "docs/SOP/MSOS_WEBSITE_PROGRAM.md",
        "load_always": ["docs/SOP/MSOS_WEBSITE_PROGRAM.md"],
        "load_on_demand": ["docs/SOP/MSOS_FRONTIER.md"],
        "next_action": "charter_thread_load_program",
    },
    {
        "id": "token_burst",
        "match": ("token economy", "burst mode", "burst plan", "adaptive burst", "token budget"),
        "sop": "docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md",
        "load_always": ["docs/SOP/PPE_TOKEN_ECONOMY_MONITOR_V1.md"],
        "load_on_demand": [".cursor/rules/ppe-burst-mode.mdc"],
        "next_action": "operator_thread_burst_or_single",
    },
    {
        "id": "sop_discovery",
        "match": (
            "sop discovery",
            "resolve_sop",
            "chapter doc index",
            "chapter_doc_index",
            "which sop",
            "which doc to load",
        ),
        "sop": ROUTING_CANON_REL,
        "load_always": [ROUTING_CANON_REL, CHAPTER_DOC_INDEX_REL],
        "load_on_demand": [ARCHIVE_INDEX_REL, ".cursor/rules/sop-discovery.mdc"],
        "next_action": "run_resolve_sop_cli",
        "agent_steps": [
            "python scripts/resolve_sop.py --topic \"<phrase>\" --json",
            "python scripts/resolve_sop.py --list-topics --json",
            "python scripts/resolve_sop.py --role <role> --json",
        ],
    },
]

ROLE_ROUTES: dict[str, dict[str, Any]] = {
    "operator": {
        "sop": ROUTING_CANON_REL,
        "load_always": [
            "artifacts/orchestrator/OPERATOR_STATUS.md",
            "docs/SOP/AGENT_CONTINUITY_BRIEF.md",
            "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json",
        ],
        "never_load": [
            "docs/SOP/UX_EXECUTION_BACKLOG_V1.md",
            "docs/SOP/MSOS_UX_DESIGN_PHILOSOPHY_V1.md",
        ],
        "next_action": "operator_thread_burst_or_single",
        "agent_steps": [
            "python scripts/ppe_burst_plan.py --write",
            "Read artifacts/orchestrator/OPERATOR_STATUS.md Mode: line first.",
        ],
    },
    "charter": {
        "sop": ROUTING_CANON_REL,
        "load_always": [],
        "never_load": [
            "artifacts/orchestrator/OPERATOR_STATUS.md",
            "artifacts/control_plane/BURST_PLAN.json",
        ],
        "next_action": "charter_thread_load_program",
        "agent_steps": [
            "Load only the stated program/SELECTION doc.",
            "python scripts/resolve_sop.py --topic \"<topic>\" --json for unclear topics.",
        ],
    },
    "ide_build": {
        "sop": ROUTING_CANON_REL,
        "load_always": [],
        "never_load": [
            "artifacts/orchestrator/OPERATOR_STATUS.md",
            "artifacts/control_plane/BURST_PLAN.json",
            "docs/SOP/PHASE_QUEUE.json",
        ],
        "next_action": "load_ide_build_starter_only",
        "agent_steps": [
            "Load only @artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md",
        ],
    },
    "explore": {
        "sop": ROUTING_CANON_REL,
        "load_always": [],
        "never_load": [
            "artifacts/orchestrator/OPERATOR_STATUS.md",
            "artifacts/control_plane/BURST_PLAN.json",
        ],
        "next_action": "explore_user_scope_only",
        "agent_steps": ["Load only user @ files; no relay or commits unless asked."],
    },
    "neutral": {
        "sop": ROUTING_CANON_REL,
        "load_always": [],
        "never_load": ["artifacts/orchestrator/OPERATOR_STATUS.md"],
        "next_action": "answer_user_scope_only",
        "agent_steps": ["Do not lead with operator status or relay verdict."],
    },
}


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
    archived = queue_status == "DONE"

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
        "archived": archived,
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
    active = [row for row in chapters if not row.get("archived")]
    archived_rows = [row for row in chapters if row.get("archived")]
    return {
        "version": 1,
        "generated_at": _utc_now(),
        "canon": ROUTING_CANON_REL,
        "resolve_cmd": "python scripts/resolve_sop.py --chapter <id> --json",
        "chapter_count": len(chapters),
        "active_chapter_count": len(active),
        "archived_chapter_count": len(archived_rows),
        "chapters": chapters,
        "active_chapters": active,
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
    write_archive_index(repo, data=data)
    write_program_doc_index(repo)
    sync_agent_steering_doc_hints(repo)
    return out



def _index_without_timestamp(data: dict[str, Any]) -> dict[str, Any]:
    copy = dict(data)
    copy.pop("generated_at", None)
    return copy


def _archive_markdown(data: dict[str, Any]) -> str:
    archived = [row for row in (data.get("chapters") or []) if row.get("archived")]
    archived.sort(key=lambda r: str(r.get("chapter_id") or ""))
    lines = [
        "# SOP archive index (generated)",
        "",
        f"**Generated:** {data.get('generated_at', 'unknown')} · "
        f"**Archived chapters:** {len(archived)}",
        "",
        "> **Do not load for BUILD** — archived chapters only. "
        "Use `python scripts/resolve_sop.py --chapter <id> --json` for active work.",
        "",
        "| chapter_id | selection | evidence | plan |",
        "|------------|-----------|----------|------|",
    ]
    for row in archived:
        cid = str(row.get("chapter_id") or "")
        sel = str(row.get("selection") or "—")
        ev = str(row.get("evidence") or "—")
        plan = str(row.get("plan_path") or "—")
        lines.append(f"| `{cid}` | `{sel}` | `{ev}` | `{plan}` |")
    if not archived:
        lines.append("| _none_ | — | — | — |")
    lines.extend(
        [
            "",
            f"Regenerate: `python scripts/generate_chapter_doc_index.py --write` · "
            f"canon: [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)",
            "",
        ]
    )
    return "\n".join(lines)


def write_archive_index(repo: Path, *, data: dict[str, Any] | None = None) -> Path:
    repo = repo.resolve()
    payload = data if data is not None else build_chapter_doc_index(repo)
    out = repo / ARCHIVE_INDEX_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(_archive_markdown(payload), encoding="utf-8")
    return out


def chapter_doc_index_fresh(repo: Path) -> tuple[bool, str]:
    repo = repo.resolve()
    index_path = repo / CHAPTER_DOC_INDEX_REL
    archive_path = repo / ARCHIVE_INDEX_REL
    if not index_path.is_file():
        return False, f"missing {CHAPTER_DOC_INDEX_REL}"
    if not archive_path.is_file():
        return False, f"missing {ARCHIVE_INDEX_REL}"
    try:
        on_disk = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False, f"unreadable {CHAPTER_DOC_INDEX_REL}"
    expected = build_chapter_doc_index(repo)
    if _index_without_timestamp(on_disk) != _index_without_timestamp(expected):
        return False, f"stale {CHAPTER_DOC_INDEX_REL} (run --write)"
    expected_archive = _archive_markdown(expected)
    try:
        archive_text = archive_path.read_text(encoding="utf-8")
    except OSError:
        return False, f"unreadable {ARCHIVE_INDEX_REL}"

    def _archive_body(text: str) -> str:
        rows = [ln for ln in text.splitlines() if ln.startswith("|")]
        return "\n".join(rows)

    if _archive_body(archive_text) != _archive_body(expected_archive):
        return False, f"stale {ARCHIVE_INDEX_REL} (run --write)"
    return True, "fresh"


def list_topics() -> list[dict[str, Any]]:
    return [
        {
            "id": route["id"],
            "sop": route["sop"],
            "match": list(route.get("match") or ()),
            "next_action": route.get("next_action"),
        }
        for route in TOPIC_ROUTES
    ]


def expand_carry_docs_for_closeout(
    repo: Path,
    *,
    carry_docs: list[str] | None,
    chapter_id: str,
    plan_path: str,
) -> list[str]:
    repo = repo.resolve()
    base = [_norm(p) for p in (carry_docs or []) if str(p).strip()]
    try:
        bundle = chapter_doc_bundle(repo, chapter_id=chapter_id, plan_path=plan_path)
    except (OSError, json.JSONDecodeError, KeyError):
        return list(dict.fromkeys(base))
    extras = [
        p
        for p in (
            bundle.get("program_doc"),
            bundle.get("selection"),
            bundle.get("sprint"),
            bundle.get("evidence"),
            bundle.get("next_selection"),
            *(bundle.get("carry_docs") or []),
        )
        if p
    ]
    return list(dict.fromkeys(base + extras))


def sync_agent_steering_doc_hints(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    steering_path = repo / STEERING_REL
    if not steering_path.is_file():
        return {"ok": False, "reason": "steering_missing"}
    try:
        steering = json.loads(steering_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"ok": False, "reason": "steering_unreadable"}
    if not isinstance(steering, dict):
        return {"ok": False, "reason": "steering_invalid"}
    hints: dict[str, Any] = {}
    next_id = str(steering.get("nextBuildCandidateId") or "").strip()
    if next_id:
        report = resolve_by_chapter(repo, chapter_id=next_id)
        if report.get("ok"):
            hints["nextBuildCandidate"] = {
                "chapter_id": next_id,
                "resolve_cmd": f"python scripts/resolve_sop.py --chapter {next_id} --json",
                "program_doc": report.get("program_doc"),
                "load_always": list(report.get("load_always") or []),
                "load_for_build": list(report.get("load_for_build") or []),
                "load_on_demand": list(report.get("load_on_demand") or []),
            }
    steering["docHints"] = hints
    steering_path.write_text(json.dumps(steering, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "docHints": hints}


def refresh_sop_discovery_artifacts(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    out = write_chapter_doc_index(repo)
    archive_out = repo / ARCHIVE_INDEX_REL
    data = build_chapter_doc_index(repo)
    return {
        "ok": True,
        "index_path": _norm(str(out.relative_to(repo))),
        "archive_index_path": _norm(str(archive_out.relative_to(repo))),
        "chapter_count": data.get("chapter_count"),
        "active_chapter_count": data.get("active_chapter_count"),
        "archived_chapter_count": data.get("archived_chapter_count"),
    }


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



def resolve_by_role(role: str) -> dict[str, Any]:
    key = role.strip().lower()
    route = ROLE_ROUTES.get(key)
    if route is None:
        return {
            "ok": False,
            "role": key,
            "next_action": "unknown_role",
            "sop": ROUTING_CANON_REL,
            "load_always": [ROUTING_CANON_REL],
            "never_load": list(DO_NOT_LOAD),
            "do_not_load": list(DO_NOT_LOAD),
            "agent_steps": [
                f"Valid roles: {', '.join(sorted(ROLE_ROUTES))}",
                "python scripts/resolve_sop.py --role <role> --json",
            ],
        }
    return {
        "ok": True,
        "role": key,
        "sop": route.get("sop") or ROUTING_CANON_REL,
        "load_always": list(route.get("load_always") or []),
        "never_load": list(route.get("never_load") or []),
        "do_not_load": list(dict.fromkeys(list(route.get("never_load") or []) + list(DO_NOT_LOAD))),
        "next_action": route.get("next_action"),
        "agent_steps": list(route.get("agent_steps") or []),
    }


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
            if not row.get("archived") and row.get("queue_status") in (
                None,
                "READY",
                "RUNNING",
                "PLANNED",
            ):
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
        "archived": bundle.get("archived"),
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


def build_program_doc_index(repo: Path) -> dict[str, Any]:
    """Catalog of program docs for charter agents."""
    repo = repo.resolve()
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for mod_id, path in sorted(MODULE_PROGRAM_DOCS.items()):
        norm = _norm(path)
        rows.append({"module_id": mod_id, "program_doc": norm})
        seen.add(norm)
    sop = repo / "docs" / "SOP"
    if sop.is_dir():
        for path in sorted(sop.glob("*PROGRAM_V1.md")):
            rel = _norm(str(path.relative_to(repo)))
            if rel in seen:
                continue
            rows.append({"module_id": None, "program_doc": rel})
            seen.add(rel)
    return {
        "version": 1,
        "generated_at": _utc_now(),
        "program_count": len(rows),
        "programs": rows,
        "resolve_cmd": "python scripts/resolve_sop.py --module <module_id> --json",
    }


def write_program_doc_index(repo: Path) -> Path:
    repo = repo.resolve()
    data = build_program_doc_index(repo)
    out = repo / PROGRAM_DOC_INDEX_REL
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out


def _load_chapter_index(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    index_path = repo / CHAPTER_DOC_INDEX_REL
    if index_path.is_file():
        try:
            data = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return build_chapter_doc_index(repo)


def search_sop_docs(repo: Path, query: str, *, limit: int = 8) -> list[dict[str, Any]]:
    """Search active chapters + module program docs (not full SOP tree)."""
    needle = query.strip().lower()
    if not needle:
        return []
    hits: list[tuple[int, dict[str, Any]]] = []
    index = _load_chapter_index(repo)

    def _score(text: str) -> int:
        low = text.lower().replace("_", " ")
        if needle in low or needle.replace(" ", "_") in text.lower():
            return max(len(needle), 3)
        return 0

    for row in index.get("active_chapters") or []:
        if not isinstance(row, dict) or row.get("archived"):
            continue
        cid = str(row.get("chapter_id") or "")
        best = 0
        for field in ("chapter_id", "selection", "sprint", "program_doc", "plan_path"):
            best = max(best, _score(str(row.get(field) or "")))
        if best:
            hits.append(
                (
                    best,
                    {
                        "kind": "chapter",
                        "chapter_id": cid,
                        "program_doc": row.get("program_doc"),
                        "resolve_cmd": f"python scripts/resolve_sop.py --chapter {cid} --json",
                    },
                )
            )

    for mod_id, prog in MODULE_PROGRAM_DOCS.items():
        score = max(_score(mod_id), _score(prog))
        if score:
            hits.append(
                (
                    score,
                    {
                        "kind": "module",
                        "module_id": mod_id,
                        "program_doc": prog,
                        "resolve_cmd": f"python scripts/resolve_sop.py --module {mod_id} --json",
                    },
                )
            )

    for route in TOPIC_ROUTES:
        rid = str(route.get("id") or "")
        sop = str(route.get("sop") or "")
        score = max(_score(rid), _score(sop))
        match_phrases = list(route.get("match") or ())
        for phrase in match_phrases:
            score = max(score, _score(str(phrase)))
        if score:
            sample = str(match_phrases[0]) if match_phrases else rid
            hits.append(
                (
                    score,
                    {
                        "kind": "topic_route",
                        "topic_route_id": rid,
                        "sop": sop,
                        "resolve_cmd": f'python scripts/resolve_sop.py --topic "{sample}" --json',
                    },
                )
            )

    hits.sort(key=lambda item: (-item[0], str(item[1].get("chapter_id") or item[1].get("module_id") or "")))
    deduped: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for _, row in hits:
        key = str(row.get("chapter_id") or row.get("module_id") or row.get("topic_route_id") or "")
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(row)
        if len(deduped) >= limit:
            break
    return deduped


def resolve_by_search(repo: Path, query: str) -> dict[str, Any]:
    results = search_sop_docs(repo, query)
    if not results:
        return {
            "ok": False,
            "query": query,
            "next_action": "grep_or_ask_steward",
            "sop": ROUTING_CANON_REL,
            "load_always": [ROUTING_CANON_REL, PROGRAM_DOC_INDEX_REL],
            "do_not_load": list(DO_NOT_LOAD),
            "agent_steps": [
                "python scripts/resolve_sop.py --list-topics --json",
                "python scripts/resolve_sop.py --topic \"<phrase>\" --json",
            ],
        }
    if len(results) == 1 and results[0].get("kind") == "chapter" and results[0].get("chapter_id"):
        merged = resolve_by_chapter(repo, chapter_id=str(results[0]["chapter_id"]))
        merged["search_query"] = query
        merged["search_match_count"] = 1
        return merged
    return {
        "ok": True,
        "query": query,
        "search_match_count": len(results),
        "results": results,
        "next_action": "pick_from_search_results",
        "sop": ROUTING_CANON_REL,
        "load_always": [ROUTING_CANON_REL],
        "load_on_demand": [PROGRAM_DOC_INDEX_REL, CHAPTER_DOC_INDEX_REL],
        "do_not_load": list(DO_NOT_LOAD),
        "agent_steps": [
            "Pick one result and re-run resolve with --chapter or --module.",
        ],
    }


def format_operator_resolve_lines(
    repo: Path,
    *,
    plan_path: str | None = None,
    next_build_candidate: str | None = None,
) -> list[str]:
    """Lines for OPERATOR_STATUS.md doc-resolve block."""
    repo = repo.resolve()
    cid: str | None = None
    if plan_path:
        try:
            from scripts.ppe_chapter_mode import plan_chapter_id

            cid = plan_chapter_id(plan_path.replace("\\", "/").strip())
        except Exception:
            cid = _chapter_id_from_plan(plan_path)
    elif next_build_candidate:
        cid = str(next_build_candidate).strip() or None
    if not cid:
        return []
    report = resolve_by_chapter(repo, chapter_id=cid)
    if not report.get("ok"):
        return []
    lines = [f"**Doc resolve:** `python scripts/resolve_sop.py --chapter {cid} --json`"]
    build = report.get("load_for_build") or []
    if build:
        lines.append("  " + " · ".join(f"`{p}`" for p in build[:3]))
    prog = report.get("program_doc")
    if prog and prog not in build:
        lines.append(f"  program: `{prog}`")
    return lines
