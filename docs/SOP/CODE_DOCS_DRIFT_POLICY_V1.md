# CODE_DOCS_DRIFT_POLICY_V1

**Advisory — not a hard gate.** Same posture as `docs/SOP/WORKFLOW_CONTEXT_AUDIT_001.md`.

## Principle

SOP documents that reference **numeric, versioned, or enum values that live in
code** MUST satisfy at least one of:

(a) **Cite the code symbol by name** — e.g. "see `MANIFEST_SCHEMA_VERSION` in
    `scripts/implied_lab_ui_smoke_harness.py`" rather than embedding the raw
    integer. Readers can verify the doc against the code without a test.

(b) **Be backed by a unit test** that imports the code constant and asserts it
    matches the value declared in the doc. The test acts as a continuous
    alignment check across all future changes.

Satisfying (a) alone is acceptable when the value is stable and the doc already
contains a clear cross-reference. (b) is preferred when the value is expected to
change over time (e.g. version counters).

## Rationale

The schema-version drift between `CURRENT_FRONTIER.md` ("manifest/schema v2")
and the harness (literal `schema_version: 1`) was discovered during
Sprint004-Slice003 closeout prep (2026-04-27). The harness emitted `v1` while
steering docs described `v2`, creating ambiguity about which was authoritative.
The fix (bump + constant + drift test) is the first instance of pattern (b) in
this repo. This policy captures the lesson to prevent recurrence.

## Advisory clause

This is a **guideline, not a gate**. Failing to follow it does not block a BUILD
or a closeout. However, when a new versioned/enum constant is introduced in code
and cited in SOP docs, the author is expected to apply (a) or (b) before
submitting the slice for steward review.

## First instance of pattern (b)

`docs/SOP/MANIFEST_SCHEMA.md` + `tests/test_manifest_schema_drift.py` —
introduced in the Sprint004-Slice003 BUILD-CLOSEOUT pass (2026-04-27).
The test imports `MANIFEST_SCHEMA_VERSION` from
`scripts/implied_lab_ui_smoke_harness.py` and asserts it equals the version
declared in `MANIFEST_SCHEMA.md` under the line
`Canonical schema version: vN`.
