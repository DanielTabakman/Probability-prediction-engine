# PROTOCOL TRIAL LIFECYCLE V1

**Status: TRIAL** (see `docs/SOP/PROTOCOL_TRIAL_LEDGER.md`, Trial #002)

> This document is itself in TRIAL stage. It applies to future CONTROL-PLANE protocol changes
> while this lifecycle is being evaluated. Cross-references from existing canon docs are deferred
> to WH-Slice-006, after this trial closes.

---

## §1. Purpose and Applicability

Ad-hoc protocol changes leave two recurring wounds: stale canon (existing docs describe the old
way long after the new way is live) and no shared evidence record (every soft-launch reinvents
its own tracking and closure logic). This lifecycle formalizes the pattern the project already
uses informally — proposal, soft-launch, observed cycles, steward decision, canonization or
rollback — so that every future protocol change runs the same repeatable rails and leaves a
durable evidence trail.

**Applies to:** CONTROL-PLANE protocol changes — authority delegation changes, workflow process
introductions or revisions, validation rubrics, new SOP document introductions, schema
evolutions, and agent-role changes.

**Does NOT apply to:** product code changes (those use the regular BUILD-slice flow), runtime
bug fixes, or one-off ledger bookkeeping updates that do not alter any operative rule.

---

## §2. The Five Stages

Each stage has a designated **entrant** (who moves the trial into this stage), an **exit
condition**, and **mandatory artifacts** that must exist before the exit can occur.

---

### Stage 1 — PROPOSAL

**Entrant:** any agent or the steward.

**Exit condition:** steward explicitly authorizes the trial to move to TRIAL stage.

**Mandatory artifacts:**
- A proposal block in `docs/SOP/PROTOCOL_TRIAL_LEDGER.md`, headed with the trial number and
  title, containing at minimum: hypothesis, affected canon docs, proposed cycle target N, and
  rollback plan.

**Key constraints:**
- No trial proceeds to TRIAL without steward authorization. An agent may draft a proposal, but
  the steward's explicit approval is required before any live-state changes are made.
- The proposal block must be committed before TRIAL stage begins.

---

### Stage 2 — TRIAL (soft-launch)

**Entrant:** parent agent, after steward authorization.

**Exit condition:** all N evidence cycles are complete and a DECISION has been recorded.

**Mandatory artifacts:**
- **Stale-canon pointers** added to every affected canon document, at the top of that document,
  pointing at the live trial state. No trial may go live without these pointers in place.
  This is a non-negotiable pre-condition. The project learned this the hard way during the
  tiered-delegation soft-launch, where operating without such pointers caused fresh-context
  agents to apply stale canon rules throughout an active trial. The pointer must be specific
  enough that a fresh-context agent can navigate to the live state without further escalation.
- Trial ledger entry updated to Status `TRIAL`.

**Key constraints:**
- The live trial state (the actual operative rule) must live in a single, linkable location.
  Splitting the live state across multiple locations defeats the pointer-protection mechanism.
- PREFLIGHT for any TRIAL-stage agent dispatch must verify that stale-canon pointers exist on
  every affected canon doc; if they are absent, the agent must add them before proceeding with
  any other work.

---

### Stage 3 — EVIDENCE

**Entrant:** parent agent, at the close of each BUILD or CONTROL-PLANE cycle that operates
under the trial.

**Exit condition:** N cycles of observed operation have been recorded.

**Mandatory artifacts:**
- A brief observation entry appended to the ledger trial block after each cycle, noting: cycle
  number, slice or event identifier, what worked, what did not work, and any surprises.
- The cycle counter in the ledger entry updated to reflect cycles complete.

**Key constraints:**
- Evidence entries must be written before the next cycle begins, not retrospectively after the
  decision gate. Retrospective evidence weakens the integrity of the decision.
- An observation entry may be as short as two or three sentences; completeness matters more
  than length.

---

### Stage 4 — DECISION

**Entrant:** steward only.

**Exit condition:** steward records one of three decisions: **PROMOTE**, **AMEND-AND-RE-TRIAL**,
or **ROLLBACK**.

**Mandatory artifacts:**
- Decision recorded in the ledger trial block, with date and brief rationale.
- Ledger status updated to `DECIDED-PROMOTE`, `DECIDED-AMEND`, or `DECIDED-ROLLBACK`.

**Key constraints:**
- Only the steward owns this decision. The parent agent may present the evidence summary and
  the three decision options, but may not select among them.
- A steward may call an early decision (before N cycles) if evidence is decisive, but must
  record the rationale for early termination in the ledger.

---

### Stage 5a — CANONIZATION

**Entrant:** parent agent, after a PROMOTE decision.

**Exit condition:** old canon fully updated, trial markers retired, ledger entry marked
`CANONIZED`.

**Mandatory artifacts:**
- Formal SOP document (or updated version of the existing doc) reflecting the promoted change.
- Cross-references from all previously affected canon docs updated to point at the new canon
  (replacing the TRIAL-stage stale-canon pointers).
- All trial-state markers removed from interim locations.
- Ledger entry marked `CANONIZED` with the date.

**Key constraints:**
- The stale-canon pointers from Stage 2 must be replaced (not merely removed) with stable
  cross-references to the new canonical location. Removing without replacing leaves the same
  navigation gap they were meant to solve.

---

### Stage 5b — ROLLBACK

**Entrant:** parent agent, after a ROLLBACK decision.

**Exit condition:** prior canon fully restored, trial artifacts cleaned up, postmortem written,
ledger entry marked `ROLLED-BACK`.

**Mandatory artifacts:**
- Old canon language restored in every affected doc.
- Stale-canon trial pointers removed.
- Trial-state location cleared or annotated as rolled-back.
- Postmortem entry written in the ledger trial block (using the postmortem template in
  `docs/SOP/PROTOCOL_TRIAL_LEDGER.md`).
- Ledger entry marked `ROLLED-BACK` with the date.

**Key constraints:**
- Rollback must be clean: no doc graveyard, no half-merged logic, no orphaned tests. The repo
  must be in a state indistinguishable from one in which the trial never ran — except for the
  ledger record, which is permanent.

---

## §3. Mandatory Constraints (Non-Negotiable)

The following constraints apply to every trial regardless of scope:

1. **Stale-canon protection.** No trial goes live without pointers from all affected canon docs
   to the live trial state. At PREFLIGHT for any TRIAL-stage agent dispatch, verify these
   pointers exist. If they are absent, add them before any other work proceeds.

2. **Default cycle count N = 2.** Trials default to two observed cycles. The cycle count is set
   in the PROPOSAL and may be adjusted by the steward, but must be recorded in the ledger before
   TRIAL stage begins.

3. **Reversibility.** Every trial must be structured so it can be cleanly undone. The rollback
   plan must be written at PROPOSAL time. A trial that cannot be stated in reversible terms
   should not be approved.

4. **Single trial ledger.** All trials — past, active, and decided — live in
   `docs/SOP/PROTOCOL_TRIAL_LEDGER.md`, one heading per trial. The ledger is append-only for
   completed entries; only the current active entry may be edited. Valid status values:
   `PROPOSED` / `TRIAL` / `DECIDED-PROMOTE` / `DECIDED-AMEND` / `DECIDED-ROLLBACK` /
   `CANONIZED` / `ROLLED-BACK`.

5. **Recursion safety.** This lifecycle protocol applies to itself. `PROTOCOL_TRIAL_LIFECYCLE_V1`
   ships in TRIAL stage (not CANONIZED), with N = 2, and is recorded in the ledger as Trial
   #002. It will be canonized or rolled back only after two CONTROL-PLANE protocol changes
   have successfully run through its stages.

---

## §4. Roles

**Steward (user):** the sole authority over trial approval and the DECISION gate. The steward
authorizes every TRIAL-stage start and owns the PROMOTE / AMEND-AND-RE-TRIAL / ROLLBACK
decision. The steward may cancel any trial mid-flight at any time. The steward's strategic
ownership is preserved in full; this lifecycle reduces tactical coordination load, not
authority.

**Parent agent (orchestrator):** authors proposals on behalf of the project; dispatches
TRIAL-stage, EVIDENCE-recording, CANONIZATION, and ROLLBACK BUILD agents; records observation
entries after each cycle; presents the decision-gate summary to the steward with the three
decision options but without selecting among them.

**BUILD agents:** execute scoped work as dispatched by the parent agent. BUILD agents do not
own protocol-level decisions and do not modify the lifecycle or ledger except as explicitly
directed by their dispatch instructions.

---

## §5. Worked Example — Tiered-Delegation Soft-Launch

The following illustrates how this lifecycle maps to the in-flight tiered-delegation trial,
which predates this document and is being retroactively catalogued as Trial #001.

**PROPOSAL stage:**
- Date: 2026-04-27.
- Author: parent agent.
- Authorizer: steward.
- Hypothesis: Tier-2 SELECTION and Tier-2/3 CONTROL-CLOSEOUT can be safely delegated to the
  parent agent under explicit guardrails (rubric verification, semantic-contract gates,
  escalation triggers), reducing steward tactical load while preserving strategic ownership.

**TRIAL stage:**
- Began: 2026-04-27.
- Stale-canon pointer protection: being added to `CODEX_AUTONOMY_V1.md`,
  `FRONTIER_STEWARD_PROTOCOL.md`, and `HANDOFF.md` by WH-Slice-004 (in BUILD at time of
  writing).
- Live state location: `docs/SOP/CURRENT_FRONTIER.md` → "Authority (tiered-delegation
  soft-launch — 2026-04-27 onward)".

