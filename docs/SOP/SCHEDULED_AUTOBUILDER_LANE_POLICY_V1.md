# Scheduled Autobuilder and lane policy v1

**Plane:** CONTROL-PLANE  
**Status:** Approved operating policy; runtime implementation pending  
**Canonical home:** GitHub  
**Issue:** #5356  
**Purpose:** Define how registered pipelines may be continuously supplied to the MSOS Autobuilder without requiring Daniel to repeatedly return, while preserving product authority, path ownership, evidence, review backpressure, and single-publisher safety.

## Decision

The scheduled Autobuilder uses **continuous capacity scheduling**, not blind clock-based launches.

The founder sets a desired number of active build-worker slots. While automatic mode is enabled, the system may refill empty slots from already accepted, registered, implementation-ready work. It may not invent product scope, resolve founder decisions, bypass dependencies, or call queued work running.

The initial production target is **two Codex write-worker slots across the whole portfolio**, reached only through staged witnesses:

1. continuous single-slot refill;
2. two non-overlapping write lanes in one repository;
3. one cross-pipeline or cross-repository two-lane witness;
4. continuous two-slot refill with backpressure.

Configured capability is not proof. A higher capacity remains disabled until its required witness is accepted.

## Vocabulary

| Term | Meaning |
|---|---|
| **Pipeline** | A registered production line such as `ppe`, `autobuilder`, or `txline` |
| **Work item** | One canonical bounded objective with acceptance criteria and a stable ID |
| **Work lane** | One execution instance with its own source identity, branch, workspace, allowed paths, and evidence |
| **Worker slot** | One actual running Codex or equivalent build process |
| **Execution batch** | A temporary grouping of compatible work lanes for one scheduler invocation |
| **Processing stage** | Build, relay, candidate gate, revision, publication, or review |
| **Desired capacity** | Maximum active build-worker slots requested by the founder |
| **Refill** | Selecting and dispatching a safe ready work item after capacity becomes available |
| **Backpressure** | A rule that stops new dispatch because queue, review, failure, or publication limits have been reached |

Pipelines, work lanes, worker slots, and processing stages must not be presented as interchangeable.

## Founder commands

This policy extends [`FOUNDER_PIPELINE_COMMANDS_V1.md`](FOUNDER_PIPELINE_COMMANDS_V1.md).

### `keep N running`

**Type:** Continuous desired-capacity command.

It records an automatic-build target of up to `N` active build-worker slots. It then reconciles current state and fills only safe available capacity.

It does not promise that `N` jobs will run. The result may contain:

- `RUNNING` — execution has actually started;
- `QUEUED` — accepted but waiting for capacity;
- `BLOCKED` — a selected item cannot proceed;
- `UNFILLED` — no additional safe ready item exists;
- `BACKPRESSURE` — work exists but a queue, review, failure, or publisher limit stops dispatch.

`keep N running` remains active across individual job completions and host restarts only after the runtime implementation provides durable policy state and restart evidence.

### `pause builds`

**Type:** Graceful automatic-dispatch pause.

It must:

- stop selecting or dispatching new build work;
- preserve the previous desired capacity;
- allow current workers to finish;
- allow relay, gate, bounded revision, evidence archival, and already-authorized publication to finish safely;
- preserve queue and execution evidence.

It must not kill running workers or erase work. Emergency cancellation remains a separate recovery action.

### `resume builds`

**Type:** Reconciliation and refill command.

It must:

1. refresh registered pipeline state;
2. verify runtime health and evidence freshness;
3. verify queue and review backpressure;
4. restore the previous desired capacity;
5. refill safe empty slots.

Resume must fail closed when the prior capacity or current state cannot be established.

## What is scheduled

The primary scheduling target is **capacity**.

The system does not normally schedule a named job at a fixed time. It maintains a desired amount of safe active work from the accepted portfolio frontier.

Clock windows are secondary policy. A dispatch window may prevent new starts outside permitted hours, but closing a window must not terminate running work.

The v1 default is:

