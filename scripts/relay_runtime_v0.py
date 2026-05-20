"""Relay Runtime v0 - local, file-backed, staged runtime for Codex Autonomy v1.

Implements the canonical spec at docs/SOP/RELAY_RUNTIME_V0.md against the
upstream contracts:

- docs/SOP/CODEX_AUTONOMY_V1.md  -- protocol + relay schema (sections 14-15)
- docs/SOP/JOB_REGISTRY_V1.md    -- the four supported jobs (section 3)

Stdlib-only. No LLM calls. No control-plane writes. No network except
optional read-only git introspection. Single in-flight run at a time.

CLI:
    python scripts/relay_runtime_v0.py status
    python scripts/relay_runtime_v0.py stage <job> [job-specific args]
    python scripts/relay_runtime_v0.py resume
    python scripts/relay_runtime_v0.py abort
    python scripts/relay_runtime_v0.py reset

Canonical inconsistency noticed during implementation (to reconcile in a
later bounded control-plane pass, not this evidence-plane pass):
RELAY_RUNTIME_V0.md sections 5 and 6 enumerate five decisions/terminal
states (CONTINUE / RETRY / STOP_CLEAN / STOP_HARD / BLOCKED), but the
higher-precedence CODEX_AUTONOMY_V1.md section 15.1 enumerates four:
CONTINUE / RETRY_ALLOWED / STOP_FOR_REVIEW / BLOCKED. Per the precedence
rule in RELAY_RUNTIME_V0.md section 0, CODEX_AUTONOMY_V1 wins. This
implementation encodes the canonical four-value enum.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional, Tuple

from scripts.relay.canonical_docs import CANONICAL_DOC_PATHS

# ---------------------------------------------------------------------------
# Canonical constants. Changing these without a steward-accepted amendment
# to the upstream doc is a schema violation.
# ---------------------------------------------------------------------------

PROTOCOL = "CODEX_AUTONOMY_V1"
SCHEMA_VERSION = "1"
RETRY_BUDGET_MAX_CANONICAL = 2  # CODEX_AUTONOMY_V1 section 7

# Section 15.1 decision enum (canonical, 4 values).
DECISION_CONTINUE = "CONTINUE"
DECISION_RETRY_ALLOWED = "RETRY_ALLOWED"
DECISION_STOP_FOR_REVIEW = "STOP_FOR_REVIEW"
DECISION_BLOCKED = "BLOCKED"
ALL_DECISIONS = frozenset(
    {DECISION_CONTINUE, DECISION_RETRY_ALLOWED, DECISION_STOP_FOR_REVIEW, DECISION_BLOCKED}
)

# Section 14.2 stop_condition enum (10 values including null).
HARD_STOP_CONDITIONS = frozenset(
    {
        "PREFLIGHT_FAIL",
        "MIXED_PLANE_CONTAMINATION",
        "UNEXPECTED_CONTRACT_CHANGE",
        "REPO_STATE_DRIFT",
        "SELECTION_BOUNDARY_REACHED",
        "CONTROL_PLANE_CLOSEOUT_NEEDED",
    }
)
REVIEW_STOP_CONDITIONS = frozenset(
    {"SCOPE_AMBIGUITY", "UNCLEAR_TEST_RESULTS", "MAX_RETRIES_EXCEEDED"}
)
ALL_STOP_CONDITIONS = HARD_STOP_CONDITIONS | REVIEW_STOP_CONDITIONS

# Exit codes (RELAY_RUNTIME_V0 section 5, reconciled to canonical 4-value enum).
EXIT_CONTINUE = 0
EXIT_RETRY_ALLOWED = 10
EXIT_STOP_FOR_REVIEW = 20
EXIT_BLOCKED = 40
EXIT_REFUSAL = 2
EXIT_INTERNAL_ERROR = 1

DECISION_TO_EXIT = {
    DECISION_CONTINUE: EXIT_CONTINUE,
    DECISION_RETRY_ALLOWED: EXIT_RETRY_ALLOWED,
    DECISION_STOP_FOR_REVIEW: EXIT_STOP_FOR_REVIEW,
    DECISION_BLOCKED: EXIT_BLOCKED,
}

# Job Registry v1 section 3 names (pinned).
JOB_RUN_SLICE = "run_selected_slice_v1"
JOB_GATE_DECISION = "relay_gate_decision"
JOB_HEALTH = "codebase_health_report"
JOB_CONSISTENCY = "control_plane_consistency_check"
JOB_CLOSEOUT = "apply_control_closeout_v1"
SUPPORTED_JOBS = frozenset(
    {JOB_RUN_SLICE, JOB_GATE_DECISION, JOB_HEALTH, JOB_CONSISTENCY, JOB_CLOSEOUT}
)

# State machine.
STATE_IDLE = "idle"
STATE_STAGED_FOR_WORKER = "staged_for_worker"
STATE_VALIDATING = "validating"
STATE_DECIDING = "deciding"
STATE_RETRY_WAITING = "retry_waiting"
STATE_DECIDED_CONTINUE = "decided_continue"
STATE_DECIDED_RETRY_ALLOWED = "decided_retry_allowed"
STATE_DECIDED_STOP_FOR_REVIEW = "decided_stop_for_review"
STATE_DECIDED_BLOCKED = "decided_blocked"
STATE_ABORTED = "aborted"
NON_TERMINAL_STATES = frozenset(
    {STATE_IDLE, STATE_STAGED_FOR_WORKER, STATE_VALIDATING, STATE_DECIDING, STATE_RETRY_WAITING}
)
TERMINAL_STATES = frozenset(
    {
        STATE_DECIDED_CONTINUE,
        STATE_DECIDED_RETRY_ALLOWED,
        STATE_DECIDED_STOP_FOR_REVIEW,
        STATE_DECIDED_BLOCKED,
        STATE_ABORTED,
    }
)
DECISION_TO_STATE = {
    DECISION_CONTINUE: STATE_DECIDED_CONTINUE,
    DECISION_RETRY_ALLOWED: STATE_DECIDED_RETRY_ALLOWED,
    DECISION_STOP_FOR_REVIEW: STATE_DECIDED_STOP_FOR_REVIEW,
    DECISION_BLOCKED: STATE_DECIDED_BLOCKED,
}

# Section 14.1 field enums.
DECLARED_PLANES = frozenset({"PRODUCT-PLANE", "EVIDENCE-PLANE"})
PYTEST_STATUSES = frozenset({"PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"})
UI_PRIMARY_STATUSES = frozenset({"PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN"})
UI_CONDITIONAL_STATUSES = frozenset({"PASS", "FAIL", "INCONCLUSIVE", "NOT_RUN", "NOT_REQUIRED"})
VALIDATION_CLASSIFICATIONS = frozenset(
    {"deterministic", "environment-sensitive", "live-data-sensitive", "mixed"}
)
PROMOTION_METHODS = frozenset({"fast-forward", "merge"})  # plus None handled separately


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def _iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _read_json(path: Path, default: Any = None) -> Any:
    try:
        with path.open("r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)


def _run_git(repo: Path, args: list[str]) -> Tuple[str, int]:
    proc = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=False
    )
    return (proc.stdout or "").strip(), int(proc.returncode)


def _repo_root(start: Path) -> Optional[Path]:
    out, code = _run_git(start, ["rev-parse", "--show-toplevel"])
    if code != 0 or not out:
        return None
    return Path(out)


# ---------------------------------------------------------------------------
# Section 14.1 schema validation.
#
# Returns a list of human-readable violation strings.  An empty list means
# the payload is structurally valid.  The caller must additionally run
# invariant checks (section 14.3) before treating the payload as safe.
# ---------------------------------------------------------------------------


def _is_bool(v: Any) -> bool:
    return isinstance(v, bool)


def _is_str(v: Any) -> bool:
    return isinstance(v, str)


def _is_int(v: Any) -> bool:
    # Exclude bool (which is a subclass of int in Python).
    return isinstance(v, int) and not isinstance(v, bool)


def _is_str_or_none(v: Any) -> bool:
    return v is None or isinstance(v, str)


def _require(obj: Any, key: str, out: list[str], path: str) -> bool:
    if not isinstance(obj, dict) or key not in obj:
        out.append(f"{path}: missing required field '{key}'")
        return False
    return True


def validate_relay_result_schema(payload: Any) -> list[str]:
    """Validate a payload against CODEX_AUTONOMY_V1.md section 14.1.

    Checks structural shape and enum values. Does not enforce section 14.3
    cross-field invariants (see check_invariants for that).
    """

    v: list[str] = []

    if not isinstance(payload, dict):
        return ["payload is not a JSON object"]

    top_level = (
        "protocol",
        "schema_version",
        "slice_id",
        "run_id",
        "declared_plane",
        "build_branch",
        "baseline_branch",
        "baseline_tip_before",
        "baseline_tip_after",
        "product_commit_sha",
        "preflight",
        "retry_count",
        "retry_budget_max",
        "retry_budget_exhausted",
        "tests",
        "tree_cleanliness",
        "promotion",
        "stop_condition",
        "ready_for_control_closeout",
        "safe_to_continue",
        "artifacts",
        "notes",
    )
    for key in top_level:
        _require(payload, key, v, "payload")

    def _check(cond: bool, msg: str) -> None:
        if not cond:
            v.append(msg)

    if "protocol" in payload:
        _check(payload["protocol"] == PROTOCOL, f"protocol must be '{PROTOCOL}'")
    if "schema_version" in payload:
        _check(
            payload["schema_version"] == SCHEMA_VERSION,
            f"schema_version must be '{SCHEMA_VERSION}' (got {payload.get('schema_version')!r})",
        )
    if "slice_id" in payload:
        _check(_is_str(payload["slice_id"]) and payload["slice_id"].strip(), "slice_id must be a non-empty string")
    if "run_id" in payload:
        _check(_is_str(payload["run_id"]) and payload["run_id"].strip(), "run_id must be a non-empty string")
    if "declared_plane" in payload:
        _check(
            payload["declared_plane"] in DECLARED_PLANES,
            f"declared_plane must be one of {sorted(DECLARED_PLANES)}",
        )
    for field in ("build_branch", "baseline_branch", "baseline_tip_before", "baseline_tip_after"):
        if field in payload:
            _check(_is_str(payload[field]) and payload[field].strip(), f"{field} must be a non-empty string")
    if "product_commit_sha" in payload:
        _check(
            _is_str_or_none(payload["product_commit_sha"]),
            "product_commit_sha must be a string or null",
        )

    # preflight subobject.
    pf = payload.get("preflight")
    if isinstance(pf, dict):
        for key in ("build_allowed", "tree_clean", "untracked_canonical_docs", "mixed_plane_dirty"):
            if not _require(pf, key, v, "preflight"):
                continue
            _check(_is_bool(pf[key]), f"preflight.{key} must be a bool")
        if _require(pf, "blocker", v, "preflight"):
            _check(_is_str_or_none(pf["blocker"]), "preflight.blocker must be a string or null")
    elif "preflight" in payload:
        v.append("preflight must be an object")

    # retry numbers.
    for key in ("retry_count", "retry_budget_max"):
        if key in payload:
            _check(_is_int(payload[key]) and payload[key] >= 0, f"{key} must be a non-negative integer")
    if "retry_budget_exhausted" in payload:
        _check(_is_bool(payload["retry_budget_exhausted"]), "retry_budget_exhausted must be a bool")

    # tests subobject.
    tests = payload.get("tests")
    if isinstance(tests, dict):
        if _require(tests, "pytest_status", v, "tests"):
            _check(
                tests["pytest_status"] in PYTEST_STATUSES,
                f"tests.pytest_status must be one of {sorted(PYTEST_STATUSES)}",
            )
        if _require(tests, "pytest_count", v, "tests"):
            _check(_is_int(tests["pytest_count"]) and tests["pytest_count"] >= 0, "tests.pytest_count must be a non-negative integer")
        if _require(tests, "ui_smoke_primary_status", v, "tests"):
            _check(
                tests["ui_smoke_primary_status"] in UI_PRIMARY_STATUSES,
                f"tests.ui_smoke_primary_status must be one of {sorted(UI_PRIMARY_STATUSES)}",
            )
        if _require(tests, "ui_smoke_conditional_status", v, "tests"):
            _check(
                tests["ui_smoke_conditional_status"] in UI_CONDITIONAL_STATUSES,
                f"tests.ui_smoke_conditional_status must be one of {sorted(UI_CONDITIONAL_STATUSES)}",
            )
        if _require(tests, "ui_inspection_evidence_present", v, "tests"):
            _check(_is_bool(tests["ui_inspection_evidence_present"]), "tests.ui_inspection_evidence_present must be a bool")
        if _require(tests, "validation_classification", v, "tests"):
            _check(
                tests["validation_classification"] in VALIDATION_CLASSIFICATIONS,
                f"tests.validation_classification must be one of {sorted(VALIDATION_CLASSIFICATIONS)}",
            )
    elif "tests" in payload:
        v.append("tests must be an object")

    # tree_cleanliness subobject.
    tc = payload.get("tree_cleanliness")
    if isinstance(tc, dict):
        for key in ("build_branch_clean", "mixed_plane_residue", "untracked_canonical_docs"):
            if _require(tc, key, v, "tree_cleanliness"):
                _check(_is_bool(tc[key]), f"tree_cleanliness.{key} must be a bool")
    elif "tree_cleanliness" in payload:
        v.append("tree_cleanliness must be an object")

    # promotion subobject.
    promo = payload.get("promotion")
    if isinstance(promo, dict):
        for key in ("attempted", "performed", "ancestor_check_pass"):
            if _require(promo, key, v, "promotion"):
                _check(_is_bool(promo[key]), f"promotion.{key} must be a bool")
        if _require(promo, "method", v, "promotion"):
            m = promo["method"]
            _check(
                m is None or m in PROMOTION_METHODS,
                f"promotion.method must be null or one of {sorted(PROMOTION_METHODS)}",
            )
    elif "promotion" in payload:
        v.append("promotion must be an object")

    # stop_condition.
    if "stop_condition" in payload:
        sc = payload["stop_condition"]
        _check(
            sc is None or sc in ALL_STOP_CONDITIONS,
            f"stop_condition must be null or one of {sorted(ALL_STOP_CONDITIONS)}",
        )

    # booleans.
    for key in ("ready_for_control_closeout", "safe_to_continue"):
        if key in payload:
            _check(_is_bool(payload[key]), f"{key} must be a bool")

    # artifacts subobject.
    art = payload.get("artifacts")
    if isinstance(art, dict):
        for key in ("ui_smoke_manifest", "ui_smoke_screenshot", "run_log"):
            if _require(art, key, v, "artifacts"):
                _check(_is_str_or_none(art[key]), f"artifacts.{key} must be a string or null")
    elif "artifacts" in payload:
        v.append("artifacts must be an object")

    # notes (soft length cap at 280 chars per section 14.1).
    if "notes" in payload:
        _check(_is_str(payload["notes"]), "notes must be a string")
        if _is_str(payload.get("notes")) and len(payload["notes"]) > 280:
            v.append("notes must be <= 280 chars")

    return v


# ---------------------------------------------------------------------------
# Section 14.3 invariant enforcement.
# ---------------------------------------------------------------------------


def check_invariants(payload: dict) -> list[str]:
    """Cross-field invariants from CODEX_AUTONOMY_V1.md section 14.3.

    Assumes schema-level validation has already passed (no KeyError-safe
    paranoia here; caller must run validate_relay_result_schema first).
    """

    v: list[str] = []

    # retry_count within [0, retry_budget_max].
    rc = payload["retry_count"]
    rbm = payload["retry_budget_max"]
    if rc > rbm:
        v.append(f"retry_count ({rc}) exceeds retry_budget_max ({rbm})")
    if rbm > RETRY_BUDGET_MAX_CANONICAL:
        v.append(
            f"retry_budget_max ({rbm}) exceeds canonical max ({RETRY_BUDGET_MAX_CANONICAL}) per CODEX_AUTONOMY_V1 section 7"
        )

    # retry_budget_exhausted iff retry_count == retry_budget_max AND validation not green.
    exhausted = payload["retry_budget_exhausted"]
    validation_green = (
        payload["stop_condition"] is None
        and payload["tests"]["pytest_status"] == "PASS"
        and payload["tests"]["ui_smoke_primary_status"] == "PASS"
        and payload["tests"]["ui_smoke_conditional_status"] in ("PASS", "NOT_REQUIRED")
    )
    at_cap = rc == rbm
    expected_exhausted = at_cap and not validation_green
    if exhausted and not expected_exhausted:
        v.append(
            "retry_budget_exhausted=true but not (retry_count==retry_budget_max AND validation not green)"
        )
    if expected_exhausted and not exhausted:
        v.append(
            "retry_budget_exhausted=false but retry_count==retry_budget_max AND validation not green"
        )

    # promotion.performed requires all tree_cleanliness gates green.
    promo = payload["promotion"]
    tc = payload["tree_cleanliness"]
    if promo["performed"]:
        if not tc["build_branch_clean"]:
            v.append("promotion.performed=true but tree_cleanliness.build_branch_clean=false")
        if tc["mixed_plane_residue"]:
            v.append("promotion.performed=true but tree_cleanliness.mixed_plane_residue=true")
        if tc["untracked_canonical_docs"]:
            v.append("promotion.performed=true but tree_cleanliness.untracked_canonical_docs=true")

    # ready_for_control_closeout requires promotion.performed AND stop_condition is null.
    if payload["ready_for_control_closeout"]:
        if not promo["performed"]:
            v.append("ready_for_control_closeout=true but promotion.performed=false")
        if payload["stop_condition"] is not None:
            v.append(
                f"ready_for_control_closeout=true but stop_condition={payload['stop_condition']!r}"
            )

    # safe_to_continue requires stop_condition null AND no tree residues.
    if payload["safe_to_continue"]:
        if payload["stop_condition"] is not None:
            v.append(f"safe_to_continue=true but stop_condition={payload['stop_condition']!r}")
        if tc["mixed_plane_residue"]:
            v.append("safe_to_continue=true but tree_cleanliness.mixed_plane_residue=true")
        if tc["untracked_canonical_docs"]:
            v.append("safe_to_continue=true but tree_cleanliness.untracked_canonical_docs=true")

    # promotion.attempted must be true if performed is true (self-consistency).
    if promo["performed"] and not promo["attempted"]:
        v.append("promotion.performed=true but promotion.attempted=false")

    # promotion.method must not be null if performed is true.
    if promo["performed"] and promo["method"] is None:
        v.append("promotion.performed=true but promotion.method is null")

    return v


# ---------------------------------------------------------------------------
# Section 15.2 decision engine. Top-down; first matching rule wins.
# ---------------------------------------------------------------------------


def decide(payload: Any) -> dict:
    """Apply section 15.2 decision rules to a payload.

    Returns a record:
      {
        "decision": "<enum>",
        "rule_matched": "<short rule id>",
        "reason":   "<short factual string>",
        "schema_violations":    [str, ...],   # empty if ok
        "invariant_violations": [str, ...],   # empty if ok
      }
    """

    schema_v = validate_relay_result_schema(payload)
    invariant_v: list[str] = []
    if not schema_v:
        invariant_v = check_invariants(payload)

    # Rule 1: schema / invariant violation -> BLOCKED.
    if schema_v or invariant_v:
        reason_bits = []
        if schema_v:
            reason_bits.append(f"{len(schema_v)} schema violation(s): {schema_v[0]!r}")
        if invariant_v:
            reason_bits.append(f"{len(invariant_v)} invariant violation(s): {invariant_v[0]!r}")
        return {
            "decision": DECISION_BLOCKED,
            "rule_matched": "15.2 rule 1",
            "reason": "schema/invariant violation: " + "; ".join(reason_bits),
            "schema_violations": schema_v,
            "invariant_violations": invariant_v,
        }

    sc = payload["stop_condition"]
    tests = payload["tests"]
    tc = payload["tree_cleanliness"]
    promo = payload["promotion"]

    # Rule 2: hard section 8 conditions -> BLOCKED.
    if sc in HARD_STOP_CONDITIONS:
        return {
            "decision": DECISION_BLOCKED,
            "rule_matched": "15.2 rule 2",
            "reason": f"hard section 8 stop_condition={sc}",
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 3: retry budget exhausted -> STOP_FOR_REVIEW.
    if sc == "MAX_RETRIES_EXCEEDED" or payload["retry_budget_exhausted"]:
        return {
            "decision": DECISION_STOP_FOR_REVIEW,
            "rule_matched": "15.2 rule 3",
            "reason": "retry budget exhausted",
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 4: judgment-required stops -> STOP_FOR_REVIEW.
    if sc in ("SCOPE_AMBIGUITY", "UNCLEAR_TEST_RESULTS"):
        return {
            "decision": DECISION_STOP_FOR_REVIEW,
            "rule_matched": "15.2 rule 4",
            "reason": f"judgment-required stop_condition={sc}",
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 5: in-slice repair eligible -> RETRY_ALLOWED.
    any_test_failed = (
        tests["pytest_status"] == "FAIL"
        or tests["ui_smoke_primary_status"] == "FAIL"
        or tests["ui_smoke_conditional_status"] == "FAIL"
    )
    if (
        sc is None
        and any_test_failed
        and payload["retry_count"] < payload["retry_budget_max"]
        and not tc["mixed_plane_residue"]
        and tests["validation_classification"] == "deterministic"
    ):
        return {
            "decision": DECISION_RETRY_ALLOWED,
            "rule_matched": "15.2 rule 5",
            "reason": (
                f"deterministic test FAIL with retry_count={payload['retry_count']} "
                f"< retry_budget_max={payload['retry_budget_max']}"
            ),
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 6: inconclusive / non-deterministic without hard stop -> STOP_FOR_REVIEW.
    any_test_inconclusive = (
        tests["pytest_status"] == "INCONCLUSIVE"
        or tests["ui_smoke_primary_status"] == "INCONCLUSIVE"
        or tests["ui_smoke_conditional_status"] == "INCONCLUSIVE"
    )
    any_test_non_pass = (
        tests["pytest_status"] != "PASS"
        or tests["ui_smoke_primary_status"] != "PASS"
        or (tests["ui_smoke_conditional_status"] not in ("PASS", "NOT_REQUIRED"))
    )
    non_deterministic = tests["validation_classification"] in (
        "environment-sensitive",
        "live-data-sensitive",
        "mixed",
    )
    if sc is None and (any_test_inconclusive or (non_deterministic and any_test_non_pass)):
        return {
            "decision": DECISION_STOP_FOR_REVIEW,
            "rule_matched": "15.2 rule 6",
            "reason": "inconclusive or non-deterministic validation without hard stop",
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 7: clean closure -> CONTINUE.
    if (
        sc is None
        and promo["performed"]
        and payload["ready_for_control_closeout"]
        and payload["safe_to_continue"]
        and tests["pytest_status"] == "PASS"
        and tests["ui_smoke_primary_status"] == "PASS"
        and tests["ui_smoke_conditional_status"] in ("PASS", "NOT_REQUIRED")
        and tests["ui_inspection_evidence_present"]
        and tc["build_branch_clean"]
    ):
        return {
            "decision": DECISION_CONTINUE,
            "rule_matched": "15.2 rule 7",
            "reason": "clean closure; hand back to steward for CONTROL-CLOSEOUT",
            "schema_violations": [],
            "invariant_violations": [],
        }

    # Rule 8: default / unclassified -> STOP_FOR_REVIEW.
    return {
        "decision": DECISION_STOP_FOR_REVIEW,
        "rule_matched": "15.2 rule 8",
        "reason": "unclassified; safe default is steward review",
        "schema_violations": [],
        "invariant_violations": [],
    }


# ---------------------------------------------------------------------------
# State machine persistence and paths.
# ---------------------------------------------------------------------------


class Runtime:
    """File-backed runtime state.  Instances are cheap; every method persists."""

    def __init__(self, repo_root: Path, artifacts_root: Optional[Path] = None) -> None:
        self.repo_root = repo_root
        self.artifacts_root = artifacts_root or (repo_root / "artifacts" / "relay")

    @property
    def state_dir(self) -> Path:
        return self.artifacts_root / "state"

    @property
    def runs_dir(self) -> Path:
        return self.artifacts_root / "runs"

    @property
    def run_state_path(self) -> Path:
        return self.state_dir / "run_state.json"

    @property
    def current_job_path(self) -> Path:
        return self.state_dir / "current_job.json"

    @property
    def last_decision_path(self) -> Path:
        return self.state_dir / "last_decision.json"

    def run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def events_log_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "events.log"

    def load_run_state(self) -> dict:
        default = {"status": STATE_IDLE, "run_id": None, "job": None, "updated_at": None}
        raw = _read_json(self.run_state_path, default)
        if not isinstance(raw, dict):
            return default
        # Backfill any missing keys.
        for key, val in default.items():
            raw.setdefault(key, val)
        return raw

    def save_run_state(self, state: dict) -> None:
        state["updated_at"] = _iso_now()
        _write_json(self.run_state_path, state)

    def log_event(self, run_id: str, message: str) -> None:
        p = self.events_log_path(run_id)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(f"[{_iso_now()}] {message}\n")


# ---------------------------------------------------------------------------
# Preflight for slice staging (RELAY_RUNTIME_V0 section 8).
# ---------------------------------------------------------------------------


def slice_preflight(repo_root: Path, baseline_branch: str, build_branch: str) -> list[str]:
    """Return list of preflight violations (empty list -> ok)."""

    violations: list[str] = []

    # Must be a git repo.
    toplevel, code = _run_git(repo_root, ["rev-parse", "--show-toplevel"])
    if code != 0:
        violations.append("repo_root is not a git repository")
        return violations

    # Tree must be clean (no tracked modifications, no staged changes).
    status_out, code = _run_git(repo_root, ["status", "--porcelain=v1"])
    if code != 0:
        violations.append("git status failed")
        return violations
    dirty_tracked = []
    untracked_canonical = []
    for line in status_out.splitlines():
        if not line:
            continue
        code2 = line[:2]
        path = line[3:].strip()
        # Untracked marker.
        if code2 == "??":
            # Untracked canonical docs (docs/SOP/** or docs/CONTROL_PLANE/**) are a hard stop.
            norm = path.replace("\\", "/")
            if norm.startswith("docs/SOP/") or norm.startswith("docs/CONTROL_PLANE/"):
                untracked_canonical.append(norm)
            # Other untracked paths are ignored by preflight (operator sandbox).
            continue
        # Any non-"??" status line is a tracked change -- blocks staging.
        dirty_tracked.append(f"{code2} {path}")
    if dirty_tracked:
        violations.append(
            f"tracked tree not clean: {len(dirty_tracked)} change(s); first: {dirty_tracked[0]!r}"
        )
    if untracked_canonical:
        violations.append(
            f"untracked canonical docs present (count={len(untracked_canonical)}): {untracked_canonical[0]!r}"
        )

    # build_branch must not already exist locally.
    _, exists_code = _run_git(repo_root, ["rev-parse", "--verify", "--quiet", f"refs/heads/{build_branch}"])
    if exists_code == 0:
        violations.append(f"build_branch {build_branch!r} already exists locally")

    # baseline_branch must exist locally.
    _, base_code = _run_git(repo_root, ["rev-parse", "--verify", "--quiet", f"refs/heads/{baseline_branch}"])
    if base_code != 0:
        violations.append(f"baseline_branch {baseline_branch!r} does not exist locally")

    return violations


# ---------------------------------------------------------------------------
# Job dispatchers.
# ---------------------------------------------------------------------------


def dispatch_stage_slice(
    runtime: Runtime,
    slice_id: str,
    sprint_spec_path: str,
    declared_plane: str,
    baseline_branch: str,
    build_branch: str,
    retry_budget_max: int = RETRY_BUDGET_MAX_CANONICAL,
) -> Tuple[int, str]:
    """Stage a run_selected_slice_v1 task for an external worker."""

    state = runtime.load_run_state()
    if state["status"] in NON_TERMINAL_STATES and state["status"] != STATE_IDLE:
        return (
            EXIT_REFUSAL,
            f"refusal: a run is already in flight (status={state['status']}, run_id={state['run_id']})",
        )
    if state["status"] in TERMINAL_STATES:
        return (
            EXIT_REFUSAL,
            f"refusal: last run reached terminal state {state['status']}; run 'reset' first",
        )

    if declared_plane not in DECLARED_PLANES:
        return EXIT_REFUSAL, f"refusal: declared_plane must be one of {sorted(DECLARED_PLANES)}"
    if not slice_id.strip() or not sprint_spec_path.strip() or not build_branch.strip():
        return EXIT_REFUSAL, "refusal: slice_id, sprint_spec_path, and build_branch must be non-empty"
    if retry_budget_max < 0 or retry_budget_max > RETRY_BUDGET_MAX_CANONICAL:
        return (
            EXIT_REFUSAL,
            f"refusal: retry_budget_max must be between 0 and {RETRY_BUDGET_MAX_CANONICAL}",
        )

    spec_abs = (runtime.repo_root / sprint_spec_path).resolve()
    if not spec_abs.is_file():
        return EXIT_REFUSAL, f"refusal: sprint_spec_path does not exist: {sprint_spec_path}"

    pf_violations = slice_preflight(runtime.repo_root, baseline_branch, build_branch)
    if pf_violations:
        # Record a terminal state so the operator can see and reset.
        run_id = _now_stamp()
        runtime.run_dir(run_id).mkdir(parents=True, exist_ok=True)
        for vmsg in pf_violations:
            runtime.log_event(run_id, f"preflight violation: {vmsg}")
        runtime.save_run_state(
            {
                "status": STATE_DECIDED_STOP_FOR_REVIEW,
                "run_id": run_id,
                "job": JOB_RUN_SLICE,
                "reason": "preflight_fail",
            }
        )
        return (
            EXIT_STOP_FOR_REVIEW,
            "preflight_fail (mapped to STOP_FOR_REVIEW):\n  - " + "\n  - ".join(pf_violations),
        )

    run_id = _now_stamp()
    runtime.run_dir(run_id).mkdir(parents=True, exist_ok=True)

    task_envelope = {
        "protocol": PROTOCOL,
        "schema_version": SCHEMA_VERSION,
        "job": JOB_RUN_SLICE,
        "run_id": run_id,
        "slice_id": slice_id,
        "sprint_spec_path": sprint_spec_path,
        "declared_plane": declared_plane,
        "baseline_branch": baseline_branch,
        "build_branch": build_branch,
        "retry_budget_max": retry_budget_max,
        "expected_relay_result_path": str(
            (runtime.run_dir(run_id) / "relay_result.json").relative_to(runtime.repo_root)
        ).replace("\\", "/"),
        "staged_at": _iso_now(),
    }
    _write_json(runtime.run_dir(run_id) / "task_envelope.json", task_envelope)
    _write_json(runtime.current_job_path, task_envelope)
    runtime.save_run_state(
        {
            "status": STATE_STAGED_FOR_WORKER,
            "run_id": run_id,
            "job": JOB_RUN_SLICE,
            "slice_id": slice_id,
            "build_branch": build_branch,
            "baseline_branch": baseline_branch,
            "attempt": 0,
        }
    )
    runtime.log_event(run_id, f"staged {slice_id} for worker on {build_branch}")

    msg = (
        f"Staged run_selected_slice_v1 run_id={run_id} slice={slice_id}.\n"
        f"  envelope:  {task_envelope['expected_relay_result_path'].rsplit('/', 1)[0]}/task_envelope.json\n"
        f"  expected:  {task_envelope['expected_relay_result_path']}\n"
        f"Worker performs the slice per CODEX_AUTONOMY_V1 section 2 and writes\n"
        f"the relay_result.json at the path above.  Then run:\n"
        f"  python scripts/relay_runtime_v0.py resume"
    )
    return EXIT_CONTINUE, msg


def dispatch_resume(runtime: Runtime) -> Tuple[int, str]:
    """Consume the staged slice's relay_result.json and apply section 15."""

    state = runtime.load_run_state()
    if state["status"] not in (STATE_STAGED_FOR_WORKER, STATE_RETRY_WAITING):
        return (
            EXIT_REFUSAL,
            f"refusal: no slice staged (current status={state['status']})",
        )

    run_id = state["run_id"]
    result_path = runtime.run_dir(run_id) / "relay_result.json"
    if not result_path.is_file():
        return (
            EXIT_REFUSAL,
            f"refusal: relay_result.json not found at {result_path}; worker has not finished",
        )

    # Attempt counter (for durable attempt artifacts).
    attempt = int(state.get("attempt") or 0) + 1

    # Transition to validating.
    state["status"] = STATE_VALIDATING
    runtime.save_run_state(state)
    runtime.log_event(run_id, "state=validating; loading relay_result.json")

    try:
        raw_text = result_path.read_text(encoding="utf-8-sig")
        payload = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        # Malformed JSON -> BLOCKED.
        decision_record = {
            "decision": DECISION_BLOCKED,
            "rule_matched": "15.2 rule 1",
            "reason": f"relay_result.json is not valid JSON: {exc}",
            "schema_violations": ["payload is not valid JSON"],
            "invariant_violations": [],
            "generated_at": _iso_now(),
            "run_id": run_id,
        }
        _finalize_decision(runtime, state, decision_record)
        return DECISION_TO_EXIT[DECISION_BLOCKED], _format_decision(decision_record)

    # Preserve the raw payload for this attempt (even if a later retry overwrites relay_result.json).
    attempt_path = runtime.run_dir(run_id) / f"relay_result_attempt_{attempt}.json"
    attempt_path.write_text(raw_text, encoding="utf-8")

    # Transition to deciding.
    state["status"] = STATE_DECIDING
    runtime.save_run_state(state)
    runtime.log_event(run_id, "state=deciding; applying section 15")

    dec = decide(payload)
    dec["generated_at"] = _iso_now()
    dec["run_id"] = run_id

    # Persist attempt decision record.
    _write_json(runtime.run_dir(run_id) / f"decision_attempt_{attempt}.json", dec)
    _write_json(runtime.last_decision_path, dec)

    if dec["decision"] == DECISION_RETRY_ALLOWED:
        # Keep run non-terminal; allow an external orchestrator to re-run the worker.
        state["status"] = STATE_RETRY_WAITING
        state["attempt"] = attempt
        state["last_decision"] = dec["decision"]
        state["last_rule_matched"] = dec["rule_matched"]
        runtime.save_run_state(state)
        runtime.log_event(run_id, f"decision=RETRY_ALLOWED via {dec['rule_matched']}; awaiting worker retry")
        msg = _format_decision(dec) + (
            "\n\nretry: allowed. Re-run the worker for the same slice, then overwrite relay_result.json and run:\n"
            "  python scripts/relay_runtime_v0.py resume"
        )
        return DECISION_TO_EXIT[dec["decision"]], msg

    _finalize_decision(runtime, state, dec)
    return DECISION_TO_EXIT[dec["decision"]], _format_decision(dec)


