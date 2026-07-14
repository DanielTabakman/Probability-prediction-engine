# Founder pipeline commands v1

**Plane:** CONTROL-PLANE  
**Status:** Approved command contract; portfolio router implementation pending  
**Canonical home:** GitHub  
**Issue:** #5354  
**Purpose:** Give Daniel a very small command vocabulary for understanding and starting work across PPE, MSOS Autobuilder, TxLINE, and future registered pipelines.

## Core rule

Daniel should not have to remember repository names, branch commands, worker types, prompt templates, or which pipeline has the next safe build.

The founder command layer is a **portfolio router**. It reads canonical pipeline state, selects or reports work, and delegates execution to each pipeline's registered adapter. It does not replace the internal operator, scheduler, gate, publication, or review rules of any pipeline.

A command is not considered implemented merely because its semantics are defined here. Until a command has an evidence-backed implementation, ChatGPT must say that it is interpreting the command manually rather than claiming the installed system executed it.

## Canonical founder commands

### `what's next`

**Type:** Read-only portfolio briefing.

It answers:

- which pipelines are registered;
- which pipelines need attention or execution;
- the next action in each relevant pipeline;
- the single recommended next action overall;
- whether each action is a build, review, evidence check, founder decision, or blocker resolution;
- what is already running or queued when that changes the recommendation.

It must not start, queue, approve, or mutate work.

The output should optimize for the founder's practical question: **What needs to happen next, and on which pipeline?**

### `build next`

**Type:** Single-dispatch command.

It selects and dispatches exactly **one** highest-priority safe work item from the registered portfolio.

Selection must consider:

1. explicit founder priority;
2. deadlines and time-sensitive commitments;
3. pipeline readiness;
4. dependency order;
5. current running and queued work;
6. repository, path, branch, and authority conflicts;
7. available worker and publication capacity.

The selected work item must already be:

- chartered or otherwise bounded;
- marked `READY_TO_BUILD` by its pipeline;
- assigned an execution adapter;
- supplied with acceptance criteria or deterministic evidence requirements;
- within the pipeline's authority boundary.

It must return a build receipt naming at least:

- pipeline;
- work item;
- repository;
- execution adapter or worker lane;
- state (`RUNNING`, `QUEUED`, or `BLOCKED`);
- branch, job, workspace, or other traceable execution identity when available.

One invocation must not silently expand into several builds.

### `build next N`

**Type:** Desired-capacity dispatch command.

It asks the portfolio router to fill **up to N build slots** with the next safe, non-conflicting work.

`N` is desired portfolio capacity, not a promise that N jobs will begin simultaneously. The response must distinguish:

- `RUNNING` — execution has actually started;
- `QUEUED` — accepted but waiting for worker or pipeline capacity;
- `BLOCKED` — selected work cannot proceed;
- `UNFILLED` — no additional safe ready work exists.

The router must never call queued work running.

This command remains an interface contract until multi-lane dispatch and cross-pipeline capacity have production evidence. Initial rollout should prove one build, then two non-overlapping builds, before higher requested capacity is treated as routine.

### `what's running`

**Type:** Read-only execution check-in.

It reports, across all registered pipelines:

- running work;
- queued work;
- blocked work;
- awaiting-review work;
- available and configured capacity;
- stale, failed, or evidence-missing work requiring attention.

For each active item, prefer:

- pipeline;
- work item;
- stage;
- worker or execution lane;
- traceable branch/job/workspace identity;
- blocker or next expected transition.

It must distinguish actual runtime evidence from inferred, stale, or proposed state.

### `commands`

**Type:** Read-only help command.

It lists only the founder-facing command vocabulary, short meanings, and one example each. It must not dump internal scripts or implementation details unless explicitly requested.

The canonical list is:

```text
what's next
build next
build next <number>
what's running
commands
create pipeline <name>
```

### `create pipeline <name>`

**Type:** Pipeline-registration workflow.

It invokes [`PIPELINE_CREATION_SOP_V1.md`](PIPELINE_CREATION_SOP_V1.md).

It does not automatically begin implementation. A pipeline may first be registered as read-only or charter-only. It becomes eligible for `build next` only after its required execution and authority fields are complete and it exposes at least one `READY_TO_BUILD` item.

## Optional precision forms

