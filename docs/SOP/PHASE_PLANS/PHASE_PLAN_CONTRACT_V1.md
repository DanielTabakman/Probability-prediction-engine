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
  "baselineBranch": "string (optional; wrapper defaults to CURRENT_FRONTIER baseline)",
  "slices": [
    {
      "sliceId": "string (required)",
      "sprintSpecPath": "string (required; repo-relative path to the sprint spec naming the slice)",
      "declaredPlane": "PRODUCT-PLANE | EVIDENCE-PLANE (required)",
      "buildBranch": "string (required; must be unique per run or per invocation)",
      "susMinutes": 15,
      "hardMinutes": 30,
      "maxAttempts": 2
    }
  ]
}
```

Notes:

- `susMinutes` and `hardMinutes` implement the **15/30 rule** (SUS at 15m; cancel at 30m).
- `maxAttempts` is the orchestrator max total attempts. Relay may also impose retry-budget invariants.
- Phase runner semantics are **stop-on-first-non-CONTINUE**.

