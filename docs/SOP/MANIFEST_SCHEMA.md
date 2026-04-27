# MANIFEST_SCHEMA

**Canonical schema version: v3**

Source of truth for the integer constant: `MANIFEST_SCHEMA_VERSION` in
`scripts/implied_lab_ui_smoke_harness.py`. The drift-detection test
`tests/test_manifest_schema_drift.py` asserts that this doc and the constant agree.

---

## Closeout block — `workflow_hardening_slice003_closeout`

Emitted in every manifest at the top level, keyed
`workflow_hardening_slice003_closeout`.

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | int | Schema version of this block (currently `3`). |
| `primary_scenario_ran` | bool | Whether `A_width_target_payoff` was included in the run. |
| `evidence_plane_complete` | bool | True when **both** width_vol and directional witnesses are in acceptable states: width_vol in (`WITNESS_OK`, `DEGRADED_STRIP_NOT_SHOWN`) AND directional in (`WITNESS_OK`, `BOUNDED_LIVE_DATA_NO_DIRECTIONAL_STRIP`). |
| `bounded_live_data_miss` | bool | True when width_vol classification is `DEGRADED_STRIP_NOT_SHOWN`. Present only when `primary_scenario_ran` is true. |
| `width_vol_signal` | str | Signal for the width_vol witness. One of: `WITNESS_OK`, `BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP`, `NEEDS_FIX_OR_RETRY`, `NOT_APPLICABLE`. |
| `directional_signal` | str | Signal for the directional witness. One of: `WITNESS_OK`, `BOUNDED_LIVE_DATA_NO_DIRECTIONAL_STRIP`, `NEEDS_FIX_OR_RETRY`, `NOT_APPLICABLE`. |
| `classification` | str | Raw `slice003_classification` (width_vol) from `ScenarioResult`. Present only when `primary_scenario_ran` is true. |
| `detail` | str | Free-text notes from the width_vol witness or `"A_width_target_payoff not in this run."` |

### Accepted closeout signals

For `evidence_plane_complete: true`, **both** witnesses must be in an acceptable state:
- **width_vol**: `WITNESS_OK` or `BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP`
- **directional**: `WITNESS_OK` or `BOUNDED_LIVE_DATA_NO_DIRECTIONAL_STRIP`

`NEEDS_FIX_OR_RETRY` for either witness is not acceptable.

Scenario A (the official one-command scenario) produces width_vol conditions; the
directional strip is not expected to appear there. `BOUNDED_LIVE_DATA_NO_DIRECTIONAL_STRIP`
is the sanctioned bounded-degraded path for scenario A's directional witness.

---

## Witness row — `slice003_witness` (per scenario, width_vol)

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

## Witness row — `slice004_directional_witness` (per scenario, directional)

Emitted inside each scenario's entry in the `scenarios` list (Sprint004-Slice004).

| Field | Type | Meaning |
|---|---|---|
| `classification` | str | `WITNESS_OK`, `BOUNDED_LIVE_DATA_NO_DIRECTIONAL_STRIP`, `DEGRADED_PAGE_NOT_LOADED`, `DEGRADED_SCENARIO_INCOMPLETE`, or `NOT_APPLICABLE`. |
| `candidate_strip_heading_found` | bool | Whether the directional strip heading ("Location-shaped tension") was found in the DOM. |
| `notes` | str | Free-text witness notes. For scenario A, this explains the sanctioned bounded-degraded path (width_vol conditions preclude directional strip). |

---

## Version history

| Version | Date | Change |
|---|---|---|
| v1 | 2026-04-22 | Initial schema; shipped with `Workflow-Hardening-Slice-003`. Literal `1` embedded in harness. |
| v2 | 2026-04-27 | Same structure and semantics as v1. Terminology aligned with `CURRENT_FRONTIER.md` "manifest/schema v2" language. Integer literal replaced by `MANIFEST_SCHEMA_VERSION` constant in harness. This is a documentation-version reconciliation, not a structural change. |
| v3 | 2026-04-27 | Sprint004-Slice004: added `slice004_directional_witness` row per scenario; added `width_vol_signal` and `directional_signal` fields to closeout block; `evidence_plane_complete` now requires both witnesses to be in acceptable states. `workflow_hardening_slice003_signal` field removed (superseded by `width_vol_signal`). |

v2 → v3 is a **structural bump**: the closeout block gains two new fields (`width_vol_signal`,
`directional_signal`) and the per-scenario entries gain a new witness row
(`slice004_directional_witness`). The `workflow_hardening_slice003_signal` field is removed
(replaced by `width_vol_signal`). The `evidence_plane_complete` gate is tightened to require
both witnesses acceptable.
