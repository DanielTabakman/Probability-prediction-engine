"""Daily operator metrics: completions, loop uptime, intentional downtime."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

METRICS_REL = "artifacts/control_plane/OPERATOR_DAILY_METRICS.json"
_BLOCKED_VERDICTS = frozenset({"IDE_BUILD", "FIX_PLAN", "STALE_STATE", "ERROR"})


def metrics_path(repo: Path) -> Path:
    return repo / METRICS_REL


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _parse_utc(value: str) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _local_date(dt: datetime | None = None) -> str:
    return (dt or _utc_now()).astimezone().date().isoformat()


def _empty_day() -> dict[str, Any]:
    return {
        "runningSec": 0,
        "downSec": 0,
        "downIntentionalSec": 0,
        "downUnexpectedSec": 0,
        "blockedSec": 0,
        "slicesCompleted": [],
        "chaptersCompleted": [],
    }


def load_metrics(repo: Path) -> dict[str, Any]:
    path = metrics_path(repo)
    if not path.is_file():
        return {"version": 1, "days": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "days": {}}
    if not isinstance(data, dict):
        return {"version": 1, "days": {}}
    data.setdefault("version", 1)
    data.setdefault("days", {})
    return data


def save_metrics(repo: Path, data: dict[str, Any]) -> None:
    path = metrics_path(repo)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _day_bucket(data: dict[str, Any], local_date: str) -> dict[str, Any]:
    days = data.setdefault("days", {})
    if local_date not in days or not isinstance(days.get(local_date), dict):
        days[local_date] = _empty_day()
    day = days[local_date]
    day.setdefault("runningSec", 0)
    day.setdefault("downSec", 0)
    day.setdefault("downIntentionalSec", 0)
    day.setdefault("downUnexpectedSec", 0)
    day.setdefault("blockedSec", 0)
    day.setdefault("slicesCompleted", [])
    day.setdefault("chaptersCompleted", [])
    return day


def slice_kind(slice_id: str) -> str:
    lower = slice_id.lower()
    for kind in ("product", "control", "smoke", "closeout", "witness", "platform"):
        if kind in lower:
            return kind
    return "other"


def _down_intentional(*, maintenance_active: bool) -> bool:
    """Only explicit maintenance counts as intentional downtime."""
    return maintenance_active


def _apply_interval(
    day: dict[str, Any],
    *,
    seconds: float,
    loop_running: bool,
    verdict: str,
    maintenance_active: bool,
) -> None:
    sec = max(0.0, seconds)
    if sec <= 0:
        return
    if loop_running:
        day["runningSec"] = int(day.get("runningSec") or 0) + int(sec)
        if verdict in _BLOCKED_VERDICTS:
            day["blockedSec"] = int(day.get("blockedSec") or 0) + int(sec)
    else:
        day["downSec"] = int(day.get("downSec") or 0) + int(sec)
        if _down_intentional(maintenance_active=maintenance_active):
            day["downIntentionalSec"] = int(day.get("downIntentionalSec") or 0) + int(sec)
        else:
            day["downUnexpectedSec"] = int(day.get("downUnexpectedSec") or 0) + int(sec)


def _split_interval_across_days(
    data: dict[str, Any],
    *,
    start: datetime,
    end: datetime,
    loop_running: bool,
    verdict: str,
    maintenance_active: bool,
) -> None:
    if end <= start:
        return
    cursor = start
    while cursor < end:
        local = cursor.astimezone()
        day_start = local.replace(hour=0, minute=0, second=0, microsecond=0)
        next_day = day_start + timedelta(days=1)
        chunk_end = min(end, next_day.astimezone(timezone.utc))
        seconds = (chunk_end - cursor).total_seconds()
        _apply_interval(
            _day_bucket(data, local.date().isoformat()),
            seconds=seconds,
            loop_running=loop_running,
            verdict=verdict,
            maintenance_active=maintenance_active,
        )
        cursor = chunk_end


def record_watch_sample(
    repo: Path,
    *,
    loop_running: bool,
    verdict: str,
    now: datetime | None = None,
) -> None:
    """Accumulate loop uptime from mobile watch polls (~2 min granularity)."""
    repo = repo.resolve()
    now = now or _utc_now()
    data = load_metrics(repo)

    from scripts.ppe_operator_maintenance import is_maintenance_active

    maintenance_active = is_maintenance_active(repo, now)

    last_at_raw = str(data.get("lastSampleAt") or "")
    last_at = _parse_utc(last_at_raw)
    last_loop = bool(data.get("lastLoopRunning"))
    last_verdict = str(data.get("lastVerdict") or verdict)
    last_maintenance = bool(data.get("lastMaintenanceActive"))

    if last_at is not None:
        _split_interval_across_days(
            data,
            start=last_at,
            end=now,
            loop_running=last_loop,
            verdict=last_verdict,
            maintenance_active=last_maintenance,
        )

    data["lastSampleAt"] = now.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    data["lastLocalDate"] = _local_date(now)
    data["lastLoopRunning"] = loop_running
    data["lastVerdict"] = verdict
    data["lastMaintenanceActive"] = maintenance_active
    save_metrics(repo, data)


def _append_unique(items: list[dict[str, Any]], entry: dict[str, Any], *, key: str) -> None:
    value = str(entry.get(key) or "").strip()
    if not value:
        return
    if any(str(row.get(key) or "") == value for row in items if isinstance(row, dict)):
        return
    items.append(entry)


def record_slice_completed(
    repo: Path,
    *,
    slice_id: str,
    plan_path: str = "",
    at: datetime | None = None,
) -> None:
    repo = repo.resolve()
    sid = str(slice_id or "").strip()
    if not sid:
        return
    at = at or _utc_now()
    data = load_metrics(repo)
    day = _day_bucket(data, _local_date(at))
    slices = day.setdefault("slicesCompleted", [])
    _append_unique(
        slices,
        {
            "id": sid,
            "kind": slice_kind(sid),
            "planPath": plan_path.replace("\\", "/").strip(),
            "at": at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        key="id",
    )
    save_metrics(repo, data)


def record_chapter_completed(
    repo: Path,
    *,
    chapter_id: str,
    at: datetime | None = None,
) -> None:
    repo = repo.resolve()
    cid = str(chapter_id or "").strip()
    if not cid:
        return
    at = at or _utc_now()
    data = load_metrics(repo)
    day = _day_bucket(data, _local_date(at))
    chapters = day.setdefault("chaptersCompleted", [])
    _append_unique(
        chapters,
        {
            "id": cid,
            "at": at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        },
        key="id",
    )
    save_metrics(repo, data)


def format_duration(seconds: int) -> str:
    sec = max(0, int(seconds))
    hours, rem = divmod(sec, 3600)
    minutes, secs = divmod(rem, 60)
    if hours >= 1:
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"
    if minutes >= 1:
        return f"{minutes}m"
    return f"{secs}s"


def format_pct(part: int, whole: int) -> str:
    if whole <= 0:
        return "0%"
    return f"{int(round(100 * part / whole))}%"


def yesterday_local_date(now: datetime | None = None) -> str:
    now = now or _utc_now()
    return (now.astimezone().date() - timedelta(days=1)).isoformat()


def day_window_local(local_date: str) -> tuple[datetime, datetime]:
    """UTC bounds for one local calendar day (YYYY-MM-DD)."""
    tz = _utc_now().astimezone().tzinfo
    year, month, day = (int(x) for x in local_date.split("-"))
    start = datetime(year, month, day, 0, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def backfill_completions_from_sends(
    repo: Path,
    *,
    local_date: str,
    sends: list[dict[str, Any]],
) -> dict[str, Any]:
    """Merge slice/chapter done titles from ntfy send log into a day bucket."""
    day = _empty_day()
    start, end = day_window_local(local_date)
    for item in sends:
        title = str(item.get("title") or "")
        at = _parse_utc(str(item.get("at") or ""))
        if at is None or not (start <= at < end):
            continue
        lower = title.lower()
        if lower.startswith("ppe slice done:"):
            sid = title.split(":", 1)[-1].strip()
            _append_unique(
                day["slicesCompleted"],
                {"id": sid, "kind": slice_kind(sid), "planPath": "", "at": item.get("at", "")},
                key="id",
            )
        elif lower.startswith("ppe chapter done:"):
            cid = title.split(":", 1)[-1].strip()
            _append_unique(
                day["chaptersCompleted"],
                {"id": cid, "at": item.get("at", "")},
                key="id",
            )
    return day


def merge_day_metrics(primary: dict[str, Any], secondary: dict[str, Any]) -> dict[str, Any]:
    out = _empty_day()
    for key in ("runningSec", "downSec", "downIntentionalSec", "downUnexpectedSec", "blockedSec"):
        out[key] = max(int(primary.get(key) or 0), int(secondary.get(key) or 0))
    for row in (primary.get("slicesCompleted") or []) + (secondary.get("slicesCompleted") or []):
        if isinstance(row, dict):
            _append_unique(out["slicesCompleted"], row, key="id")
    for row in (primary.get("chaptersCompleted") or []) + (secondary.get("chaptersCompleted") or []):
        if isinstance(row, dict):
            _append_unique(out["chaptersCompleted"], row, key="id")
    return out


def backfill_completions_from_progress(repo: Path, *, local_date: str) -> dict[str, Any]:
    """When metrics ledger has no slice rows, infer from PHASE_SLICE_PROGRESS updated that day."""
    day = _empty_day()
    try:
        from scripts.ppe_phase_plan_window import load_progress
    except ImportError:
        return day

    progress = load_progress(repo.resolve())
    updated_at = _parse_utc(str(progress.get("updatedAt") or ""))
    if updated_at is None:
        return day
    if updated_at.astimezone().date().isoformat() != local_date:
        return day

    plan_path = str(progress.get("planPath") or "").replace("\\", "/").strip()
    for sid in progress.get("completedSliceIds") or []:
        slice_id = str(sid or "").strip()
        if not slice_id:
            continue
        _append_unique(
            day["slicesCompleted"],
            {
                "id": slice_id,
                "kind": slice_kind(slice_id),
                "planPath": plan_path,
                "at": progress.get("updatedAt", ""),
            },
            key="id",
        )
    return day


def uptime_pct(day_metrics: dict[str, Any]) -> float | None:
    running = int(day_metrics.get("runningSec") or 0)
    down = int(day_metrics.get("downSec") or 0)
    total = running + down
    if total <= 0:
        return None
    return 100.0 * running / total


def uptime_trend_line(repo: Path, local_date: str, *, sends: list[dict[str, Any]] | None = None) -> str | None:
    """Compare uptime % vs prior local calendar day."""
    try:
        prior_date = (datetime.fromisoformat(local_date).date() - timedelta(days=1)).isoformat()
    except ValueError:
        return None
    current = get_day_metrics(repo, local_date, sends=sends)
    prior = get_day_metrics(repo, prior_date, sends=sends)
    u1, u0 = uptime_pct(current), uptime_pct(prior)
    if u1 is None or u0 is None:
        return None
    delta = int(round(u1 - u0))
    return f"vs prior day: {delta:+d} pt uptime ({format_pct(int(current.get('runningSec') or 0), int(current.get('runningSec') or 0) + int(current.get('downSec') or 0))} vs {format_pct(int(prior.get('runningSec') or 0), int(prior.get('runningSec') or 0) + int(prior.get('downSec') or 0))})"


def get_day_metrics(repo: Path, local_date: str, *, sends: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    data = load_metrics(repo)
    stored = data.get("days", {}).get(local_date) or _empty_day()
    if not isinstance(stored, dict):
        stored = _empty_day()
    backfill = backfill_completions_from_sends(repo, local_date=local_date, sends=sends or [])
    merged = merge_day_metrics(stored, backfill)
    if not merged.get("slicesCompleted"):
        progress_backfill = backfill_completions_from_progress(repo, local_date=local_date)
        merged = merge_day_metrics(merged, progress_backfill)
    return merged
