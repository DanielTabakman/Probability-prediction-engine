# Pipeline creation SOP v1

**Plane:** CONTROL-PLANE  
**Status:** Approved registration contract; implementation adapters may be pending  
**Canonical home:** GitHub  
**Issues:** #5354, #5356  
**Purpose:** Define the minimum information and safety boundary required before a project or workstream becomes a founder-visible pipeline, before it becomes eligible for build selection, and before it may participate in continuous scheduled refill.

## Principle

A pipeline is not merely a repository, idea, module, or backlog. It is a named production line with:

- a stable identity;
- a defined outcome;
- canonical state;
- an ordered frontier;
- a way to report status;
- a way to dispatch bounded work;
- explicit authority, validation, concurrency, and scheduling boundaries.

The `create pipeline <name>` command creates or completes this contract. It does not automatically start implementation or scheduled execution.

## Registration stages

A pipeline moves through these registration stages:

| Stage | Meaning | Eligible for `what's next` | Eligible for `build next` | Eligible for `keep N running` |
|---|---|---:|---:|---:|
| `PROPOSED` | Named idea with no accepted contract | No | No | No |
| `REGISTERED_READ_ONLY` | Identity, repo, purpose, and status source exist | Yes | No | No |
| `CHARTERED` | Outcome, scope, non-goals, definition of done, and frontier accepted | Yes | No | No |
| `EXECUTION_READY` | Build adapter, authority, paths, tests, and ready work exist | Yes | Yes | No |
| `SCHEDULE_READY` | Continuous-refill, backpressure, pause/resume, and runtime evidence requirements are accepted | Yes | Yes | Yes |
| `ACTIVE` | Work is running or queued | Yes | Already active | According to recorded automatic-build policy |
| `COMPLETE` | Definition of done satisfied | Historical | No, unless reopened | No, unless reopened and revalidated |

A pipeline may remain read-only, charter-only, or manually dispatchable indefinitely. Technical ability to execute does not automatically grant scheduled eligibility.

## Required pipeline record

Every pipeline must have one canonical record containing the following sections.

### 1. Identity

Required:

- `pipeline_id` — stable lowercase canonical ID;
- display name;
- aliases;
- canonical repository or repositories;
- owner/steward;
- pipeline type, such as product, infrastructure, hackathon, research, or operations.

Rules:

- aliases may be conversational;
- one canonical ID must appear in receipts and status outputs;
- renaming the display name must not silently change the canonical ID;
- a pipeline spanning multiple repos must state which repo owns canon and which repos are execution targets.

### 2. Purpose and outcome

Required:

- problem or opportunity;
- target user or operator;
- intended outcome;
- why this pipeline exists separately from existing pipelines;
- definition of done;
- deadline or external commitment when applicable.

The outcome must be understandable without implementation details.

### 3. Scope and non-goals

Required:

- in-scope capabilities or workstreams;
- explicit non-goals;
- dependencies on other pipelines or shared contracts;
- product, legal, financial, credential, or destructive decisions that remain founder-owned.

A pipeline must not be used to hide scope expansion inside a build or scheduling command.

### 4. Canon and state source

Required:

- canonical charter or program document;
- canonical frontier/backlog/issue source;
- canonical runtime/evidence source;
- precedence rule when documents, runtime, or agents disagree;
- freshness expectations.

GitHub owns accepted decisions. Local runtime state may own mutable execution facts, but it must be summarized through evidence-backed status rather than treated as product canon.

### 5. Frontier

Required:

- completed work;
- current work;
- ordered next work;
- blockers;
- dependencies;
- items awaiting founder or review decisions.

Each build-eligible work item must include:

- stable work-item ID;
- goal;
- why it matters;
- relevant canon;
- allowed paths or repository scope;
- forbidden paths or authority;
- required behavior;
- non-goals;
- acceptance criteria;
- validation commands or evidence;
- ownership/overlap warning.

Scheduled selection may only use work items currently marked `READY_TO_BUILD` by the pipeline's authoritative frontier/status adapter.

### 6. Status adapter

Required for `REGISTERED_READ_ONLY`:

- how `what's next` reads current state;
- how `what's running` reads actual runtime state;
- native-to-founder state mapping;
- how stale or missing evidence is reported;
- what counts as ready, running, queued, backpressured, blocked, awaiting review, awaiting founder, unfilled, and complete.

The adapter may be manual at first, but the output must identify that fact. Manual or inferred state is not sufficient for reporting a build as actually running.

