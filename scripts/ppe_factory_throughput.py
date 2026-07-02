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
FACTORY_THROUGHPUT_DOC = "docs/SOP/FACTORY_THROUGHPUT_V1.md"

VERDICT_MOVING = "moving"
VERDICT_IDLE_OK = "idle_ok"
VERDICT_STUCK = "stuck"
VERDICT_STACK_DOWN = "stack_down"

# Phase stuck thresholds (seconds) for desktop diagnostic.
PHASE_STUCK_THRESHOLDS: dict[str, int] = {
    "BUILD_IN_FLIGHT": 2 * 3600,
    "FINISH_IN_FLIGHT": 3600,
    "RUN_LOCAL_PENDING": 4 * 3600,
    "CLOSEOUT_PENDING": 4 * 3600,
}

ZERO_THROUGHPUT_WARN_HOURS = 12
ZERO_THROUGHPUT_ALERT_HOURS = 24

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


def _throughput_counts(repo: Path, *, hours: int) -> dict[str, int]:
    slices = _count_slices_hours(repo, hours)
    closeouts = _count_closeouts_hours(repo, hours)
    return {
        "slices": slices,
        "closeouts": closeouts,
        "weighted_slices": slices,
    }


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


def _phase_age_minutes(repo: Path, phase: str) -> float | None:
    since_path = repo / "artifacts/control_plane/VM_IN_FLIGHT_SINCE.json"
    since = _load_json(since_path)
    if str(since.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(since.get("since") or "")))
        if hrs is not None:
            return round(hrs * 60, 1)

    mirror = _load_json(repo / "docs/SOP/VM_OPERATOR_PHASE.json")
    if str(mirror.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(mirror.get("as_of") or "")))
        if hrs is not None:
            return round(hrs * 60, 1)

    ab_path = repo / "artifacts/orchestrator/AUTOBUILDER_STATUS.json"
    ab = _load_json(ab_path)
    if str(ab.get("phase") or "") == phase:
        hrs = _hours_since(_parse_utc(str(ab.get("as_of") or "")))
        if hrs is not None:
            return round(hrs * 60, 1)
    return None


def assess_supply_health(repo: Path, status: dict[str, Any] | None = None) -> dict[str, Any]:
    if status is None:
        try:
            from scripts.ppe_operator_status import prepare_operator_status

            status = prepare_operator_status(repo)
        except Exception:
            status = {}

    supply = status.get("supply") if isinstance(status.get("supply"), dict) else {}
    backlog = supply.get("backlog") if isinstance(supply.get("backlog"), dict) else {}
    next_promo = supply.get("next_promotable_blocked")
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
        "next_promotable": next_promo if isinstance(next_promo, dict) else None,
        "promote_reason": supply.get("promote_reason"),
    }


def detect_phase_stuck(repo: Path, phase: str) -> Issue | None:
    threshold = PHASE_STUCK_THRESHOLDS.get(phase)
    if not threshold:
        return None
    age_min = _phase_age_minutes(repo, phase)
    if age_min is None:
        return None
    age_sec = age_min * 60
    if age_sec < threshold:
        return None
    hours = round(age_sec / 3600, 1)
    limit_h = round(threshold / 3600, 1)
    return {
        "code": "PHASE_STUCK",
        "severity": "high",
        "message": f"Phase `{phase}` for ~{hours}h (limit {limit_h}h) — factory spinning, not shipping.",
        "fix": "VM: ppe_autobuilder.cmd advance or diagnose. Desktop: DESKTOP_CONTINUE when RUN_LOCAL due.",
        "phase": phase,
        "minutes_in_phase": age_min,
        "threshold_seconds": threshold,
    }


