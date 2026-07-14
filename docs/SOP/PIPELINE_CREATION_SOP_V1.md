# Pipeline creation SOP v1

**Plane:** CONTROL-PLANE  
**Status:** Approved registration contract; implementation adapters may be pending  
**Canonical home:** GitHub  
**Issue:** #5354  
**Purpose:** Define the minimum information and safety boundary required before a project or workstream becomes a founder-visible pipeline and before it becomes eligible for automatic build selection.

## Principle

A pipeline is not merely a repository, idea, module, or backlog. It is a named production line with:

- a stable identity;
- a defined outcome;
- canonical state;
- an ordered frontier;
- a way to report status;
- a way to dispatch bounded work;
- explicit authority, validation, and concurrency boundaries.

The `create pipeline <name>` command creates or completes this contract. It does not automatically start implementation.

## Registration stages

A pipeline moves through these registration stages:

| Stage | Meaning | Eligible for `what's next` | Eligible for `build next` |
|---|---|---:|---:|
| `PROPOSED` | Named idea with no accepted contract | No | No |
| `REGISTERED_READ_ONLY` | Identity, repo, purpose, and status source exist | Yes | No |
| `CHARTERED` | Outcome, scope, non-goals, definition of done, and frontier accepted | Yes | No |
| `EXECUTION_READY` | Build adapter, authority, paths, tests, and ready work exist | Yes | Yes |
| `ACTIVE` | Work is running or queued | Yes | Already active |
| `COMPLETE` | Definition of done satisfied | Historical | No, unless reopened |

A pipeline may remain read-only or charter-only indefinitely.

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

A pipeline must not be used to hide scope expansion inside a build command.

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

### 6. Status adapter

Required for `REGISTERED_READ_ONLY`:

- how `what's next` reads current state;
- how `what's running` reads actual runtime state;
- native-to-founder state mapping;
- how stale or missing evidence is reported;
- what counts as running, queued, blocked, awaiting review, and complete.

The adapter may be manual at first, but the output must identify that fact.

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

A pipeline cannot inherit broader authority merely because the Autobuilder can technically execute commands.

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
6. capacity is a maximum, not an obligation to fill unsafe slots.

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

No pipeline is complete because an agent said it completed.

### 11. Founder visibility

Required:

- how the pipeline appears in `what's next`;
- how it appears in `what's running`;
- short founder-facing name;
- current stage;
- next action;
- blocker or decision language;
- traceable links or identities.

The founder view should hide low-level mechanics by default while preserving inspectability.

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

## Pipeline-registration receipt

The receipt should contain:

```text
PIPELINE REGISTERED

ID: <pipeline_id>
Name: <display name>
Stage: <REGISTERED_READ_ONLY | CHARTERED | EXECUTION_READY>
Canonical repo: <owner/repo>
Canon: <document/issue>
Status source: <adapter/source>
Build adapter: <adapter or NOT READY>
Next action: <work item or decision>
Build-next eligible: <yes/no>
Missing requirements: <none or concise list>
```

## Initial portfolio application

### PPE

Expected canonical ID: `ppe`.

It already has substantial product canon, frontiers, operator status, worker routing, and build/closeout commands. Portfolio registration should adapt those existing sources rather than create a replacement operator.

### MSOS Autobuilder

Expected canonical ID: `autobuilder`.

Its canonical repository is `DanielTabakman/msos-autobuilder`. Registration must distinguish infrastructure implementation, installed-host runtime, update-supervisor evidence, and product-job execution. Autobuilder improvements must not silently become product priorities.

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

Conversational aliases may include `hackathon` and `world-cup`.

## Scheduling boundary

Pipeline registration does not decide scheduled execution.

A later scheduled-Autobuilder design must determine:

- whether schedules target pipelines, work items, capacity, or time windows;
- whether one scheduler spans repositories;
- how many lanes may run concurrently;
- how slots refill;
- pause/resume and quiet-hours behavior;
- power, network, authentication, cost, and deadline policies;
- how founder-required decisions stop automatic refill;
- how failed or stale work affects prioritization;
- how one publisher serializes multiple completed candidates.

Until that design is accepted, pipeline registration only makes work visible and dispatchable; it does not make it continuously scheduled.

## Acceptance checklist

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

## COORDINATION STATUS

Agreement: aligned  
Compared: founder decision, control-plane SOP, PPE operator/worker contracts, Autobuilder operating manual, current host/scheduler architecture, and planned TxLINE work  
Disagreement: none  
Evidence gap: portfolio registry implementation and completed TxLINE registration  
Ownership overlap: pipeline canon belongs in its canonical repo; portfolio registry and adapters require one control-plane writer  
Risk if unresolved: named pipelines may exist without reliable next-state, authority, or execution boundaries  
Recommended default: register pipelines read-only first, then promote each to execution-ready only with evidence-backed adapters  
Founder decision required: no
