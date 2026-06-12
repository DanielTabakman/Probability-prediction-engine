"""Product-focus gate: validation report + urgent bypass (thin runtime layer).

Stewards use PRODUCT_FOCUS_PLAYBOOK_V1.md; BUILD agents get a 3-line excerpt only.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALIDATION_REPORT_REL = "docs/SOP/MSOS_P8_VALIDATION_REPORT_V1.md"
BACKLOG_REL = "docs/SOP/PHASE_CHAPTER_BACKLOG.json"
QUEUE_REL = "docs/SOP/PHASE_QUEUE.json"

NORTH_STAR = (
    "See what BTC options imply, where you disagree, and what payoff fits — in under 15 seconds."
)

TIER_DRIFT = {
    "P0": "Wedge proof / tester sessions — no platform expansion.",
    "P1": "Chartered chapter closeout only — stay sim-only.",
    "P2": "Lab legibility — no new assets or execution.",
    "P3": "Distribution — public URL / partners.",
    "P4": "Monetization signal — manual pilot only.",
    "defer": "Deferred — escalate if slice widens scope.",
}


def focus_gate_enabled() -> bool:
    env = os.environ.get("PPE_FOCUS_GATE", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return False
    if env in ("1", "true", "yes", "on"):
        return True
    return True


def _norm_plan(plan_path: str) -> str:
    return plan_path.replace("\\", "/").strip()


def _load_json(repo: Path, rel: str) -> dict[str, Any] | None:
    p = repo / rel.replace("\\", "/")
    if not p.is_file():
        return None
    import json

    return json.loads(p.read_text(encoding="utf-8-sig"))


def validation_report_status(repo: Path) -> str:
    """Return DRAFT | COMPLETE | MISSING."""
    p = repo / VALIDATION_REPORT_REL
    if not p.is_file():
        return "MISSING"
    text = p.read_text(encoding="utf-8", errors="replace")
    if re.search(r"\*\*Status:\*\*\s*\*\*COMPLETE\*\*", text, re.IGNORECASE):
        return "COMPLETE"
    if re.search(r"\*\*Status:\*\*\s*\*\*DRAFT\*\*", text, re.IGNORECASE):
        return "DRAFT"
    if "COMPLETE" in text[:800] and "DRAFT" not in text[:400]:
        return "COMPLETE"
    return "DRAFT"


def validation_report_blocks_selection(repo: Path) -> bool:
    if not focus_gate_enabled():
        return False
    return validation_report_status(repo) != "COMPLETE"


def _item_urgent(item: dict[str, Any]) -> bool:
    raw = item.get("urgent")
    if raw is True:
        return True
    if isinstance(raw, str) and raw.strip().lower() in ("1", "true", "yes", "on"):
        return True
    return False


def _tier_from_item(item: dict[str, Any]) -> str:
    tier = str(item.get("focusPlaybookTier") or "").strip()
    if tier:
        return tier
    reason = str(item.get("reason") or "")
    m = re.search(r"\[(P0|P1|P2|P3|P4|defer)\]", reason, re.IGNORECASE)
    if m:
        return m.group(1).upper() if m.group(1).lower() != "defer" else "defer"
    return "P2"


def backlog_item_for_plan(repo: Path, plan_path: str) -> dict[str, Any] | None:
    norm = _norm_plan(plan_path)
    backlog = _load_json(repo, BACKLOG_REL)
    if not backlog:
        return None
    for item in backlog.get("items") or []:
        if not isinstance(item, dict):
            continue
        if _norm_plan(str(item.get("planPath") or "")) == norm:
            return item
    return None


def queue_item_for_plan(repo: Path, plan_path: str) -> dict[str, Any] | None:
    norm = _norm_plan(plan_path)
    queue = _load_json(repo, QUEUE_REL)
    if not queue:
        return None
    for item in queue.get("items") or []:
        if not isinstance(item, dict):
            continue
        if _norm_plan(str(item.get("planPath") or "")) == norm:
            return item
    return None


def merged_item_meta(repo: Path, plan_path: str) -> dict[str, Any]:
    """Backlog fields win; queue may add urgent."""
    out: dict[str, Any] = {}
    q = queue_item_for_plan(repo, plan_path)
    b = backlog_item_for_plan(repo, plan_path)
    if q:
        out.update(q)
    if b:
        out.update(b)
    return out


@dataclass
class FocusGateResult:
    allowed: bool
    reason: str = ""
    urgent_bypass: bool = False
    tier: str = "P2"


def evaluate_focus_gate(repo: Path, plan_path: str) -> FocusGateResult:
    norm = _norm_plan(plan_path)
    meta = merged_item_meta(repo, norm)
    tier = _tier_from_item(meta)
    urgent = _item_urgent(meta)
    urgent_reason = str(meta.get("urgentReason") or "").strip()

    if not focus_gate_enabled():
        return FocusGateResult(allowed=True, tier=tier)

    if not validation_report_blocks_selection(repo):
        return FocusGateResult(allowed=True, tier=tier)

    if urgent:
        detail = urgent_reason or "urgent flag set on backlog/queue row"
        return FocusGateResult(
            allowed=True,
            reason=f"urgent bypass: {detail}",
            urgent_bypass=True,
            tier=tier,
        )

    status = validation_report_status(repo)
    return FocusGateResult(
        allowed=False,
        reason=(
            f"validation report {status} ({VALIDATION_REPORT_REL}); "
            "steward SELECTION or set urgent:true on backlog row"
        ),
        tier=tier,
    )


def format_ide_focus_block(*, tier: str, urgent_bypass: bool = False) -> str:
    drift = TIER_DRIFT.get(tier, TIER_DRIFT["P2"])
    urgent_line = "- **Urgent bypass:** yes (IRL override — log in reality checks).\n" if urgent_bypass else ""
    return "\n".join(
        [
            "## Focus (3 lines — do not widen scope)",
            "",
            f"- **North star:** {NORTH_STAR}",
            f"- **Playbook tier:** {tier} — {drift}",
            f"- **Drift:** If this slice adds assets, execution, or platform surface → stop and escalate.",
            urgent_line.rstrip(),
        ]
    ).strip() + "\n"


def focus_gate_skip_code() -> int:
    from scripts.ppe_operator_guards import GUARD_SKIP_CHAPTER

    return GUARD_SKIP_CHAPTER
