# Engineering OS Phase 0 Inventory — 2026-09-26

Status: working control-plane inventory  
Parent: #5488  
Canon: `docs/SOP/ENGINEERING_OPERATING_SYSTEM_V1.md`

## Executive state

The portfolio is not yet running as an autonomous multi-lane system.

Current registry truth:

- `ppe` / MSOS is `EXECUTION_READY` for manual or single dispatch;
- `autobuilder` is registered for read-only visibility and is not dispatch-ready through the PPE portfolio;
- continuous refill is disabled for both;
- future steady-state build-worker capacity remains globally capped at 2 until staged witnesses prove it safe;
- publication remains serialized per target repository.

The immediate cleanup problem is not an absence of work. It is mixed lifecycle state and historical residue.

Observed open work:

- PPE/MSOS open issues before Phase 0 additions: 15;
- Autobuilder open issues before Phase 0 additions: 20;
- PPE open PRs: 52;
- Autobuilder open PRs: 7.

Most open issues are legible. The larger source of confusion is the open-PR surface, especially old PPE reconciliation/control-plane drafts.

## Portfolio lanes

### Factory / Autobuilder

#### NOW — Committed

- `msos-autobuilder#119` — stable pilot production lane and useful builds. This is the current practical production bridge while full autonomy remains incomplete.
- `msos-autobuilder#61` / draft PR #63 — Phase 1 continuous-improvement proposal automation.
- `msos-autobuilder#115` — work admission, writer claims, duplicate-PR reconciliation.
- `msos-autobuilder#205` — Cursor-independent pluggable coding backends.

#### NEXT — Committed

- `msos-autobuilder#51` — prove two non-overlapping write lanes and cross-pipeline scheduling.
- `msos-autobuilder#78` — founder-visible status surface.
- `msos-autobuilder#32` — self-update supervisor acceptance/rollback completion.
- `msos-autobuilder#73` — guarded automatic merge/cleanup; implementation may exist but activation remains authority-gated.

#### Runtime repair / witness backlog — Committed but evidence-gated

- #74 publisher success association
- #79 managed PPE source freshness
- #82 canonical dependency-source hashing
- #95 deterministic refill graceful stop
- #110 Windows staged-pytest timeout diagnosis
- #131 Windows-safe staging temp path
- #134 namespace-aware stable supervisor handoff

These should not be treated as independent product priorities. They are runtime/witness defects feeding #119/#32/#51 and should close when their installed acceptance evidence is satisfied.

#### Candidate / improvement backlog

- #33 continuous-improvement planner umbrella
- #65 recurring candidate-gate result summarizer
- #86 adopt-before-build reuse gate
- #88 Technical Founder Operating Loop V1
- #103 deferred historical migration/passive clean generation

`#88` substantially overlaps the newly merged Engineering OS policy and should be reconciled rather than expanded as a parallel operating model.

### MSOS

#### NOW — Committed

- `msos-autobuilder#202` — Financial Primitive #001 / `implied_range` API. This remains the first Qatom-facing external product priority.
- PPE #5381 — Options Made Simple option-horizon comparison, READY_TO_BUILD.
- PPE #5382 — Options Made Simple expression-fit ranking; controlled candidate exists as draft PR #5428.
- PPE #5391 — market proposal + hedge-capacity preview; implementation exists as draft PR #5395.

#### Product system backlog — Committed

- PPE #5490 — UI/UX simplification.
- PPE #5491 — Market Thesis end-to-end workflow.

#### Research

- PPE #5389 — issuer-created hedgeable event markets; explicitly deferred until #5391 is accepted and reviewed.
- PPE #5493 — asset-backed prediction-market architecture/feasibility.

### API / Distribution

#### NOW — Committed

- Autobuilder #202 — first external API primitive / implied range.

#### NEXT — Committed

- PPE #5492 — inventory useful capabilities, define shared machine-interface conventions, and produce the ordered API/Qatom catalog.

Qatom is a distribution adapter, not the core interface.

### Structured Launchpad

#### Research / Incubation

- PPE #5494 — permissionless on-chain structured-product launchpad decision packet.

No sustained implementation is authorized until explicit promotion to a Product lane.

### Labs

#### Research / Candidate

