# Founder pipeline commands v1

**Plane:** CONTROL-PLANE  
**Status:** Approved command contract; portfolio router and continuous refill implementation pending  
**Canonical home:** GitHub  
**Issues:** #5354, #5356  
**Purpose:** Give Daniel a very small command vocabulary for understanding and starting work across PPE, MSOS Autobuilder, TxLINE, and future registered pipelines.

## Core rule

Daniel should not have to remember repository names, branch commands, worker types, prompt templates, which pipeline has the next safe build, or when a worker slot has become free.

The founder command layer is a **portfolio router**. It reads canonical pipeline state, selects or reports work, and delegates execution to each pipeline's registered adapter. It does not replace the internal operator, scheduler, gate, publication, or review rules of any pipeline.

A command is not considered implemented merely because its semantics are defined here. Until a command has an evidence-backed implementation, ChatGPT must say that it is interpreting the command manually rather than claiming the installed system executed it.

Continuous build behavior is governed by [`SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md`](SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md).

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
3. dependency-unblock value;
4. pipeline readiness and evidence freshness;
5. current running and queued work;
6. repository, path, branch, and authority conflicts;
7. available worker and publication capacity;
8. portfolio fairness and age within the same priority class.

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

**Type:** One-time desired-capacity dispatch command.

It asks the portfolio router to fill **up to N build slots once** with the next safe, non-conflicting work.

`N` is desired portfolio capacity for this reconciliation, not a promise that N jobs will begin simultaneously. The response must distinguish:

- `RUNNING` — execution has actually started;
- `QUEUED` — accepted but waiting for worker or pipeline capacity;
- `BLOCKED` — selected work cannot proceed;
- `UNFILLED` — no additional safe ready work exists;
- `BACKPRESSURE` — work exists but a queue, review, failure, or publisher limit stops dispatch.

The router must never call queued work running.

Unlike `keep N running`, this command does not establish a persistent refill target. It fills safe current capacity and then returns.

This command remains an interface contract until multi-lane dispatch and cross-pipeline capacity have production evidence. Initial rollout must prove one build, then two non-overlapping builds, before higher requested capacity is treated as routine.

### `keep N running`

**Type:** Continuous desired-capacity command.

It records a persistent automatic-build target of up to `N` active build-worker slots and refills safe empty slots as work completes.

It must:

1. reconcile registered pipeline and runtime state;
2. calculate actual available build capacity;
3. apply readiness, ownership, authority, queue, review, failure, and publisher limits;
4. select only accepted `READY_TO_BUILD` work;
5. dispatch enough work to fill safe capacity;
6. continue reconciling after relevant events and host restarts when durable policy evidence exists;
7. report running, queued, blocked, backpressure, and unfilled states distinctly.

It may leave slots empty. It may not invent scope or resolve founder decisions to satisfy the requested number.

The staged rollout is:

```text
keep 1 running → single-slot witness
keep 2 running → only after same-repo, cross-pipeline, refill, and backpressure witnesses pass
```

The initial future steady-state target is two build-worker slots across the whole portfolio, not two per pipeline.

### `pause builds`

**Type:** Graceful automatic-dispatch pause.

It must:

- stop selecting and dispatching new build work;
- preserve the previous desired capacity;
- allow current workers to finish;
- allow relay, gate, bounded revision, evidence archival, and already-authorized publication to finish safely;
- preserve queue and execution evidence.

It must not terminate running workers or erase work. Emergency cancellation remains a separate recovery action.

### `resume builds`

**Type:** Reconciliation and refill command.

It must refresh canonical pipeline state, runtime health, evidence freshness, queue state, review backpressure, and publisher state before restoring the previous desired capacity.

It must fail closed when the prior target or current state cannot be established.

### `what's running`

**Type:** Read-only execution check-in.

It reports, across all registered pipelines:

- automatic build mode (`ENABLED`, `PAUSED`, or `DISABLED`);
- desired and configured capacity;
- running work;
- queued work;
- blocked work;
- awaiting-review work;
- available capacity;
- active backpressure;
- stale, failed, or evidence-missing work requiring attention;
- the last reconciliation identity and freshness when available.

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
keep <number> running
pause builds
resume builds
what's running
commands
create pipeline <name>
```

### `create pipeline <name>`

**Type:** Pipeline-registration workflow.

It invokes [`PIPELINE_CREATION_SOP_V1.md`](PIPELINE_CREATION_SOP_V1.md).

It does not automatically begin implementation. A pipeline may first be registered as read-only or charter-only. It becomes eligible for `build next` only after its required execution and authority fields are complete and it exposes at least one `READY_TO_BUILD` item.

It becomes eligible for `keep N running` only after its scheduling eligibility, concurrency contract, backpressure limits, and runtime evidence are complete.

## Optional precision forms

These forms are allowed when Daniel deliberately wants to narrow the router, but they are not required daily memory:

```text
what's next <pipeline>
build next <pipeline>
build <pipeline> <work-item>
keep <number> running for <pipeline>
```

Plain `what's next`, `build next`, and `keep N running` remain the default founder interface.

An explicit pipeline form narrows selection but must not bypass safety, dependency, authority, or backpressure rules.

## Normalized portfolio states

The founder layer may normalize pipeline-specific states into:

