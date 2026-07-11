# Autobuilder extraction chapter v1

**Chapter ID:** `AUTOBUILDER-EXTRACTION-V1`  
**Tracking issue:** #5348  
**Status:** ACTIVE — discovery, contract, and read-only scaffold work allowed  
**Cutover dependency:** #5321 host acceptance and zero-churn verification

## Decision

Begin extraction work immediately. Do not wait idly for the 24-hour observation window.

The observation window gates only the transfer of **production write authority**. It does not block:

- boundary inventory;
- contract design;
- repository scaffold design;
- fixture and test creation;
- read-only planning;
- shadow execution;
- lane and worker-interface design.

Until cutover, the current in-repository operator remains the only production publisher.

## Why this chapter exists

The present repository contains both:

1. the MSOS/PPE product being built; and
2. the Autobuilder system that selects, coordinates, validates, publishes, and closes product work.

That coupling creates unnecessary interference:

- factory changes invoke product CI;
- factory runtime failures can disturb the product repository;
- product and factory work compete for branch, PR, test, and context surfaces;
- adding more workers increases collision risk;
- compute backends cannot be changed cleanly without touching product operations.

The target is operational isolation without premature product fragmentation.

## Outcomes

At chapter close:

1. Autobuilder can evolve and test independently of MSOS/PPE.
2. MSOS/PPE exposes a small versioned project contract rather than factory internals.
3. Autobuilder can execute multiple disjoint MSOS lanes concurrently.
4. Each lane has isolated workspace, ownership, lease, branch, validation, and evidence.
5. Worker compute can be selected through a narrow adapter using capabilities and cost class.
6. Exactly one production publisher is enabled at any time.
7. Runtime queue, lease, worker, cost, and phase state remains outside product Git.

## Target repository boundary

### MSOS/PPE product repository owns

- `apps/msos-web/`;
- PPE engine, data, models, and visualization code;
- product tests and integration tests;
- product deployment configuration;
- product vision, research, and product canon;
- a declarative Autobuilder project contract;
- product-local validation commands.

### Autobuilder repository owns

- chapter and task routing;
- lane scheduling;
- isolated workspace creation;
- worker leases and heartbeat handling;
- worker backend selection;
- publication and PR lifecycle;
- closeout and evidence collection;
- factory runtime state;
- factory CI, fixtures, and runbooks;
- compute adapters.

### Boundary rule

Autobuilder may invoke declared product commands and operate through Git/GitHub interfaces. It must not import MSOS/PPE business modules as runtime dependencies.

## Execution model

### Chapter

A chapter is a bounded product outcome with one stable identity and at most one open PR.

### Lane

A lane is one independently executable workstream within or across chapters. Every lane declares:

- `lane_id`;
- `chapter_id`;
- repository and base revision;
- branch name;
- layer preset;
- allowed paths;
- forbidden paths;
- required capabilities;
- validation commands;
- publication policy;
- dependency and integration constraints.

### Workspace

Each lane runs in an isolated clone or Git worktree. No two active workers share a mutable checkout.

### Lease

Every active worker owns a renewable lease containing:

- lane and worker identity;
- claimed ownership paths;
- start and expiry timestamps;
- heartbeat timestamp;
- workspace path;
- branch and base SHA;
- status and cancellation state.

Expired leases may be recovered only through an explicit recovery transition. A second worker must not silently take over a live workspace.

### Ownership rule

Parallel workers are allowed. Parallel ownership of overlapping files is not.

Two lanes may run concurrently when their allowed ownership sets are disjoint. Overlap requires an explicit integration lane or ordered dependency.

### Publication rule

Multiple workers may build and validate concurrently. Only the designated publisher may create or update durable GitHub publication for a lane.

Every chapter retains:

- one stable chapter branch;
- one open chapter PR maximum;
- semantic-content idempotency;
- duplicate-head and duplicate-chapter rejection;
- runtime-only path rejection;
- explicit merge authorization.

## Compute backend design

This chapter defines a narrow worker interface. It does not build a generalized distributed platform.

Each backend must support the semantic operations:

```text
claim(task)
prepare_workspace(task)
execute(task)
collect_evidence(task)
cancel(task)
```

Each backend advertises:

- capabilities;
- maximum concurrency;
- cost class;
- expected latency;
- timeout limits;
- operating-system/runtime constraints;
- credential and network requirements.

### Initial backend

The existing local/Codex workflow is the reference backend.

### Deferred backend implementations

After the adapter and local multi-lane witness are proven, additional backends may include:

- inexpensive remote VMs over SSH;
- hosted coding agents;
- batch workers;
- specialized high-context or low-cost model workers.

Provider-specific implementation is not required for the first extraction cutover.

## Product project contract

The product repository must expose a versioned contract sufficient for Autobuilder to operate without product imports.

Minimum contract fields:

```yaml
version: 1
project:
  id: msos
  default_branch: main

layers:
  msos-shell:
    allowed_paths: ["apps/msos-web/**"]
  ppe-ui:
    allowed_paths: ["src/viz/**"]
  ppe-core:
    allowed_paths:
      - "src/engine/**"
      - "src/data/**"
      - "src/models/**"

commands:
  fast_gate: "python scripts/run_pushable_gate.py"
  full_gate: "python scripts/run_pushable_gate.py --pre-push"
  web_gate: "python scripts/verify_msos_web_build.py"

publication:
  branch_pattern: "chapter/{chapter_id}"
  max_open_prs_per_chapter: 1
  direct_main_writes: false

runtime_only_paths:
  - "artifacts/**"
  - ".env"
```

