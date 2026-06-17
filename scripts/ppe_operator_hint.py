"""Shared operator copy for ppe_go.cmd handoff (phone, toast, guard reports)."""

from __future__ import annotations

from pathlib import Path

PPE_GO_CMD = "ppe_go.cmd"
PPE_GO_HINT = f"{PPE_GO_CMD} → new Agent → Ctrl+V → Enter"

from scripts.ppe_do_the_thing import BUTTON_NAME

DESKTOP_BUILD_CMD = "DESKTOP BUILD"
DESKTOP_CONTINUE_CMD = "DESKTOP CONTINUE"
DO_THE_THING_CMD = BUTTON_NAME
VM_RESTART_CMD = "VM_RESTART"

VERDICT_BUTTON_HINTS: dict[str, str] = {
    "IDE_BUILD": (
        f"Desktop PC: double-click **{DESKTOP_BUILD_CMD}** → `@ppe-build-worker` + starter in Agent. "
        f"After merge: **{DESKTOP_CONTINUE_CMD}** (SSH finish on VM)."
    ),
    "RUN_LOCAL": "VM relay finishes automatically when the stack is up — no action needed.",
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


def resolve_operator_hint(
    verdict: str,
    *,
    phase: str | None = None,
    repo: Path | None = None,
) -> str | None:
    """Context-aware operator hint (stack, CLI quota, build in flight)."""
    if phase == "STACK_DOWN":
        return VERDICT_BUTTON_HINTS["STACK_DOWN"]

    stack: dict = {}
    if repo is not None:
        try:
            from scripts.ppe_desktop_operator_stack import stack_status

            stack = stack_status(repo.resolve())
        except ImportError:
            stack = {}

    loop = bool(stack.get("loop_running"))
    watch = bool(stack.get("watch_running"))
    ntfy_listen = bool(stack.get("ntfy_listen_running"))

    if verdict == "IDE_BUILD" and repo is not None:
        try:
            from scripts.ppe_ide_build_automation_trigger import load_trigger
            from scripts.ppe_ide_handoff import cli_usage_exhausted, prefer_ide_over_cli
            from scripts.ppe_remote_build_agent import read_build_lock

            lock = read_build_lock(repo)
            trigger = load_trigger(repo)
            trig_status = str(trigger.get("status") or "").lower()
            if lock or trig_status == "dispatched":
                return (
                    "Auto-build in progress — no action unless stuck >30m "
                    "(see artifacts/orchestrator/REMOTE_BUILD_AGENT.log)."
                )
            if prefer_ide_over_cli(repo) or cli_usage_exhausted(repo):
                return VERDICT_BUTTON_HINTS["IDE_BUILD"]
            if stack.get("local_trigger_watcher_running"):
                return "Local watcher will dispatch CLI when allowed — no action unless stuck >30m."
        except ImportError:
            pass
        if not loop:
            return VERDICT_BUTTON_HINTS["STACK_DOWN"]

    if verdict == "RUN_LOCAL":
        if loop and watch:
            return VERDICT_BUTTON_HINTS["RUN_LOCAL"]
        return VERDICT_BUTTON_HINTS["STACK_DOWN"]

    if repo is not None and not ntfy_listen and verdict in PPE_GO_VERDICTS and not loop:
        return (
            f"{VERDICT_BUTTON_HINTS['STACK_DOWN']} "
            "Phone status/build commands need the VM stack up (ntfy listener off)."
        )

    return operator_button_hint(verdict, phase=phase) or ppe_go_hint_for_verdict(verdict)


PROCEDURAL_RELAY_HINT = (
    "Auto-advancing — promotion_recovery handles this relay stop; no IDE action needed."
)


def is_procedural_relay_text(text: str) -> bool:
    lower = text.lower()
    return any(
        marker in lower
        for marker in (
            "promotion_recovery advances",
            "rule 7b",
            "deterministic evidence slice passed",
            "auto_advance_promotion_recovery",
        )
    )


def append_ppe_go_hint(
    text: str,
    verdict: str,
    *,
    phase: str | None = None,
    repo: Path | None = None,
) -> str:
    """Append operator button hint to blocker/notify body when verdict needs action."""
    if is_procedural_relay_text(text):
        return text
    hint = resolve_operator_hint(verdict, phase=phase, repo=repo)
    if not hint:
        return text
    if hint in text or PPE_GO_CMD in text:
        return text
    base = text.rstrip()
    if base:
        return f"{base}\n\n{hint}"
    return hint
