"""Unit tests for scripts/run_pushable_gate.py tier classification."""

from __future__ import annotations

from scripts import run_pushable_gate as gate


def test_tier0_docs_only():
    plan = gate.classify_paths(("docs/SOP/FOO.md", "docs/README.md"))
    assert plan.tier == gate.GateTier.DOCS_ONLY
    assert plan.pytest_paths == ()
    assert plan.escalate_reason is None


def test_tier2_any_src():
    plan = gate.classify_paths(("docs/SOP/X.md", "src/viz/app.py"))
    assert plan.tier == gate.GateTier.PRODUCT
    assert plan.uses_full_pytest


def test_tier1_script_with_matching_test():
    plan = gate.classify_paths(("scripts/relay_runtime_v0.py",))
    assert plan.tier == gate.GateTier.CONTROL_PLANE
    assert plan.pytest_paths == ("tests/test_relay_runtime_v0.py",)
    assert not plan.uses_full_pytest


def test_tier1_changed_test_file():
    plan = gate.classify_paths(("tests/test_msos_snapshot.py",))
    assert plan.tier == gate.GateTier.CONTROL_PLANE
    assert plan.pytest_paths == ("tests/test_msos_snapshot.py",)


def test_tier1_msos_build_snapshot_extra_tests():
    plan = gate.classify_paths(("scripts/msos/build_snapshot.py",))
    assert plan.tier == gate.GateTier.CONTROL_PLANE
    assert "tests/test_msos_snapshot.py" in plan.pytest_paths
    assert "tests/test_sync_msos_repo_truth.py" in plan.pytest_paths


def test_tier1_unmapped_script_escalates_to_full_pytest():
    plan = gate.classify_paths(("scripts/unknown_new_tool.py",))
    assert plan.tier == gate.GateTier.PRODUCT
    assert plan.escalate_reason is not None
    assert plan.uses_full_pytest


def test_tier1_mixed_docs_and_scripts():
    plan = gate.classify_paths(("docs/SOP/X.md", "scripts/sync_msos_repo_truth.py"))
    assert plan.tier == gate.GateTier.CONTROL_PLANE
    assert "tests/test_sync_msos_repo_truth.py" in plan.pytest_paths


def test_plan_commands_docs_only_empty():
    plan = gate.classify_paths(("docs/a.md",))
    assert gate.plan_commands(plan) == []


def test_plan_commands_product_includes_ruff_and_pytest():
    plan = gate.classify_paths(("src/foo.py",))
    cmds = gate.plan_commands(plan)
    assert len(cmds) == 2
    assert "ruff" in " ".join(cmds[0])
    assert cmds[1] == [gate.sys.executable, "-m", "pytest", "-q"]