This example is provisional. The contract must be validated against the current repository before cutover.

## Phases

### Phase A — boundary inventory

Inventory factory-related code and classify every item:

- **MOVE** — belongs wholly in Autobuilder;
- **KEEP IN PRODUCT** — product build, test, deploy, or witness logic;
- **REFACTOR BEFORE MOVE** — mixed dependency must be separated;
- **TEMPORARY COMPATIBILITY** — retained only for bounded migration;
- **DELETE AS LEGACY** — obsolete after runtime-state and publication repair.

Inventory surfaces include:

- `scripts/`;
- `tests/`;
- `docs/SOP/`;
- root Windows wrappers;
- `.cursor/` agents and rules;
- `.github/workflows/`;
- configuration and environment variables;
- runtime artifact paths;
- imports between factory and product modules;
- files written by operator processes.

### Phase B — contract and interlocks

Deliver:

- project contract schema and MSOS instance;
- one-writer interlock;
- lane ownership model;
- lease model;
- compute adapter protocol;
- migration and rollback runbook.

### Phase C — independent scaffold

Create the private Autobuilder repository with:

- package layout;
- focused factory CI;
- fixture product repositories;
- no production credentials;
- no production write authority;
- read-only GitHub and local-repository adapters.

### Phase D — read-only shadow

Run the extracted system against MSOS in plan/read-only mode and compare:

- chapter selection;
- lane routing;
- layer and path ownership;
- workspace and branch intent;
- validation selection;
- publication intent;
- closeout evidence.

Unexpected write attempts fail the phase.

### Phase E — single-writer cutover

Cutover is permitted only after #5321 acceptance and successful shadow evidence.

Sequence:

1. stop the in-repository writer;
2. prove old supervisors/processes are stopped;
3. verify legacy publication variables are absent;
4. enable the extracted publisher;
5. run one low-risk chapter;
6. verify branch, PR, evidence, runtime state, and rollback;
7. retain the old writer disabled for a bounded rollback window.

### Phase F — parallel lane witness

Execute at least two disjoint MSOS lanes simultaneously.

Suggested first witness:

- one `msos-shell` lane;
- one `ppe-core` or docs/research lane;
- separate workspaces, branches, leases, gates, and PRs;
- no overlapping owned paths;
- normal integration through review and CI.

### Phase G — low-cost compute witness

After the local parallel-lane witness passes:

- implement one additional compute backend;
- assign it a bounded low-risk lane;
- enforce the same task, evidence, ownership, and publication contracts;
- compare cost, latency, reliability, and correction burden.

This may be a follow-on chapter if provider work would widen the extraction cutover.

## What may begin before #5321 closes

- inventory and classification;
- interface extraction;
- contract schema and examples;
- fixtures and focused tests;
- private repository creation;
- read-only or no-credential scaffold;
- shadow planning;
- lane and lease implementation that has no production writer authority.

## What must wait for the cutover gate

- switching production repository targets;
- enabling a second publisher;
- changing loop-host production checkout paths;
- removing the existing writer from the product repo;
- deleting compatibility code needed for rollback;
- running old and extracted writers concurrently.

## Acceptance criteria

- [ ] Boundary inventory is complete and reviewed.
- [ ] Autobuilder has independent repository and CI.
- [ ] Factory tests no longer block normal product-only CI.
- [ ] Autobuilder imports no MSOS/PPE business modules.
- [ ] MSOS project contract is versioned and validated.
- [ ] Runtime queue, lease, worker, and cost state is outside product Git.
- [ ] One-writer interlock is tested.
- [ ] Read-only shadow produces no unexpected writes.
- [ ] One low-risk chapter completes through the extracted publisher.
- [ ] Rollback to the disabled prior writer is demonstrated.
- [ ] Two disjoint MSOS lanes complete concurrently without interference.
- [ ] Worker backend selection uses capabilities/cost class without changing chapter semantics.
- [ ] Product deployment and PPE calculation behavior remain unchanged.

## Non-goals

- splitting MSOS web from PPE;
- renaming the product repository;
- rewriting Autobuilder from scratch;
- arbitrary DAG orchestration;
- multi-tenant build infrastructure;
- provider-specific compute marketplace design;
- weakening layer or publication safety to increase concurrency;
- allowing multiple uncontrolled publishers.

## Stop conditions

Stop and escalate if:

- a new timestamped runtime-state PR appears;
- the running host still uses obsolete publication code;
- extraction requires importing product business modules;
- two lanes claim overlapping paths without an integration plan;
- a second production publisher becomes active;
- runtime state is proposed for storage in product Git;
- the chapter expands into general platform orchestration.

## Relationship to current work

- #5321 remains the production cutover gate.
- #5345 remains the separate stale-work reconciliation queue.
- This chapter does not merge preserved stale branches wholesale.
- The first objective is separation and enforceable contracts; concurrency follows on top of that boundary.
