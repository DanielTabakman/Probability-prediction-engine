## STEWARD_AUTOPILOT_V1

Purpose: define an **autonomous Steward** layer that sits above the relay-gated orchestrator and runs a **preapproved phase queue** as far as possible without crossing authority boundaries.

This doc defines **what the steward autopilot may do**, **what it must never do**, and **when it must stop and escalate to the human steward**.

### Source-of-truth order (unchanged)

1. Pushed repo + accepted docs
2. `docs/SOP/CURRENT_FRONTIER.md`
3. `docs/SOP/HANDOFF.md`
4. `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`
5. Phase/sprint docs
6. This doc (durable autopilot policy)
7. Older chat only when the above are silent

### Components

- **Steward autopilot (LLM)**: makes bounded decisions only; never performs git/tool actions directly.
- **Orchestrator (driver)**: runs `agent acp`, manages worktrees, timeouts, retries.
- **Relay (hard gate)**: `scripts/relay_runtime_v0.py` stages, validates, and decides (`CONTINUE | RETRY_ALLOWED | STOP_FOR_REVIEW | BLOCKED`).

### Queue semantics (Option 1)

The only allowed “what’s next” surface for autopilot is:

- `docs/SOP/PHASE_PLANS/*.json`

The steward autopilot **may auto-advance only within the slices listed in the plan file**.

Autopilot must **not** select a slice that is not already named in the plan.

### Authority boundaries (never cross)

The steward autopilot must **never**:

- Perform **SELECTION** outside the plan queue.
- Perform **CONTROL-CLOSEOUT** edits to `docs/SOP/**` unless explicitly authorized by the human steward for that run.
- Change phase/sprint scope, semantic contracts, or acceptance criteria.
- Ignore relay `STOP_FOR_REVIEW` / `BLOCKED` outcomes.

### Allowed autonomous actions

Within the queue only, the steward autopilot may:

- **Advance** to the next slice when the prior slice run returns relay decision `CONTINUE`.
- **Retry** the same slice when relay decision is `RETRY_ALLOWED` (bounded by orchestrator `maxAttempts` and relay retry budget).
- **Skip-as-closed** a slice in the queue when repo/docs truth indicates it is already `CLOSED / shipped` (with evidence pointers recorded).
- **Stop-for-human** on any ambiguity or boundary trigger.

### Stop triggers (must escalate to human)

Autopilot must stop and require human disposition when any are true:

- Relay decision is `STOP_FOR_REVIEW` or `BLOCKED`.
- Worker reports: scope ambiguity, contract drift, mixed-plane contamination, unclear validation classification, repo-state drift.
- A slice is already closed/accepted but the plan still includes it (plan drift).
- A slice is at **CONTROL-CLOSEOUT boundary** per `CURRENT_FRONTIER.md` (e.g., “awaiting steward CONTROL-CLOSEOUT” / “BUILD-CLOSEOUT complete”). Autopilot must stop rather than re-run execution.
- The plan references missing files (sprint spec path missing) or a slice ID not found in the sprint spec.
- Next step would require CONTROL-PLANE edits but the run is not explicitly authorized as CONTROL-PLANE.

### Required artifacts (feedback loop)

Each autopilot phase run must emit:

- `artifacts/orchestrator/steward_phase_summary.json` (one file per run; includes cursor, decisions, skips, and artifact pointers).

Autopilot must be able to resume from this file after a crash.

