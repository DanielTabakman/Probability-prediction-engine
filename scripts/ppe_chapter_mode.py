"""Resolve chapter execution mode for operator status and IDE BUILD starters."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MODE_CLOSEOUT_ONLY = "CLOSEOUT_ONLY"
MODE_IDE_BUILD = "IDE_BUILD"
MODE_RUN_LOCAL = "RUN_LOCAL"
MODE_RUN_AUTO = "RUN_AUTO"
MODE_OTHER = "OTHER"

DIRECTION_REL = "docs/SOP/ACTIVE_PRODUCT_DIRECTION.json"
STEERING_REL = "docs/SOP/AGENT_STEERING_V1.json"


def _load_steering_raw(repo: Path) -> dict[str, Any]:
    path = repo / STEERING_REL
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    steering = _load_direction_raw(repo).get("agentSteering")
    return steering if isinstance(steering, dict) else {}


def load_agent_steering(repo: Path) -> dict[str, Any]:
    return _load_steering_raw(repo)


def plan_chapter_id(plan_path: str) -> str:
    name = Path(plan_path.replace("\\", "/")).name
    if name.endswith("_relay.json"):
        return name[: -len("_relay.json")]
    return name.replace(".json", "")


def product_slices_on_main(repo: Path, plan_path: str) -> list[str]:
    from scripts.ppe_ide_product_ready import _product_touchset_on_main
    from scripts.ppe_manifest import load_phase_plan
    from scripts.ppe_slice_worker_mode import infer_slice_kind

    norm = plan_path.replace("\\", "/").strip()
    try:
        plan = load_phase_plan(repo, norm)
    except (FileNotFoundError, OSError):
        return []
    on_main: list[str] = []
    for sl in plan.get("slices") or []:
        if not isinstance(sl, dict):
            continue
        sid = str(sl.get("sliceId") or "").strip()
        if not sid:
            continue
        if infer_slice_kind(sid, sl) == "product" and _product_touchset_on_main(
            repo, slice_id=sid, plan_path=norm
        ):
            on_main.append(sid)
    return on_main


def is_closeout_only_chapter(
    repo: Path,
    *,
    plan_path: str | None,
    chapter_name: str | None,
) -> bool:
    ids = load_agent_steering(repo).get("closeoutOnlyChapterIds") or []
    if not isinstance(ids, list):
        return False
    chapter_id = plan_chapter_id(plan_path or "") if plan_path else ""
    if chapter_id and chapter_id in ids:
        return True
    if chapter_name:
        cn = chapter_name.lower()
        for cid in ids:
            token = str(cid).replace("_", " ")
            if token in cn or str(cid) in cn.replace(" ", "_"):
                return True
    return False


def resolve_chapter_mode(
    repo: Path,
    *,
    verdict: str,
    plan_path: str | None,
    guard_reason: str | None,
    chapter_name: str | None = None,
) -> dict[str, Any]:
    norm_plan = (plan_path or "").replace("\\", "/").strip() or None
    on_main = product_slices_on_main(repo, norm_plan) if norm_plan else []
    product_on_main = bool(on_main)
    closeout_flag = is_closeout_only_chapter(
        repo, plan_path=norm_plan, chapter_name=chapter_name
    )
    steering = load_agent_steering(repo)

    mode = MODE_OTHER
    do_not_rebuild = False
    instructions: list[str] = []

    if guard_reason == "IDE_MARKER_OK":
        mode = MODE_CLOSEOUT_ONLY
        do_not_rebuild = True
        instructions = [
            "Product slice(s) marked ready — do NOT re-implement product code.",
            "Finish relay: witness/closeout slices only.",
            "Desktop: DESKTOP_CONTINUE.cmd. VM: run_ppe_local.cmd or @ppe-finish-worker.",
        ]
    elif verdict == "RUN_LOCAL":
        if product_on_main or closeout_flag:
            mode = MODE_CLOSEOUT_ONLY
            do_not_rebuild = True
            instructions = [
                "Product already on main — closeout/witness relay only; do NOT re-BUILD product.",
                "Desktop: DESKTOP_CONTINUE.cmd. VM: run_ppe_local.cmd or @ppe-finish-worker.",
            ]
        else:
            mode = MODE_RUN_LOCAL
            instructions = [
                "Continue relay. Desktop: DESKTOP_CONTINUE.cmd. VM: run_ppe_local.cmd.",
            ]
    elif verdict == "IDE_BUILD":
        if closeout_flag or product_on_main:
            mode = MODE_CLOSEOUT_ONLY
            do_not_rebuild = True
            if closeout_flag and not product_on_main:
                instructions = [
                    "Chapter is closeout-only in agentSteering — product shipped on main.",
                    "Do NOT re-implement; run mark_ide_product_ready / finish closeout slices.",
                    "Desktop: DESKTOP_CONTINUE.cmd after merge. VM: run_ppe_local.cmd.",
                ]
            else:
                instructions = [
                    "Product is on main for this chapter — do NOT re-implement; finish marker/closeout.",
                ]
        else:
            mode = MODE_IDE_BUILD
            instructions = [
                "Implement product slice from IDE_BUILD_STARTER only.",
                "Do NOT read OPERATOR_STATUS in IDE BUILD thread.",
            ]
    elif verdict == "RUN_AUTO":
        mode = MODE_RUN_AUTO

    pending_closeout = steering.get("closeoutOnlyChapterIds") or []
    if not isinstance(pending_closeout, list):
        pending_closeout = []

    return {
        "mode": mode,
        "product_on_main": product_on_main,
        "product_slices_on_main": on_main,
        "do_not_rebuild": do_not_rebuild,
        "closeout_only_registry": closeout_flag,
        "agent_instructions": instructions,
        "pending_closeout_chapters": pending_closeout,
        "next_build_candidate": steering.get("nextBuildCandidateId"),
    }


def format_chapter_mode_block(info: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    if info.get("do_not_rebuild"):
        lines.append(
            "**Mode:** `CLOSEOUT_ONLY` — product on main; **do NOT re-BUILD** product slices."
        )
        on_main = info.get("product_slices_on_main") or []
        if on_main:
            lines.append(f"  Product on main: {', '.join(str(s) for s in on_main)}")
    elif str(info.get("mode") or "") == MODE_IDE_BUILD:
        lines.append("**Mode:** `IDE_BUILD` — implement pending product slice only.")
    elif info.get("mode"):
        lines.append(f"**Mode:** `{info['mode']}`")

    for inst in info.get("agent_instructions") or []:
        lines.append(f"  → {inst}")

    pending = info.get("pending_closeout_chapters") or []
    if pending and info.get("do_not_rebuild"):
        lines.append(f"  Registry closeout-only: {', '.join(str(p) for p in pending)}")

    next_c = info.get("next_build_candidate")
    if next_c and info.get("do_not_rebuild"):
        lines.append(f"  Next BUILD candidate (after closeout): `{next_c}`")

    return lines


def compose_steward_action_snippet(repo: Path) -> str:
    """Compose steward next-action text from agentSteering fields (SSOT)."""
    steering = load_agent_steering(repo)
    if not steering:
        try:
            return str(_load_direction_raw(repo).get("nextStewardAction") or "")
        except Exception:
            return ""

    parts: list[str] = []
    next_build = str(steering.get("nextBuildCandidateId") or "").strip()
    next_note = str(steering.get("nextBuildCandidateNote") or "promote READY").strip()
    if next_build:
        parts.append(
            "Direction/UX: docs/SOP/UX_EXECUTION_BACKLOG_V1.md — "
            f"next BUILD candidate {next_build} ({next_note})."
        )

    closeout = steering.get("closeoutOnlyChapterIds") or []
    if isinstance(closeout, list) and closeout:
        ids = ", ".join(str(c) for c in closeout)
        parts.append(
            f"Spine relay: finish closeout only for [{ids}] — product on main; "
            "do NOT re-BUILD (see OPERATOR_STATUS Mode)."
        )

    spine = steering.get("spineQueueAfterCloseout") or []
    if isinstance(spine, list) and spine:
        parts.append(f"Then spine queue: {' → '.join(str(s) for s in spine)}.")

    parallel = str(steering.get("parallelWork") or "").strip()
    if parallel:
        parts.append(parallel if parallel.endswith(".") else f"{parallel}.")

    return " ".join(parts)


def _load_direction_raw(repo: Path) -> dict[str, Any]:
    path = repo / DIRECTION_REL
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def is_loop_host_allowed() -> bool:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        return bool(loop_host_start_allowed()[0])
    except Exception:
        return False


def resolve_operator_commands(
    *,
    verdict: str,
    chapter_mode: dict[str, Any] | None,
    loop_host_allowed: bool,
) -> tuple[list[str], list[str]]:
    """Return (commands, avoid) tailored to chapter mode and machine role."""
    info = chapter_mode or {}
    do_not_rebuild = bool(info.get("do_not_rebuild"))
    mode = str(info.get("mode") or "")

    if do_not_rebuild and verdict in ("RUN_LOCAL", "IDE_BUILD"):
        if loop_host_allowed:
            return (
                ["run_ppe_local.cmd (witness/closeout only — do NOT re-BUILD product)"],
                [
                    "Re-implementing product slices (CLOSEOUT_ONLY)",
                    "run_ppe_auto_local_loop.cmd (use run_ppe_local.cmd once first)",
                ],
            )
        return (
            ["DESKTOP_CONTINUE.cmd --no-pause (SSH → VM finish_ide_build)"],
            [
                "run_ppe_local.cmd on desktop (forbidden — use DESKTOP_CONTINUE)",
                "IDE BUILD / re-implement product (CLOSEOUT_ONLY)",
            ],
        )

    if verdict == "IDE_BUILD" and mode == MODE_IDE_BUILD:
        from scripts.ppe_operator_hint import PPE_GO_HINT

        return (
            [PPE_GO_HINT],
            ["run_ppe_auto_local_loop.cmd  (will hit PRODUCT_BLOCKED)"],
        )

    if verdict == "RUN_LOCAL":
        if loop_host_allowed:
            return (
                ["run_ppe_local.cmd"],
                ["run_ppe_auto_local_loop.cmd  (use run_ppe_local.cmd once first)"],
            )
        return (
            ["DESKTOP_CONTINUE.cmd --no-pause"],
            ["run_ppe_local.cmd on desktop (forbidden — use DESKTOP_CONTINUE)"],
        )

    if verdict in ("FIX_PLAN", "STALE_STATE", "ERROR"):
        from scripts.ppe_operator_hint import PPE_GO_HINT

        return ([PPE_GO_HINT], [])

    if verdict == "RUN_AUTO":
        if loop_host_allowed:
            return (["run_ppe_auto_local_loop.cmd"], [])
        return (
            [
                "ssh ppeloop@desktop-caqll8k \"cd /d C:\\Users\\ppeloop\\Probability-prediction-engine && ppe_autobuilder.cmd status --brief\""
            ],
            ["run_ppe.cmd / run_ppe_auto_local_loop on desktop (forbidden on daily PC)"],
        )

    if verdict == "SUPPLY_LOW":
        return (
            [
                "python scripts/ppe_operator_status.py  (supply auto-heal + re-check)",
                "If still SUPPLY_LOW: python scripts/ppe_control_plane.py reconcile",
            ],
            [],
        )

    return ([], [])


def prune_closeout_chapter(repo: Path, *, plan_path: str) -> bool:
    """Remove chapter from closeoutOnlyChapterIds after relay closeout completes."""
    chapter_id = plan_chapter_id(plan_path)
    if not chapter_id:
        return False
    path = repo / STEERING_REL
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    if not isinstance(data, dict):
        return False
    ids = data.get("closeoutOnlyChapterIds") or []
    if not isinstance(ids, list) or chapter_id not in ids:
        return False
    data["closeoutOnlyChapterIds"] = [str(i) for i in ids if str(i) != chapter_id]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return True


def slice_product_on_main(repo: Path, *, slice_id: str, phase_plan: str) -> bool:
    from scripts.ppe_ide_product_ready import _product_touchset_on_main

    return _product_touchset_on_main(repo, slice_id=slice_id, plan_path=phase_plan)
