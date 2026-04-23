"""Focused unit tests for scripts/relay_runtime_v0.py.

Covers the areas called out by the implementation pass:
  - section 14.1 schema validation
  - section 14.3 invariant enforcement
  - section 15.2 decision policy outcomes
  - state transitions for stage / resume / abort / reset

Uses only stdlib and a tempdir sandbox; does not require a real git repo
except in the tests that explicitly shell out to git.
"""

from __future__ import annotations

import copy
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import relay_runtime_v0 as relay  # noqa: E402


# ---------------------------------------------------------------------------
# Canonical minimal valid payload (clean-closure shape). Individual tests
# deep-copy this and mutate one field to exercise a specific branch.
# ---------------------------------------------------------------------------

_VALID_PAYLOAD = {
    "protocol": "CODEX_AUTONOMY_V1",
    "schema_version": "1",
    "slice_id": "Sprint999-Slice001",
    "run_id": "20260420_120000",
    "declared_plane": "PRODUCT-PLANE",
    "build_branch": "build/test",
    "baseline_branch": "recovery/frontier-steward-v2_1-baseline",
    "baseline_tip_before": "aaaaaaa",
    "baseline_tip_after": "bbbbbbb",
    "product_commit_sha": "ccccccc",
    "preflight": {
        "build_allowed": True,
        "tree_clean": True,
        "untracked_canonical_docs": False,
        "mixed_plane_dirty": False,
        "blocker": None,
    },
    "retry_count": 0,
    "retry_budget_max": 2,
    "retry_budget_exhausted": False,
    "tests": {
        "pytest_status": "PASS",
        "pytest_count": 55,
        "ui_smoke_primary_status": "PASS",
        "ui_smoke_conditional_status": "NOT_REQUIRED",
        "ui_inspection_evidence_present": True,
        "validation_classification": "deterministic",
    },
    "tree_cleanliness": {
        "build_branch_clean": True,
        "mixed_plane_residue": False,
        "untracked_canonical_docs": False,
    },
    "promotion": {
        "attempted": True,
        "performed": True,
        "method": "fast-forward",
        "ancestor_check_pass": True,
    },
    "stop_condition": None,
    "ready_for_control_closeout": True,
    "safe_to_continue": True,
    "artifacts": {
        "ui_smoke_manifest": "artifacts/ui_smoke/20260420_120000/manifest.json",
        "ui_smoke_screenshot": "artifacts/ui_smoke/20260420_120000/A.png",
        "run_log": "artifacts/ui_smoke/20260420_120000/run.log",
    },
    "notes": "clean run",
}


def valid_payload() -> dict:
    return copy.deepcopy(_VALID_PAYLOAD)


# ---------------------------------------------------------------------------
# Schema validation (section 14.1)
# ---------------------------------------------------------------------------


