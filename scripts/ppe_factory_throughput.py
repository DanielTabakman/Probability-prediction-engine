"""Factory throughput diagnostics — is the pipeline moving?

Canon: docs/SOP/FACTORY_THROUGHPUT_V1.md
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

FACTORY_THROUGHPUT_REL = "artifacts/control_plane/FACTORY_THROUGHPUT.json"
FACTORY_THROUGHPUT_STATE_REL = "artifacts/control_plane/FACTORY_THROUGHPUT_STATE.json"
AUTO_ADVANCE_STATE_REL = "artifacts/control_plane/FACTORY_AUTO_ADVANCE_STATE.json"
WEEKLY_DIGEST_STATE_REL = "artifacts/control_plane/FACTORY_WEEKLY_DIGEST_STATE.json"
FACTORY_THROUGHPUT_DOC = "docs/SOP/FACTORY_THROUGHPUT_V1.md"

VERDICT_MOVING = "moving"
VERDICT_IDLE_OK = "idle_ok"
VERDICT_STUCK = "stuck"
VERDICT_STACK_DOWN = "stack_down"

PHASE_STUCK_THRESHOLDS: dict[str, int] = {
    "BUILD_IN_FLIGHT": 2 * 3600,
    "FINISH_IN_FLIGHT": 3600,
    "RUN_LOCAL_PENDING": 4 * 3600,
    "CLOSEOUT_PENDING": 4 * 3600,
}

ZERO_THROUGHPUT_WARN_HOURS = 12
ZERO_THROUGHPUT_ALERT_HOURS = 24
AUTO_ADVANCE_COOLDOWN_SEC = 3600
AUTO_ADVANCE_MAX_PER_DAY = 3
AUTO_ADVANCE_MIN_STUCK_MINUTES = 30
SUPPLY_FORECAST_MIN_SLICES_PER_DAY = 0.25
WEEKLY_DIGEST_INTERVAL_HOURS = 168

Issue = dict[str, Any]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_utc(value: str | None) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _hours_since(dt: datetime | None) -> float | None:
    if dt is None:
        return None
    return max(0.0, (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _last_slice_completed(repo: Path) -> dict[str, Any] | None:
    try:
        from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _parse_iso, _read_jsonl

        rows = _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
        best: dict[str, Any] | None = None
        best_dt: datetime | None = None
        for row in rows:
            if not isinstance(row, dict):
                continue
            dt = _parse_iso(str(row.get("completed_at") or ""))
            if dt is None:
                continue
            if best_dt is None or dt > best_dt:
                best_dt = dt
                best = row
        if best is None or best_dt is None:
            return None
        return {
            "slice_id": best.get("slice_id"),
            "completed_at": best_dt.isoformat().replace("+00:00", "Z"),
            "hours_ago": round(_hours_since(best_dt) or 0.0, 2),
        }
    except Exception:
        return None


def _count_slices_hours(repo: Path, hours: int) -> int:
    from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _parse_iso, _read_jsonl

    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    return sum(
        1
        for row in _read_jsonl(_metrics_dir(repo) / SLICES_FILE)
        if (t := _parse_iso(str(row.get("completed_at") or ""))) and t.timestamp() >= cutoff
    )


def _count_closeouts_hours(repo: Path, hours: int) -> int:
    from scripts.workflow_metrics_cli import read_context_windows, _parse_iso

    cutoff = datetime.now(timezone.utc).timestamp() - hours * 3600
    return sum(
        1
        for row in read_context_windows(repo)
        if (t := _parse_iso(str(row.get("closed_at") or ""))) and t.timestamp() >= cutoff
    )


def _throughput_counts(repo: Path, *, hours: int) -> dict[str, Any]:
    slices = _count_slices_hours(repo, hours)
    closeouts = _count_closeouts_hours(repo, hours)
    weighted = slices
    wspc = 0.0
    try:
        from scripts.ppe_workflow_aggregate import summarize_aggregate

        days = max(1, (hours + 23) // 24)
        agg = summarize_aggregate(repo, days=days)
        weighted = int(agg.get("weighted_slices") or slices)
        wspc = float(agg.get("weighted_slices_per_closeout") or 0.0)
    except Exception:
        pass
    return {
        "slices": slices,
        "closeouts": closeouts,
        "weighted_slices": weighted,
        "weighted_slices_per_closeout": round(wspc, 2),
    }


def _stack_snapshot(repo: Path) -> dict[str, Any]:
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if not loop_host_start_allowed()[0]:
            return {
                "phase": None,
                "loop_running": None,
                "watch_running": None,
                "unknown": True,
                "reason": "desktop_not_loop_host",
            }
    except Exception:
        pass
    try:
        from scripts.ppe_autobuilder import collect_autobuilder_status

        ab = collect_autobuilder_status(repo)
        stack = ab.get("stack") if isinstance(ab.get("stack"), dict) else {}
        return {
            "phase": ab.get("phase"),
            "verdict": ab.get("verdict"),
            "recommended_action": ab.get("recommended_action"),
            "loop_running": stack.get("loop_running"),
            "watch_running": stack.get("watch_running"),
            "as_of": ab.get("as_of"),
            "unknown": False,
        }
    except Exception as exc:
        return {"error": str(exc), "loop_running": None, "watch_running": None, "unknown": True}


def _phase_age_with_trust(
    repo: Path,
    phase: str,
    *,
    stack: dict[str, Any] | None = None,
) -> tuple[float | None, bool, str | None]:
    stack = stack or {}
    on_desktop = bool(stack.get("unknown"))

    since = _load_json(repo / "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json")
    if str(since.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(since.get("since") or "")))
        if hrs is not None:
            return round(hrs * 60, 1), True, None

    mirror = _load_json(repo / "docs/SOP/VM_OPERATOR_PHASE.json")
    if str(mirror.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(mirror.get("as_of") or "")))
        if hrs is not None:
            stale_warn: str | None = None
            trusted = True
            if on_desktop:
                try:
                    from scripts.ppe_operator_vm_mirror_refresh import mirror_is_stale

                    if mirror_is_stale(mirror):
                        trusted = False
                        stale_warn = "VM mirror stale — phase age approximate"
                except Exception:
                    pass
            return round(hrs * 60, 1), trusted, stale_warn

    ab = _load_json(repo / "artifacts/orchestrator/AUTOBUILDER_STATUS.json")
    if str(ab.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(ab.get("as_of") or "")))
        if hrs is not None:
            return round(hrs * 60, 1), True, None
    return None, True, None


def _phase_age_minutes(repo: Path, phase: str, *, stack: dict[str, Any] | None = None) -> float | None:
    minutes, _, _ = _phase_age_with_trust(repo, phase, stack=stack)
    return minutes


def _slice_prefix(slice_id: str) -> str:
    parts = str(slice_id or "").split("-")
    if len(parts) >= 3:
        return "-".join(parts[:3])
    return str(slice_id or "")


def collect_chapter_throughput(repo: Path, status: dict[str, Any]) -> dict[str, Any]:
    plan_path = str(status.get("phase_plan_path") or "").replace("\\", "/").strip()
    chapter_name = str(status.get("chapter_name") or "").strip()
    chapter_id = ""
    if plan_path:
        try:
            from scripts.ppe_chapter_mode import plan_chapter_id

            chapter_id = plan_chapter_id(plan_path)
        except Exception:
            pass

    pending: list[str] = []
    if plan_path:
        try:
            from scripts.ppe_phase_plan_window import non_closeout_slices_pending

            pending = non_closeout_slices_pending(repo, plan_path)
        except Exception:
            pass

    prefix = _slice_prefix(pending[0]) if pending else ""
    if not prefix and plan_path:
        try:
            from scripts.ppe_manifest import load_phase_plan

            plan = load_phase_plan(repo, plan_path)
            for sl in plan.get("slices") or []:
                if isinstance(sl, dict) and sl.get("sliceId"):
                    prefix = _slice_prefix(str(sl["sliceId"]))
                    break
        except Exception:
            pass

    last_in_chapter: dict[str, Any] | None = None
    slices_in_chapter_7d = 0
    if prefix:
        try:
            from scripts.workflow_metrics_cli import SLICES_FILE, _metrics_dir, _parse_iso, _read_jsonl

            cutoff = datetime.now(timezone.utc).timestamp() - 7 * 86400
            for row in _read_jsonl(_metrics_dir(repo) / SLICES_FILE):
                sid = str(row.get("slice_id") or "")
                if not sid.startswith(prefix):
                    continue
                dt = _parse_iso(str(row.get("completed_at") or ""))
                if dt and dt.timestamp() >= cutoff:
                    slices_in_chapter_7d += 1
                if dt and (
                    last_in_chapter is None
                    or dt > _parse_utc(str(last_in_chapter.get("completed_at") or ""))
                ):
                    last_in_chapter = {
                        "slice_id": sid,
                        "completed_at": dt.isoformat().replace("+00:00", "Z"),
                        "hours_ago": round(_hours_since(dt) or 0.0, 2),
                    }
        except Exception:
            pass

    stall_hours = last_in_chapter.get("hours_ago") if last_in_chapter else None
    return {
        "chapter_id": chapter_id or None,
        "chapter_name": chapter_name or None,
        "plan_path": plan_path or None,
        "slice_prefix": prefix or None,
        "pending_slices": pending,
        "pending_count": len(pending),
        "slices_completed_7d": slices_in_chapter_7d,
        "last_slice_in_chapter": last_in_chapter,
        "stall_hours": stall_hours,
    }


def forecast_supply_days(supply: dict[str, Any], throughput_7d: dict[str, Any]) -> dict[str, Any]:
    ready = int(supply.get("queue_ready") or 0)
    queued = int(supply.get("backlog_queued") or 0)
    blocked = int(supply.get("backlog_blocked") or 0)
    pool = ready + queued + blocked
    slices_7d = int(throughput_7d.get("slices") or 0)
    slices_per_day = slices_7d / 7.0 if slices_7d > 0 else 0.0

    if supply.get("idle_risk") or pool == 0:
        return {
            "days_until_supply_low": 0.0,
            "slices_per_day": round(slices_per_day, 2),
            "supply_pool": pool,
            "at_risk": True,
            "note": "Already at or near supply idle",
        }
    if slices_per_day < SUPPLY_FORECAST_MIN_SLICES_PER_DAY:
        return {
            "days_until_supply_low": None,
            "slices_per_day": round(slices_per_day, 2),
            "supply_pool": pool,
            "at_risk": pool <= 3,
            "note": "Burn rate too low to forecast",
        }
    days = round(pool / slices_per_day, 1)
    return {
        "days_until_supply_low": days,
        "slices_per_day": round(slices_per_day, 2),
        "supply_pool": pool,
        "at_risk": days <= 3,
        "note": f"~{days}d at {slices_per_day:.1f} slices/day",
    }


def assess_supply_health(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    if status is None:
        status = {}
    supply = status.get("supply") if isinstance(status.get("supply"), dict) else {}
    backlog = supply.get("backlog") if isinstance(supply.get("backlog"), dict) else {}
    verdict = str(status.get("verdict") or "")
    queued = int(backlog.get("queued") or 0)
    blocked = int(backlog.get("blocked") or 0)
    ready = int(supply.get("queue_ready") or 0)
    idle_risk = verdict == "SUPPLY_LOW" or (ready == 0 and queued == 0 and blocked == 0)
    return {
        "queue_ready": ready,
        "backlog_queued": queued,
        "backlog_blocked": blocked,
        "verdict": verdict,
        "idle_risk": idle_risk,
        "next_promotable": supply.get("next_promotable_blocked"),
        "promote_reason": supply.get("promote_reason"),
    }


def detect_phase_stuck(repo: Path, phase: str, *, stack: dict[str, Any] | None = None) -> Issue | None:
    threshold = PHASE_STUCK_THRESHOLDS.get(phase)
    if not threshold:
        return None
    age_min, trusted, stale_warn = _phase_age_with_trust(repo, phase, stack=stack)
    if age_min is None:
        return None
    age_sec = age_min * 60
    if age_sec < threshold:
        return None
    hours = round(age_sec / 3600, 1)
    limit_h = round(threshold / 3600, 1)
    msg = f"Phase `{phase}` for ~{hours}h (limit {limit_h}h) — factory spinning, not shipping."
    if stale_warn:
        msg = f"{msg} ({stale_warn})"
    return {
        "code": "PHASE_STUCK",
        "severity": "high" if trusted else "medium",
        "message": msg,
        "fix": "VM: ppe_autobuilder.cmd advance or diagnose. Desktop: DESKTOP_CONTINUE when RUN_LOCAL due.",
        "phase": phase,
        "minutes_in_phase": age_min,
        "phase_age_trusted": trusted,
        "threshold_seconds": threshold,
    }


def maybe_auto_advance_stuck(repo: Path, throughput: dict[str, Any]) -> dict[str, Any]:
    """Loop host only: rate-limited ppe_autobuilder advance when stuck/stack_down."""
    result: dict[str, Any] = {"attempted": False, "skipped": True}
    try:
        from scripts.ppe_loop_host_guard import loop_host_start_allowed

        if not loop_host_start_allowed()[0]:
            result["reason"] = "not_loop_host"
            return result
    except Exception:
        result["reason"] = "loop_host_check_failed"
        return result

    verdict = str(throughput.get("verdict") or "")
    if verdict not in (VERDICT_STUCK, VERDICT_STACK_DOWN):
        result["reason"] = f"verdict={verdict}"
        return result

    phase_min = throughput.get("phase_minutes")
    if verdict == VERDICT_STUCK and (
        not isinstance(phase_min, (int, float)) or phase_min < AUTO_ADVANCE_MIN_STUCK_MINUTES
    ):
        result["reason"] = "below_min_stuck_minutes"
        return result

    state = _load_json(repo / AUTO_ADVANCE_STATE_REL)
    last_at = _parse_utc(str(state.get("last_advance_at") or ""))
    if last_at is not None:
        elapsed = (datetime.now(timezone.utc) - last_at).total_seconds()
        if elapsed < AUTO_ADVANCE_COOLDOWN_SEC:
            result["reason"] = f"cooldown ({int(AUTO_ADVANCE_COOLDOWN_SEC - elapsed)}s left)"
            return result

    day_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count_today = int(state.get("count_today") or 0)
    count_day = _parse_utc(str(state.get("count_day") or ""))
    if count_day is None or count_day < day_start:
        count_today = 0

    if count_today >= AUTO_ADVANCE_MAX_PER_DAY:
        result["reason"] = "daily_cap"
        return result

    try:
        from scripts.ppe_autobuilder import action_advance

        advance_result = action_advance(repo)
        result = {
            "attempted": True,
            "skipped": bool(advance_result.get("skipped")),
            "action": advance_result.get("action"),
            "phase": advance_result.get("phase"),
            "reason": advance_result.get("reason"),
        }
        state = {
            "last_advance_at": _utc_now(),
            "count_today": count_today + 1,
            "count_day": day_start.isoformat().replace("+00:00", "Z"),
            "last_verdict": verdict,
            "last_result": advance_result,
        }
        path = repo / AUTO_ADVANCE_STATE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except Exception as exc:
        result = {"attempted": True, "skipped": True, "error": str(exc)}
    return result


def maybe_notify_weekly_rollup(repo: Path, throughput: dict[str, Any]) -> bool:
    """Weekly ntfy digest of factory throughput (7d stats)."""
    prev = _load_json(repo / WEEKLY_DIGEST_STATE_REL)
    last_sent = _parse_utc(str(prev.get("last_sent_at") or ""))
    if last_sent is not None and (_hours_since(last_sent) or 0) < WEEKLY_DIGEST_INTERVAL_HOURS:
        return False

    t7 = throughput.get("throughput_7d") if isinstance(throughput.get("throughput_7d"), dict) else {}
    sla = throughput.get("weighted_sla") if isinstance(throughput.get("weighted_sla"), dict) else {}
    chapter = throughput.get("chapter") if isinstance(throughput.get("chapter"), dict) else {}
    forecast = throughput.get("supply_forecast") if isinstance(throughput.get("supply_forecast"), dict) else {}

    lines = [
        f"7d: {t7.get('slices', 0)} slices, {t7.get('closeouts', 0)} closeouts",
        f"Weighted: {sla.get('weighted_slices_7d', 0)} (wspc={sla.get('weighted_slices_per_closeout_7d', 0)})",
        f"Factory verdict: {throughput.get('verdict')}",
    ]
    if chapter.get("chapter_id"):
        lines.append(
            f"Active chapter: {chapter['chapter_id']} ({chapter.get('pending_count', 0)} pending)"
        )
    if forecast.get("note"):
        lines.append(f"Supply: {forecast['note']}")

    try:
        from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

        if not (notify_enabled() and ntfy_configured()):
            return False
        sent = send_ntfy(
            "PPE factory weekly rollup",
            "\n".join(lines),
            tags=["ppe", "factory", "weekly"],
            priority="low",
        )
    except Exception:
        return False

    if sent:
        path = repo / WEEKLY_DIGEST_STATE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"last_sent_at": _utc_now(), "lines": lines}, indent=2) + "\n",
            encoding="utf-8",
        )
    return sent


def assess_factory_throughput(
    repo: Path,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo = repo.resolve()
    if status is None:
        try:
            from scripts.ppe_operator_status import prepare_operator_status

            status = prepare_operator_status(repo)
        except Exception:
            status = {}

    stack = _stack_snapshot(repo)
    phase = str(stack.get("phase") or "")
    operator_verdict = str(status.get("verdict") or stack.get("verdict") or "")

    last_slice = _last_slice_completed(repo)
    t24 = _throughput_counts(repo, hours=24)
    t7d = _throughput_counts(repo, hours=168)
    supply = assess_supply_health(repo, status)
    chapter = collect_chapter_throughput(repo, status)
    supply_forecast = forecast_supply_days(supply, t7d)
    phase_min, phase_trusted, _ = _phase_age_with_trust(repo, phase, stack=stack) if phase else (None, True, None)

    issues: list[Issue] = []
    loop_ok = bool(stack.get("loop_running")) and bool(stack.get("watch_running"))
    unknown_stack = bool(stack.get("unknown")) or (
        stack.get("loop_running") is None and stack.get("watch_running") is None
    )
    stack_down = phase == "STACK_DOWN" or (not unknown_stack and not loop_ok)

    if stack_down and not unknown_stack:
        issues.append(
            {
                "code": "STACK_DOWN",
                "severity": "high",
                "message": "VM loop or watch not running — factory is down.",
                "fix": "VM: VM_RESTART.cmd or ppe_autobuilder.cmd ensure",
            }
        )

    phase_stuck = detect_phase_stuck(repo, phase, stack=stack) if phase and not unknown_stack else None
    if phase_stuck:
        issues.append(phase_stuck)

    if (
        chapter.get("pending_count")
        and chapter.get("stall_hours") is not None
        and float(chapter["stall_hours"]) >= 24
    ):
        issues.append(
            {
                "code": "CHAPTER_STALL",
                "severity": "medium",
                "message": (
                    f"Chapter `{chapter.get('chapter_id') or chapter.get('chapter_name')}` — "
                    f"no slice in {chapter['stall_hours']:.0f}h ({chapter.get('pending_count')} pending)."
                ),
                "fix": "ppe_autobuilder.cmd advance on VM.",
            }
        )

    hours_since_slice = last_slice.get("hours_ago") if last_slice else None
    moving = (t24.get("slices") or 0) > 0 or (t24.get("closeouts") or 0) > 0
    idle_ok = operator_verdict == "SUPPLY_LOW" or phase == "HEALTHY_IDLE"

    if not stack_down and not moving and not idle_ok and not unknown_stack:
        hrs = float(hours_since_slice or 999)
        if hrs >= ZERO_THROUGHPUT_ALERT_HOURS:
            issues.append(
                {
                    "code": "ZERO_THROUGHPUT_24H",
                    "severity": "high",
                    "message": f"No slices/closeouts in 24h — last slice {hrs:.0f}h ago.",
                    "fix": "ppe_autobuilder.cmd diagnose && advance",
                }
            )
        elif hrs >= ZERO_THROUGHPUT_WARN_HOURS:
            issues.append(
                {
                    "code": "ZERO_THROUGHPUT_12H",
                    "severity": "medium",
                    "message": f"Throughput low — last slice {hrs:.0f}h ago.",
                    "fix": "ppe_pipeline_health.cmd",
                }
            )

    if supply_forecast.get("at_risk") and not supply.get("idle_risk"):
        days_left = supply_forecast.get("days_until_supply_low")
        if days_left is not None and days_left <= 7:
            issues.append(
                {
                    "code": "SUPPLY_FORECAST_LOW",
                    "severity": "medium" if days_left > 3 else "high",
                    "message": f"Supply forecast: ~{days_left}d until queue exhausted.",
                    "fix": "Charter/promote next chapter.",
                }
            )

    if supply.get("idle_risk") and operator_verdict != "SUPPLY_LOW":
        issues.append(
            {
                "code": "SUPPLY_STARVATION_RISK",
                "severity": "medium",
                "message": f"Queue READY={supply.get('queue_ready')} — supply may idle factory soon.",
                "fix": "Promote PHASE_CHAPTER_BACKLOG.",
            }
        )

    if stack_down and not unknown_stack:
        verdict = VERDICT_STACK_DOWN
    elif idle_ok and not issues:
        verdict = VERDICT_IDLE_OK
    elif moving and not any(i.get("code") == "PHASE_STUCK" for i in issues):
        verdict = VERDICT_MOVING
    elif issues and not unknown_stack:
        verdict = VERDICT_STUCK
    elif moving:
        verdict = VERDICT_MOVING
    elif unknown_stack:
        verdict = VERDICT_MOVING if moving else VERDICT_IDLE_OK
    else:
        verdict = VERDICT_IDLE_OK

    top = issues[0] if issues else None
    commands = [str(top["fix"])] if top and top.get("fix") else []

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "ok": verdict in (VERDICT_MOVING, VERDICT_IDLE_OK),
        "stack": {**stack, "unknown": unknown_stack},
        "phase": phase,
        "phase_minutes": phase_min,
        "phase_age_trusted": phase_trusted,
        "operator_verdict": operator_verdict,
        "last_slice": last_slice,
        "throughput_24h": t24,
        "throughput_7d": t7d,
        "weighted_sla": {
            "weighted_slices_7d": t7d.get("weighted_slices"),
            "weighted_slices_per_closeout_7d": t7d.get("weighted_slices_per_closeout"),
        },
        "chapter": chapter,
        "supply": supply,
        "supply_forecast": supply_forecast,
        "issues": issues,
        "top_issue": top,
        "top_issue_code": str(top.get("code") or "") if top else None,
        "top_issue_message": str(top.get("message") or "") if top else None,
        "commands": commands[:3],
        "blocks_advance": verdict == VERDICT_STACK_DOWN,
        "docs": [FACTORY_THROUGHPUT_DOC, "docs/SOP/PPE_AUTOBUILDER_V1.md"],
    }


def write_factory_throughput(repo: Path, payload: dict[str, Any]) -> Path:
    out = repo / FACTORY_THROUGHPUT_REL
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out


def format_throughput_lines(throughput: dict[str, Any]) -> list[str]:
    verdict = throughput.get("verdict") or "?"
    t24 = throughput.get("throughput_24h") if isinstance(throughput.get("throughput_24h"), dict) else {}
    phase = throughput.get("phase") or "?"
    phase_min = throughput.get("phase_minutes")
    trusted = throughput.get("phase_age_trusted", True)
    phase_s = f"{phase}" + (f" ({phase_min:.0f}m)" if isinstance(phase_min, (int, float)) else "")
    if trusted is False:
        phase_s += " ~mirror"
    wspc = (throughput.get("weighted_sla") or {}).get("weighted_slices_per_closeout_7d")
    wspc_s = f" · wspc7d={wspc}" if wspc else ""
    lines = [
        f"**FACTORY:** `{verdict}` — phase `{phase_s}` · "
        f"24h: {t24.get('slices', 0)} slices, {t24.get('closeouts', 0)} closeouts{wspc_s}",
    ]
    chapter = throughput.get("chapter") if isinstance(throughput.get("chapter"), dict) else {}
    if chapter.get("chapter_id") and chapter.get("pending_count"):
        stall = chapter.get("stall_hours")
        stall_s = f", last slice {stall:.0f}h ago" if isinstance(stall, (int, float)) else ""
        lines.append(
            f"**CHAPTER:** `{chapter['chapter_id']}` — {chapter['pending_count']} pending{stall_s}"
        )
    if throughput.get("top_issue_message"):
        lines.append(f"  → {throughput['top_issue_message']}")
    supply = throughput.get("supply") if isinstance(throughput.get("supply"), dict) else {}
    forecast = throughput.get("supply_forecast") if isinstance(throughput.get("supply_forecast"), dict) else {}
    if supply.get("queue_ready") is not None:
        fc = ""
        if forecast.get("days_until_supply_low") is not None:
            fc = f" · ~{forecast['days_until_supply_low']}d supply"
        lines.append(
            f"**SUPPLY:** READY={supply.get('queue_ready')} "
            f"queued={supply.get('backlog_queued')} blocked={supply.get('backlog_blocked')}{fc}"
        )
    return lines


def format_founder_throughput_report(throughput: dict[str, Any]) -> str:
    lines = ["Factory throughput", ""]
    lines.append(f"Verdict: {throughput.get('verdict')}")
    t24 = throughput.get("throughput_24h") or {}
    t7 = throughput.get("throughput_7d") or {}
    sla = throughput.get("weighted_sla") or {}
    lines.append(
        f"24h: slices={t24.get('slices', 0)} closeouts={t24.get('closeouts', 0)} | "
        f"7d: slices={t7.get('slices', 0)} weighted={sla.get('weighted_slices_7d', 0)} "
        f"wspc={sla.get('weighted_slices_per_closeout_7d', 0)}"
    )
    chapter = throughput.get("chapter") or {}
    if chapter.get("chapter_id"):
        lines.append(
            f"Chapter: {chapter['chapter_id']} pending={chapter.get('pending_count', 0)} "
            f"7d_slices={chapter.get('slices_completed_7d', 0)}"
        )
    forecast = throughput.get("supply_forecast") or {}
    if forecast.get("note"):
        lines.append(f"Supply forecast: {forecast['note']}")
    if throughput.get("top_issue_message"):
        lines.append(f"Issue: {throughput['top_issue_message']}")
    cmds = throughput.get("commands") or []
    if cmds:
        lines.append(f"Fix: {cmds[0]}")
    lines.append("")
    lines.append("OK" if throughput.get("ok") else "ACTION NEEDED")
    return "\n".join(lines)


def _load_state(repo: Path) -> dict[str, Any]:
    return _load_json(repo / FACTORY_THROUGHPUT_STATE_REL)


def _write_state(repo: Path, state: dict[str, Any]) -> None:
    path = repo / FACTORY_THROUGHPUT_STATE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def maybe_notify_throughput_regression(repo: Path, throughput: dict[str, Any]) -> bool:
    prev = _load_state(repo)
    prev_verdict = str(prev.get("verdict") or "")
    now_verdict = str(throughput.get("verdict") or "")
    prev_ok = bool(prev.get("ok"))
    now_ok = bool(throughput.get("ok"))

    should = False
    title = "PPE factory throughput"
    body_parts: list[str] = []

    if prev_ok and not now_ok:
        should = True
        title = f"PPE factory: {now_verdict}"
        body_parts.append(f"Was {prev_verdict} → now {now_verdict}")
    elif now_verdict in (VERDICT_STUCK, VERDICT_STACK_DOWN) and now_verdict != prev_verdict:
        should = True
        title = f"PPE factory: {now_verdict}"
        body_parts.append(str(throughput.get("top_issue_message") or now_verdict))

    top_code = throughput.get("top_issue_code")
    if top_code in ("ZERO_THROUGHPUT_24H", "PHASE_STUCK", "STACK_DOWN", "CHAPTER_STALL"):
        last_alert = _parse_utc(str(prev.get("last_alert_at") or ""))
        if last_alert is None or (_hours_since(last_alert) or 0) >= 12:
            if not should:
                should = True
                title = f"PPE factory: {top_code}"
            body_parts.append(str(throughput.get("top_issue_message") or top_code))

    state = {
        "as_of": _utc_now(),
        "verdict": now_verdict,
        "ok": now_ok,
        "top_issue_code": top_code,
    }
    if should:
        state["last_alert_at"] = _utc_now()
        cmds = throughput.get("commands") or []
        if cmds:
            body_parts.append(f"Fix: {cmds[0]}")
        try:
            from scripts.ppe_notify_push import ntfy_configured, notify_enabled, send_ntfy

            if notify_enabled() and ntfy_configured():
                send_ntfy(
                    title,
                    "\n".join(body_parts),
                    tags=["ppe", "factory", now_verdict],
                    priority="high" if now_verdict == VERDICT_STACK_DOWN else "default",
                )
        except Exception:
            should = False
    else:
        state["last_alert_at"] = prev.get("last_alert_at")

    _write_state(repo, state)
    maybe_notify_weekly_rollup(repo, throughput)
    return should


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Factory throughput diagnostic")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--notify", action="store_true")
    ap.add_argument("--auto-advance", action="store_true", help="Loop host: auto-advance when stuck")
    ap.add_argument("--no-status", action="store_true")
    args = ap.parse_args(argv)

    repo = args.repo_root.resolve()
    status = None
    if not args.no_status:
        from scripts.ppe_operator_status import prepare_operator_status

        status = prepare_operator_status(repo)

    payload = assess_factory_throughput(repo, status)
    if args.write:
        path = write_factory_throughput(repo, payload)
        if not args.json:
            print(f"ppe_factory_throughput: wrote {path.relative_to(repo)}")

    if args.auto_advance:
        adv = maybe_auto_advance_stuck(repo, payload)
        payload["auto_advance"] = adv
        if not args.json:
            print(f"ppe_factory_throughput: auto_advance={adv}")

    if args.notify:
        maybe_notify_throughput_regression(repo, payload)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_founder_throughput_report(payload))

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