| State | Meaning |
|---|---|
| `READY_TO_BUILD` | Bounded work may be safely dispatched |
| `RUNNING` | Execution has actually started |
| `QUEUED` | Accepted and waiting for capacity |
| `AWAITING_REVIEW` | Implementation/evidence exists and needs review |
| `AWAITING_FOUNDER` | Product, strategic, legal, financial, or irreversible decision required |
| `BACKPRESSURE` | Work exists but a configured queue, review, failure, or publisher limit stops new dispatch |
| `BLOCKED` | Dependency, conflict, failure, or missing evidence prevents progress |
| `UNFILLED` | Requested capacity remains empty because no safe ready work exists |
| `COMPLETE` | Pipeline-specific definition of done is satisfied |

A pipeline's native state remains authoritative. Normalization is for founder visibility only.

## Constructed-prompt behavior

These commands are concise founder intents backed by a longer control-plane procedure.

For example, `build next` semantically means:

1. refresh registered pipeline status from GitHub and current runtime evidence;
2. exclude unregistered, unchartered, blocked, conflicting, stale, backpressured, or unauthorized work;
3. rank ready work using accepted priority, deadlines, dependency value, fairness, and age;
4. select one bounded work item;
5. acquire the required ownership or lease;
6. dispatch through that pipeline's registered adapter;
7. return an evidence-backed receipt and selection explanation.

`keep N running` performs the same safe selection repeatedly whenever capacity becomes available, while automatic mode remains enabled.

The detailed procedure belongs in canon and code, not in Daniel's memory.

## Authority and safety rules

1. GitHub is the source of truth for pipeline identity, accepted priorities, charters, interfaces, definitions of done, and scheduling eligibility.
2. Runtime evidence is required before reporting work as running or complete.
3. The portfolio router selects and delegates; each pipeline retains its own internal execution and publication authority.
4. Product decisions are not converted into implementation work without an accepted charter or bounded task packet.
5. Parallel work must fail closed on overlapping paths, unresolved shared interfaces, incompatible source commits, or publisher conflicts.
6. Only one production publisher may own a given publication target unless a later canonical design explicitly changes that boundary.
7. A command must report partial fulfillment honestly. `build next 3` or `keep 3 running` may result in two running and one queued, blocked, backpressured, or unfilled.
8. Pausing automatic dispatch does not cancel running work.
9. Founder-required decisions block affected work only; unrelated safe pipelines may continue.
10. Approved Autobuilder improvements may be selected, but autonomous new-work generation and self-deployment require their separate acceptance boundaries.

## Scheduling policy

The accepted scheduling and lane model lives in [`SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md`](SCHEDULED_AUTOBUILDER_LANE_POLICY_V1.md).

Key v1 defaults are:

```text
Scheduling target: continuous safe capacity
Future steady-state build-worker capacity: 2 total
First enabled witness capacity: 1
Maximum queued ready builds: 4 total
Maximum awaiting-review candidates: 2 per target repository
Automatic bounded revisions: 1 per candidate
Production publishers: 1 per target repository
Dispatch window: whenever the host is awake, healthy, authenticated, and automatic mode is enabled
```

Clock windows may suppress new starts but must not kill running work.

## Initial registered pipelines

The intended initial portfolio is:

- `ppe` — Probability Prediction Engine / MSOS product pipeline;
- `autobuilder` — MSOS Autobuilder infrastructure pipeline;
- `txline` — World Cup / TxLINE hackathon pipeline, after its repository and charter are registered.

Aliases may be conversational, but every pipeline must have one stable canonical ID.

## Acceptance for implementation

A portfolio-router and continuous-command implementation is acceptable only when:

- `what's next`, `what's running`, and `commands` are read-only and evidence-backed;
- plain `build next` dispatches at most one bounded item;
- receipts distinguish running, queued, blocked, backpressure, and unfilled;
- unregistered or non-ready work cannot be selected;
- explicit pipeline overrides do not bypass dependencies or safety rules;
- `keep N running` persists and reconciles desired capacity without duplicate jobs;
- pause stops new dispatch without killing current work;
- resume performs a full fail-closed reconciliation;
- queue and review backpressure are enforced;
- current commands and implementation status are discoverable through `commands`;
- tests cover ambiguity, no-ready-work, blocked work, stale evidence, capacity exhaustion, pause/resume, backpressure, path/authority conflicts, and restart recovery;
- staged runtime witnesses prove capacity one before capacity two.

## COORDINATION STATUS

Agreement: aligned  
Compared: founder decisions, control-plane SOP, PPE canonical operator scripts, ARCP worker interface, MSOS Autobuilder operating manual, scheduler, persistent host, controlled publisher, and scheduled Autobuilder lane policy  
Disagreement: none  
Evidence gap: portfolio router implementation, registered TxLINE pipeline, continuous refill controller, and staged concurrent write-lane witnesses  
Ownership overlap: PPE owns founder command and registry semantics; msos-autobuilder owns refill runtime and queue execution  
Risk if unresolved: conversational commands may be mistaken for installed capabilities or dispatch ambiguous/unbounded work  
Recommended default: use these semantics immediately in Chat, then implement read-only portfolio status before single-slot automatic refill  
Founder decision required: no