def _finalize_decision(runtime: Runtime, state: dict, dec: dict) -> None:
    run_id = state["run_id"]
    _write_json(runtime.run_dir(run_id) / "decision.json", dec)
    _write_json(runtime.last_decision_path, dec)
    state["status"] = DECISION_TO_STATE[dec["decision"]]
    state["last_decision"] = dec["decision"]
    state["last_rule_matched"] = dec["rule_matched"]
    runtime.save_run_state(state)
    runtime.log_event(
        run_id,
        f"decision={dec['decision']} via {dec['rule_matched']}; state={state['status']}",
    )


def _format_decision(dec: dict) -> str:
    lines = [
        f"decision:       {dec['decision']}",
        f"rule_matched:   {dec['rule_matched']}",
        f"reason:         {dec['reason']}",
    ]
    if dec.get("schema_violations"):
        lines.append(f"schema_violations:    {len(dec['schema_violations'])}")
        for msg in dec["schema_violations"][:5]:
            lines.append(f"  - {msg}")
        if len(dec["schema_violations"]) > 5:
            lines.append(f"  ... {len(dec['schema_violations']) - 5} more")
    if dec.get("invariant_violations"):
        lines.append(f"invariant_violations: {len(dec['invariant_violations'])}")
        for msg in dec["invariant_violations"][:5]:
            lines.append(f"  - {msg}")
        if len(dec["invariant_violations"]) > 5:
            lines.append(f"  ... {len(dec['invariant_violations']) - 5} more")
    return "\n".join(lines)


