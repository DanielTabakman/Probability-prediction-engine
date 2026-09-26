# API / MSOS / Autobuilder coordination handoff v1

**Execution step:** CONTROL-PLANE · CLOSEOUT/coordination documentation only.  
**Purpose:** Make three *work lanes* legible while using the existing authorized PPE and Autobuilder machinery. This is **not** three new pipeline registrations, a new queue, a new authority class, a new operator command, or approval to run a build or deploy.  
**Planning entry point:** `DanielTabakman/daniel-os/docs/THREE_TRACK_OPERATING_MAP.md`.  
**Authority remains:** [OPERATING_RULES](OPERATING_RULES.md), [PIPELINE_CREATION_SOP](PIPELINE_CREATION_SOP_V1.md), [REPO_LAYER_MAP](REPO_LAYER_MAP_V1.md), [PARALLEL_AGENT_CHECKLIST](PARALLEL_AGENT_CHECKLIST_V1.md), [AGENT_ROUTING](AGENT_ROUTING_V1.md), actual selected slice/BUILD packet, and the factory's own operating manual. In a conflict, those sources and current machine-derived evidence win over this summary.

## Three lanes are not three competing production pipelines

| Lane | Canon / repository | Sole ownership for an individual task | Out of scope |
| --- | --- | --- | --- |
| **API / partner** | PPE (`DanielTabakman/Probability-prediction-engine`); active product direction, API spec, selected API chapter | Existing options calculation/producer/cache, read-only `GET /v1/options-market-read` schema v1.3, API help/OpenAPI, conformance and independent Qatom handoff. Declare actual allowed files and layer preset per slice; an API is not its own catch-all layer preset. | Qatom source/config; customer-facing MSOS chrome; new assets, execution, exposure, ratings or recommendations without a new decision. |
| **MSOS / human UI** | Same PPE repo; selected MSOS product slice and `MSOS_UI` layer where appropriate | `apps/msos-web/` explanation, date/expiry selection, existing market-read console/monitor/history rendering; use the already-produced API/display data. | Porting PPE math to TypeScript, a second options-market producer/cache, unchartered v1.3 schema changes. |
| **Autobuilder / factory** | `DanielTabakman/msos-autobuilder`; approved job feed, `results` evidence and local host | Freeze approved PPE source + exact packet, run disposable workers, enforce paths/leases/gates, publish within recorded authority, terminalize based on exact evidence. | Product meaning, a second PPE source of truth, independently selecting wider work, a product merge or factory installation without the applicable approved gate/witness. |

**Registration clarification:** PPE's registered pipeline (canonical ID `ppe`) covers PPE product work. Autobuilder's canonical pipeline is `autobuilder`; API and MSOS are scoped lanes within the existing product system unless separately registered under the existing SOP. No `create pipeline`, portfolio-registry change, manifest rewrite or refill change is part of this cleanup.

## Source-of-truth and precedence

| Question | Read first | What this handoff may say |
| --- | --- | --- |
| Which product objective? | `ACTIVE_PRODUCT_DIRECTION.json` and selected sprint/SELECTION | A link, never a replacement decision. |
| What is READY/selected? | `ACTIVE_PHASE_MANIFEST.json`, `PHASE_QUEUE.json`, `PHASE_CHAPTER_BACKLOG.json`, chapter resolver and fresh operator status | Report the current gate or `unknown`; never treat a Daniel OS checkbox as READY. |
| Where can a worker write? | Exact phase-plan slice + BUILD packet + `REPO_LAYER_PATH_PREFIXES.json` | State one owner and explicit allowed/forbidden paths, not broad inferred permission. |
| Is product merged? | Exact PPE PR/head, CI and merge commit | Distinguish merged product from a pending CONTROL closeout. |
| Is factory running/installed? | Factory local host/refill/supervisor witnesses tied to exact managed release; job/result Git branches for immutable evidence | GitHub source merge is not proof of a live Windows service or released host. |
| Is API live/partner-ready? | API contract, exact staging/production conformance, partner decisions, monitor and rollback receipts | A charter or passing old test is not production acceptance. |