```text
Dispatch window: whenever the installed host is awake, healthy, authenticated, and automatic mode is enabled
```

Quiet hours, battery policy, network limits, and cost windows may be added later as explicit policy fields. They may suppress refill; they may not weaken safety checks.

## Architecture and ownership

```text
GitHub pipeline canon and frontiers
        ↓
PPE portfolio registry and status adapters
        ↓
Deterministic selection decision
        ↓
MSOS Autobuilder refill controller
        ↓
Immutable approved job(s)
        ↓
Persistent host queue
        ↓
Parallel worker scheduler and isolated workspaces
        ↓
Relay → candidate gate → bounded revision → controlled draft publisher
```

Ownership is split deliberately:

### PPE control plane owns

- founder command semantics;
- pipeline registration;
- accepted priorities and deadlines;
- native-to-founder status normalization;
- work-item readiness;
- product and strategy canon;
- selection policy and explanation.

### MSOS Autobuilder owns

- durable automatic-build runtime policy;
- refill reconciliation;
- queue supply;
- immutable job construction or import;
- worker capacity enforcement;
- leases, workspaces, and execution evidence;
- host recovery;
- relay, gate, revision, and controlled publication execution.

The Autobuilder must not implement a competing portfolio registry or silently reinterpret PPE priorities. PPE must not implement a second runtime queue or publisher.

## Pipeline and repository scope

One portfolio scheduler may span multiple registered pipelines and repositories.

Each pipeline retains its own:

- canonical repository or execution target;
- status adapter;
- build adapter;
- source-commit policy;
- allowed and forbidden paths;
- validation and evidence rules;
- publication and merge boundary;
- definition of done.

The refill controller delegates through those adapters. It must not assume every pipeline uses the PPE host configuration or publication path.

Cross-repository dispatch remains disabled until the registry, repository allowlist, adapter contract, and a real witness are accepted.

## Work-item and batch model

Work items remain independent canonical units.

Each scheduled work item requires:

- stable pipeline and work-item IDs;
- exact canonical source identity;
- bounded instruction;
- allowed and forbidden ownership scope;
- acceptance criteria;
- validation or evidence requirements;
- authority and publication boundary;
- current `READY_TO_BUILD` evidence.

Compatible work items may be grouped into one execution batch when the installed host requires a multi-lane manifest. Grouping is an implementation optimization only.

A batch must not erase independent:

- work-item identity;
- success or failure state;
- retry/revision limits;
- evidence;
- review status;
- publication outcome.

A failed lane must not make unrelated completed lanes disappear. A batch must not become a giant cross-project all-or-nothing unit.

## Selection policy

The portfolio registry ranks eligible work in this order:

1. explicit accepted founder priority;
2. accepted external deadline;
3. dependency-unblock value;
4. pipeline readiness and evidence freshness;
5. portfolio fairness;
6. age within the same priority class.

Portfolio fairness means:

- prefer one active slot per ready pipeline before assigning a second slot to one pipeline;
- allow both slots on one pipeline when no other pipeline has safe ready work;
- allow an explicit founder priority or accepted deadline to override fairness;
- never fill capacity merely to satisfy fairness.

The selection record must state why the chosen item ranked above other eligible items.

The following are excluded:

- unregistered pipelines;
- pipelines below `EXECUTION_READY`;
- stale or missing runtime evidence;
- `AWAITING_FOUNDER` items;
- blocked dependencies;
- unresolved shared-interface ownership;
- path or branch conflicts;
- incompatible source identities;
- unavailable or unauthorized adapters;
- work that exceeds queue, review, revision, cost, or publisher limits.

An explicit pipeline override may narrow the candidate set but may not bypass exclusions.

## Refill behavior

Refill is **event-driven with periodic reconciliation**.

A reconciliation should occur when:

- a worker starts, completes, fails, or is interrupted;
- a candidate gate passes or fails;
- a bounded revision completes or exhausts its limit;
- a draft candidate enters or leaves review backlog;
- a pipeline publishes a new `READY_TO_BUILD` item;
- a priority, deadline, or founder decision changes;
- authentication, network, host, or publisher health changes;
- automatic mode is paused or resumed.

