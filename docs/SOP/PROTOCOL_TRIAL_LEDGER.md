# PROTOCOL TRIAL LEDGER

This ledger is the single authoritative record of all CONTROL-PLANE protocol trials run against
the Probability Prediction Engine. Each trial occupies one heading block. Completed entries are
append-only; only the currently active entry may be updated. All trials — proposed, in flight,
decided, or closed — live here permanently.

**Cross-reference:** `docs/SOP/PROTOCOL_TRIAL_LIFECYCLE_V1.md` — the lifecycle rules that
govern how entries move through the stages below.

---

## Status Legend

| Status | Meaning |
|---|---|
| `PROPOSED` | Proposal written; awaiting steward authorization to begin TRIAL. |
| `TRIAL` | Steward has authorized; live state is active; cycles are being observed. |
| `DECIDED-PROMOTE` | Steward has decided to promote; canonization work in progress. |
| `DECIDED-AMEND` | Steward has decided to amend and re-trial; amendment in progress. |
| `DECIDED-ROLLBACK` | Steward has decided to roll back; rollback work in progress. |
| `CANONIZED` | Fully promoted; new canon is in place; trial markers retired. |
| `ROLLED-BACK` | Rolled back; prior canon restored; postmortem written below. |

---

## Trial #001 — Tiered-Delegation Soft-Launch (Steward → Parent Agent)

**Status:** `TRIAL`

**Opened:** 2026-04-27

**Proposer:** parent agent (this conversation)

**Authorizer:** steward (user)

**Hypothesis:** Tier-2 SELECTION and Tier-2/3 CONTROL-CLOSEOUT can be safely delegated from
steward to parent agent under explicit guardrails (rubric verification, semantic-contract gates,
escalation triggers), reducing steward tactical load while preserving strategic ownership and
discipline.

**Affected canon docs:**
- `docs/SOP/CODEX_AUTONOMY_V1.md`
- `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
- `docs/SOP/HANDOFF.md`

Stale-canon pointer protection is being added to the above docs by `WH-Slice-004` (in BUILD
at time of this ledger entry).

**Live state location:** `docs/SOP/CURRENT_FRONTIER.md` → section "Authority (tiered-delegation
soft-launch — 2026-04-27 onward)".

**Cycle target:** N = 2.

**Cycles complete:** 1

- **Cycle 1 — Sprint004-Slice003** (closed 2026-04-27): closed under tiered-delegation
  CONTROL-CLOSEOUT; pytest 121 passed; UI smoke PASS; schema_version 2; no escalation triggers
  fired; no failures. Observation: delegated authority operated without incident for a full
  BUILD-CLOSEOUT cycle.

**Cycle pending:** `Sprint004-Slice004` (directional strip + payload/harness refactor) —
currently in BUILD.

**Decision gate:** after `Sprint004-Slice004` CONTROL-CLOSEOUT closes; steward to decide
PROMOTE / AMEND-AND-RE-TRIAL / ROLLBACK.

**Rollback plan:** restore steward-only authority language in `CODEX_AUTONOMY_V1.md` and
`FRONTIER_STEWARD_PROTOCOL.md`; clear the tiered-delegation live-state subsection in
`CURRENT_FRONTIER.md`; clear trial pointers from `HANDOFF.md`; write a postmortem entry below
this block using the template at the bottom of this file; mark this entry `ROLLED-BACK`.

---

## Trial #002 — Protocol Trial Lifecycle V1 (Recursion)

**Status:** `TRIAL`

**Opened:** 2026-04-27

**Proposer:** parent agent

**Authorizer:** steward (user)

**Hypothesis:** A formal 5-stage lifecycle (PROPOSAL → TRIAL → EVIDENCE → DECISION →
CANONIZATION / ROLLBACK) with mandatory stale-canon protection makes future protocol changes
cheaper, more reversible, and safer for fresh-context agents than the current ad-hoc
soft-launch pattern.

**Affected canon docs:** none yet. The lifecycle introduces a new document
(`PROTOCOL_TRIAL_LIFECYCLE_V1.md`) rather than modifying existing canon. Cross-references from
existing canon docs pointing to this lifecycle are deferred to `WH-Slice-006`, after this
trial closes.

**Live state location:** `docs/SOP/PROTOCOL_TRIAL_LIFECYCLE_V1.md` (the document itself is its
own live state; it ships in TRIAL, not CANONIZED).

**Cycle target:** N = 2.

**Cycles complete:** 0 (newborn — this ledger entry is written at the moment of first
deployment).

**Cycle pending:** the next two CONTROL-PLANE protocol changes that run through this lifecycle's
stages will count as cycle 1 and cycle 2.

**Decision gate:** after the second such protocol change completes its lifecycle passage;
steward to decide PROMOTE / AMEND-AND-RE-TRIAL / ROLLBACK.

**Rollback plan:** delete `docs/SOP/PROTOCOL_TRIAL_LIFECYCLE_V1.md` and
`docs/SOP/PROTOCOL_TRIAL_LEDGER.md`; document the failure mode in steward-facing notes;
revert to the ad-hoc soft-launch pattern; ensure any protocol changes that ran through this
lifecycle's stages during the trial are not disrupted by the removal.

---

## Postmortem Template

*(Referenced by §5b of `PROTOCOL_TRIAL_LIFECYCLE_V1.md`. Copy this block into the relevant
trial entry when recording a ROLLBACK postmortem.)*

```
### Postmortem — [Trial Number and Title]

**Decision date:**
**Decider:** steward

**What was tried:**
[One or two sentences describing the change that was trialled.]

**What evidence forced rollback:**
[Specific observations from the EVIDENCE cycles that indicated the trial was not working.
Include cycle numbers and what was expected versus what was observed.]

**What we would try differently next time:**
[Concrete adjustments: narrower scope, different guardrails, different cycle count, amended
hypothesis, etc.]

**Affected canon docs to restore:**
[List every doc that must be reverted to its pre-trial state, with a note on what specifically
needs to change in each.]
```

---

*Cross-reference: `docs/SOP/PROTOCOL_TRIAL_LIFECYCLE_V1.md` — lifecycle rules governing this
ledger.*