def dispatch_status(runtime: Runtime) -> Tuple[int, str]:
    state = runtime.load_run_state()
    last_dec = _read_json(runtime.last_decision_path, default=None)
    lines = [
        f"status:     {state['status']}",
        f"run_id:     {state.get('run_id')}",
        f"job:        {state.get('job')}",
        f"updated_at: {state.get('updated_at')}",
    ]
    if state.get("slice_id"):
        lines.append(f"slice_id:   {state['slice_id']}")
    if state.get("build_branch"):
        lines.append(f"build_branch:    {state['build_branch']}")
    if state.get("baseline_branch"):
        lines.append(f"baseline_branch: {state['baseline_branch']}")
    if state.get("last_decision"):
        lines.append(f"last_decision:   {state['last_decision']} ({state.get('last_rule_matched','')})")
    if last_dec and not state.get("last_decision"):
        lines.append(f"last_decision (from disk): {last_dec.get('decision')}")
    return EXIT_CONTINUE, "\n".join(lines)


def dispatch_abort(runtime: Runtime) -> Tuple[int, str]:
    state = runtime.load_run_state()
    if state["status"] in TERMINAL_STATES:
        return EXIT_REFUSAL, f"refusal: already terminal (status={state['status']})"
    old = state["status"]
    state["status"] = STATE_ABORTED
    runtime.save_run_state(state)
    if state.get("run_id"):
        runtime.log_event(state["run_id"], f"operator abort from state={old}")
    return EXIT_REFUSAL, f"aborted (previous status={old})"


