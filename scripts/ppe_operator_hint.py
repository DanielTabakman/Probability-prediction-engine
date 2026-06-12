"""Shared operator copy for ppe_go.cmd handoff (phone, toast, guard reports)."""

from __future__ import annotations

PPE_GO_CMD = "ppe_go.cmd"
PPE_GO_HINT = f"{PPE_GO_CMD} → new Agent → Ctrl+V → Enter"

# Verdicts where the operator should run ppe_go.cmd (director spawns workers).
PPE_GO_VERDICTS = frozenset(
    {
        "IDE_BUILD",
        "RUN_LOCAL",
        "FIX_PLAN",
        "STALE_STATE",
        "ERROR",
    }
)


def ppe_go_hint_for_verdict(verdict: str) -> str | None:
    if verdict in PPE_GO_VERDICTS:
        return PPE_GO_HINT
    return None


def append_ppe_go_hint(text: str, verdict: str) -> str:
    """Append ppe_go hint to blocker/notify body when verdict needs IDE action."""
    hint = ppe_go_hint_for_verdict(verdict)
    if not hint:
        return text
    if hint in text or PPE_GO_CMD in text:
        return text
    base = text.rstrip()
    if base:
        return f"{base}\n\n{hint}"
    return hint
