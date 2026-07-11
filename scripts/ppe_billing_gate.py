"""Hard pre-dispatch gate for preventable token/context spend.

This is a policy gate, not an invoice reader. It composes the repo's existing
Cursor/token audit and scoped context preflight before an autobuilder command
can dispatch product work.

Policy:
- OK/NORMAL: allow.
- WATCH: block unless the operator supplies an explicit override and reason.
- ESCALATE: always block; shrink/fix the context surface first.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ARTIFACT_REL = "artifacts/control_plane/BILLING_GATE_LATEST.json"

_VERDICT_RANK = {
    "OK": 0,
    "NORMAL": 0,
    "WATCH": 1,
    "ESCALATE": 2,
}


@dataclass(frozen=True)
class BillingGateDecision:
    command: str
    phase: str
    verdict: str
    allowed: bool
    overridden: bool = False
    override_reason: str = ""
    reasons: tuple[str, ...] = field(default_factory=tuple)
    token_audit: dict[str, Any] = field(default_factory=dict)
    context_preflight: dict[str, Any] = field(default_factory=dict)
    checked: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at_utc": _utc_now(),
            "command": self.command,
            "phase": self.phase,
            "verdict": self.verdict,
            "allowed": self.allowed,
            "overridden": self.overridden,
            "override_reason": self.override_reason,
            "reasons": list(self.reasons),
            "token_audit": self.token_audit,
            "context_preflight": self.context_preflight,
            "checked": self.checked,
            "evidence_boundary": (
                "Repo policy/context evidence only; this is not provider billing telemetry "
                "or a claim about hidden token usage."
            ),
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_verdict(value: object) -> str:
    verdict = str(value or "").strip().upper()
    return verdict if verdict in _VERDICT_RANK else "ESCALATE"


def worst_verdict(*values: object) -> str:
    verdicts = [normalize_verdict(value) for value in values]
    return max(verdicts, key=lambda value: _VERDICT_RANK[value]) if verdicts else "ESCALATE"


def should_gate_command(command: str, phase: str) -> bool:
    """Gate direct dispatch commands; gate advance only when it would dispatch BUILD."""
    command_n = command.strip().lower()
    phase_n = phase.strip().upper()
    if command_n in {"retry-build", "handoff"}:
        return True
    return command_n == "advance" and phase_n == "AWAITING_BUILD"


def decide_budget_gate(
    *,
    command: str,
    phase: str,
    token_verdict: object,
    context_verdict: object,
    allow_watch: bool = False,
    watch_reason: str = "",
    reasons: list[str] | tuple[str, ...] | None = None,
    token_audit: dict[str, Any] | None = None,
    context_preflight: dict[str, Any] | None = None,
) -> BillingGateDecision:
    """Pure policy decision, separated for deterministic testing."""
    verdict = worst_verdict(token_verdict, context_verdict)
    reason_text = watch_reason.strip()
    base_reasons = tuple(reasons or ())

    if verdict == "ESCALATE":
        return BillingGateDecision(
            command=command,
            phase=phase,
            verdict=verdict,
            allowed=False,
            reasons=base_reasons or ("A token/context audit returned ESCALATE.",),
            token_audit=token_audit or {},
            context_preflight=context_preflight or {},
        )

    if verdict == "WATCH":
        if allow_watch and reason_text:
            return BillingGateDecision(
                command=command,
                phase=phase,
                verdict=verdict,
                allowed=True,
                overridden=True,
                override_reason=reason_text,
                reasons=base_reasons or ("WATCH accepted with an explicit operator reason.",),
                token_audit=token_audit or {},
                context_preflight=context_preflight or {},
            )
        missing = (
            "WATCH requires --allow-budget-watch plus a non-empty reason."
            if not allow_watch or not reason_text
            else "WATCH override was incomplete."
        )
        return BillingGateDecision(
            command=command,
            phase=phase,
            verdict=verdict,
            allowed=False,
            reasons=base_reasons + (missing,),
            token_audit=token_audit or {},
            context_preflight=context_preflight or {},
        )

    return BillingGateDecision(
        command=command,
        phase=phase,
        verdict="OK",
        allowed=True,
        reasons=base_reasons or ("Token/context audits are within policy budgets.",),
        token_audit=token_audit or {},
        context_preflight=context_preflight or {},
    )


def _report_reasons(token_data: dict[str, Any], context_data: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for recommendation in token_data.get("recommendations") or []:
        text = str(recommendation).strip()
        if text:
            reasons.append(f"token_audit: {text}")
    for action in context_data.get("advisory_actions") or []:
        text = str(action).strip()
        if text:
            reasons.append(f"context_preflight: {text}")
    return reasons


def collect_billing_gate(
    repo: Path,
    *,
    command: str,
    allow_watch: bool = False,
    watch_reason: str = "",
) -> BillingGateDecision:
    """Collect current scope and audits, then apply the hard dispatch policy."""
    repo = repo.resolve()

    from scripts.ppe_autobuilder import collect_autobuilder_status

    status = collect_autobuilder_status(repo)
    phase = str(status.get("phase") or "")
    if not should_gate_command(command, phase):
        return BillingGateDecision(
            command=command,
            phase=phase,
            verdict="OK",
            allowed=True,
            checked=False,
            reasons=(f"{command} in phase {phase or 'UNKNOWN'} does not dispatch product BUILD.",),
        )

    build = status.get("build") if isinstance(status.get("build"), dict) else {}
    slice_id = str(build.get("slice_id") or "").strip()
    plan_path = str(build.get("plan_path") or "").strip()
    if not slice_id or not plan_path:
        return BillingGateDecision(
            command=command,
            phase=phase,
            verdict="ESCALATE",
            allowed=False,
            reasons=("Dispatch scope is incomplete: both slice_id and plan_path are required.",),
        )

    try:
        from scripts.ppe_token_audit import build_token_audit

        token_report = build_token_audit(repo)
        token_data = token_report.to_dict()
        token_verdict = str(token_report.verdict or "ESCALATE")
    except Exception as exc:  # fail closed: an unavailable budget audit is not an OK audit
        token_data = {"error": f"{type(exc).__name__}: {exc}"}
        token_verdict = "ESCALATE"

    try:
        from scripts.ppe_context_preflight import run_preflight

        context_data = run_preflight(repo, phase_plan=plan_path, slice_id=slice_id)
        context_verdict = str(context_data.get("overall_band") or "ESCALATE")
    except Exception as exc:  # fail closed for the same reason
        context_data = {"error": f"{type(exc).__name__}: {exc}"}
        context_verdict = "ESCALATE"

    reasons = _report_reasons(token_data, context_data)
    if token_data.get("error"):
        reasons.append(f"token_audit unavailable: {token_data['error']}")
    if context_data.get("error"):
        reasons.append(f"context_preflight unavailable: {context_data['error']}")

    return decide_budget_gate(
        command=command,
        phase=phase,
        token_verdict=token_verdict,
        context_verdict=context_verdict,
        allow_watch=allow_watch,
        watch_reason=watch_reason,
        reasons=reasons,
        token_audit=token_data,
        context_preflight=context_data,
    )


def write_gate_artifact(repo: Path, decision: BillingGateDecision) -> Path:
    path = repo.resolve() / ARTIFACT_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(decision.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def _print_human(decision: BillingGateDecision) -> None:
    state = "ALLOW" if decision.allowed else "BLOCK"
    suffix = " (WATCH override recorded)" if decision.overridden else ""
    print(f"ppe_billing_gate: {state} verdict={decision.verdict} phase={decision.phase}{suffix}")
    for reason in decision.reasons[:8]:
        print(f"  - {reason}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hard token/context gate before autobuilder dispatch.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--command", required=True, choices=("retry-build", "handoff", "advance"))
    parser.add_argument("--allow-watch", action="store_true")
    parser.add_argument("--watch-reason", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    decision = collect_billing_gate(
        args.repo_root,
        command=args.command,
        allow_watch=args.allow_watch,
        watch_reason=args.watch_reason,
    )
    artifact = write_gate_artifact(args.repo_root, decision)
    payload = decision.to_dict()
    payload["artifact"] = str(artifact.relative_to(args.repo_root.resolve())).replace("\\", "/")

    if args.json:
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    else:
        _print_human(decision)
    return 0 if decision.allowed else 2


if __name__ == "__main__":
    raise SystemExit(main())
