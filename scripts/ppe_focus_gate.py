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
P8_EVIDENCE_REL = "docs/SOP/MSOS_P8_TESTER_RELEASE_EVIDENCE_STATUS.md"
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


def focus_gate_enabled(repo: Path | None = None) -> bool:
    from scripts.ppe_operator_config import focus_gate_enabled as focus_gate_from_config

    if repo is not None:
        return focus_gate_from_config(repo.resolve())
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
    if not focus_gate_enabled(repo):
        return False
    return validation_report_status(repo) != "COMPLETE"


def _item_urgent(item: dict[str, Any]) -> bool:
    raw = item.get("urgent")
    if raw is True:
        return True
    if isinstance(raw, str) and raw.strip().lower() in ("1", "true", "yes", "on"):
        return True
    return False


def infer_focus_playbook_tier_from_reason(reason: str) -> str:
    """Map backlog/queue reason tags to playbook tier when focusPlaybookTier omitted."""
    text = str(reason or "")
    m = re.search(r"\[(P0|P1|P2|P3|P4|defer|LOW|MEDIUM|HIGH)\]", text, re.IGNORECASE)
    if not m:
        return "P2"
    tag = m.group(1).upper()
    if tag in ("P0", "P1", "P2", "P3", "P4"):
        return tag
    if tag in ("LOW", "MEDIUM"):
        return "P2"
    if tag == "HIGH":
        return "P1"
    return "P2"


def _tier_from_item(item: dict[str, Any]) -> str:
    tier = str(item.get("focusPlaybookTier") or "").strip()
    if tier:
        return tier
    return infer_focus_playbook_tier_from_reason(str(item.get("reason") or ""))


def _priority_from_item(item: dict[str, Any]) -> str:
    raw = str(item.get("priority") or "medium").strip().lower()
    return raw if raw in ("high", "medium", "low") else "medium"


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

    if tier.lower() == "defer":
        return FocusGateResult(
            allowed=False,
            reason="focusPlaybookTier Defer — steward SELECTION required before propagate",
            tier=tier,
        )

    if not focus_gate_enabled(repo):
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

    priority = _priority_from_item(meta)
    if tier == "P2" and priority == "low":
        return FocusGateResult(
            allowed=True,
            reason=(
                "P2 low-priority lab legibility — validation gate deferred "
                "(see BACKLOG_OPERATOR.md priority=low)"
            ),
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


def _p8_chapter_marked_complete(repo: Path) -> bool:
    p = repo / P8_EVIDENCE_REL
    if not p.is_file():
        return False
    head = p.read_text(encoding="utf-8", errors="replace")[:1200]
    return bool(re.search(r"\*\*Status:\*\*\s*\*\*COMPLETE\*\*", head, re.IGNORECASE))


def validation_report_gate_issues(repo: Path) -> list[str]:
    """Hard health issues: P8 evidence COMPLETE but validation report still blocks selection."""
    if not focus_gate_enabled(repo):
        return []
    if not _p8_chapter_marked_complete(repo):
        return []
    status = validation_report_status(repo)
    if status == "COMPLETE":
        return []
    return [
        "focus_gate: P8 evidence COMPLETE but "
        f"{VALIDATION_REPORT_REL} is {status} — complete §1–§5 and set **Status:** **COMPLETE** "
        "(see MSOS_P8_VALIDATION_REPORT_V1.md)"
    ]


def focus_gate_status_summary(repo: Path, plan_path: str | None = None) -> dict[str, Any]:
    """Machine-readable snapshot for operator status."""
    report = validation_report_status(repo)
    blocks = validation_report_blocks_selection(repo)
    out: dict[str, Any] = {
        "report_status": report,
        "blocks_selection": blocks,
        "enabled": focus_gate_enabled(repo),
        "issues": validation_report_gate_issues(repo),
    }
    if plan_path:
        result = evaluate_focus_gate(repo, plan_path)
        out["next_plan"] = _norm_plan(plan_path)
        out["next_allowed"] = result.allowed
        out["next_reason"] = result.reason
    return out
