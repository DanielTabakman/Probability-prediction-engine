# Engineering Operating System v1

Status: **canonical founder operating policy**

Owner of policy: `DanielTabakman/Probability-prediction-engine`  
Runtime executor: `DanielTabakman/msos-autobuilder`

This document defines how Daniel's engineering portfolio is organized and how work is allowed to move from idea to released software. It does not claim a capability is installed merely because the policy describes it. Runtime evidence, tests, gates, and installed witnesses remain authoritative for implementation state.

## Objective

Operate several engineering lanes continuously with minimal founder attention while keeping product meaning, strategic commitments, high-risk authority, and promotion of speculative work with Daniel.

Target flow:

```
idea/backlog
  -> triage
  -> charter
  -> acceptance criteria/tests defined
  -> ready
  -> implementation
  -> automated test
  -> review
  -> staging
  -> release
  -> monitoring/feedback
  -> closed
```

Cursor or any individual agent session is an interface, never the source of truth.

## Portfolio lanes

### 1. Factory / Autobuilder

Purpose: improve the system that executes work across the portfolio.

Workstreams include:

- already-chartered Autobuilder improvements;
- continuous-improvement backlog;
- autonomous execution and refill;
- open-source/API coding backends so execution does not depend on Cursor;
- external usability, testing, and feedback.

Factory remains the first priority until the control plane can reliably run multiple independent lanes with low founder attention.

### 2. MSOS

Purpose: build the Market Structure OS product.

Workstreams include:

- regular committed MSOS development;
- MSOS candidate and research backlog;
- UI/UX simplification;
- Market Thesis end-to-end workflow;
- asset-backed prediction-market exploration and, only if promoted, implementation.

### 3. API / Distribution

Purpose: make useful MSOS capabilities machine-accessible without coupling core product logic to one distribution channel.

Preferred architecture:

```
core capability
  -> stable machine interface
  -> REST/API/MCP adapters
  -> web UI / Qatom / other agent clients
```

Qatom is an important distribution channel, not the core architecture.

### 4. Structured Launchpad

Initial class: **Research / Incubation**

Purpose: investigate a permissionless on-chain structured-product launchpad.

Allowed before promotion:

- architecture research;
- protocol and dependency investigation;
- prototypes;
- feasibility work;
- decision material.

Sustained implementation requires an explicit founder decision to promote this from Incubation to Product.

### 5. Labs

Purpose: contain opportunistic work without contaminating the committed roadmap.

Examples:

- hackathons;
- projects arising from meetings;
- experimental integrations;
- small collaborative builds;
- rapid prototypes.

Every Labs effort must eventually be killed, absorbed into an existing product, or explicitly promoted. Labs is not a permanent holding state.

## Backlog classes

Every item belongs to exactly one class.

### Research

We do not yet know whether the item should be built.

Automation may research, prototype, gather evidence, or draft a charter. It may not promote Research into committed implementation.

### Candidate

The item appears potentially useful but has not earned execution capacity.

Automation may refine scope, deduplicate, estimate, draft acceptance criteria, and prepare a charter. It may not start implementation without approval.

### Committed

The founder has decided the bounded item should be built.

Committed work may enter automated execution after dependencies, authority, charter, and acceptance criteria are satisfied.

## Canonical lifecycle

Production work uses these states:

- `BACKLOG`
- `TRIAGE`
- `CHARTERED`
- `ACCEPTANCE_DEFINED`
- `READY_TO_BUILD`
- `RUNNING`
- `TESTING`
- `REVIEW`
- `STAGING`
- `RELEASED`
- `MONITORING`
- `COMPLETE`

Exceptional states:

- `AWAITING_FOUNDER`
- `BLOCKED`
- `REJECTED`
- `SUPERSEDED`

Adapters may map pipeline-native states into this vocabulary but must not destroy native evidence or falsely imply runtime state.

## Charter contract

No substantial implementation begins without a bounded charter containing:

1. Problem
2. Intended outcome
3. Scope
4. Explicit non-scope
5. Acceptance criteria
6. Dependencies
7. Risks and authority limits
8. Verification
9. Rollback where applicable
10. Ownership / path overlap boundaries

Agents may make ordinary implementation decisions inside an accepted charter.

## Source-of-truth boundary

The existing founder portfolio registry and founder command canon remain the portfolio/control-plane source of truth.

Do not create a competing runtime portfolio registry in `msos-autobuilder`.

Repository responsibilities:

- PPE/MSOS control plane owns founder intent, product priority, pipeline registration, backlog class, product canon, and normalized portfolio visibility.
- Autobuilder owns runtime queue supply, execution, isolation, candidate gates, bounded revision, controlled publication, runtime health, and self-update machinery.
- GitHub issues/PRs/docs contain durable work and evidence. Chat history and Cursor state do not.
- Runtime claims require runtime evidence. Policy text is not proof that a command or lane is installed.

## Lane execution policy

Each active production lane gets an independent queue/status surface.

Failure, blocking, or founder input in one lane must not stall unrelated eligible lanes.

Initial implementation WIP target:

- Factory: 1 active implementation
- MSOS: 1 active implementation
- API / Distribution: 1 active implementation

Research, chartering, testing, and review may proceed concurrently where safe.

Do not expand implementation concurrency merely to maximize activity. Expand only after evidence shows correct isolation, terminal-state recognition, backpressure, refill, review, publication, and recovery.

## Refill and supervision

The target supervisor behavior is:

1. refresh portfolio and runtime evidence;
2. determine actual lane capacity;
3. identify the highest-priority eligible Committed item for each available safe lane;
4. verify dependencies, authority, path ownership, queue/review caps, and freshness;
5. dispatch through the accepted Autobuilder path;
6. observe terminal or blocked state;
7. refill freed capacity without founder prompting;
8. remain silent unless a meaningful exception or founder decision exists.

Retries must be bounded. Repeated failure becomes `BLOCKED` with diagnosis; it must not create an infinite loop.

## Founder escalation boundary

Escalate to Daniel for:

- product-direction choices;
- changes to intended customer behavior;
- promotion of Research/Candidate work into Committed work;
- major architecture changes;
- material new external dependencies or commitments;
- credentials or security-sensitive changes;
- meaningful ongoing spend;
- destructive or irreversible operations;
- production-data risk;
- material charter expansion/contraction;
- conflicting product requirements;
- expansion of merge, deployment, or other high-risk authority.

Do not escalate routine implementation details, formatting, normal refactoring, bounded retries, ordinary test repairs, branch creation, or other decisions already authorized by a charter and policy.

## Feedback policy

External feedback follows:

```
feedback
  -> capture
  -> normalize/deduplicate
  -> Candidate backlog
  -> assess/charter
  -> founder approval when required
  -> execution
```

Feedback never becomes automatic product scope.

## Dashboard requirement

Founder-facing portfolio status must make these questions answerable without reconstructing agent conversations:

- What is running?
- What is next?
- What just finished?
- What is blocked?
- Which decisions actually require Daniel?

Detailed implementation evidence remains available through drill-down.

## Rollout order

Until the control plane is reliable, the portfolio priority is:

1. inventory and clean current engineering state;
2. establish the canonical lifecycle/backlog classification across current work;
3. clean queues and remove/supersede stale or duplicate work;
4. prove independent multi-lane execution;
5. harden refill, terminal-state detection, backpressure, recovery, and supervision;
6. establish Cursor-independent execution through accepted coding APIs/backends;
7. run Factory, MSOS, and API / Distribution as genuine independent production lanes;
8. add a founder dashboard and exception-only reporting;
9. add external testing/feedback ingestion;
10. accelerate MSOS/API backlog consumption;
11. decide whether Structured Launchpad graduates into a Product lane;
12. operate Labs continuously under kill/absorb/promote discipline.

Non-urgent implementation that bypasses steps 1-7 should be resisted until those foundations are functional.

## Existing canon and implementation relationship

This policy extends rather than replaces the existing scheduled-lane, founder-command, pipeline-creation, build-packet, and Autobuilder safety contracts.

In particular:

- the existing `keep N running`, pause/resume, backpressure, and capacity policy remains valid;
- the accepted founder portfolio registry remains canonical;
- Autobuilder's existing candidate gate, revision, controlled publisher, and self-update boundaries remain in force;
- automatic merge/deployment authority is not granted by this document;
- open Factory issues remain authoritative implementation work until inventory explicitly closes, supersedes, or reclassifies them.

## Definition of success

The Engineering Operating System is operational when Daniel can approve several bounded charters, leave the development interface, and later return to evidence that:

- multiple independent lanes progressed;
- completed work was verified;
- failures were diagnosed and bounded;
- staging/release state is visible;
- freed capacity refilled safely;
- product and runtime state are durable in GitHub;
- only genuine founder decisions are waiting.

Closing Cursor must not stop normal eligible engineering execution.

## Governing rule

**Founder attention is the scarce resource.**

Use computation and automation to resolve routine engineering uncertainty before consuming founder attention, while preserving founder control over product meaning and high-risk authority.