A periodic reconciliation acts only as a missed-event fallback. It must not create duplicate immutable jobs.

On each reconciliation:

1. read durable automatic-build policy;
2. refresh pipeline registry and native status;
3. read actual worker, queue, gate, review, and publisher state;
4. calculate available build capacity;
5. apply exclusions and backpressure;
6. rank eligible work;
7. dispatch only enough work to fill safe capacity;
8. record the decision and evidence;
9. report running, queued, blocked, backpressure, and unfilled states honestly.

## Capacity policy

### Initial configured limits

```text
Future steady-state build-worker capacity: 2 total
First enabled witness capacity: 1
Maximum queued ready builds: 4 total
Maximum awaiting-review candidates: 2 per target repository
Automatic bounded revisions: 1 per candidate
Production publishers: 1 per target repository
```

These are initial safety limits, not permanent product commitments.

A processing-stage service such as relay, gate, revision loop, or publisher does not consume a Codex build-worker slot unless it actually invokes a configured build backend.

Capacity is a maximum. The system may intentionally leave slots empty.

## Backpressure

New dispatch stops for an affected target when any configured limit is reached.

Backpressure conditions include:

- awaiting-review candidate cap;
- pending/queued job cap;
- exhausted revision limit;
- unresolved repeated failure class;
- stale source or main-branch drift;
- unavailable candidate gate;
- unavailable or conflicting publisher;
- failed authentication, network, power, or host health;
- founder-required decision;
- missing ready work.

Backpressure is scoped when possible. A blocked TxLINE pipeline should not stop unrelated PPE or Autobuilder work.

Review backpressure exists to prevent automatic scheduling from converting founder orchestration savings into an unbounded draft-PR backlog.

## Failure and revision policy

The v1 automatic path permits at most one configured bounded revision per candidate.

After the revision limit is exhausted:

1. mark the affected work item `BLOCKED`;
2. preserve immutable reports, patches, gate evidence, and failure classification;
3. release its build capacity;
4. continue unrelated safe work;
5. notify Daniel only when the failure is meaningful or requires a decision.

Repeated failures are evidence about design. The controller must not create endless retries, flags, bypasses, or rewritten job IDs.

Interrupted work is archived according to the host recovery contract and must not be silently rerun without a new allowed decision.

## Shared interfaces and parallel work

Two lanes may run simultaneously only when:

- they have separate work-item and lane IDs;
- they use isolated branches and workspaces;
- their allowed ownership roots do not overlap;
- shared interfaces are already accepted and owned;
- both start from compatible exact source identities;
- each has independent validation and evidence;
- publication can be serialized safely.

Dependent work that requires another lane's unfinished output is queued, not run in parallel.

Context windows are independent. Shared truth must exist in GitHub and the source checkout; workers must not depend on hidden conversation or another worker's uncommitted reasoning.

## Publication policy

Builds may run concurrently. Publication remains serialized per target repository.

The controlled publisher remains the only writer for its configured product target and retains no authority to:

- write product `main`;
- force-push;
- mark a PR ready;
- add automerge authority;
- merge.

Multiple completed candidates may wait for publication or review. Each candidate is revalidated against current target state and fails closed on overlapping drift.

## Founder decisions

Founder-required decisions block only affected work.

Examples include:

- product meaning or customer-facing behavior;
- trading or wagering semantics;
- materially different architecture or strategy;
- legal, compliance, credential, spending, or destructive actions;
- a change to definition of done;
- a priority conflict not already resolved in canon.

The scheduler may continue unrelated work with current authority. It may not infer a decision merely because a worker slot is empty.

## Autobuilder self-improvement

Autobuilder infrastructure work may participate in scheduled selection when it is already accepted, bounded, execution-ready, and non-conflicting.

The following remain separate authority levels:

1. execute a founder-selected bounded job;
2. select among already accepted ready jobs;
3. propose or generate new internal improvements from evidence;
4. deploy a new Autobuilder release automatically.

This policy authorizes the design and staged implementation of level 2 only.

Level 3 remains governed by `DanielTabakman/msos-autobuilder#33`. Level 4 remains governed by the complete acceptance boundary of `DanielTabakman/msos-autobuilder#32` and its update-supervisor witnesses.

Scheduled building must not silently expand autonomous self-improvement or deployment authority.

## Rollout and acceptance witnesses

### Phase 1 — read-only portfolio visibility

- implement the canonical registry;
- register PPE and Autobuilder;
- expose evidence-backed `what's next`, `what's running`, and `commands`;
- do not dispatch.

### Phase 2 — continuous single-slot refill

- implement durable policy state;
- support `keep 1 running`, pause, and resume;
- prove one real job refills without Daniel returning;
- prove restart, backpressure, and fail-closed behavior.

### Phase 3 — two same-repository lanes

- run two disjoint PPE or equivalent lanes simultaneously;
- prove separate contexts, workspaces, ownership, evidence, and outcomes;
- keep publication serialized.

### Phase 4 — cross-pipeline witness

- run one lane from two independently registered pipelines;
- prove global capacity, fairness, independent failures, and adapter boundaries.

### Phase 5 — continuous two-slot refill

- enable `keep 2 running`;
- complete one lane and refill exactly one free slot without disturbing the other;
- prove queue and review backpressure;
- prove pause/resume with active work.

Routine capacity 2 is not accepted before all Phase 3–5 witnesses pass.

## Status output

Automatic mode should expose at least:

```text
AUTOMATIC BUILD MODE: ENABLED | PAUSED | DISABLED
DESIRED CAPACITY: <N>
CONFIGURED MAX: <N>
RUNNING: <count>
QUEUED: <count>
AWAITING REVIEW: <count by repository>
BACKPRESSURE: <none or reason>
NEXT ELIGIBLE: <pipeline/work item or none>
LAST RECONCILIATION: <timestamp and evidence identity>
```

Every active item should retain a traceable pipeline, work-item, job, branch, workspace, candidate, and evidence identity where applicable.

## Current implementation status

At policy approval:

- the persistent host already polls an immutable approved-job feed continuously;
- one host process claims one approved job at a time;
- one job may contain multiple compatible lanes;
- the internal scheduler already uses isolated workspaces, leases, lane conflict checks, and backend concurrency limits;
- the installed Codex host is configured with `max_concurrency: 2`;
- the controlled publisher is single-writer and draft-only;
- the founder portfolio registry and continuous refill controller are not yet implemented;
- cross-repository scheduling and production two-lane witnesses are not yet accepted.

Commands defined here remain interface contracts until runtime evidence proves their implementation.

## Linked implementation sequence

- PPE #5357 — portfolio registry and read-only command adapters;
- PPE #5359 — deterministic priority and fairness policy implementation;
- PPE #5358 — TxLINE registration;
- msos-autobuilder #50 — bounded continuous single-slot refill controller;
- msos-autobuilder #51 — two-lane, cross-pipeline, and continuous two-slot witnesses;
- PPE #5360 — cross-repository sequence tracking.

## COORDINATION STATUS

Agreement: aligned  
Compared: founder decision, founder command contract, pipeline creation SOP, PPE operator model, current Autobuilder persistent host, scheduler, lane ownership checks, controlled publisher, and msos-autobuilder issues #32 and #33  
Disagreement: none  
Evidence gap: portfolio registry, refill controller, staged runtime witnesses, and cross-repository adapter evidence  
Ownership overlap: PPE owns policy/registry/priority; msos-autobuilder owns runtime refill and queue execution  
Risk if unresolved: duplicate schedulers, unbounded review backlog, misleading running state, or automatic dispatch across unresolved ownership  
Recommended default: execute the staged rollout and keep enabled capacity at one until the required witnesses pass  
Founder decision required: no