def dispatch_reset(runtime: Runtime) -> Tuple[int, str]:
    state = runtime.load_run_state()
    if state["status"] == STATE_IDLE:
        return EXIT_CONTINUE, "already idle; no-op"
    if state["status"] in NON_TERMINAL_STATES:
        return (
            EXIT_REFUSAL,
            f"refusal: non-terminal state {state['status']}; run 'abort' first",
        )
    # Terminal -> idle.
    runtime.save_run_state({"status": STATE_IDLE, "run_id": None, "job": None})
    # Best-effort: clear staged job pointer.
    try:
        if runtime.current_job_path.exists():
            runtime.current_job_path.unlink()
    except OSError:
        pass
    return EXIT_CONTINUE, "reset to idle"


# ---------------------------------------------------------------------------
# Inline read-only jobs.
# ---------------------------------------------------------------------------


def dispatch_codebase_health_report(runtime: Runtime, baseline_branch: Optional[str] = None) -> Tuple[int, str]:
    repo = runtime.repo_root
    head, _ = _run_git(repo, ["rev-parse", "HEAD"])
    head_short, _ = _run_git(repo, ["rev-parse", "--short", "HEAD"])
    branch, _ = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"])
    status_out, _ = _run_git(repo, ["status", "--porcelain=v1"])

    tracked_modified = 0
    staged = 0
    untracked = 0
    untracked_paths: list[str] = []
    for line in status_out.splitlines():
        if not line:
            continue
        code2 = line[:2]
        path = line[3:].strip()
        if code2 == "??":
            untracked += 1
            untracked_paths.append(path)
        else:
            if code2[0] != " " and code2[0] != "?":
                staged += 1
            if code2[1] != " " and code2[1] != "?":
                tracked_modified += 1

    canonical_present = {
        p: (repo / p).is_file() for p in CANONICAL_DOC_PATHS
    }

    orchestrator_dir = repo / "orchestrator"
    orch_tracked_out, _ = _run_git(repo, ["ls-files", "orchestrator"])
    orchestrator_status = {
        "on_disk": orchestrator_dir.exists(),
        "tracked_file_count": len([p for p in orch_tracked_out.splitlines() if p]),
        "gitignored": False,
    }
    if orchestrator_dir.exists():
        # Probe one child to confirm ignore.
        probe = orchestrator_dir / "relay.py"
        if probe.exists():
            _, ci_code = _run_git(repo, ["check-ignore", "-q", "orchestrator/relay.py"])
            orchestrator_status["gitignored"] = ci_code == 0

    report = {
        "protocol": PROTOCOL,
        "job": JOB_HEALTH,
        "repo_root": str(repo),
        "branch": branch or None,
        "head_sha": head or None,
        "head_sha_short": head_short or None,
        "tree_cleanliness": {
            "tracked_modified": tracked_modified,
            "staged": staged,
            "untracked": untracked,
            "untracked_paths": untracked_paths,
        },
        "canonical_docs_present": canonical_present,
        "orchestrator_status": orchestrator_status,
        "known_unresolved_items": [
            p for p in untracked_paths if not _looks_like_artifact(p)
        ],
        "generated_at": _iso_now(),
    }

    ts = _now_stamp()
    out_path = repo / "artifacts" / "health" / ts / "codebase_health_report.json"
    _write_json(out_path, report)

    lines = [
        f"codebase_health_report  (artifact: {out_path.relative_to(repo)})",
        f"  branch:          {report['branch']}",
        f"  head:            {report['head_sha_short']}",
        f"  tree:            {tracked_modified} modified, {staged} staged, {untracked} untracked",
        f"  canonical_docs:  {sum(canonical_present.values())}/{len(canonical_present)} present",
        f"  orchestrator:    on_disk={orchestrator_status['on_disk']}, "
        f"tracked={orchestrator_status['tracked_file_count']}, "
        f"gitignored={orchestrator_status['gitignored']}",
    ]
    return EXIT_CONTINUE, "\n".join(lines)