class TestSchemaValidation(unittest.TestCase):
    def test_valid_payload_has_no_violations(self) -> None:
        self.assertEqual(relay.validate_relay_result_schema(valid_payload()), [])

    def test_non_dict_payload_is_rejected(self) -> None:
        self.assertEqual(relay.validate_relay_result_schema("not an object"), ["payload is not a JSON object"])

    def test_wrong_protocol_literal(self) -> None:
        p = valid_payload()
        p["protocol"] = "SOMETHING_ELSE"
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("protocol must be" in v for v in violations))

    def test_wrong_schema_version(self) -> None:
        p = valid_payload()
        p["schema_version"] = "2"
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("schema_version" in v for v in violations))

    def test_missing_required_top_level_field(self) -> None:
        p = valid_payload()
        del p["slice_id"]
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("slice_id" in v and "missing" in v for v in violations))

    def test_unknown_declared_plane(self) -> None:
        p = valid_payload()
        p["declared_plane"] = "CONTROL-PLANE"
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("declared_plane" in v for v in violations))

    def test_unknown_stop_condition_enum(self) -> None:
        p = valid_payload()
        p["stop_condition"] = "TOTALLY_MADE_UP"
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("stop_condition" in v for v in violations))

    def test_unknown_pytest_status_enum(self) -> None:
        p = valid_payload()
        p["tests"]["pytest_status"] = "SORT_OF_PASS"
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("pytest_status" in v for v in violations))

    def test_bool_fields_reject_non_bool(self) -> None:
        p = valid_payload()
        p["safe_to_continue"] = "yes"  # string not bool
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("safe_to_continue" in v for v in violations))

    def test_retry_budget_negative_rejected(self) -> None:
        p = valid_payload()
        p["retry_budget_max"] = -1
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("retry_budget_max" in v for v in violations))

    def test_notes_length_cap(self) -> None:
        p = valid_payload()
        p["notes"] = "x" * 281
        violations = relay.validate_relay_result_schema(p)
        self.assertTrue(any("notes" in v and "280" in v for v in violations))

    def test_product_commit_sha_may_be_null(self) -> None:
        p = valid_payload()
        p["product_commit_sha"] = None
        self.assertEqual(relay.validate_relay_result_schema(p), [])

    def test_ui_smoke_conditional_accepts_not_required(self) -> None:
        p = valid_payload()
        p["tests"]["ui_smoke_conditional_status"] = "NOT_REQUIRED"
        self.assertEqual(relay.validate_relay_result_schema(p), [])

    def test_promotion_method_null_with_performed_false(self) -> None:
        p = valid_payload()
        p["promotion"] = {
            "attempted": False,
            "performed": False,
            "method": None,
            "ancestor_check_pass": False,
        }
        p["ready_for_control_closeout"] = False
        # schema allows this; we are only testing schema shape here.
        self.assertEqual(relay.validate_relay_result_schema(p), [])


# ---------------------------------------------------------------------------
# Invariant enforcement (section 14.3)
# ---------------------------------------------------------------------------


class TestInvariants(unittest.TestCase):
    def test_valid_payload_passes_invariants(self) -> None:
        self.assertEqual(relay.check_invariants(valid_payload()), [])

    def test_retry_count_exceeds_budget(self) -> None:
        p = valid_payload()
        p["retry_count"] = 3
        p["retry_budget_max"] = 2
        violations = relay.check_invariants(p)
        self.assertTrue(any("exceeds retry_budget_max" in v for v in violations))

    def test_retry_budget_max_exceeds_canonical_cap(self) -> None:
        p = valid_payload()
        p["retry_budget_max"] = 5
        violations = relay.check_invariants(p)
        self.assertTrue(any("canonical max" in v for v in violations))

    def test_retry_exhausted_iff_at_cap_and_not_green(self) -> None:
        p = valid_payload()
        # at cap, validation green -> exhausted must be False
        p["retry_count"] = 2
        p["retry_budget_max"] = 2
        p["retry_budget_exhausted"] = True  # wrong (validation is green)
        violations = relay.check_invariants(p)
        self.assertTrue(any("retry_budget_exhausted=true" in v for v in violations))

    def test_retry_exhausted_false_but_should_be_true(self) -> None:
        p = valid_payload()
        p["retry_count"] = 2
        p["retry_budget_max"] = 2
        p["tests"]["pytest_status"] = "FAIL"
        p["retry_budget_exhausted"] = False  # should be True
        p["ready_for_control_closeout"] = False
        p["safe_to_continue"] = False
        p["promotion"]["performed"] = False
        p["promotion"]["method"] = None
        violations = relay.check_invariants(p)
        self.assertTrue(any("retry_budget_exhausted=false" in v for v in violations))

    def test_promotion_performed_but_tree_dirty(self) -> None:
        p = valid_payload()
        p["tree_cleanliness"]["build_branch_clean"] = False
        violations = relay.check_invariants(p)
        self.assertTrue(any("build_branch_clean=false" in v for v in violations))

    def test_promotion_performed_but_mixed_residue(self) -> None:
        p = valid_payload()
        p["tree_cleanliness"]["mixed_plane_residue"] = True
        violations = relay.check_invariants(p)
        self.assertTrue(any("mixed_plane_residue=true" in v for v in violations))

    def test_ready_for_closeout_requires_promotion(self) -> None:
        p = valid_payload()
        p["promotion"] = {
            "attempted": False,
            "performed": False,
            "method": None,
            "ancestor_check_pass": False,
        }
        # ready_for_control_closeout=True but promotion.performed=False -> violation
        violations = relay.check_invariants(p)
        self.assertTrue(any("ready_for_control_closeout=true but promotion.performed=false" in v for v in violations))

    def test_ready_for_closeout_requires_null_stop_condition(self) -> None:
        p = valid_payload()
        p["stop_condition"] = "UNCLEAR_TEST_RESULTS"
        # safe_to_continue must flip to False then; but we also test ready_for_closeout.
        p["safe_to_continue"] = False
        violations = relay.check_invariants(p)
        self.assertTrue(any("ready_for_control_closeout=true but stop_condition" in v for v in violations))

    def test_safe_to_continue_requires_clean_tree(self) -> None:
        p = valid_payload()
        p["tree_cleanliness"]["untracked_canonical_docs"] = True
        violations = relay.check_invariants(p)
        self.assertTrue(any("safe_to_continue=true but tree_cleanliness.untracked_canonical_docs=true" in v for v in violations))

    def test_promotion_performed_but_not_attempted(self) -> None:
        p = valid_payload()
        p["promotion"]["attempted"] = False
        violations = relay.check_invariants(p)
        self.assertTrue(any("promotion.attempted=false" in v for v in violations))

    def test_promotion_performed_but_method_null(self) -> None:
        p = valid_payload()
        p["promotion"]["method"] = None
        violations = relay.check_invariants(p)
        self.assertTrue(any("promotion.method is null" in v for v in violations))


