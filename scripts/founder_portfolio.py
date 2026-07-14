"""Read-only founder portfolio commands.

Implements the v1 read surface for:

- what's next
- what's running
- commands

This script does not dispatch, enqueue, approve, repair, reconcile, or write
artifacts. It reads registry/configuration plus pipeline-native evidence and
labels evidence quality in the founder-facing snapshot.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.founder_portfolio_registry import load_registry, pipelines, validate_registry  # noqa: E402

COMMANDS = [
    ("what's next", "Read-only portfolio briefing across registered pipelines.", "what's next"),
    ("build next", "Dispatch one safe ready item. Not implemented in this read-only v1.", "build next"),
    ("build next <number>", "Fill up to N safe build slots once. Not implemented in this read-only v1.", "build next 2"),
    ("keep <number> running", "Maintain continuous safe capacity. Not implemented in this read-only v1.", "keep 1 running"),
    ("pause builds", "Pause automatic dispatch. Not implemented in this read-only v1.", "pause builds"),
    ("resume builds", "Refresh state and resume prior capacity. Not implemented in this read-only v1.", "resume builds"),
    ("what's running", "Read-only execution and capacity check-in.", "what's running"),
    ("commands", "Show founder command vocabulary.", "commands"),
    ("create pipeline <name>", "Start pipeline-registration workflow. Not implemented in this read-only v1.", "create pipeline txline"),
]

NATIVE_TO_FOUNDER_STATE = {
    "READY": "READY_TO_BUILD",
    "RUNNING": "RUNNING",
    "QUEUED": "QUEUED",
    "PLANNED": "BLOCKED",
    "BLOCKED": "BLOCKED",
    "DEFERRED": "AWAITING_FOUNDER",
    "DONE": "COMPLETE",
    "COMPLETE": "COMPLETE",
    "IDE_BUILD": "READY_TO_BUILD",
    "RUN_AUTO": "READY_TO_BUILD",
    "RUN_LOCAL": "READY_TO_BUILD",
    "SUPPLY_LOW": "UNFILLED",
    "STALE_STATE": "BLOCKED",
    "ERROR": "BLOCKED",
    "STACK_DOWN": "BACKPRESSURE",
    "HEALTHY_IDLE": "UNFILLED",
    "AWAITING_BUILD": "READY_TO_BUILD",
    "BUILD_IN_FLIGHT": "RUNNING",
    "CLOSEOUT_PENDING": "AWAITING_REVIEW",
    "FINISH_IN_FLIGHT": "AWAITING_REVIEW",
    "RUN_LOCAL_PENDING": "AWAITING_REVIEW",
    "FIX_PLAN": "BLOCKED",
    "DEGRADED": "BACKPRESSURE",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(raw: Any) -> datetime | None:
    value = str(raw or "").strip()
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _age_seconds(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds())


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"invalid: {exc}"
    if not isinstance(data, dict):
        return None, "invalid: expected object"
    return data, None


def _file_evidence(repo: Path, rel: str, *, freshness_seconds: int | None = None) -> dict[str, Any]:
    path = repo / rel
    if not path.is_file():
        return {
            "kind": "missing",
            "source": rel,
            "fresh": False,
            "message": "source not present",
        }
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age = _age_seconds(mtime)
    fresh = freshness_seconds is None or (age is not None and age <= freshness_seconds)
    return {
        "kind": "native_runtime" if fresh else "stale",
        "source": rel,
        "fresh": fresh,
        "as_of": mtime.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "age_seconds": int(age or 0),
    }


def _payload_evidence(
    rel: str,
    payload: dict[str, Any] | None,
    *,
    fallback_kind: str = "manual",
    freshness_seconds: int | None = None,
) -> dict[str, Any]:
    if payload is None:
        return {"kind": "missing", "source": rel, "fresh": False, "message": "source not present"}
    as_of = _parse_utc(payload.get("as_of") or payload.get("asOf") or payload.get("timestamp"))
    age = _age_seconds(as_of)
    fresh = as_of is not None and (freshness_seconds is None or (age is not None and age <= freshness_seconds))
    return {
        "kind": fallback_kind if fresh else ("stale" if as_of else "manual"),
        "source": rel,
        "fresh": fresh,
        "as_of": as_of.replace(microsecond=0).isoformat().replace("+00:00", "Z") if as_of else None,
        "age_seconds": int(age) if age is not None else None,
    }


def _norm_state(native: Any, *, default: str = "BLOCKED") -> str:
    return NATIVE_TO_FOUNDER_STATE.get(str(native or "").strip().upper(), default)


def _ready_queue_items(repo: Path) -> list[dict[str, Any]]:
    data, _ = _load_json(repo / "docs/SOP/PHASE_QUEUE.json")
    out: list[dict[str, Any]] = []
    for item in (data or {}).get("items") or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").strip().upper()
        if status != "READY":
            continue
        out.append(
            {
                "work_item_id": Path(str(item.get("planPath") or "")).stem.replace("_relay", ""),
                "title": str(item.get("reason") or item.get("planPath") or "").strip(),
                "native_state": status,
                "state": "READY_TO_BUILD",
                "trace": str(item.get("planPath") or "").replace("\\", "/"),
                "evidence": "manual",
            }
        )
    return out


def _backlog_counts(repo: Path) -> dict[str, int]:
    data, _ = _load_json(repo / "docs/SOP/PHASE_CHAPTER_BACKLOG.json")
    counts = {"queued": 0, "ready": 0, "blocked": 0, "awaiting_founder": 0, "done": 0, "other": 0}
    for item in (data or {}).get("items") or []:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "").strip().lower()
        if status == "ready":
            counts["ready"] += 1
        elif status == "queued":
            counts["queued"] += 1
        elif status == "blocked":
            counts["blocked"] += 1
        elif status in {"deferred", "awaiting_founder"}:
            counts["awaiting_founder"] += 1
        elif status == "done":
            counts["done"] += 1
        else:
            counts["other"] += 1
    return counts


def _ppe_status(repo: Path, pipe: dict[str, Any]) -> dict[str, Any]:
    freshness = int((pipe.get("status_adapter") or {}).get("freshness_seconds") or 21600)
    manifest, manifest_error = _load_json(repo / "docs/SOP/ACTIVE_PHASE_MANIFEST.json")
    active_run, active_error = _load_json(repo / "artifacts/orchestrator/ACTIVE_RUN.json")
    active_evidence = _payload_evidence(
        "artifacts/orchestrator/ACTIVE_RUN.json",
        active_run,
        fallback_kind="native_runtime",
        freshness_seconds=freshness,
    )
    ready = _ready_queue_items(repo)
    backlog = _backlog_counts(repo)

    manifest_state = str((manifest or {}).get("status") or "").strip().upper()
    manifest_plan = str((manifest or {}).get("phasePlanPath") or "").strip()
    running: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []

    if active_run and active_evidence.get("kind") == "native_runtime":
        running.append(
            {
                "work_item_id": str(active_run.get("slice_id") or active_run.get("chapter_id") or manifest_plan or "ppe-active"),
                "stage": str(active_run.get("stage") or "RUNNING"),
                "state": "RUNNING",
                "native_state": "ACTIVE_RUN",
                "trace": {
                    "branch": active_run.get("branch"),
                    "workspace": active_run.get("workspace"),
                    "source": "artifacts/orchestrator/ACTIVE_RUN.json",
                },
                "evidence": "native_runtime",
            }
        )
    elif active_run:
        stale.append(
            {
                "state": "RUNNING",
                "native_state": "ACTIVE_RUN",
                "source": "artifacts/orchestrator/ACTIVE_RUN.json",
                "message": "ACTIVE_RUN.json exists but is stale or lacks a fresh as_of timestamp",
            }
        )
    elif manifest_state == "RUNNING":
        stale.append(
            {
                "state": "RUNNING",
                "native_state": manifest_state,
                "source": "docs/SOP/ACTIVE_PHASE_MANIFEST.json",
                "message": "manifest says RUNNING but ACTIVE_RUN.json is missing",
            }
        )

    queued = [
        {
            "work_item_id": item["work_item_id"],
            "state": "QUEUED",
            "native_state": item["native_state"],
            "title": item["title"],
            "trace": item["trace"],
            "evidence": item["evidence"],
        }
        for item in ready
    ]

    native_status = manifest_state or ("READY" if ready else "COMPLETE")
    normalized = _norm_state(native_status, default="UNFILLED")
    if running:
        normalized = "RUNNING"
    elif stale:
        normalized = "BLOCKED"
    elif ready:
        normalized = "READY_TO_BUILD"

    backpressure: list[dict[str, Any]] = []
    if len(ready) >= 4:
        backpressure.append(
            {
                "state": "BACKPRESSURE",
                "reason": "maximum queued ready builds reached",
                "limit": 4,
                "evidence": "manual",
            }
        )
    if stale:
        backpressure.append(
            {
                "state": "BACKPRESSURE",
                "reason": "stale running evidence blocks honest dispatch",
                "evidence": "stale",
            }
        )

    manifest_evidence = _file_evidence(repo, "docs/SOP/ACTIVE_PHASE_MANIFEST.json", freshness_seconds=None)
    if manifest_error and manifest_error != "missing":
        stale.append({"state": "BLOCKED", "source": "docs/SOP/ACTIVE_PHASE_MANIFEST.json", "message": manifest_error})
    if active_error and active_error != "missing":
        stale.append({"state": "BLOCKED", "source": "artifacts/orchestrator/ACTIVE_RUN.json", "message": active_error})

    return {
        "pipeline_id": "ppe",
        "display_name": pipe.get("display_name"),
        "registration_stage": pipe.get("registration_stage"),
        "canonical_repo": pipe.get("canonical_repo"),
        "native_state": native_status,
        "state": normalized,
        "evidence": [manifest_evidence, active_evidence],
        "capacity": {
            "automatic_mode": "DISABLED",
            "desired": 0,
            "configured_max": 1,
            "available": max(0, 1 - len(running)),
            "source": "registry/default; no durable automatic policy in PPE repo",
            "evidence": "manual",
        },
        "running_work": running,
        "queued_work": queued,
        "awaiting_review_work": [],
        "awaiting_founder_count": backlog["awaiting_founder"],
        "blocked_count": backlog["blocked"],
        "backpressure": backpressure,
        "stale_evidence": stale,
        "next_action": _ppe_next_action(ready, running, stale),
    }


def _ppe_next_action(
    ready: list[dict[str, Any]],
    running: list[dict[str, Any]],
    stale: list[dict[str, Any]],
) -> dict[str, Any]:
    if stale:
        return {
            "state": "BLOCKED",
            "action_type": "evidence check",
            "summary": "Resolve stale PPE runtime evidence before any build selection.",
            "evidence": "stale",
        }
    if running:
        return {
            "state": "RUNNING",
            "action_type": "wait",
            "summary": "PPE has evidence-backed running work; wait for the pipeline-native transition.",
            "evidence": "native_runtime",
        }
    if ready:
        top = ready[0]
        return {
            "state": "READY_TO_BUILD",
            "action_type": "build",
            "summary": top["title"],
            "work_item_id": top["work_item_id"],
            "trace": top["trace"],
            "evidence": "manual",
        }
    return {
        "state": "UNFILLED",
        "action_type": "evidence check",
        "summary": "No READY PPE queue item found in PHASE_QUEUE.json.",
        "evidence": "manual",
    }


def _autobuilder_status(repo: Path, pipe: dict[str, Any]) -> dict[str, Any]:
    freshness = int((pipe.get("status_adapter") or {}).get("freshness_seconds") or 21600)
    status_rel = "artifacts/orchestrator/AUTOBUILDER_STATUS.json"
    policy_rel = "artifacts/control_plane/AUTOMATIC_BUILD_POLICY.json"
    reconcile_rel = "artifacts/control_plane/PORTFOLIO_RECONCILIATION.json"
    status, status_error = _load_json(repo / status_rel)
    policy, _ = _load_json(repo / policy_rel)
    reconcile, _ = _load_json(repo / reconcile_rel)

    phase = str((status or {}).get("phase") or "").strip().upper()
    normalized = _norm_state(phase, default="BLOCKED" if status is None else "UNFILLED")
    status_evidence = _payload_evidence(status_rel, status, fallback_kind="native_runtime", freshness_seconds=freshness)
    evidence = [
        status_evidence,
        _payload_evidence(policy_rel, policy, fallback_kind="native_runtime", freshness_seconds=freshness),
        _payload_evidence(reconcile_rel, reconcile, fallback_kind="native_runtime", freshness_seconds=freshness),
    ]
    stale = [item for item in evidence if item["kind"] in {"missing", "stale"}]
    running: list[dict[str, Any]] = []
    queued: list[dict[str, Any]] = []
    awaiting_review: list[dict[str, Any]] = []
    backpressure: list[dict[str, Any]] = []

    build = status.get("build") if isinstance(status, dict) and isinstance(status.get("build"), dict) else {}
    if status_evidence.get("kind") == "stale" and normalized in {"RUNNING", "AWAITING_REVIEW"}:
        normalized = "BLOCKED"

    if normalized == "RUNNING" and status_evidence.get("kind") == "native_runtime":
        running.append(
            {
                "work_item_id": build.get("slice_id") or "autobuilder-active",
                "stage": phase,
                "state": "RUNNING",
                "native_state": phase,
                "trace": {
                    "plan_path": build.get("plan_path"),
                    "lock": build.get("lock"),
                    "source": status_rel,
                },
                "evidence": "native_runtime",
            }
        )
    if normalized == "AWAITING_REVIEW":
        awaiting_review.append(
            {
                "work_item_id": build.get("slice_id") or "autobuilder-review",
                "stage": phase,
                "state": "AWAITING_REVIEW",
                "native_state": phase,
                "trace": build.get("plan_path"),
                "evidence": "native_runtime",
            }
        )
    if normalized == "BACKPRESSURE":
        backpressure.append(
            {
                "state": "BACKPRESSURE",
                "reason": phase or status_error or "autobuilder status evidence missing",
                "evidence": "native_runtime" if status else "missing",
            }
        )

    queued_items = (reconcile or {}).get("queued_work") if isinstance(reconcile, dict) else None
    if isinstance(queued_items, list):
        for item in queued_items:
            if isinstance(item, dict):
                queued.append({**item, "state": "QUEUED", "evidence": "native_runtime"})

    mode = str((policy or {}).get("automatic_mode") or (policy or {}).get("mode") or "DISABLED").upper()
    desired = int((policy or {}).get("desired_capacity") or 0)
    configured = int((policy or {}).get("configured_max") or 2)
    if policy is None:
        mode = "DISABLED"
        desired = 0
        configured = 2

    if status_error and status_error != "missing":
        stale.append({"kind": "stale", "source": status_rel, "fresh": False, "message": status_error})

    return {
        "pipeline_id": "autobuilder",
        "display_name": pipe.get("display_name"),
        "registration_stage": pipe.get("registration_stage"),
        "canonical_repo": pipe.get("canonical_repo"),
        "native_state": phase or "MISSING",
        "state": normalized,
        "evidence": evidence,
        "capacity": {
            "automatic_mode": mode if mode in {"ENABLED", "PAUSED", "DISABLED"} else "DISABLED",
            "desired": desired,
            "configured_max": configured,
            "available": max(0, configured - len(running)),
            "source": policy_rel if policy else "registry/default; durable policy missing",
            "evidence": "native_runtime" if policy else "missing",
        },
        "running_work": running,
        "queued_work": queued,
        "awaiting_review_work": awaiting_review,
        "awaiting_founder_count": 0,
        "blocked_count": 0,
        "backpressure": backpressure,
        "stale_evidence": stale,
        "next_action": _autobuilder_next_action(status, normalized, stale),
    }


def _autobuilder_next_action(
    status: dict[str, Any] | None,
    normalized: str,
    stale: list[dict[str, Any]],
) -> dict[str, Any]:
    if status is None:
        return {
            "state": "BLOCKED",
            "action_type": "evidence check",
            "summary": "Autobuilder runtime status artifact is missing; read-only registry cannot claim running work.",
            "evidence": "missing",
        }
    if any(item.get("kind") == "stale" for item in stale):
        return {
            "state": "BLOCKED",
            "action_type": "evidence check",
            "summary": "Refresh Autobuilder runtime evidence before relying on capacity state.",
            "evidence": "stale",
        }
    action = str(status.get("recommended_action") or "").strip()
    if action:
        return {
            "state": normalized,
            "action_type": "evidence check" if normalized in {"BLOCKED", "BACKPRESSURE"} else "wait",
            "summary": f"Pipeline-native recommended action: {action}",
            "evidence": "native_runtime",
        }
    return {
        "state": normalized,
        "action_type": "evidence check",
        "summary": "Autobuilder is visible read-only; no PPE dispatch adapter is enabled.",
        "evidence": "native_runtime",
    }


def collect_portfolio(repo: Path) -> dict[str, Any]:
    repo = repo.resolve()
    errors = validate_registry(repo)
    registry = load_registry(repo)
    snapshots: list[dict[str, Any]] = []
    for pipe in pipelines(repo):
        kind = str((pipe.get("status_adapter") or {}).get("kind") or "")
        if kind == "ppe_phase_queue":
            snapshots.append(_ppe_status(repo, pipe))
        elif kind == "autobuilder_readonly_artifacts":
            snapshots.append(_autobuilder_status(repo, pipe))
        else:
            snapshots.append(
                {
                    "pipeline_id": pipe.get("pipeline_id"),
                    "display_name": pipe.get("display_name"),
                    "registration_stage": pipe.get("registration_stage"),
                    "canonical_repo": pipe.get("canonical_repo"),
                    "native_state": "UNKNOWN",
                    "state": "BLOCKED",
                    "evidence": [{"kind": "missing", "source": kind or "unknown", "fresh": False}],
                    "capacity": {"automatic_mode": "DISABLED", "desired": 0, "configured_max": 0, "available": 0},
                    "running_work": [],
                    "queued_work": [],
                    "awaiting_review_work": [],
                    "backpressure": [],
                    "stale_evidence": [],
                    "next_action": {
                        "state": "BLOCKED",
                        "action_type": "evidence check",
                        "summary": "No registered status adapter implementation.",
                        "evidence": "missing",
                    },
                }
            )

    capacity_cfg = registry.get("portfolio_capacity") if isinstance(registry.get("portfolio_capacity"), dict) else {}
    running_count = sum(len(p.get("running_work") or []) for p in snapshots)
    queued_count = sum(len(p.get("queued_work") or []) for p in snapshots)
    awaiting_review_count = sum(len(p.get("awaiting_review_work") or []) for p in snapshots)
    configured_max = int(capacity_cfg.get("future_steady_state_build_workers") or 2)
    return {
        "version": 1,
        "as_of": _utc_now(),
        "read_only": True,
        "registry_errors": errors,
        "capacity": {
            "automatic_mode": "DISABLED",
            "desired": 0,
            "configured_max": configured_max,
            "first_enabled_witness_capacity": int(capacity_cfg.get("first_enabled_witness_capacity") or 1),
            "available": max(0, configured_max - running_count),
            "running": running_count,
            "queued": queued_count,
            "awaiting_review": awaiting_review_count,
            "source": "config/founder_pipeline_registry.json",
        },
        "pipelines": snapshots,
        "recommended_next_action": _recommend_next(snapshots),
    }


def _recommend_next(pipelines_snapshot: list[dict[str, Any]]) -> dict[str, Any]:
    priority = {
        "BLOCKED": 0,
        "BACKPRESSURE": 1,
        "AWAITING_FOUNDER": 2,
        "AWAITING_REVIEW": 3,
        "RUNNING": 4,
        "READY_TO_BUILD": 5,
        "UNFILLED": 6,
        "COMPLETE": 7,
    }
    candidates = []
    for pipe in pipelines_snapshot:
        action = pipe.get("next_action") if isinstance(pipe.get("next_action"), dict) else {}
        state = str(action.get("state") or pipe.get("state") or "BLOCKED")
        candidates.append((priority.get(state, 99), pipe, action))
    if not candidates:
        return {
            "pipeline_id": None,
            "state": "UNFILLED",
            "action_type": "evidence check",
            "summary": "No registered pipelines.",
            "evidence": "missing",
        }
    _, pipe, action = sorted(candidates, key=lambda item: item[0])[0]
    return {
        "pipeline_id": pipe.get("pipeline_id"),
        "state": action.get("state") or pipe.get("state"),
        "action_type": action.get("action_type"),
        "summary": action.get("summary"),
        "work_item_id": action.get("work_item_id"),
        "evidence": action.get("evidence"),
    }


def format_commands() -> str:
    lines = ["Founder commands (read-only implementation status)", ""]
    for name, meaning, example in COMMANDS:
        marker = "implemented read-only" if name in {"what's next", "what's running", "commands"} else "not implemented"
        lines.append(f"- {name}: {meaning} Example: `{example}` ({marker})")
    lines.append("")
    lines.append("Read-only v1 confirmation: this entrypoint never dispatches, enqueues, approves, repairs, or writes.")
    return "\n".join(lines) + "\n"


def format_whats_next(snapshot: dict[str, Any]) -> str:
    lines = [
        "Founder portfolio: what's next",
        "",
        "Read-only: yes. No work was dispatched, queued, approved, repaired, or written.",
        f"As of: {snapshot.get('as_of')}",
        "",
    ]
    rec = snapshot.get("recommended_next_action") or {}
    lines.append(
        "Recommended next action: "
        f"{rec.get('pipeline_id') or 'none'} / {rec.get('state')} / {rec.get('action_type')} - {rec.get('summary')}"
    )
    lines.append("")
    lines.append("Pipelines:")
    for pipe in snapshot.get("pipelines") or []:
        action = pipe.get("next_action") or {}
        evidence = action.get("evidence") or "missing"
        lines.append(
            f"- {pipe.get('pipeline_id')}: {pipe.get('state')} "
            f"(native={pipe.get('native_state')}, evidence={evidence}) - {action.get('summary')}"
        )
    errors = snapshot.get("registry_errors") or []
    if errors:
        lines.extend(["", "Registry validation errors:"])
        lines.extend(f"- {err}" for err in errors)
    return "\n".join(lines) + "\n"


def format_whats_running(snapshot: dict[str, Any]) -> str:
    cap = snapshot.get("capacity") or {}
    lines = [
        "Founder portfolio: what's running",
        "",
        "Read-only: yes. No work was dispatched, queued, approved, repaired, or written.",
        f"As of: {snapshot.get('as_of')}",
        f"AUTOMATIC BUILD MODE: {cap.get('automatic_mode')}",
        f"DESIRED CAPACITY: {cap.get('desired')}",
        f"CONFIGURED MAX: {cap.get('configured_max')}",
        f"RUNNING: {cap.get('running')}",
        f"QUEUED: {cap.get('queued')}",
        f"AWAITING REVIEW: {cap.get('awaiting_review')}",
        f"AVAILABLE CAPACITY: {cap.get('available')}",
        "",
    ]
    for pipe in snapshot.get("pipelines") or []:
        pcap = pipe.get("capacity") or {}
        lines.append(f"{pipe.get('pipeline_id')} ({pipe.get('registration_stage')}):")
        lines.append(
            f"  mode={pcap.get('automatic_mode')} desired={pcap.get('desired')} "
            f"configured={pcap.get('configured_max')} available={pcap.get('available')}"
        )
        for label, key in (
            ("running", "running_work"),
            ("queued", "queued_work"),
            ("awaiting review", "awaiting_review_work"),
            ("backpressure", "backpressure"),
            ("stale evidence", "stale_evidence"),
        ):
            items = pipe.get(key) or []
            if not items:
                lines.append(f"  {label}: none")
            else:
                lines.append(f"  {label}:")
                for item in items[:6]:
                    if isinstance(item, dict):
                        name = item.get("work_item_id") or item.get("reason") or item.get("source") or item.get("message")
                        ev = item.get("evidence") or item.get("kind") or "unknown"
                        lines.append(f"    - {name} (state={item.get('state')}, evidence={ev})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _normalize_command(words: list[str]) -> str:
    text = " ".join(words).strip().lower()
    text = text.replace("’", "'")
    aliases = {
        "whats-next": "what's next",
        "whats next": "what's next",
        "what next": "what's next",
        "next": "what's next",
        "whats-running": "what's running",
        "whats running": "what's running",
        "running": "what's running",
        "help": "commands",
    }
    return aliases.get(text, text)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read-only founder portfolio commands")
    ap.add_argument("command", nargs="*", help="commands | what's next | what's running")
    ap.add_argument("--repo-root", type=Path, default=ROOT)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    command = _normalize_command(args.command or ["commands"])
    repo = args.repo_root.resolve()

    if command == "commands":
        payload = {"read_only": True, "commands": COMMANDS}
        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(format_commands(), end="")
        return 0

    if command not in {"what's next", "what's running"}:
        print(
            f"founder_portfolio: unsupported or non-read-only command `{command}`. "
            "Implemented read-only commands: what's next, what's running, commands.",
            file=sys.stderr,
        )
        return 2

    snapshot = collect_portfolio(repo)
    if args.json:
        print(json.dumps(snapshot, indent=2))
    elif command == "what's next":
        print(format_whats_next(snapshot), end="")
    else:
        print(format_whats_running(snapshot), end="")
    return 1 if snapshot.get("registry_errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
