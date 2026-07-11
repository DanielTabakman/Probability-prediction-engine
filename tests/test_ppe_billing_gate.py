"""Tests for the hard token/context dispatch gate."""

from __future__ import annotations

from scripts.ppe_billing_gate import (
    decide_budget_gate,
    should_gate_command,
    worst_verdict,
)


def test_worst_verdict_normalizes_ok_and_normal():
    assert worst_verdict("OK", "NORMAL") == "OK"
    assert worst_verdict("OK", "WATCH") == "WATCH"
    assert worst_verdict("WATCH", "ESCALATE") == "ESCALATE"


def test_unknown_verdict_fails_closed():
    assert worst_verdict("OK", "mystery") == "ESCALATE"


def test_ok_allows_dispatch():
    decision = decide_budget_gate(
        command="retry-build",
        phase="AWAITING_BUILD",
        token_verdict="OK",
        context_verdict="NORMAL",
    )
    assert decision.allowed is True
    assert decision.verdict == "OK"
    assert decision.overridden is False


def test_watch_blocks_without_explicit_override():
    decision = decide_budget_gate(
        command="retry-build",
        phase="AWAITING_BUILD",
        token_verdict="WATCH",
        context_verdict="NORMAL",
    )
    assert decision.allowed is False
    assert decision.verdict == "WATCH"


def test_watch_requires_non_empty_reason():
    decision = decide_budget_gate(
        command="handoff",
        phase="AWAITING_BUILD",
        token_verdict="OK",
        context_verdict="WATCH",
        allow_watch=True,
        watch_reason="   ",
    )
    assert decision.allowed is False
    assert decision.overridden is False


def test_watch_override_records_reason():
    decision = decide_budget_gate(
        command="advance",
        phase="AWAITING_BUILD",
        token_verdict="WATCH",
        context_verdict="NORMAL",
        allow_watch=True,
        watch_reason="Known oversized legacy starter; bounded one-file fix.",
    )
    assert decision.allowed is True
    assert decision.verdict == "WATCH"
    assert decision.overridden is True
    assert decision.override_reason.startswith("Known oversized")


def test_escalate_cannot_be_overridden():
    decision = decide_budget_gate(
        command="retry-build",
        phase="AWAITING_BUILD",
        token_verdict="ESCALATE",
        context_verdict="NORMAL",
        allow_watch=True,
        watch_reason="Try anyway",
    )
    assert decision.allowed is False
    assert decision.verdict == "ESCALATE"
    assert decision.overridden is False


def test_advance_is_gated_only_when_it_would_dispatch_build():
    assert should_gate_command("retry-build", "HEALTHY_IDLE") is True
    assert should_gate_command("handoff", "DEGRADED") is True
    assert should_gate_command("advance", "AWAITING_BUILD") is True
    assert should_gate_command("advance", "STACK_DOWN") is False
    assert should_gate_command("advance", "CLOSEOUT_PENDING") is False