# ---------------------------------------------------------------------------
# Decision policy (section 15.2)
# ---------------------------------------------------------------------------


class TestDecisionPolicy(unittest.TestCase):
    def test_rule_1_schema_violation_blocked(self) -> None:
        p = valid_payload()
        p["protocol"] = "NOT_THE_PROTOCOL"
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_BLOCKED)
        self.assertIn("rule 1", dec["rule_matched"])

    def test_rule_1_invariant_violation_blocked(self) -> None:
        p = valid_payload()
        p["tree_cleanliness"]["mixed_plane_residue"] = True
        # safe_to_continue=True + mixed_plane_residue=true -> invariant violation
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_BLOCKED)
        self.assertIn("rule 1", dec["rule_matched"])

    def test_rule_2_hard_stop_condition_blocked(self) -> None:
        p = valid_payload()
        p["stop_condition"] = "MIXED_PLANE_CONTAMINATION"
        p["safe_to_continue"] = False
        p["ready_for_control_closeout"] = False
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = False
        p["promotion"]["method"] = None
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_BLOCKED)
        self.assertIn("rule 2", dec["rule_matched"])

    def test_rule_3_retry_exhausted_stop_for_review(self) -> None:
        p = valid_payload()
        p["stop_condition"] = "MAX_RETRIES_EXCEEDED"
        p["retry_count"] = 2
        p["retry_budget_max"] = 2
        p["retry_budget_exhausted"] = True
        p["tests"]["pytest_status"] = "FAIL"
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = True
        p["promotion"]["method"] = None
        p["ready_for_control_closeout"] = False
        p["safe_to_continue"] = False
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_STOP_FOR_REVIEW)
        self.assertIn("rule 3", dec["rule_matched"])

    def test_rule_4_scope_ambiguity_stop_for_review(self) -> None:
        p = valid_payload()
        p["stop_condition"] = "SCOPE_AMBIGUITY"
        p["safe_to_continue"] = False
        p["ready_for_control_closeout"] = False
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = False
        p["promotion"]["method"] = None
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_STOP_FOR_REVIEW)
        self.assertIn("rule 4", dec["rule_matched"])

    def test_rule_5_deterministic_fail_with_budget_retry_allowed(self) -> None:
        p = valid_payload()
        p["tests"]["pytest_status"] = "FAIL"
        p["retry_count"] = 0
        p["retry_budget_max"] = 2
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = True
        p["promotion"]["method"] = None
        p["ready_for_control_closeout"] = False
        p["safe_to_continue"] = True  # stop_condition is null; tree clean
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_RETRY_ALLOWED)
        self.assertIn("rule 5", dec["rule_matched"])

    def test_rule_5_blocked_when_non_deterministic(self) -> None:
        # non-deterministic validation classification with a FAIL should go to
        # rule 6 (STOP_FOR_REVIEW), never rule 5 (RETRY_ALLOWED).
        p = valid_payload()
        p["tests"]["pytest_status"] = "FAIL"
        p["tests"]["validation_classification"] = "environment-sensitive"
        p["retry_count"] = 0
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = True
        p["promotion"]["method"] = None
        p["ready_for_control_closeout"] = False
        p["safe_to_continue"] = True
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_STOP_FOR_REVIEW)
        self.assertIn("rule 6", dec["rule_matched"])

    def test_rule_6_inconclusive_stop_for_review(self) -> None:
        p = valid_payload()
        p["tests"]["pytest_status"] = "INCONCLUSIVE"
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = True
        p["promotion"]["method"] = None
        p["ready_for_control_closeout"] = False
        p["safe_to_continue"] = True
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_STOP_FOR_REVIEW)
        self.assertIn("rule 6", dec["rule_matched"])

    def test_rule_7_clean_closure_continue(self) -> None:
        dec = relay.decide(valid_payload())
        self.assertEqual(dec["decision"], relay.DECISION_CONTINUE)
        self.assertIn("rule 7", dec["rule_matched"])

    def test_rule_8_default_stop_for_review(self) -> None:
        # A payload that passes schema + invariants but does not match rules 2-7:
        # stop_condition is null, all tests PASS, but promotion.performed=false
        # and ready_for_control_closeout=false -> falls through to rule 8.
        p = valid_payload()
        p["promotion"]["performed"] = False
        p["promotion"]["attempted"] = True
        p["promotion"]["method"] = None
        p["ready_for_control_closeout"] = False
        # safe_to_continue may still be True; tree clean, stop_condition null.
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_STOP_FOR_REVIEW)
        self.assertIn("rule 8", dec["rule_matched"])

    def test_rule_1_takes_precedence_over_rule_7(self) -> None:
        # A payload that *claims* clean closure but has an invariant violation
        # must be BLOCKED, never CONTINUE.  This is the spec section 11 override.
        p = valid_payload()
        p["tree_cleanliness"]["mixed_plane_residue"] = True
        dec = relay.decide(p)
        self.assertEqual(dec["decision"], relay.DECISION_BLOCKED)

    def test_exit_code_mapping_covers_all_decisions(self) -> None:
        for d in relay.ALL_DECISIONS:
            self.assertIn(d, relay.DECISION_TO_EXIT)

    def test_hard_vs_review_stop_sets_disjoint(self) -> None:
        self.assertFalse(relay.HARD_STOP_CONDITIONS & relay.REVIEW_STOP_CONDITIONS)