def assess_factory_throughput(
    repo: Path,
    status: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Throughput + stack + supply snapshot."""
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

    phase_stuck = detect_phase_stuck(repo, phase) if phase and not unknown_stack else None
    if phase_stuck:
        issues.append(phase_stuck)

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
                    "fix": "ppe_autobuilder.cmd diagnose && advance; check pipeline health ROOT CAUSE.",
                }
            )
        elif hrs >= ZERO_THROUGHPUT_WARN_HOURS:
            issues.append(
                {
                    "code": "ZERO_THROUGHPUT_12H",
                    "severity": "medium",
                    "message": f"Throughput low — no completions in 24h; last slice {hrs:.0f}h ago.",
                    "fix": "Review OPERATOR_STATUS + ppe_pipeline_health.cmd",
                }
            )

    if supply.get("idle_risk") and operator_verdict != "SUPPLY_LOW":
        issues.append(
            {
                "code": "SUPPLY_STARVATION_RISK",
                "severity": "medium",
                "message": f"Queue READY={supply.get('queue_ready')} — supply may idle factory soon.",
                "fix": "Promote PHASE_CHAPTER_BACKLOG or charter next chapter.",
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
    commands: list[str] = []
    if top and top.get("fix"):
        commands.append(str(top["fix"]))

    return {
        "as_of": _utc_now(),
        "verdict": verdict,
        "ok": verdict in (VERDICT_MOVING, VERDICT_IDLE_OK),
        "stack": {**stack, "unknown": unknown_stack},
        "phase": phase,
        "phase_minutes": _phase_age_minutes(repo, phase) if phase else None,
        "operator_verdict": operator_verdict,
        "last_slice": last_slice,
        "throughput_24h": t24,
        "throughput_7d": t7d,
        "supply": supply,
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
    """Compact lines for OPERATOR_STATUS / pipeline health block."""
    verdict = throughput.get("verdict") or "?"
    t24 = throughput.get("throughput_24h") if isinstance(throughput.get("throughput_24h"), dict) else {}
    phase = throughput.get("phase") or "?"
    phase_min = throughput.get("phase_minutes")
    phase_s = f"{phase}" + (f" ({phase_min:.0f}m)" if isinstance(phase_min, (int, float)) else "")
    lines = [
        f"**FACTORY:** `{verdict}` — phase `{phase_s}` · "
        f"24h: {t24.get('slices', 0)} slices, {t24.get('closeouts', 0)} closeouts",
    ]
    if throughput.get("top_issue_message"):
        lines.append(f"  → {throughput['top_issue_message']}")
    supply = throughput.get("supply") if isinstance(throughput.get("supply"), dict) else {}
    if supply.get("queue_ready") is not None:
        lines.append(
            f"**SUPPLY:** READY={supply.get('queue_ready')} "
            f"queued={supply.get('backlog_queued')} blocked={supply.get('backlog_blocked')}"
        )
    return lines


def format_founder_throughput_report(throughput: dict[str, Any]) -> str:
    lines = ["Factory throughput", ""]
    lines.append(f"Verdict: {throughput.get('verdict')}")
    stack = throughput.get("stack") if isinstance(throughput.get("stack"), dict) else {}
    lines.append(
        f"Stack: loop={stack.get('loop_running')} watch={stack.get('watch_running')} phase={stack.get('phase')}"
    )
    t24 = throughput.get("throughput_24h") or {}
    t7 = throughput.get("throughput_7d") or {}
    lines.append(
        f"24h: slices={t24.get('slices', 0)} closeouts={t24.get('closeouts', 0)} | "
        f"7d: slices={t7.get('slices', 0)} closeouts={t7.get('closeouts', 0)}"
    )
    last = throughput.get("last_slice")
    if last:
        lines.append(f"Last slice: {last.get('slice_id')} ({last.get('hours_ago')}h ago)")
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
    """ntfy when factory drops to stuck/stack_down or zero throughput alert."""
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
    if top_code in ("ZERO_THROUGHPUT_24H", "PHASE_STUCK", "STACK_DOWN"):
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
    return should


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Factory throughput diagnostic")
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--notify", action="store_true")
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

    if args.notify:
        maybe_notify_throughput_regression(repo, payload)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(format_founder_throughput_report(payload))

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