These forms are allowed when Daniel deliberately wants to narrow the router, but they are not required daily memory:

```text
what's next <pipeline>
build next <pipeline>
build <pipeline> <work-item>
```

Plain `what's next` and `build next` remain the default founder interface.

## Normalized portfolio states

The founder layer may normalize pipeline-specific states into:

| State | Meaning |
|---|---|
| `READY_TO_BUILD` | Bounded work may be safely dispatched |
| `RUNNING` | Execution has actually started |
| `QUEUED` | Accepted and waiting for capacity |
| `AWAITING_REVIEW` | Implementation/evidence exists and needs review |
| `AWAITING_FOUNDER` | Product, strategic, legal, financial, or irreversible decision required |
| `BLOCKED` | Dependency, conflict, failure, or missing evidence prevents progress |
| `COMPLETE` | Pipeline-specific definition of done is satisfied |

A pipeline's native state remains authoritative. Normalization is for founder visibility only.

## Constructed-prompt behavior

These commands are concise founder intents backed by a longer control-plane procedure.

For example, `build next` semantically means:

1. refresh registered pipeline status from GitHub and current runtime evidence;
2. exclude unregistered, unchartered, blocked, conflicting, or unauthorized work;
3. rank ready work using accepted priority and deadlines;
4. select one bounded work item;
5. acquire the required ownership or lease;
6. dispatch through that pipeline's registered adapter;
7. return an evidence-backed receipt.

The detailed procedure belongs in canon and code, not in Daniel's memory.

## Authority and safety rules

1. GitHub is the source of truth for pipeline identity, accepted priorities, charters, interfaces, and definitions of done.
2. Runtime evidence is required before reporting work as running or complete.
3. The portfolio router selects and delegates; each pipeline retains its own internal execution and publication authority.
4. Product decisions are not converted into implementation work without an accepted charter or bounded task packet.
5. Parallel work must fail closed on overlapping paths, unresolved shared interfaces, incompatible source commits, or publisher conflicts.
6. Only one production publisher may own a given publication target unless a later canonical design explicitly changes that boundary.
7. A command must report partial fulfillment honestly. `build next 3` may result in two running and one queued, blocked, or unfilled.

## Explicitly deferred to follow-on design

The following are **not decided by this document**:

- clock-based build schedules;
- continuous capacity refill;
- a `keep N running` command;
- pause/resume semantics for automatic dispatch;
- cross-repository worker allocation;
- production lane count and concurrency caps;
- whether scheduled work is one multi-lane job or several independent jobs;
- automatic prioritization changes when deadlines or failures occur.

Those questions require a separate scheduled-Autobuilder and lane-policy decision grounded in the installed host, queue, scheduler, publisher, and evidence model.

## Initial registered pipelines

The intended initial portfolio is:

- `ppe` — Probability Prediction Engine / MSOS product pipeline;
- `autobuilder` — MSOS Autobuilder infrastructure pipeline;
- `txline` — World Cup / TxLINE hackathon pipeline, after its repository and charter are registered.

Aliases may be conversational, but every pipeline must have one stable canonical ID.

## Acceptance for implementation

A portfolio-router implementation is acceptable only when:

- `what's next` and `what's running` are read-only and evidence-backed;
- plain `build next` dispatches at most one bounded item;
- receipts distinguish running from queued;
- unregistered or non-ready work cannot be selected;
- explicit pipeline overrides do not bypass dependencies or safety rules;
- current commands and implementation status are discoverable through `commands`;
- tests cover ambiguity, no-ready-work, blocked work, capacity exhaustion, and path/authority conflicts.

## COORDINATION STATUS

Agreement: aligned  
Compared: founder decision, control-plane SOP, PPE canonical operator scripts, ARCP worker interface, MSOS Autobuilder operating manual, scheduler, persistent host, and Codex host configuration  
Disagreement: none; earlier examples are narrowed here into an explicit interface contract  
Evidence gap: portfolio router implementation, registered TxLINE pipeline, and real concurrent write-lane witnesses  
Ownership overlap: future router and registry paths require one bounded implementation writer  
Risk if unresolved: conversational commands may be mistaken for installed capabilities or dispatch ambiguous work  
Recommended default: use these semantics immediately in Chat while implementing read-only portfolio status before automated dispatch  
Founder decision required: no