- PPE #5413 — Market Structure EXP-001 forward validation; implementation belongs in `market-structure-engine`.
- PPE #5404 — CCXT/NDAX read-only market-data spike; Candidate until the reuse/adopt-before-build gate is accepted.
- PPE #5396 — deferred HBCC feasibility witness.
- PPE #5358 — TxLINE hackathon pipeline registration.

Labs items must eventually be killed, absorbed, or promoted.

## PPE cleanup / bookkeeping set

The following open PPE issues look primarily like control-plane residue, bookkeeping, or historical infrastructure work rather than current product lanes:

- #5412 repo-split migration bookkeeping — architecture already complete; close when referenced canonical merges are verified.
- #5316 token-audit read-only bug — implementation exists as draft PR #5410; reconcile/accept/close rather than reimplement.
- #5321 Autobuilder churn phase 2
- #5345 reconcile preserved Autobuilder branches
- #5303 universal router interlock / ambiguity guard
- #5274 Token Audit 003

The last four need explicit supersession/relevance review against current main and the standalone `msos-autobuilder` repository. Do not automatically re-execute them merely because they remain open.

## Open-PR cleanup

### Active/relevant PPE PRs

At minimum the following are tied to live work and should be independently reviewed rather than bulk-closed:

- #5489 — current control-plane closeout
- #5428 — Options Made Simple expression-fit ranking
- #5410 — token-audit read-only repair
- #5411 — MSOS Market Structure workbench / research surface
- #5395 — market proposal + hedge-capacity preview
- #5455 — PPE loop host/autostart; relevance must be checked against new Engineering OS direction
- current dependency-update PRs should be processed as dependency maintenance, not mixed with product backlog.

### Active/relevant Autobuilder PRs

- #63 — continuous-improvement proposals
- #87 — adopt-before-build reuse charter/audit
- #92 — repair-admission control
- #39/#42 — rollback witness material; disposition must follow #32 evidence
- #62 — planner charter; reconcile with #33/#61
- #144 — Cursor-native control-plane guidance is directionally superseded by Engineering OS v1's requirement that Cursor be optional and should not become new canon.

### Historical PPE PR residue

A large group of old reconciliation/control-plane/product drafts remains open (including early #433/#441/#547/#555 and many #10xx/#11xx/#18xx/#19xx branches).

These must be processed through a bounded reconciliation pass:

1. compare each PR to current `main`;
2. identify unique unresolved value;
3. classify `MERGE/REPAIR/ABSORB/SUPERSEDED/DUPLICATE`;
4. preserve provenance;
5. close only when no unique required work remains.

Do not bulk-merge historical drafts.

## Missing-work gaps now filled

Phase 0 created canonical items for previously conversational priorities:

- #5490 MSOS UI/UX simplification;
- #5491 Market Thesis end-to-end;
- #5492 API capability inventory/Qatom distribution;
- #5493 asset-backed prediction-market research;
- #5494 Structured Launchpad incubation decision;
- `msos-autobuilder#205` Cursor-independent execution.

## Control view

### NOW

Factory:
- stabilize/use #119;
- reconcile #63 and admission/control-plane pieces;
- build toward provider-independent execution (#205).

MSOS:
- implied_range external primitive (#202);
- reconcile existing finished candidates (#5428, #5395) before spawning replacements.

API:
- #202 first;
- #5492 inventory/catalog next.

Labs:
- no automatic execution while Factory control plane is being cleaned.

### NEXT

- finish Phase 1 lifecycle metadata;
- make Factory/MSOS/API visible as independent logical queues;
- execute #51 multi-lane witness under global capacity 2;
- add founder status surface;
- move coding execution off Cursor dependency.

### BLOCKED / EVIDENCE-GATED

- true continuous refill;
- routine two-worker scheduling;
- autonomous Autobuilder self-install;
- guarded auto-merge activation;
- any Structured Launchpad product build.

### DECISION NEEDED

None for Phase 0.

The Structured Launchpad decision is deliberately deferred until its research packet exists.

## Phase 0 close criteria

Phase 0 can close when:

- this inventory is canonical;
- clearly superseded Cursor-only guidance is disposed;
- historical PR cleanup has a bounded reconciliation issue/packet;
- live work is represented by the five Engineering OS lanes and three backlog classes;
- #5488 points to this inventory as the starting control view.