**EVIDENCE stage:**
- Cycle 1: `Sprint004-Slice003` — closed under tiered-delegation CONTROL-CLOSEOUT on
  2026-04-27; pytest 121 passed; UI smoke PASS; schema_version 2; no escalation triggers
  fired; no failures. Observation: tiered-delegation operated without incident for a full
  BUILD-CLOSEOUT cycle.
- Cycle 2: `Sprint004-Slice004` — currently in BUILD; outcome pending.
- Cycle target N = 2.

**DECISION stage:**
- Pending; will be presented by parent agent after Slice004 CONTROL-CLOSEOUT. Steward to
  choose PROMOTE / AMEND-AND-RE-TRIAL / ROLLBACK.

**Canonization (if PROMOTE):**
- Finalize delegated-authority language in CODEX_AUTONOMY_V1.md and
  FRONTIER_STEWARD_PROTOCOL.md; replace trial pointers with stable cross-refs; retire the
  soft-launch subsection in CURRENT_FRONTIER.md; mark Trial #001 CANONIZED.

**Rollback (if ROLLBACK):**
- Restore steward-only language in CODEX_AUTONOMY_V1.md and FRONTIER_STEWARD_PROTOCOL.md;
  clear the soft-launch subsection in CURRENT_FRONTIER.md; clear trial pointers from HANDOFF.md;
  write postmortem in Trial #001 ledger entry; mark ROLLED-BACK.

---

## §6. How a Fresh-Context Agent Uses This Document

A fresh-context agent that encounters a stale-canon pointer at the top of a CONTROL-PLANE
document should:

1. Read the live trial state at the location the pointer specifies.
2. Operate under the live trial state, not the older canon text that appears later in the
   document.
3. Record that it is operating under a trial (not settled canon) in any PREFLIGHT or CLOSEOUT
   report it produces.
4. If the live state location is ambiguous or the pointer is broken, escalate to the steward
   before proceeding. Do not guess.

A fresh-context agent that is dispatched to execute TRIAL-stage work must, as its first
PREFLIGHT step, verify that all affected canon docs carry the required stale-canon pointer. If
any pointer is missing, the agent must add it before performing any other work in the dispatch.

---

*Cross-reference: `docs/SOP/PROTOCOL_TRIAL_LEDGER.md` — running record of all trials.*