### 7. Build adapter

Required for `EXECUTION_READY`:

- command, API, job feed, issue-to-Codex handoff, or other dispatch mechanism;
- worker/runtime options;
- branch, clone, or worktree isolation model;
- lease or ownership mechanism;
- output/evidence location;
- candidate gate;
- revision behavior;
- publication boundary;
- cancellation and failure behavior.

The build adapter must fail closed if its preconditions are missing.

### 8. Authority boundary

Required:

- what the pipeline may implement automatically;
- what requires founder judgment;
- what requires independent review;
- merge authority;
- publication authority;
- credentials or spending authority;
- destructive-action authority;
- rollback or recovery owner.

A pipeline cannot inherit broader authority merely because the Autobuilder can technically execute commands or because automatic capacity is available.

### 9. Concurrency contract

Required before parallel eligibility:

- repository/workspace isolation;
- allowed and forbidden path sets;
- shared interfaces and their owner;
- source commit policy;
- path-overlap detection;
- branch naming;
- worker concurrency cap;
- publisher concurrency cap;
- integration order;
- behavior when work items depend on unfinished work.

Default rules:

1. overlapping write ownership is forbidden;
2. unresolved shared interfaces serialize dependent work;
3. parallel workers use isolated clones or worktrees;
4. running and queued are reported separately;
5. publication remains serialized when a target has one publisher;
6. capacity is a maximum, not an obligation to fill unsafe slots;
7. independent workers must not depend on hidden shared conversation context;
8. shared truth must already exist in GitHub or the accepted source checkout.

### 10. Validation and evidence

Required:

- tests or checks before candidate acceptance;
- integration validation;
- runtime or demo witness when applicable;
- immutable evidence path;
- review requirement;
- definition of failure;
- retry/revision policy;
- completion evidence.

No pipeline is complete because an agent said it completed. No pipeline is scheduled because a configuration value exists without a runtime witness.

### 11. Founder visibility

Required:

- how the pipeline appears in `what's next`;
- how it appears in `what's running`;
- short founder-facing name;
- current registration stage;
- current execution stage;
- next action;
- blocker, backpressure, or decision language;
- traceable links or identities.

The founder view should hide low-level mechanics by default while preserving inspectability.

### 12. Scheduling eligibility

Required for `SCHEDULE_READY` under [`SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md`](SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md):

- whether automatic refill is permitted;
- pipeline-specific maximum active worker slots, if lower than the portfolio maximum;
- queue and awaiting-review caps;
- automatic revision limit;
- dispatch-window or quiet-hours policy, if any;
- pause/resume behavior;
- backpressure conditions;
- failure classification and escalation behavior;
- deadline and fairness participation;
- runtime adapter used by the refill controller;
- restart/recovery behavior;
- immutable selection and dispatch evidence;
- accepted staged witness proving scheduled behavior.

A pipeline becomes schedule-ready only after its runtime evidence shows that automatic selection and dispatch fail closed. Registration alone is insufficient.

## Creation workflow

When Daniel says `create pipeline <name>`:

1. Search GitHub for an existing pipeline, charter, repo, issue, or conflicting canonical identity.
2. Reuse or extend existing canon instead of creating duplicates.
3. Resolve the stable pipeline ID and aliases.
4. Record purpose, outcome, scope, non-goals, deadline, and definition of done.
5. Identify canon, frontier, runtime evidence, and disagreement precedence.
6. Register a read-only status adapter.
7. Identify the smallest first work item.
8. Define authority, paths, validation, publication, and failure behavior.
9. Register a build adapter only when execution is genuinely ready.
10. Add the pipeline to founder portfolio visibility.
11. Open a bounded implementation issue/PR for missing automation.
12. Return a pipeline-registration receipt.
13. Promote to `SCHEDULE_READY` only through a separate scheduling review and witness.

## Pipeline-registration receipt

The receipt should contain:

```text
PIPELINE REGISTERED

ID: <pipeline_id>
Name: <display name>
Stage: <REGISTERED_READ_ONLY | CHARTERED | EXECUTION_READY | SCHEDULE_READY>
Canonical repo: <owner/repo>
Canon: <document/issue>
Status source: <adapter/source>
Build adapter: <adapter or NOT READY>
Next action: <work item or decision>
Build-next eligible: <yes/no>
Continuous-refill eligible: <yes/no>
Missing requirements: <none or concise list>
```

## Initial portfolio application

### PPE