# ---------------------------------------------------------------------------
# State machine transitions (stage / resume / abort / reset)
# ---------------------------------------------------------------------------


class TestStateMachine(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name).resolve()
        # Initialize a minimal git repo so preflight can pass.
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
             "--allow-empty", "-q", "-m", "init"],
            cwd=self.repo, check=True,
        )
        # Create a baseline branch pointing at the initial commit.
        subprocess.run(["git", "branch", "baseline"], cwd=self.repo, check=True)
        # Ensure the required sprint spec file exists for preflight arg validation.
        spec = self.repo / "docs" / "SOP" / "SPRINT_999_PHASE_2.md"
        spec.parent.mkdir(parents=True, exist_ok=True)
        spec.write_text("# Sprint 999 stub\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(
            ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
             "-q", "-m", "sprint spec"],
            cwd=self.repo, check=True,
        )
        self.runtime = relay.Runtime(self.repo)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _stage_ok(self, build_branch: str = "build/test-slice"):
        return relay.dispatch_stage_slice(
            runtime=self.runtime,
            slice_id="Sprint999-Slice001",
            sprint_spec_path="docs/SOP/SPRINT_999_PHASE_2.md",
            declared_plane="PRODUCT-PLANE",
            baseline_branch="baseline",
            build_branch=build_branch,
        )

    def test_stage_from_idle_goes_to_staged_for_worker(self) -> None:
        code, msg = self._stage_ok()
        self.assertEqual(code, relay.EXIT_CONTINUE)
        state = self.runtime.load_run_state()
        self.assertEqual(state["status"], relay.STATE_STAGED_FOR_WORKER)
        self.assertEqual(state["slice_id"], "Sprint999-Slice001")
        envelope = json.loads(
            (self.runtime.run_dir(state["run_id"]) / "task_envelope.json").read_text("utf-8")
        )
        self.assertEqual(envelope["job"], relay.JOB_RUN_SLICE)

    def test_stage_while_staged_refused(self) -> None:
        self._stage_ok()
        code, msg = self._stage_ok(build_branch="build/test-slice-2")
        self.assertEqual(code, relay.EXIT_REFUSAL)
        self.assertIn("already in flight", msg)

    def test_stage_preflight_rejects_existing_build_branch(self) -> None:
        subprocess.run(["git", "branch", "build/already-exists"], cwd=self.repo, check=True)
        code, msg = relay.dispatch_stage_slice(
            runtime=self.runtime,
            slice_id="Sprint999-Slice001",
            sprint_spec_path="docs/SOP/SPRINT_999_PHASE_2.md",
            declared_plane="PRODUCT-PLANE",
            baseline_branch="baseline",
            build_branch="build/already-exists",
        )
        self.assertEqual(code, relay.EXIT_STOP_FOR_REVIEW)
        state = self.runtime.load_run_state()
        self.assertEqual(state["status"], relay.STATE_DECIDED_STOP_FOR_REVIEW)
        self.assertIn("already exists locally", msg)

    def test_stage_preflight_rejects_missing_baseline_branch(self) -> None:
        code, msg = relay.dispatch_stage_slice(
            runtime=self.runtime,
            slice_id="Sprint999-Slice001",
            sprint_spec_path="docs/SOP/SPRINT_999_PHASE_2.md",
            declared_plane="PRODUCT-PLANE",
            baseline_branch="does-not-exist",
            build_branch="build/test-slice",
        )
        self.assertEqual(code, relay.EXIT_STOP_FOR_REVIEW)
        self.assertIn("does not exist locally", msg)

    def test_stage_refuses_unknown_declared_plane(self) -> None:
        code, msg = relay.dispatch_stage_slice(
            runtime=self.runtime,
            slice_id="Sprint999-Slice001",
            sprint_spec_path="docs/SOP/SPRINT_999_PHASE_2.md",
            declared_plane="CONTROL-PLANE",  # forbidden
            baseline_branch="baseline",
            build_branch="build/test-slice",
        )
        self.assertEqual(code, relay.EXIT_REFUSAL)

    def test_stage_refuses_missing_sprint_spec(self) -> None:
        code, msg = relay.dispatch_stage_slice(
            runtime=self.runtime,
            slice_id="Sprint999-Slice001",
            sprint_spec_path="docs/SOP/NO_SUCH_SPRINT.md",
            declared_plane="PRODUCT-PLANE",
            baseline_branch="baseline",
            build_branch="build/test-slice",
        )
        self.assertEqual(code, relay.EXIT_REFUSAL)
        self.assertIn("sprint_spec_path does not exist", msg)

    def test_abort_from_staged_transitions_to_aborted(self) -> None:
        self._stage_ok()
        code, msg = relay.dispatch_abort(self.runtime)
        self.assertEqual(code, relay.EXIT_REFUSAL)
        state = self.runtime.load_run_state()
        self.assertEqual(state["status"], relay.STATE_ABORTED)

    def test_abort_terminal_is_refused(self) -> None:
        self._stage_ok()
        relay.dispatch_abort(self.runtime)
        code, msg = relay.dispatch_abort(self.runtime)
        self.assertEqual(code, relay.EXIT_REFUSAL)
        self.assertIn("already terminal", msg)

    def test_reset_from_terminal_goes_to_idle(self) -> None:
        self._stage_ok()
        relay.dispatch_abort(self.runtime)
        code, msg = relay.dispatch_reset(self.runtime)
        self.assertEqual(code, relay.EXIT_CONTINUE)
        state = self.runtime.load_run_state()
        self.assertEqual(state["status"], relay.STATE_IDLE)

    def test_reset_from_idle_is_noop(self) -> None:
        code, msg = relay.dispatch_reset(self.runtime)
        self.assertEqual(code, relay.EXIT_CONTINUE)
        self.assertIn("idle", msg)

    def test_reset_from_non_terminal_refused(self) -> None:
        self._stage_ok()
        code, msg = relay.dispatch_reset(self.runtime)
        self.assertEqual(code, relay.EXIT_REFUSAL)
        self.assertIn("abort", msg)

    def test_resume_without_stage_refused(self) -> None:
        code, msg = relay.dispatch_resume(self.runtime)
        self.assertEqual(code, relay.EXIT_REFUSAL)

    def test_resume_without_worker_result_refused(self) -> None:
        self._stage_ok()
        code, msg = relay.dispatch_resume(self.runtime)
        self.assertEqual(code, relay.EXIT_REFUSAL)
        self.assertIn("not found", msg)

    def test_resume_with_valid_payload_exits_continue(self) -> None:
        self._stage_ok()
        state = self.runtime.load_run_state()
        run_id = state["run_id"]
        payload = valid_payload()
        payload["run_id"] = run_id
        payload["slice_id"] = "Sprint999-Slice001"
        payload["build_branch"] = "build/test-slice"
        payload["baseline_branch"] = "baseline"
        result_path = self.runtime.run_dir(run_id) / "relay_result.json"
        result_path.write_text(json.dumps(payload), encoding="utf-8")
        code, msg = relay.dispatch_resume(self.runtime)
        self.assertEqual(code, relay.EXIT_CONTINUE)
        final = self.runtime.load_run_state()
        self.assertEqual(final["status"], relay.STATE_DECIDED_CONTINUE)
        decision_path = self.runtime.run_dir(run_id) / "decision.json"
        self.assertTrue(decision_path.is_file())
        self.assertEqual(json.loads(decision_path.read_text("utf-8"))["decision"], relay.DECISION_CONTINUE)

    def test_resume_with_malformed_payload_blocks(self) -> None:
        self._stage_ok()
        state = self.runtime.load_run_state()
        run_id = state["run_id"]
        (self.runtime.run_dir(run_id) / "relay_result.json").write_text("not json", encoding="utf-8")
        code, msg = relay.dispatch_resume(self.runtime)
        self.assertEqual(code, relay.EXIT_BLOCKED)
        self.assertEqual(self.runtime.load_run_state()["status"], relay.STATE_DECIDED_BLOCKED)

    def test_resume_with_hard_stop_blocks(self) -> None:
        self._stage_ok()
        state = self.runtime.load_run_state()
        run_id = state["run_id"]
        payload = valid_payload()
        payload["run_id"] = run_id
        payload["stop_condition"] = "REPO_STATE_DRIFT"
        payload["safe_to_continue"] = False
        payload["ready_for_control_closeout"] = False
        payload["promotion"]["performed"] = False
        payload["promotion"]["attempted"] = False
        payload["promotion"]["method"] = None
        (self.runtime.run_dir(run_id) / "relay_result.json").write_text(json.dumps(payload), encoding="utf-8")
        code, msg = relay.dispatch_resume(self.runtime)
        self.assertEqual(code, relay.EXIT_BLOCKED)


