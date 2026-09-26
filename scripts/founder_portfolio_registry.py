"""Founder portfolio registry loader and validator.

This module intentionally contains only read helpers. Runtime queues, product
operators, and Autobuilder controllers remain authoritative for their own state.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY_PATH = REPO / "config" / "founder_pipeline_registry.json"

REGISTRATION_STAGES = {
    "PROPOSED",
    "REGISTERED_READ_ONLY",
    "CHARTERED",
    "EXECUTION_READY",
    "SCHEDULE_READY",
    "ACTIVE",
    "COMPLETE",
}

EVIDENCE_KINDS = {"native_runtime", "canonical", "manual", "external", "inferred", "missing", "stale"}
NORMALIZED_STATES = {
    "READY_TO_BUILD",
    "RUNNING",
    "QUEUED",
    "AWAITING_REVIEW",
    "AWAITING_FOUNDER",
    "BACKPRESSURE",
    "BLOCKED",
    "UNFILLED",
    "COMPLETE",
}

ENGINEERING_OS_LANES = {
    "factory",
    "msos",
    "api_distribution",
    "structured_launchpad",
    "labs",
}
ENGINEERING_OS_BACKLOG_CLASSES = {"RESEARCH", "CANDIDATE", "COMMITTED"}
ENGINEERING_OS_LIFECYCLE_STATES = {
    "BACKLOG",
    "TRIAGE",
    "CHARTERED",
    "ACCEPTANCE_DEFINED",
    "READY_TO_BUILD",
    "RUNNING",
    "TESTING",
    "REVIEW",
    "STAGING",
    "RELEASED",
    "MONITORING",
    "COMPLETE",
    "AWAITING_FOUNDER",
    "BLOCKED",
    "REJECTED",
    "SUPERSEDED",
}
ENGINEERING_OS_LANE_MODES = {"PRODUCTION", "INCUBATION", "RESEARCH"}


@lru_cache(maxsize=4)
def _load_registry_cached(path_str: str) -> dict[str, Any]:
    path = Path(path_str)
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"registry must be an object: {path}")
    return data


def registry_path(repo: Path | None = None) -> Path:
    return (repo or REPO) / "config" / "founder_pipeline_registry.json"


def load_registry(repo: Path | None = None) -> dict[str, Any]:
    path = registry_path(repo)
    if not path.is_file():
        raise FileNotFoundError(path)
    return _load_registry_cached(str(path.resolve()))


def pipelines(repo: Path | None = None) -> list[dict[str, Any]]:
    data = load_registry(repo)
    items = data.get("pipelines") or []
    return [item for item in items if isinstance(item, dict)]


def pipeline_by_id(pipeline_id: str, repo: Path | None = None) -> dict[str, Any] | None:
    wanted = str(pipeline_id or "").strip().lower()
    for item in pipelines(repo):
        if str(item.get("pipeline_id") or "").strip().lower() == wanted:
            return item
    return None


def _require_dict(errors: list[str], owner: str, data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        errors.append(f"{owner}: {key} must be an object")
        return {}
    return value


def validate_registry(repo: Path | None = None) -> list[str]:
    repo = (repo or REPO).resolve()
    errors: list[str] = []
    data = load_registry(repo)

    if data.get("version") != 1:
        errors.append("version must be 1")

    canon = data.get("canon")
    if not isinstance(canon, list) or not canon:
        errors.append("canon must be a non-empty array")
    else:
        for rel in canon:
            if not isinstance(rel, str) or not rel.strip():
                errors.append("canon entries must be non-empty strings")
                continue
            if not (repo / rel).is_file():
                errors.append(f"missing canon file {rel}")

    engineering_os = _require_dict(errors, "engineering_os", data, "engineering_os")
    if engineering_os:
        if engineering_os.get("version") != 1:
            errors.append("engineering_os: version must be 1")
        os_canon = str(engineering_os.get("canon") or "").strip()
        if not os_canon:
            errors.append("engineering_os: canon must be a non-empty string")
        elif not (repo / os_canon).is_file():
            errors.append(f"engineering_os: missing canon file {os_canon}")

        backlog_classes = engineering_os.get("backlog_classes")
        if set(backlog_classes or []) != ENGINEERING_OS_BACKLOG_CLASSES:
            errors.append("engineering_os: backlog_classes must exactly match canonical classes")

        lifecycle_states = engineering_os.get("lifecycle_states")
        if set(lifecycle_states or []) != ENGINEERING_OS_LIFECYCLE_STATES:
            errors.append("engineering_os: lifecycle_states must exactly match canonical states")

        dispatch_rule = _require_dict(errors, "engineering_os", engineering_os, "dispatch_rule")
        if dispatch_rule:
            if dispatch_rule.get("requires_backlog_class") != "COMMITTED":
                errors.append("engineering_os: dispatch requires COMMITTED backlog class")
            if dispatch_rule.get("requires_native_state") != "READY_TO_BUILD":
                errors.append("engineering_os: dispatch requires READY_TO_BUILD native state")

        lane_rows = engineering_os.get("lanes")
        if not isinstance(lane_rows, list):
            errors.append("engineering_os: lanes must be an array")
            lane_rows = []
        lane_ids: set[str] = set()
        for lane in lane_rows:
            if not isinstance(lane, dict):
                errors.append("engineering_os: lane entries must be objects")
                continue
            lane_id = str(lane.get("lane_id") or "").strip()
            owner = f"engineering_os lane {lane_id or '<missing>'}"
            if lane_id not in ENGINEERING_OS_LANES:
                errors.append(f"{owner}: invalid lane_id")
            if lane_id in lane_ids:
                errors.append(f"{owner}: duplicate lane_id")
            lane_ids.add(lane_id)
            if not str(lane.get("display_name") or "").strip():
                errors.append(f"{owner}: missing display_name")
            pipeline_ids = lane.get("pipeline_ids")
            if not isinstance(pipeline_ids, list) or not pipeline_ids:
                errors.append(f"{owner}: pipeline_ids must be a non-empty array")
            mode = str(lane.get("mode") or "").strip()
            if mode not in ENGINEERING_OS_LANE_MODES:
                errors.append(f"{owner}: invalid mode {mode}")
            wip = lane.get("implementation_wip_limit")
            if not isinstance(wip, int) or wip < 0:
                errors.append(f"{owner}: implementation_wip_limit must be a non-negative integer")
        if lane_ids != ENGINEERING_OS_LANES:
            errors.append("engineering_os: lanes must exactly match canonical lane ids")

    ids: set[str] = set()
    aliases: set[str] = set()
    for pipe in pipelines(repo):
        pid = str(pipe.get("pipeline_id") or "").strip()
        owner = f"pipeline {pid or '<missing>'}"
        if not pid or pid != pid.lower() or " " in pid:
            errors.append(f"{owner}: pipeline_id must be stable lowercase without spaces")
        if pid in ids:
            errors.append(f"duplicate pipeline_id {pid}")
        ids.add(pid)

        for key in ("display_name", "canonical_repo", "pipeline_type"):
            if not str(pipe.get(key) or "").strip():
                errors.append(f"{owner}: missing {key}")

        stage = str(pipe.get("registration_stage") or "").strip()
        if stage not in REGISTRATION_STAGES:
            errors.append(f"{owner}: invalid registration_stage {stage}")

        pipe_aliases = pipe.get("aliases")
        if not isinstance(pipe_aliases, list) or not pipe_aliases:
            errors.append(f"{owner}: aliases must be a non-empty array")
        else:
            for alias in pipe_aliases:
                norm = str(alias or "").strip().lower()
                if not norm:
                    errors.append(f"{owner}: blank alias")
                if norm in aliases:
                    errors.append(f"{owner}: duplicate alias {norm}")
                aliases.add(norm)

        status_adapter = _require_dict(errors, owner, pipe, "status_adapter")
        build_adapter = _require_dict(errors, owner, pipe, "build_adapter")
        authority = _require_dict(errors, owner, pipe, "authority")
        scheduling = _require_dict(errors, owner, pipe, "scheduling")

        if status_adapter and status_adapter.get("read_only") is not True:
            errors.append(f"{owner}: status_adapter.read_only must be true")
        if status_adapter and str(status_adapter.get("source_scope") or "") == "external_repository":
            if not str(status_adapter.get("external_repo") or "").strip():
                errors.append(f"{owner}: external status adapter missing external_repo")
            if not str(status_adapter.get("external_root_env") or "").strip():
                errors.append(f"{owner}: external status adapter missing external_root_env")
        dispatch_enabled = build_adapter.get("dispatch_commands_enabled") is True if build_adapter else False
        if dispatch_enabled:
            dependency = str(build_adapter.get("accepted_dispatcher_dependency") or "")
            if pid != "ppe":
                errors.append(f"{owner}: only ppe may enable one-shot dispatch")
            if dependency != "msos_autobuilder_build_next_dispatcher":
                errors.append(f"{owner}: enabled dispatch must cite accepted Autobuilder dependency")
        if scheduling and scheduling.get("continuous_refill_eligible") is not False:
            errors.append(f"{owner}: continuous_refill_eligible must remain false in v1")
        if pid != "ppe" and scheduling and scheduling.get("build_next_eligible") is True:
            errors.append(f"{owner}: only ppe may be build-next eligible in this rollout")
        if authority and not str(authority.get("portfolio_registry_owner") or "").strip():
            errors.append(f"{owner}: missing portfolio_registry_owner")

    engineering_os = data.get("engineering_os") if isinstance(data.get("engineering_os"), dict) else {}
    for lane in engineering_os.get("lanes") or []:
        if not isinstance(lane, dict):
            continue
        for pipeline_id in lane.get("pipeline_ids") or []:
            if str(pipeline_id) not in ids:
                errors.append(
                    f"engineering_os lane {lane.get('lane_id')}: unknown pipeline_id {pipeline_id}"
                )

    if "ppe" not in ids:
        errors.append("registry must include ppe")
    if "autobuilder" not in ids:
        errors.append("registry must include autobuilder")
    txline = pipeline_by_id("txline", repo)
    if txline:
        stage = str(txline.get("registration_stage") or "")
        if stage in {"EXECUTION_READY", "SCHEDULE_READY", "ACTIVE"}:
            errors.append("txline must not be execution-ready until its repo and charter exist")

    return errors