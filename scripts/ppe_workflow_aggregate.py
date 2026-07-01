"""Aggregate workflow metrics — async/mobile operator mode (no session timers)."""

from __future__ import annotations

import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.workflow_metrics_cli import (
    SESSIONS_FILE,
    _append_jsonl,
    _metrics_dir,
    _parse_iso,
    _read_jsonl,
    _slices_in_days,
    _utc_now,
    read_context_windows,
)

PULSE_EVENTS = frozenset({"thread_pulse", "session_checkin"})


def _prompt_pulse_values(
    *,
    cognitive_load: int | None = None,
    notes: str | None = None,
    non_interactive: bool = False,
) -> tuple[int, str]:
    if non_interactive or not sys.stdin.isatty():
        return (cognitive_load if cognitive_load is not None else 3), (notes or "")
    print("\n--- Thread pulse (~15s; Enter = defaults) ---")
    raw_load = input("How heavy was this thread? 1 (easy) – 5 (heavy) [3]: ").strip()
    if raw_load:
        try:
            cognitive_load = max(1, min(5, int(raw_load)))
        except ValueError:
            cognitive_load = 3
    elif cognitive_load is None:
        cognitive_load = 3
    note = input("Optional note: ").strip()
    return cognitive_load, note or (notes or "")


def record_thread_pulse(
    repo: Path,
    *,
    cognitive_load: int | None = None,
    notes: str = "",
    non_interactive: bool = False,
    source: str = "manual",
) -> int:
    load, note = _prompt_pulse_values(
        cognitive_load=cognitive_load,
        notes=notes or None,
        non_interactive=non_interactive,
    )
    row = {
        "session_id": str(uuid.uuid4()),
        "event": "thread_pulse",
        "recorded_at": _utc_now(),
        "cognitive_load_1_5": load,
        "session_notes": note,
        "source": source,
    }
    _append_jsonl(_metrics_dir(repo) / SESSIONS_FILE, row)
    print(f"ppe_workflow_aggregate: thread_pulse load={load}/5")
    return 0


def _pulses_in_days(repo: Path, days: int) -> list[dict[str, Any]]:
    rows = _read_jsonl(_metrics_dir(repo) / SESSIONS_FILE)
    if days <= 0:
        return [r for r in rows if r.get("event") in PULSE_EVENTS]
    cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
    out: list[dict[str, Any]] = []
    for row in rows:
        if row.get("event") not in PULSE_EVENTS:
            continue
        ts = str(row.get("recorded_at") or row.get("ended_at") or "")
        t = _parse_iso(ts)
        if t and t.timestamp() >= cutoff:
            out.append(row)
    return out


def summarize_aggregate(repo: Path, *, days: int = 7) -> dict[str, Any]:
    slices = _slices_in_days(repo, days)
    pulses = _pulses_in_days(repo, days)
    weighted = sum(int(s.get("size_weight_actual") or 0) for s in slices)
    roundtrips = [int(s.get("roundtrips") or 0) for s in slices if s.get("roundtrips") is not None]
    avg_rt = sum(roundtrips) / len(roundtrips) if roundtrips else 0.0
    incidents = sum(1 for s in slices if s.get("incident_flag") in (True, "true", 1, "1"))
    load_vals = [int(p.get("cognitive_load_1_5") or 0) for p in pulses if p.get("cognitive_load_1_5")]
    avg_load = sum(load_vals) / len(load_vals) if load_vals else 0.0

    if days > 0:
        cutoff = datetime.now(timezone.utc).timestamp() - days * 86400
        closeouts = sum(
            1
            for row in read_context_windows(repo)
            if (t := _parse_iso(str(row.get("closed_at") or ""))) and t.timestamp() >= cutoff
        )
    else:
        closeouts = len(read_context_windows(repo))

    wspc = round(weighted / closeouts, 2) if closeouts > 0 else 0.0
    recent_pulses = [
        {
            "recorded_at": p.get("recorded_at"),
            "cognitive_load_1_5": p.get("cognitive_load_1_5"),
            "source": p.get("source"),
            "note": (p.get("session_notes") or "")[:80],
        }
        for p in reversed(pulses[-8:])
    ]

    return {
        "days": days,
        "mode": "aggregate",
        "slices_logged": len(slices),
        "weighted_slices": weighted,
        "avg_roundtrips_per_slice": round(avg_rt, 2),
        "incident_slices": incidents,
        "thread_pulses": len(pulses),
        "avg_cognitive_load": round(avg_load, 2),
        "context_closeouts": closeouts,
        "weighted_slices_per_closeout": wspc,
        "recent_pulses": recent_pulses,
    }


def print_aggregate_summary(repo: Path, *, days: int = 7) -> int:
    stats = summarize_aggregate(repo, days=days)
    print(f"workflow_metrics aggregate (last {days} days)")
    print(f"  slices_logged: {stats['slices_logged']}")
    print(f"  weighted_slices: {stats['weighted_slices']}")
    print(f"  weighted_slices_per_closeout: {stats['weighted_slices_per_closeout']}")
    print(f"  avg_roundtrips_per_slice: {stats['avg_roundtrips_per_slice']}")
    print(f"  incident_slices: {stats['incident_slices']}")
    print(f"  thread_pulses: {stats['thread_pulses']}")
    print(f"  avg_cognitive_load: {stats['avg_cognitive_load']}")
    print(f"  context_closeouts: {stats['context_closeouts']}")
    return 0
