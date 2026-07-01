"""Thread role copy and helpers for Cursor openers and operator artifacts."""

from __future__ import annotations

from typing import Any

ROLE_OPERATOR = "operator"
ROLE_CHARTER = "charter"
ROLE_IDE_BUILD = "ide_build"
ROLE_RECOVERY = "recovery"
ROLE_EXPLORE = "explore"

VALID_THREAD_ROLES = frozenset({ROLE_OPERATOR, ROLE_CHARTER, ROLE_IDE_BUILD, ROLE_RECOVERY, ROLE_EXPLORE})

LEGACY_THREAD_ROLE_MAP = {
    "steward": ROLE_CHARTER,
    "exploratory": ROLE_CHARTER,
    "topic": ROLE_CHARTER,
    "neutral": ROLE_EXPLORE,
}

# Parked-item lanes — use when triaging mixed handoff lists (charter threads).
PARKED_LANE_CONTROL = "control_plane"
PARKED_LANE_RELAY = "relay"
PARKED_LANE_HUMAN = "human"

_RELAY_PARKED_HINTS = (
    "desktop_continue",
    "run_ppe_local",
    "finish_ide_build",
    "closeout_only",
    "ide_build",
    "relay",
    "spine closeout",
    "vm ",
    "operator_status",
    "burst",
    "ppe_go",
    "mark_ide_product_ready",
)
_CONTROL_PARKED_HINTS = (
    "merge pr",
    "delegation",
    "tracking hub",
    "stash",
    "dirty tree",
    "control-plane",
    "docs/sop",
    ".cursor/rules",
    "policy",
    "backlog",
    "triggered_ideas",
    "human_steward",
)

OPERATOR_THREAD_OPENER = (
    "Operator thread. THREAD_ROLE: operator.\n"
    "Run what's next per ppe-operator-core (burst + @ppe-director when allowed).\n"
)

IDE_BUILD_THREAD_OPENER = (
    "IDE BUILD thread. THREAD_ROLE: ide_build.\n"
    "Load only the starter file below. Do not read OPERATOR_STATUS.\n"
)

CHARTER_THREAD_OPENER = (
    "Charter thread. THREAD_ROLE: charter.\n"
    "Do NOT read OPERATOR_STATUS or run relay/burst.\n"
)

THREAD_ROTATE_FOOTER = (
    "Close this chat → open a new **operator** thread → ask what's next? "
    "(optional: close out thread for context window ritual)."
)

THREAD_ROTATE_MESSAGES = {
    "IDE_BUILD": (
        "New **IDE BUILD** thread recommended — open a fresh Agent chat, paste DESKTOP BUILD prompt."
    ),
    "RUN_LOCAL": "New **operator** thread recommended after run_ppe_local / chapter continue.",
    "CHAPTER_CLOSEOUT": "New **operator** thread recommended after chapter closeout.",
}


def normalize_thread_role(role: str) -> str:
    raw = str(role or "").strip().lower() or ROLE_OPERATOR
    return LEGACY_THREAD_ROLE_MAP.get(raw, raw)


def infer_suggest_thread_rotate(
    *,
    verdict: str,
    manifest_status: str,
    plan_path: str | None,
) -> dict[str, Any]:
    """Advisory: nudge operator to rotate thread at finish lines."""
    status = str(manifest_status or "").strip().upper()
    plan = str(plan_path or "").strip()
    v = str(verdict or "").strip().upper()

    if v == "IDE_BUILD":
        return {
            "suggest_thread_rotate": True,
            "thread_rotate_reason": "IDE_BUILD",
            "thread_rotate_message": THREAD_ROTATE_MESSAGES["IDE_BUILD"],
        }
    if v == "RUN_LOCAL":
        return {
            "suggest_thread_rotate": True,
            "thread_rotate_reason": "RUN_LOCAL",
            "thread_rotate_message": THREAD_ROTATE_MESSAGES["RUN_LOCAL"],
        }
    if v == "RUN_AUTO" and status == "COMPLETE" and not plan:
        return {
            "suggest_thread_rotate": True,
            "thread_rotate_reason": "CHAPTER_CLOSEOUT",
            "thread_rotate_message": THREAD_ROTATE_MESSAGES["CHAPTER_CLOSEOUT"],
        }
    return {
        "suggest_thread_rotate": False,
        "thread_rotate_reason": None,
        "thread_rotate_message": None,
    }


def infer_next_thread_role(*, closing_role: str, operator_verdict: str | None = None) -> str:
    """Suggest which thread role to open after context closeout."""
    role = normalize_thread_role(closing_role)
    if role == ROLE_CHARTER:
        return ROLE_CHARTER
    if role == ROLE_IDE_BUILD:
        return ROLE_OPERATOR
    verdict = str(operator_verdict or "").strip().upper()
    if verdict == "IDE_BUILD":
        return ROLE_IDE_BUILD
    return ROLE_OPERATOR


def suggested_opener_for_role(role: str) -> str:
    r = normalize_thread_role(role)
    if r == ROLE_IDE_BUILD:
        return "IDE BUILD thread. THREAD_ROLE: ide_build. Load @artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md only."
    if r == ROLE_CHARTER:
        return "Charter thread. THREAD_ROLE: charter. Load only your program doc — see docs/SOP/THREAD_STARTERS_V1.md."
    if r == ROLE_RECOVERY:
        return "Operator thread. THREAD_ROLE: operator. Load @docs/SOP/RECOVERY_PROTOCOL.md or ask what's next?"
    return "what's next?"


def classify_parked_lane(description: str) -> str:
    """Classify a parked/handoff item as control_plane, relay, or human."""
    text = str(description or "").strip().lower()
    if not text:
        return PARKED_LANE_HUMAN
    if any(h in text for h in _RELAY_PARKED_HINTS):
        return PARKED_LANE_RELAY
    if any(h in text for h in _CONTROL_PARKED_HINTS):
        return PARKED_LANE_CONTROL
    return PARKED_LANE_HUMAN


def infer_thread_role_from_opener(text: str) -> str | None:
    """Best-effort role from first user message (None if ambiguous)."""
    body = str(text or "").strip().lower()
    if not body:
        return None
    marker = "thread_role:"
    if marker in body[:240]:
        idx = body.index(marker) + len(marker)
        role_token = body[idx : idx + 32].split()[0].strip(".,;:")
        if role_token:
            return normalize_thread_role(role_token)
    operator_markers = (
        "what's next",
        "whats next",
        "operator thread",
        "ppe_go",
        "@ppe-director",
        "@ppe-autobuilder",
    )
    charter_markers = (
        "charter thread",
        "steward thread",
        "topic thread",
        "control-plane only",
        "no relay",
        "cheap upgrade",
        "delegation envelope",
        "close out thread",
        "context closeout",
    )
    ide_markers = ("ide build thread", "ide_build_starter")
    if any(m in body for m in operator_markers):
        return ROLE_OPERATOR
    if any(m in body for m in ide_markers):
        return ROLE_IDE_BUILD
    if any(m in body for m in charter_markers):
        return ROLE_CHARTER
    return None


def prepend_role_opener(text: str, opener: str) -> str:
    body = str(text or "").strip()
    if not body:
        return opener.strip()
    if "THREAD_ROLE:" in body[:200]:
        return body
    return f"{opener.strip()}\n\n{body}"