# ---------------------------------------------------------------------------
# control_plane_consistency_check -- SOP template placeholder suppression
# (Sprint003-Slice001)
#
# Narrow rule: references to `docs/SOP/SPRINT_00X.md` and
# `docs/SOP/SPRINT_00X_PHASE_Y.md` are intentional SOP template placeholders
# and must not produce unresolved-reference warnings. Any other missing
# canonical-doc reference must still produce a `warn` finding.
# ---------------------------------------------------------------------------


class TestSopTemplatePlaceholderSuppression(unittest.TestCase):
    """Covers Sprint003-Slice001 narrow-rule suppression in step 3 of
    `dispatch_control_plane_consistency_check`.

    Each test builds a minimal sandbox repo containing only the canonical
    docs listed in `relay.CANONICAL_DOC_PATHS`, where one doc embeds the
    backtick-quoted reference under test. The other canonical docs are
    written as empty stubs so that step 1 (doc presence) passes and steps
    2 and 4 do not emit noise.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name).resolve()
        sop_dir = self.repo / "docs" / "SOP"
        sop_dir.mkdir(parents=True, exist_ok=True)
        for canonical in relay.CANONICAL_DOC_PATHS:
            (self.repo / canonical).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / canonical).write_text(
                self._baseline_canonical_body(canonical), encoding="utf-8"
            )
        self.runtime = relay.Runtime(self.repo)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @staticmethod
    def _baseline_canonical_body(path: str) -> str:
        # For CODEX_AUTONOMY_V1.md step 4 requires every section 14.2 enum
        # value to appear textually; stub that content in so the test does
        # not spuriously produce `error` findings.
        if path.endswith("CODEX_AUTONOMY_V1.md"):
            enum_dump = "\n".join(sorted(relay.ALL_STOP_CONDITIONS))
            return f"# CODEX_AUTONOMY_V1 stub\n\n{enum_dump}\n"
        return f"# {Path(path).name} stub\n"

    def _run_check(self) -> list[dict]:
        self.runtime.artifacts_root.mkdir(parents=True, exist_ok=True)
        relay.dispatch_control_plane_consistency_check(self.runtime)
        health_dir = self.repo / "artifacts" / "health"
        reports = sorted(health_dir.glob("*/control_plane_consistency_report.json"))
        self.assertTrue(reports, "consistency report was not written")
        return json.loads(reports[-1].read_text(encoding="utf-8"))["findings"]

    def _inject_references(self, doc_rel: str, refs: list[str]) -> None:
        p = self.repo / doc_rel
        body = p.read_text(encoding="utf-8")
        body += "\n\n" + "\n".join(f"See `{ref}` for details." for ref in refs) + "\n"
        p.write_text(body, encoding="utf-8")

    # -- Positive (suppression) cases ---------------------------------------

    def test_sprint_00x_placeholder_is_suppressed(self) -> None:
        self._inject_references(
            "docs/SOP/OPERATING_RULES.md",
            ["docs/SOP/SPRINT_00X.md"],
        )
        findings = self._run_check()
        self.assertFalse(
            any(
                f["severity"] == "warn"
                and "SPRINT_00X.md" in f.get("locator", "")
                and "does not resolve" in f.get("message", "")
                for f in findings
            ),
            f"placeholder 'SPRINT_00X.md' should be suppressed; got findings: {findings}",
        )

    def test_sprint_00x_phase_y_placeholder_is_suppressed(self) -> None:
        self._inject_references(
            "docs/SOP/CODEX_AUTONOMY_V1.md",
            ["docs/SOP/SPRINT_00X_PHASE_Y.md"],
        )
        findings = self._run_check()
        self.assertFalse(
            any(
                f["severity"] == "warn"
                and "SPRINT_00X_PHASE_Y.md" in f.get("locator", "")
                and "does not resolve" in f.get("message", "")
                for f in findings
            ),
            f"placeholder 'SPRINT_00X_PHASE_Y.md' should be suppressed; got findings: {findings}",
        )

    def test_is_sop_template_placeholder_literal_membership(self) -> None:
        # Pure literal allow-list: only the two canonical placeholder paths
        # match; real sprint specs and lookalike strings do not.
        self.assertTrue(relay._is_sop_template_placeholder("docs/SOP/SPRINT_00X.md"))
        self.assertTrue(relay._is_sop_template_placeholder("docs/SOP/SPRINT_00X_PHASE_Y.md"))
        # A real sprint spec is not a placeholder.
        self.assertFalse(relay._is_sop_template_placeholder("docs/SOP/SPRINT_003_PHASE_2.md"))
        # Arbitrary lookalikes are not a placeholder.
        self.assertFalse(relay._is_sop_template_placeholder("docs/SOP/SPRINT_ABC.md"))
        self.assertFalse(relay._is_sop_template_placeholder("docs/SOP/SPRINT_00X_PHASE_2.md"))

    # -- Negative (still-flagged) cases -------------------------------------

    def test_genuinely_missing_doc_still_flags_warn(self) -> None:
        self._inject_references(
            "docs/SOP/OPERATING_RULES.md",
            ["docs/SOP/DEFINITELY_NOT_A_REAL_DOC.md"],
        )
        findings = self._run_check()
        self.assertTrue(
            any(
                f["severity"] == "warn"
                and "DEFINITELY_NOT_A_REAL_DOC.md" in f.get("locator", "")
                and "does not resolve" in f.get("message", "")
                for f in findings
            ),
            f"genuinely missing reference should still warn; got findings: {findings}",
        )

    def test_numbered_sprint_ref_still_flags_if_missing(self) -> None:
        # A real-shaped sprint spec that does not exist on disk must still
        # warn -- the suppression must not extend to the general SPRINT_*
        # family.
        self._inject_references(
            "docs/SOP/JOB_REGISTRY_V1.md",
            ["docs/SOP/SPRINT_042_PHASE_7.md"],
        )
        findings = self._run_check()
        self.assertTrue(
            any(
                f["severity"] == "warn"
                and "SPRINT_042_PHASE_7.md" in f.get("locator", "")
                and "does not resolve" in f.get("message", "")
                for f in findings
            ),
            f"real-shaped but missing sprint spec should still warn; got findings: {findings}",
        )


# ---------------------------------------------------------------------------
# CLI smoke (light: --help and status on a sandbox repo)
# ---------------------------------------------------------------------------


class TestCLISmoke(unittest.TestCase):
    def test_parser_builds(self) -> None:
        parser = relay._build_parser()
        # --help would call sys.exit; just confirm the parser has the subcommands.
        self.assertIn("stage", parser.format_help())
        self.assertIn("resume", parser.format_help())
        self.assertIn("status", parser.format_help())
        self.assertIn("abort", parser.format_help())
        self.assertIn("reset", parser.format_help())

    def test_main_status_on_sandbox(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp).resolve()
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
            subprocess.run(
                ["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit",
                 "--allow-empty", "-q", "-m", "init"],
                cwd=repo, check=True,
            )
            code = relay.main(["--repo-root", str(repo), "status"])
            self.assertEqual(code, relay.EXIT_CONTINUE)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
