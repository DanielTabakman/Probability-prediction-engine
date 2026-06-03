"""Advisory context-band heuristics (WORKFLOW_CONTEXT_AUDIT_001)."""

from __future__ import annotations

from typing import Literal

Band = Literal["NORMAL", "WATCH", "ESCALATE"]

WATCH_LINE_THRESHOLD = 200
ESCALATE_LINE_THRESHOLD = 400

_BAND_RANK = {"NORMAL": 0, "WATCH": 1, "ESCALATE": 2}


def classify_line_count(line_count: int) -> Band:
    if line_count > ESCALATE_LINE_THRESHOLD:
        return "ESCALATE"
    if line_count > WATCH_LINE_THRESHOLD:
        return "WATCH"
    return "NORMAL"


def worst_band(*bands: str) -> Band:
    if not bands:
        return "NORMAL"
    return max(bands, key=lambda b: _BAND_RANK.get(b, 0))  # type: ignore[return-value]


def advisory_actions(band: str) -> list[str]:
    if band == "ESCALATE":
        return [
            "Split the slice or shrink the sprint spec before BUILD.",
            "Prune handoff ledger; link paths instead of inlining specs.",
            "Prefer a new Cursor thread with IDE_BUILD_STARTER only.",
            "Consider CONTROL-PLANE interlude to compress overhead.",
        ]
    if band == "WATCH":
        return [
            "Prefer LOAD-ON-DEMAND SOP reads.",
            "Trim the handoff packet; cap retries explicitly.",
            "Record context_band: WATCH in closeout note.",
        ]
    return []


def score_text(text: str) -> dict[str, object]:
    line_count = len(text.splitlines())
    band = classify_line_count(line_count)
    triggers: list[str] = []
    if band == "ESCALATE":
        triggers.append(f"line_count>{ESCALATE_LINE_THRESHOLD}")
    elif band == "WATCH":
        triggers.append(f"line_count>{WATCH_LINE_THRESHOLD}")
    return {
        "line_count": line_count,
        "band": band,
        "triggers": triggers,
        "advisory_actions": advisory_actions(band),
    }


def score_build_packet(text: str) -> dict[str, object]:
    return score_text(text)


def format_band_hint(band: str, *, subject: str = "sprint spec") -> str:
    if band == "ESCALATE":
        return f"ESCALATE ({subject} line count > {ESCALATE_LINE_THRESHOLD} — prefer links over inline paste)"
    if band == "WATCH":
        return f"WATCH ({subject} line count > {WATCH_LINE_THRESHOLD})"
    return "NORMAL"


def file_line_count(repo_root, rel_path: str) -> int | None:
    from pathlib import Path

    p = Path(repo_root) / rel_path.replace("\\", "/")
    if not p.is_file():
        return None
    return len(p.read_text(encoding="utf-8", errors="replace").splitlines())
