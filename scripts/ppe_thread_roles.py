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
    "steward": ROLE_OPERATOR,
    "exploratory": ROLE_CHARTER,
    "topic": ROLE_CHARTER,
}

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


def prepend_role_opener(text: str, opener: str) -> str:
    body = str(text or "").strip()
    if not body:
        return opener.strip()
    if "THREAD_ROLE:" in body[:200]:
        return body
    return f"{opener.strip()}\n\n{body}"