def _looks_like_artifact(path: str) -> bool:
    norm = path.replace("\\", "/")
    return norm.startswith("artifacts/")


_HEADING_RE = re.compile(r"^(#{1,6})\s+(\d+(?:\.\d+)*)?[\.\)]?\s*(.*)$", re.UNICODE)
_LINK_PATH_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\.(?:md|py|json|txt))`")

# Intentional SOP template placeholders. These literal strings appear inside
# canonical docs (e.g. `docs/SOP/SPRINT_TEMPLATE.md`, `docs/SOP/OPERATING_RULES.md`,
# `docs/SOP/CODEX_AUTONOMY_V1.md`, `docs/SOP/JOB_REGISTRY_V1.md`) to describe
# the *shape* of a sprint-spec path, using the template variable tokens `00X`
# (slot for a sprint number) and `_Y` (slot for a phase number). They never
# name a real doc on disk and must not be reported as unresolved references.
#
# Rule scope is deliberately narrow: an explicit, exhaustive allow-list of
# literal placeholder paths -- not a pattern over arbitrary `SPRINT_*.md`
# references. Adding a new placeholder token requires a steward-accepted
# amendment to this list.
_SOP_SPRINT_TEMPLATE_PLACEHOLDERS = frozenset(
    {
        "docs/SOP/SPRINT_00X.md",
        "docs/SOP/SPRINT_00X_PHASE_Y.md",
    }
)


def _is_sop_template_placeholder(norm_path: str) -> bool:
    """Return True iff `norm_path` is an intentional SOP template placeholder.

    `norm_path` must already be forward-slash normalized. The check is a pure
    literal membership test against `_SOP_SPRINT_TEMPLATE_PLACEHOLDERS`; it
    does not match real sprint specs like `docs/SOP/SPRINT_003_PHASE_2.md`
    (those use digit+digit where the template uses the `00X` / `_Y` tokens)
    and it does not match arbitrary `docs/SOP/SPRINT_*.md` references.
    """
    return norm_path in _SOP_SPRINT_TEMPLATE_PLACEHOLDERS


def dispatch_apply_control_closeout_v1(
    runtime: Runtime,
    *,
    relay_run_dir: Path | None,
    phase_plan_path: Path,
    slice_id: str | None,
    force: bool = False,
) -> Tuple[int, str]:
    from scripts.relay.apply_control_closeout import (
        CloseoutSpec,
        apply_control_closeout,
        find_closeout_for_slice,
        load_phase_plan,
        run_consistency_check,
    )

    repo = runtime.repo_root
    plan = load_phase_plan(phase_plan_path.resolve())
    sid = slice_id
    relay_payload: dict | None = None
    if relay_run_dir is not None:
        rr_path = relay_run_dir / "relay_result.json"
        if not rr_path.is_file():
            return EXIT_REFUSAL, f"refusal: missing {rr_path}"
        relay_payload = json.loads(rr_path.read_text(encoding="utf-8-sig"))
        sid = sid or relay_payload.get("slice_id")
        if not force and not relay_payload.get("ready_for_control_closeout"):
            return (
                EXIT_BLOCKED,
                "blocked: ready_for_control_closeout is not true (use --force for backfill)",
            )
    if not sid:
        return EXIT_REFUSAL, "refusal: slice_id required (--slice-id or relay_result.json)"
    closeout_raw = find_closeout_for_slice(plan, sid)
    if closeout_raw is None:
        return EXIT_REFUSAL, f"refusal: no closeout block for slice {sid!r} in plan"
    spec = CloseoutSpec.from_dict(closeout_raw, slice_id=sid)
    report = apply_control_closeout(
        repo,
        closeout=spec,
        relay_run_dir=relay_run_dir,
    )
    if not report.get("passed"):
        return EXIT_BLOCKED, f"blocked: steering alignment failed\n{json.dumps(report, indent=2)}"
    ok, cons_out = run_consistency_check(repo)
    if not ok:
        return EXIT_BLOCKED, f"blocked: control_plane_consistency_check failed\n{cons_out}"
    brief = repo / "docs" / "SOP" / "AGENT_CONTINUITY_BRIEF.md"
    return (
        EXIT_CONTINUE,
        f"apply_control_closeout_v1  slice={sid}\n"
        f"  brief: {brief.relative_to(repo)}\n"
        f"  alignment: passed\n"
        f"  consistency: passed",
    )


def dispatch_control_plane_consistency_check(runtime: Runtime) -> Tuple[int, str]:
    repo = runtime.repo_root
    findings: list[dict] = []

    # 1. All canonical docs present.
    missing = []
    for p in CANONICAL_DOC_PATHS:
        if not (repo / p).is_file():
            missing.append(p)
            findings.append(
                {
                    "severity": "error",
                    "doc": p,
                    "locator": "precedence-list",
                    "message": "canonical doc missing from disk",
                }
            )
    if missing:
        # Hard stop: cannot proceed with structural checks.
        return _write_consistency_report(runtime, findings)

    # 2. Heading duplicate-number check per doc.
    for p in CANONICAL_DOC_PATHS:
        seen_numbers: dict[str, int] = {}
        text = (repo / p).read_text(encoding="utf-8-sig")
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = _HEADING_RE.match(line)
            if not m:
                continue
            num = m.group(2)
            if not num:
                continue
            if num in seen_numbers:
                findings.append(
                    {
                        "severity": "warn",
                        "doc": p,
                        "locator": f"line {lineno}",
                        "message": f"duplicate heading number {num!r} (first seen at line {seen_numbers[num]})",
                    }
                )
            else:
                seen_numbers[num] = lineno

    # 3. Backtick-quoted file paths in canonical docs should resolve (best-effort).
    #    Skip obvious placeholders (e.g. paths under artifacts/, orchestrator/,
    #    or with angle-bracket wildcards).
    for p in CANONICAL_DOC_PATHS:
        text = (repo / p).read_text(encoding="utf-8-sig")
        for ref in set(_LINK_PATH_RE.findall(text)):
            norm = ref.replace("\\", "/")
            if any(norm.startswith(prefix) for prefix in ("artifacts/", "orchestrator/", "src/viz/")):
                continue
            # Only check .md references into docs/** that look canonical.
            if not norm.startswith("docs/"):
                continue
            if _is_sop_template_placeholder(norm):
                # Intentional SOP template placeholder (e.g. SPRINT_00X.md,
                # SPRINT_00X_PHASE_Y.md). Not a real missing reference.
                continue
            if not (repo / norm).is_file():
                findings.append(
                    {
                        "severity": "warn",
                        "doc": p,
                        "locator": f"reference {ref!r}",
                        "message": "referenced doc path does not resolve on disk",
                    }
                )

    # 4. CODEX_AUTONOMY_V1 section 15 must reference each section 14.2 enum.
    codex_path = repo / "docs" / "SOP" / "CODEX_AUTONOMY_V1.md"
    codex_text = codex_path.read_text(encoding="utf-8-sig")
    for sc in ALL_STOP_CONDITIONS:
        if sc not in codex_text:
            findings.append(
                {
                    "severity": "error",
                    "doc": "docs/SOP/CODEX_AUTONOMY_V1.md",
                    "locator": f"enum {sc}",
                    "message": "section 14.2 enum value not mentioned anywhere in doc",
                }
            )

    return _write_consistency_report(runtime, findings)


def _write_consistency_report(runtime: Runtime, findings: list[dict]) -> Tuple[int, str]:
    repo = runtime.repo_root
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warn")
    report = {
        "protocol": PROTOCOL,
        "job": JOB_CONSISTENCY,
        "passed": errors == 0,
        "findings": findings,
        "generated_at": _iso_now(),
    }
    ts = _now_stamp()
    out_path = repo / "artifacts" / "health" / ts / "control_plane_consistency_report.json"
    _write_json(out_path, report)

    lines = [
        f"control_plane_consistency_check  (artifact: {out_path.relative_to(repo)})",
        f"  passed:   {report['passed']}",
        f"  errors:   {errors}",
        f"  warnings: {warnings}",
    ]
    for f in findings[:10]:
        lines.append(f"  [{f['severity']}] {f['doc']} {f['locator']}: {f['message']}")
    if len(findings) > 10:
        lines.append(f"  ... {len(findings) - 10} more findings")
    return EXIT_CONTINUE, "\n".join(lines)


def dispatch_gate_decision_forensic(runtime: Runtime, relay_result_path: Path) -> Tuple[int, str]:
    """Forensic replay mode: apply section 15 to an existing payload without
    touching the state machine."""
    if not relay_result_path.is_file():
        return EXIT_REFUSAL, f"refusal: path does not exist: {relay_result_path}"
    try:
        payload = json.loads(relay_result_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        dec = {
            "decision": DECISION_BLOCKED,
            "rule_matched": "15.2 rule 1",
            "reason": f"malformed JSON: {exc}",
            "schema_violations": ["payload is not valid JSON"],
            "invariant_violations": [],
            "generated_at": _iso_now(),
        }
        return DECISION_TO_EXIT[DECISION_BLOCKED], _format_decision(dec)
    dec = decide(payload)
    dec["generated_at"] = _iso_now()
    return DECISION_TO_EXIT[dec["decision"]], _format_decision(dec)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="relay_runtime_v0",
        description="Relay Runtime v0 (local, file-backed, single in-flight run).",
    )
    p.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Repo root. Defaults to git rev-parse --show-toplevel from CWD.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_status = sub.add_parser("status", help="Print current run_state.")

    sp_abort = sub.add_parser("abort", help="Terminal abort of the current run.")
    sp_reset = sub.add_parser("reset", help="Reset a terminal run back to idle.")
    sp_resume = sub.add_parser("resume", help="Consume relay_result.json for a staged slice.")

    sp_stage = sub.add_parser("stage", help="Stage or run a job.")
    sp_stage.add_argument("job", choices=sorted(SUPPORTED_JOBS))
    sp_stage.add_argument("--slice-id", default=None)
    sp_stage.add_argument("--sprint-spec-path", default=None)
    sp_stage.add_argument("--declared-plane", choices=sorted(DECLARED_PLANES), default=None)
    sp_stage.add_argument("--baseline-branch", default=None)
    sp_stage.add_argument("--build-branch", default=None)
    sp_stage.add_argument(
        "--retry-budget-max",
        type=int,
        default=RETRY_BUDGET_MAX_CANONICAL,
    )
    sp_stage.add_argument("--relay-result-path", type=Path, default=None,
                          help="For relay_gate_decision forensic replay only.")
    sp_stage.add_argument("--relay-run-dir", type=Path, default=None,
                          help="For apply_control_closeout_v1: run directory with relay_result.json")
    sp_stage.add_argument("--phase-plan", type=Path, default=None,
                          help="For apply_control_closeout_v1: phase plan JSON path")
    sp_stage.add_argument("--force", action="store_true",
                          help="For apply_control_closeout_v1: skip ready_for_control_closeout check")

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Resolve repo root.
    if args.repo_root:
        repo = args.repo_root.resolve()
    else:
        repo = _repo_root(Path.cwd())
        if repo is None:
            print("refusal: not inside a git repository", file=sys.stderr)
            return EXIT_REFUSAL
    runtime = Runtime(repo)

    try:
        if args.cmd == "status":
            code, msg = dispatch_status(runtime)
        elif args.cmd == "abort":
            code, msg = dispatch_abort(runtime)
        elif args.cmd == "reset":
            code, msg = dispatch_reset(runtime)
        elif args.cmd == "resume":
            code, msg = dispatch_resume(runtime)
        elif args.cmd == "stage":
            code, msg = _dispatch_stage(runtime, args)
        else:
            print(f"refusal: unknown subcommand {args.cmd!r}", file=sys.stderr)
            return EXIT_REFUSAL
    except Exception as exc:  # pragma: no cover - internal error path.
        print(f"internal error: {exc!r}", file=sys.stderr)
        return EXIT_INTERNAL_ERROR

    stream = sys.stdout if code in (EXIT_CONTINUE, EXIT_RETRY_ALLOWED) else sys.stderr
    print(msg, file=stream)
    return code


def _dispatch_stage(runtime: Runtime, args: argparse.Namespace) -> Tuple[int, str]:
    job = args.job
    if job == JOB_RUN_SLICE:
        missing = []
        for key in ("slice_id", "sprint_spec_path", "declared_plane", "baseline_branch", "build_branch"):
            if getattr(args, key) is None:
                missing.append(f"--{key.replace('_','-')}")
        if missing:
            return EXIT_REFUSAL, f"refusal: missing required args for run_selected_slice_v1: {', '.join(missing)}"
        return dispatch_stage_slice(
            runtime=runtime,
            slice_id=args.slice_id,
            sprint_spec_path=args.sprint_spec_path,
            declared_plane=args.declared_plane,
            baseline_branch=args.baseline_branch,
            build_branch=args.build_branch,
            retry_budget_max=args.retry_budget_max,
        )
    if job == JOB_HEALTH:
        return dispatch_codebase_health_report(runtime, baseline_branch=args.baseline_branch)
    if job == JOB_CONSISTENCY:
        return dispatch_control_plane_consistency_check(runtime)
    if job == JOB_GATE_DECISION:
        if args.relay_result_path is None:
            return (
                EXIT_REFUSAL,
                "refusal: relay_gate_decision forensic replay requires --relay-result-path",
            )
        return dispatch_gate_decision_forensic(runtime, args.relay_result_path.resolve())
    if job == JOB_CLOSEOUT:
        if args.phase_plan is None:
            return EXIT_REFUSAL, "refusal: apply_control_closeout_v1 requires --phase-plan"
        return dispatch_apply_control_closeout_v1(
            runtime,
            relay_run_dir=args.relay_run_dir.resolve() if args.relay_run_dir else None,
            phase_plan_path=args.phase_plan,
            slice_id=args.slice_id,
            force=bool(args.force),
        )
    return EXIT_REFUSAL, f"refusal: unknown job {job!r}"


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
