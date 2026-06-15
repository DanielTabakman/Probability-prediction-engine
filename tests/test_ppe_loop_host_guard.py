"""Tests for ppe_loop_host_guard."""

from __future__ import annotations

import pytest

from scripts.ppe_loop_host_guard import GUARD_EXIT, loop_host_start_allowed, main


def test_allowed_when_loop_host(monkeypatch):
    monkeypatch.delenv("PPE_STACK_FORBIDDEN", raising=False)
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    allowed, code, _ = loop_host_start_allowed()
    assert allowed is True
    assert code == "loop_host"


def test_blocked_when_forbidden(monkeypatch):
    monkeypatch.setenv("PPE_STACK_FORBIDDEN", "1")
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    allowed, code, _ = loop_host_start_allowed()
    assert allowed is False
    assert code == "stack_forbidden"


def test_blocked_when_unconfigured(monkeypatch):
    monkeypatch.delenv("PPE_STACK_FORBIDDEN", raising=False)
    monkeypatch.delenv("PPE_LOOP_HOST", raising=False)
    monkeypatch.delenv("PPE_FORCE_STACK", raising=False)
    allowed, code, _ = loop_host_start_allowed()
    assert allowed is False
    assert code == "not_loop_host"


def test_force_override(monkeypatch):
    monkeypatch.delenv("PPE_LOOP_HOST", raising=False)
    monkeypatch.setenv("PPE_FORCE_STACK", "1")
    allowed, code, _ = loop_host_start_allowed()
    assert allowed is True
    assert code == "force"


def test_require_exit_codes(monkeypatch):
    monkeypatch.delenv("PPE_LOOP_HOST", raising=False)
    monkeypatch.delenv("PPE_STACK_FORBIDDEN", raising=False)
    assert main(["--require"]) == GUARD_EXIT
    monkeypatch.setenv("PPE_LOOP_HOST", "1")
    assert main(["--require"]) == 0