Expected canonical ID: `ppe`.

It already has substantial product canon, frontiers, operator status, worker routing, and build/closeout commands. Portfolio registration should adapt those existing sources rather than create a replacement operator.

PPE scheduled eligibility requires read-only portfolio/status evidence, a valid Autobuilder build adapter for selected work, backpressure, and staged runtime witnesses. The existing single desktop worker lease is not by itself proof of portfolio-level parallel scheduling.

### MSOS Autobuilder

Expected canonical ID: `autobuilder`.

Its canonical repository is `DanielTabakman/msos-autobuilder`. Registration must distinguish:

- infrastructure implementation;
- installed-host runtime;
- update-supervisor evidence;
- product-job execution;
- refill-controller state;
- controlled publication.

Autobuilder improvements must not silently become product priorities. Scheduled building of accepted Autobuilder work does not grant autonomous new-improvement generation or self-deployment authority.

### TxLINE hackathon

Expected canonical ID: `txline`.

Before execution eligibility it requires:

- a canonical repository or explicitly isolated execution target;
- a short hackathon charter;
- deadline and demo definition of done;
- ordered frontier;
- data/API assumptions;
- allowed paths and validation;
- a status and build adapter.

Before scheduled eligibility it also requires:

- independent queue/review limits;
- failure and demo-witness behavior;
- concurrency compatibility with PPE and Autobuilder;
- a real registered adapter witness.

Conversational aliases may include `hackathon` and `world-cup`.

## Scheduling policy

Pipeline registration uses [`SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md`](SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md).

The accepted v1 model is:

- schedule continuous safe capacity, not blind named-job clock launches;
- keep enabled capacity at one until the single-slot witness passes;
- enable routine capacity two only after same-repository, cross-pipeline, refill, and backpressure witnesses pass;
- use event-driven refill with periodic reconciliation;
- maintain independent canonical work items even when grouped into one execution batch;
- serialize publication per target repository;
- stop affected refill on queue/review caps, stale evidence, failure limits, conflicts, or founder decisions;
- allow unrelated safe pipelines to continue.

A time window may suppress new starts but must not terminate running work.

## Acceptance checklists

### `EXECUTION_READY`

A pipeline may be marked `EXECUTION_READY` only when all are true:

- [ ] stable ID, aliases, and canonical repo recorded;
- [ ] purpose, outcome, scope, non-goals, and definition of done accepted;
- [ ] frontier and at least one bounded work item exist;
- [ ] status adapter reports evidence freshness;
- [ ] build adapter exists and fails closed;
- [ ] authority and founder-decision boundaries are explicit;
- [ ] allowed/forbidden paths or equivalent ownership scope exist;
- [ ] validation and immutable evidence requirements exist;
- [ ] concurrency and publisher boundaries are explicit;
- [ ] founder portfolio output is defined;
- [ ] conflicts with existing pipelines have been surfaced rather than silently resolved.

### `SCHEDULE_READY`

A pipeline may be marked `SCHEDULE_READY` only when all `EXECUTION_READY` requirements and all of the following are true:

- [ ] automatic-refill permission and runtime adapter recorded;
- [ ] queue, review, revision, and worker caps recorded;
- [ ] backpressure and founder-decision stop conditions recorded;
- [ ] pause/resume and restart recovery defined;
- [ ] priority, deadline, and fairness inputs trace to accepted canon;
- [ ] duplicate immutable job prevention exists;
- [ ] selection and dispatch evidence is durable;
- [ ] required single-slot or later concurrency witness accepted;
- [ ] cross-repository behavior remains disabled unless separately witnessed;
- [ ] no autonomous scope, merge, or deployment authority was added implicitly.

## COORDINATION STATUS

Agreement: aligned  
Compared: founder decisions, control-plane SOP, PPE operator/worker contracts, Autobuilder operating manual, scheduled Autobuilder lane policy, current host/scheduler architecture, and planned TxLINE work  
Disagreement: none  
Evidence gap: portfolio registry implementation, completed TxLINE registration, continuous refill controller, and staged runtime witnesses  
Ownership overlap: pipeline canon belongs in its canonical repo; PPE portfolio registry and msos-autobuilder refill runtime require separate single writers  
Risk if unresolved: named pipelines may become automatically selectable without reliable readiness, backpressure, authority, or execution boundaries  
Recommended default: register pipelines read-only first, promote to execution-ready with adapters, and promote to schedule-ready only after a real witness  
Founder decision required: no
