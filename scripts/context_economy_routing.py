"""Context-economy routing overlay for the public SOP resolver.

This module deliberately leaves the large discovery catalog intact and applies the
smallest safe policy correction at the CLI boundary used by operators and agents.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from scripts.sop_discovery_core import (
    CHAPTER_DOC_INDEX_REL,
    ROUTING_CANON_REL,
    resolve_by_role,
    resolve_by_topic,
)

CONTROL_PLANE_REL = "docs/SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md"
PROJECT_STARTER_REL = "docs/SOP/CHATGPT_PROJECT_STARTER.md"
CONTINUITY_REL = "docs/SOP/AGENT_CONTINUITY_BRIEF.md"
BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
ACTIVE_DIRECTION_REL = "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"

_GENERIC_FOUNDER_TOPICS = {
    "founder charter",
    "founder setup",
    "founder collaboration",
    "collaboration setup",
    "control plane setup",
}

_GENERIC_CHARTER_TOPICS = {
    "charter thread",
    "topic thread",
    "product charter",
    "start charter thread",
}


def _normalize_topic(topic: str) -> str:
    return " ".join(topic.strip().lower().split())


def _dedupe(paths: list[str]) -> list[str]:
    return list(dict.fromkeys(path for path in paths if path))


def _move_to_on_demand(report: dict[str, Any], path: str) -> None:
    always = [item for item in report.get("load_always") or [] if item != path]
    on_demand = list(report.get("load_on_demand") or [])
    if path not in on_demand:
        on_demand.append(path)
    report["load_always"] = _dedupe(always)
    report["load_on_demand"] = _dedupe(on_demand)


def _continuity_warning_steps(report: dict[str, Any]) -> None:
    steps = list(report.get("agent_steps") or [])
    warning = (
        "Load AGENT_CONTINUITY_BRIEF.md only after the token audit reports it fresh "
        "and complete; otherwise use GitHub main plus current status/direction and "
        "regenerate through apply_control_closeout_v1."
    )
    if warning not in steps:
        steps.insert(0, warning)
    report["agent_steps"] = steps


def resolve_role_context_economy(role: str) -> dict[str, Any]:
    """Resolve a role while keeping generated continuity on demand and freshness-gated."""

    report = deepcopy(resolve_by_role(role))
    if report.get("role") == "operator":
        _move_to_on_demand(report, CONTINUITY_REL)
        _continuity_warning_steps(report)
    return report


def resolve_topic_context_economy(topic: str) -> dict[str, Any]:
    """Resolve a topic without broad state bundles for generic thread phrases."""

    normalized = _normalize_topic(topic)
    if normalized in _GENERIC_FOUNDER_TOPICS:
        return {
            "ok": True,
            "topic": topic,
            "topic_route_id": "founder_control_plane",
            "sop": CONTROL_PLANE_REL,
            "load_always": [CONTROL_PLANE_REL],
            "load_for_build": [],
            "load_on_demand": [PROJECT_STARTER_REL],
            "next_action": "founder_setup_thread",
            "agent_steps": [
                "Treat ChatGPT Project instructions as already present.",
                "Load one relevant charter or issue only when the topic is known.",
                "Do not load backlog, active direction, or generated status by default.",
            ],
            "do_not_load": [BACKLOG_REL, ACTIVE_DIRECTION_REL, CONTINUITY_REL],
        }

    if normalized in _GENERIC_CHARTER_TOPICS:
        return {
            "ok": True,
            "topic": topic,
            "topic_route_id": "charter_scope_required",
            "sop": ROUTING_CANON_REL,
            "load_always": [],
            "load_for_build": [],
            "load_on_demand": [],
            "next_action": "name_relevant_program_or_issue",
            "agent_steps": [
                "Project instructions are already present; add one role contract.",
                "Name one relevant program, charter, or GitHub issue before loading repo state.",
                "Do not load PHASE_CHAPTER_BACKLOG or ACTIVE_PRODUCT_DIRECTION for a generic charter phrase.",
            ],
            "do_not_load": [BACKLOG_REL, ACTIVE_DIRECTION_REL, CONTINUITY_REL],
        }

    report = deepcopy(resolve_by_topic(topic))
    route_id = report.get("topic_route_id")

    if route_id == "sop_discovery":
        _move_to_on_demand(report, CHAPTER_DOC_INDEX_REL)
        steps = list(report.get("agent_steps") or [])
        note = "Load CHAPTER_DOC_INDEX.json only when a chapter lookup actually requires it."
        if note not in steps:
            steps.insert(0, note)
        report["agent_steps"] = steps

    if route_id == "operator_relay" or CONTINUITY_REL in (report.get("load_always") or []):
        _move_to_on_demand(report, CONTINUITY_REL)
        _continuity_warning_steps(report)

    return report
