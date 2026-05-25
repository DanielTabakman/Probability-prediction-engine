## PHASE_PLAN_CONTRACT_V1

Purpose: define a small, stable JSON contract for sequential phase execution by the local orchestrator (relay-gated, ACP-driven).

### Contract goals

- Be **explicit**: slice ID, sprint spec path, declared plane, build branch.
- Be **portable**: paths are repo-relative unless absolute.
- Be **boring**: no embedded prompts, no nested planning, no dynamic branching. The relay remains the hard gate.

### File location (canonical)

- Store tracked phase plans under `docs/SOP/PHASE_PLANS/`.
- Each plan should be named by phase boundary and be revisioned only when the intended slice set changes.

### Schema (JSON)

Top-level object:

```json
{
  "name": "string",
  "baselineBranch": "string (optional; wrapper defaults to main)",
  "sprintSpecPath": "string (optional; repo-relative; plan-level default)",
  "selectionRecord": "string (optional; SELECTION outcome doc)",
  "slices": [
    {
      "sliceId": "string (required)",
      "declaredPlane": "CONTROL-PLANE | PRODUCT-PLANE | EVIDENCE-PLANE (required)",
      "touchSet": ["optional repo-relative path prefixes allowed in this slice"],
      "forbiddenTouch": ["optional prefixes that must not change"],
      "dependsOnSliceId": "optional sliceId that must merge first",
      "susMinutes": 15,
      "hardMinutes": 30,
      "maxAttempts": 2,
      "closeout": { }
    }
  ]
}
```

### `closeout` object (required on chapter **Closeout** slice only)

Required on the final slice whose `sliceId` ends with `Closeout-Slice` (or contains `-Closeout-`). `post_relay_continue.py` refuses phase completion without it on that slice.

| Field | Type | Required |
|-------|------|----------|
| `chapterId` | string | yes |
| `chapterTitle` | string | yes |
| `chapterStatus` | string | yes (`COMPLETE`) |
| `closedDate` | string | yes (`YYYY-MM-DD`) |
| `evidenceDoc` | string | yes (repo-relative) |
| `sprintSpec` | string | yes |
| `nextSelectionDoc` | string | yes |
| `selectionOutcomeDoc` | string | no |
| `carryDocs` | string[] | no |
| `dualSmokeRunIds` | string[] | no |
| `pytestCount` | int | no |
| `closedChaptersLine` | string | no (HANDOFF gate bullet; auto-built if omitted) |

Example: see `mvp1_friends_first_screen_relay.json`.

Notes:

- `susMinutes` and `hardMinutes` implement the **15/30 rule** (SUS at 15m; cancel at 30m).
- `maxAttempts` is the orchestrator max total attempts. Relay may also impose retry-budget invariants.
- Phase runner semantics are **stop-on-first-non-CONTINUE**.
- After slice `CONTINUE`, **`apply_control_closeout_v1`** runs automatically when `closeout` is present (`RELAY_RUNTIME_V1.md`).
- **`touchSet` / `forbiddenTouch`:** optional parallel-agent ownership; see [`VIZ_LAYER_DISCIPLINE_V1.md`](../VIZ_LAYER_DISCIPLINE_V1.md). Verify with `python scripts/check_touch_set.py` when running disjoint BUILD branches.

