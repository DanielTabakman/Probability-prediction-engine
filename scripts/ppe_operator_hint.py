"""Shared operator copy for ppe_go.cmd handoff (phone, toast, guard reports)."""

from __future__ import annotations

PPE_GO_CMD = "ppe_go.cmd"
PPE_GO_HINT = f"{PPE_GO_CMD} → new Agent → Ctrl+V → Enter"

DESKTOP_BUILD_CMD = "DESKTOP BUILD"
DESKTOP_CONTINUE_CMD = "DESKTOP CONTINUE"
VM_RESTART_CMD = "VM_RESTART"

VERDICT_BUTTON_HINTS: dict[str, str] = {
    "IDE_BUILD": (
        f"Desktop PC: double-click **{DESKTOP_BUILD_CMD}** → paste in Agent chat. "
        f"After merge: **{DESKTOP_CONTINUE_CMD}** (SSH finish on VM)."
    ),
    "RUN_LOCAL": "VM loop continues relay automatically after product is marked ready.",
    "STACK_DOWN": f"VM: double-click **{VM_RESTART_CMD}** (or VM_AUTO). Desktop must stay loop-off.",
    "FIX_PLAN": f"VM: **VM_STATUS** → **fix_vm_operator.cmd** or vm_bootstrap --recover. Desktop: steward chat.",
    "STALE_STATE": f"VM: **fix_vm_operator.cmd** (vm_bootstrap --recover). Check VM_STATUS.",
    "ERROR": f"VM: **VM_STATUS** + artifacts/orchestrator/LAST_RUN_REPORT.md. VM_RESTART if stack_loop=False.",
}

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


def operator_button_hint(verdict: str, *, phase: str | None = None) -> str | None:
    if phase == "STACK_DOWN":
        return VERDICT_BUTTON_HINTS["STACK_DOWN"]
    return VERDICT_BUTTON_HINTS.get(verdict)


def ppe_go_hint_for_verdict(verdict: str) -> str | None:
    button = operator_button_hint(verdict)
    if button:
        return button
    if verdict in PPE_GO_VERDICTS:
        return PPE_GO_HINT
    return None


def append_ppe_go_hint(text: str, verdict: str, *, phase: str | None = None) -> str:
    """Append operator button hint to blocker/notify body when verdict needs action."""
    hint = operator_button_hint(verdict, phase=phase) or ppe_go_hint_for_verdict(verdict)
    if not hint:
        return text
    if hint in text or PPE_GO_CMD in text:
        return text
    base = text.rstrip()
    if base:
        return f"{base}\n\n{hint}"
    return hint
