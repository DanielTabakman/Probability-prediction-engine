# MANIFEST_SCHEMA

**Canonical schema version: v2**

Source of truth for the integer constant: `MANIFEST_SCHEMA_VERSION` in
`scripts/implied_lab_ui_smoke_harness.py`. The drift-detection test
`tests/test_manifest_schema_drift.py` asserts that this doc and the constant agree.

---

## Closeout block — `workflow_hardening_slice003_closeout`

Emitted in every manifest at the top level, keyed
`workflow_hardening_slice003_closeout`.

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | int | Schema version of this block (currently `2`). |
| `primary_scenario_ran` | bool | Whether `A_width_target_payoff` was included in the run. |
| `evidence_plane_complete` | bool | True when classification is `WITNESS_OK` or `DEGRADED_STRIP_NOT_SHOWN`. |
| `bounded_live_data_miss` | bool | True when classification is `DEGRADED_STRIP_NOT_SHOWN` (live data unavailable; bounded degraded path). Present only when `primary_scenario_ran` is true. |
| `workflow_hardening_slice003_signal` | str | One of: `WITNESS_OK`, `BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP`, `NEEDS_FIX_OR_RETRY`, `NOT_APPLICABLE`. |
| `classification` | str | Raw `slice003_classification` from `ScenarioResult`. Present only when `primary_scenario_ran` is true. |
| `detail` | str | Free-text notes from the witness or `"A_width_target_payoff not in this run."` |

### Accepted closeout signals

`WITNESS_OK` or `BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP` — both are acceptable for
honest Slice003 closeout per steward decision (2026-04-22). The achieved signal
must be recorded in the ledger entry. `NEEDS_FIX_OR_RETRY` is not acceptable.

---

## Witness row — `slice003_witness` (per scenario)

Emitted inside each scenario's entry in the `scenarios` list.

| Field | Type | Meaning |
|---|---|---|
| `classification` | str | `WITNESS_OK`, `DEGRADED_STRIP_NOT_SHOWN`, `NEEDS_FIX_OR_RETRY`, or `NOT_APPLICABLE`. |
| `candidate_strip_heading_found` | bool | Whether the width_vol candidate strip heading was found in the DOM. |
| `history_expander_found` | bool | Whether the "History (this session)" expander was found. |
| `clear_history_control_found` | bool | Whether the clear-history control was found. |
| `witness_screenshot_path` | str | Path to the witness screenshot, or empty string. |
| `notes` | str | Free-text witness notes. |

---

## Version history

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-22 | Initial schema; shipped with `Workflow-Hardening-Slice-003`. Literal `1` embedded in harness. |
| v2 | 2026-04-27 | Same structure and semantics as v1. Terminology aligned with `CURRENT_FRONTIER.md` "manifest/schema v2" language. Integer literal replaced by `MANIFEST_SCHEMA_VERSION` constant in harness. This is a documentation-version reconciliation, not a structural change. |

v1 → v2 is a **zero-structural-change bump**: field names, field types, signal
enum values, and witness row shape are identical. The only code change is replacing
the hard-coded integer `1` with the named constant `MANIFEST_SCHEMA_VERSION = 2`
in `scripts/implied_lab_ui_smoke_harness.py`, eliminating future schema-drift risk.