**Observed snapshot, not an automatic status feed (Sep 22, 2026):** MSOS product PR #5483 merged; partner-acceptance charter PR #5484 merged but its product/closeout slices remained PENDING and PLANNED when chartered. Order-13 CONTROL closeout PR #5485 was open and non-mergeable on inspection; it says order 13 product is already merged and orders 14–17 are held. Recheck before taking any action. Never rebuild order 13 just because an old manifest still shows READY.

## Desktop worktree isolation: safe procedure, not an automated migration

The PPE operator loop belongs on the Hyper-V VM; daily desktop is IDE BUILD only (`PPE_OPERATOR_LAYOUT_ADR.md`). Do **not** create worktrees in the VM loop checkout, change a running agent's checkout, reset, clean, stash, prune, or force-move an existing branch as a housekeeping shortcut.

On the **desktop**, before assigning a new task, inspect the actual checkout and existing worktrees:

```powershell
cd <existing-PPE-checkout>
git status --short --branch
git worktree list --porcelain
git branch --list
git rev-parse HEAD
```

If dirty, active, or uncertain: **STOP and continue with that agent** or park the work explicitly under the existing recovery protocol. When clean and no existing task branch/worktree covers the work, an authorized operator may use normal `git worktree add -b <unique-scoped-branch> <new-disjoint-desktop-directory> <verified-base-ref>` *after* verifying the base ref and destination. Example lane branch prefixes are `api/` and `msos/`; these labels are not authority. The factory continues to use its own disposable clones and `_worktrees/orchestrator/<slice>` per its actual packet and lease contracts; do not repurpose those directories for manual UI work.

**Isolation is necessary but insufficient:** two PPE worktrees can still conflict at merge time. Before concurrent work compare exact changed/allowed file sets and any shared API fields. Shared-interface/API schema edits are serialized first; a dependent MSOS task begins after the contract is frozen or explicitly recorded as blocked. A task that needs both `apps/msos-web/` and API implementation is split into two separately scoped slices and merged in dependency order. Never silently extend one layer preset.

## Minimal handoff card (paste into existing issue/packet/PR; no new state file)

```text
TASK / CHAPTER ID:
LANE: API | MSOS | FACTORY
OBJECTIVE / USER OUTCOME:
AUTHORITY CLASS + FOUNDER DECISIONS:
CANON / SELECTED SPRINT + SOURCE SHA:
SINGLE OWNER / AGENT + CONTINUITY STATE:
MACHINE / REPO / BRANCH / WORKTREE (or disposable clone):
PLANE + LAYER PRESET:
ALLOWED PATHS / FORBIDDEN PATHS:
SHARED CONTRACT OWNER + DEPENDENCIES:
ACCEPTANCE / TEST COMMANDS / EVIDENCE LOCATION:
PR / EXACT HEAD / CI / MERGE RECEIPT:
RUNTIME / DEPLOY / ROLLBACK RECEIPT (if applicable):
NEXT ACTION + BLOCKER + WHO CAN UNBLOCK:
```

**Handoff sequence:** intake once in PPE canon → select only an eligible chapter → freeze exact source/authority/paths → work in isolated checkout → run applicable layer audit and tests → review exact PR/head and required gates → merge only within recorded authority → separately verify release/runtime → terminal receipt and next frontier. Factory and UI consumers cite the *same* product task ID rather than creating duplicate competing queue items.

### Stop immediately when

- An active agent has unresolved dirty/stashed work or the new task overlaps a leased file set.
- The selected chapter says `CLOSEOUT_ONLY`, no valid approved packet exists, or fresh status is unavailable.
- API/MSOS paths, producer semantics, or public schema need to expand beyond the task's recorded preset.
- A PR is non-mergeable, exact-head CI is missing, partner access decisions are unsettled, or deployment/installation approval is absent.
- A UI screenshot or API conformance witness is missing where required.

**Closeout of this coordination cleanup:** this document and the matching read-only handoff in the factory may be reviewed/merged as documentation. No worktree was created on Daniel's machine, no active manifest/jobs changed, and no merge, deploy or supervisor update was authorized by this document. The next real build remains subject to a fresh operator preflight and selected packet.
