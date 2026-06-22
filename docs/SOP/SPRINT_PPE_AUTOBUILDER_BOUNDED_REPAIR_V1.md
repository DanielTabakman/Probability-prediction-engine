# PPE autobuilder bounded repair v1 — relay sprint spec

**SELECTION:** [`POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md`](POST_PPE_AUTOBUILDER_FACTORY_SELECTION.md)

## Intent

Bounded gate-failure retry in build closeout path (N attempts) before `@ppe-triage-worker` escalation.

## Acceptance

1. Config `autobuilder.buildRepairMaxAttempts` (default 3).
2. `ppe_ide_build_closeout` or build-worker path retries `run_pushable_gate` with repair hint.
3. Evidence doc **COMPLETE**; pytest green.

## Slices

`PPE-AutobuilderRepair-Control/ Product / Witness / Closeout` per phase plan.
