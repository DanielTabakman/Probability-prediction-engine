# PPE IDE-native operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters without Cursor API / ACP when credits are exhausted.

**Checklist:** [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)

**Desktop loop host:** [`DESKTOP_OPERATOR_SETUP_STARTER.md`](DESKTOP_OPERATOR_SETUP_STARTER.md) · [`PPE_MOBILE_OPERATOR_V1.md`](PPE_MOBILE_OPERATOR_V1.md)

---

## Quick start — two commands for you

| When | Command |
|------|---------|
| **VM loop** (24/7) | Hyper-V VM: **`VM_RESTART.cmd`** · status: **`VM_STATUS.cmd`** — see [`PPE_VM_DESKTOP_OPERATOR_HANDOFF.md`](PPE_VM_DESKTOP_OPERATOR_HANDOFF.md) |
| **Phone buzzes** (`IDE_BUILD` / operator ping) | **Desktop:** `ppe_go.cmd` → new Agent chat → **Ctrl+V** → Enter — or enable **DESKTOP AUTO START** (runs BUILD/CONTINUE for you) |

`ppe_go.cmd` refreshes status, copies the `@ppe-director` prompt, and opens Cursor. It does **not** run the product BUILD or `run_ppe_local` — the director/build worker handles that after you paste the prompt.

**After IDE BUILD in Cursor:** `mark_ide_product_ready.cmd <sliceId>` then **`run_ppe_local.cmd`** on the **VM** (loop host) to continue relay.

Monitor (optional): `.\scripts\watch_ppe_live.ps1`

---

## What the loop does (background)

Startup preflight writes `artifacts/orchestrator/OPERATOR_STATUS.md`. Control/witness/closeout slices run unattended; **product** slices stop until IDE BUILD completes. After closeout, the next blocked MSOS row with `planPath` promotes to **queued** automatically.

### Director agents (behind `ppe_go.cmd`)

| Agent | Role |
|-------|------|
| `@ppe-director` | Read `OPERATOR_STATUS.md`; spawn workers; never run `run_ppe_auto_local_loop` |
| `@ppe-build-worker` | One product slice from `IDE_BUILD_STARTER_*.md` → gate → commit → mark ready → `run_ppe_local` |
| `@ppe-finish-worker` | `RUN_LOCAL` only — `run_ppe_local.cmd` when marker present |
| `@ppe-triage-worker` | `FIX_PLAN` / `STALE_STATE` / `ERROR` diagnosis |

Definitions: [`.cursor/agents/`](../.cursor/agents/). Handoff script: [`scripts/ppe_director_go.py`](../../scripts/ppe_director_go.py).

**Manual fallback** (same as clipboard from `ppe_go.cmd`):

```text
@ppe-director Director pass. Terminal loop running.
```

**After chapter closeout:** new Agent thread with `AGENT_CONTINUITY_BRIEF.md` only, then `ppe_go.cmd` again.

**Optional Automation (zero-click happy path):** Cursor Automation on `.cursor/IDE_BUILD_TRIGGER.json` — prompt in [`.cursor/IDE_BUILD_AUTOMATION_PROMPT.md`](../.cursor/IDE_BUILD_AUTOMATION_PROMPT.md). Use Automation for `IDE_BUILD`; use `ppe_go.cmd` for exceptions.

**Autobuilder (pipeline SRE):** [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · `ppe_autobuilder.cmd` · `@ppe-autobuilder-operator` — status, diagnose, and `advance` without product BUILD.

---

## Two profiles

Use **one profile at a time**.

| When | Entry (continuous) | Config |
|------|-------------------|--------|
| **No API credits** | `run_ppe_auto_local_loop.cmd` | [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Have API credits** | `run_ppe_auto_acp_loop.cmd` | [`PPE_AUTO_OPERATOR.acp.json`](PPE_AUTO_OPERATOR.acp.json) |

Plain `run_ppe_auto.cmd` uses [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) (defaults to **local**).

Set profile explicitly: `set PPE_OPERATOR_PROFILE=local` or `=acp`.

---

## Distribution snapshot collector (MVP)

Headless daily CSV capture (same schema as implied-lab download):

```bat
python scripts/collect_distribution_stats_snapshot.py
```

Writes under `artifacts/distribution_snapshots/YYYY-MM-DD/`. Schedule via Task Scheduler or cron on a machine with Deribit network access; not run by the relay loop.

---

## Cross-venue snapshot collector (MVP)

Headless daily CSV capture (same schema as implied-lab **Download cross-venue prob panel (CSV)**):

```bat
python scripts/collect_cross_venue_snapshot.py
```

Writes under `artifacts/cross_venue_snapshots/YYYY-MM-DD/`. Requires Deribit + Polymarket network access; not run by the relay loop.

---

## IDE BUILD closeout (product slices)

After implementing a product slice, run the full closeout — **do not stop at “code looks done”**:

```bat
ppe_ide_build_closeout.cmd <sliceId> <phasePlanPath>
```

That script runs gate → reminds you to commit on `buildBranch` → `mark_ide_product_ready.cmd` → `run_ppe_local.cmd` with **git sync disabled** on `build/auto/*` branches (avoids checkout to `main` mid-closeout).

Manual equivalent:

```bat
mark_ide_product_ready.cmd MVP1-CrossVenue-Product-Slice003 docs/SOP/PHASE_PLANS/mvp1_cross_venue_prob_panel_relay.json
set PPE_GIT_SYNC_PULL=0
set PPE_GIT_SYNC_PUSH=0
run_ppe_local.cmd
```

---

## IDE product-ready marker

After IDE BUILD and commit, write `artifacts/orchestrator/IDE_PRODUCT_READY.json` so continuous guards allow the phase to run:

```bat
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002 docs/SOP/PHASE_PLANS/my_relay.json
```

Requires commits on the plan `buildBranch` ahead of baseline. Cleared automatically when `run_ppe_local.cmd` exits 0.

### Pushable gate (mixed-plane branches)

On `build/auto/*` with multiple planes in branch history, scope the gate to the slice commit:

```bat
python scripts/run_pushable_gate.py --base-ref HEAD~1 --no-auto-upstream
```

Docs-only closeout: stage only `docs/SOP/*`, then `--base-ref HEAD --no-auto-upstream`.

### Evidence doc stub (closeout hardening)

Relay chapters with a closeout block get a **PENDING** evidence stub automatically when `ppe_auto_select.py --apply` selects the plan. Closeout flips it to COMPLETE. Do not delete the stub before closeout.

### Control/smoke `STOP_FOR_REVIEW` in worktrees

Control and smoke slices often exit `STOP_FOR_REVIEW` / `UNCLEAR_TEST_RESULTS` in isolated worktrees — **normal, not a manual review**. `ppe_promotion_recovery` advances the phase automatically; `LAST_RUN_REPORT` buckets these as `auto_advance_promotion_recovery` with `awaiting_user: false`. **Only product slices** block on `IDE_PRODUCT_READY` (operator verdict `IDE_BUILD`).

| Relay signal | You needed? |
|--------------|-------------|
| Exit 20 + evidence/control/smoke slice | **No** — loop continues |
| Exit 20 + product `SCOPE_AMBIGUITY` | **Yes** — IDE BUILD + marker |
| Guard exit **7** / `PRODUCT_BLOCKED` | **Yes** — `ppe_go.cmd` |

---

## What runs unattended

| Step | Local profile |
|------|----------------|
| Backlog → queue propagation | Yes |
| Steward charter when idle | **No** (no API) |
| Control / smoke / closeout slices | Yes (pytest/scripts) |
| Product slices | **No** — guard stop until marker + `run_ppe_local` |

---

## Jump-in matrix

| Signal | You do |
|--------|--------|
| Guard exit **7** / `PRODUCT_BLOCKED` | **`ppe_go.cmd`** → Ctrl+V in Agent |
| Relay exit **20** on control/smoke/witness | **Nothing** — auto-advance (see above) |
| `CONTEXT_ESCALATE` / `TOO_MANY_SLICES` | Fix plan/spec; see guard report |
| `SCOPE_AMBIGUITY` on product slice | Same as product blocked |
| Queue idle, no `READY` | Add `queued` row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) |
| Test/smoke fail | Fix code or env; `run_ppe_local.cmd` |
| Chapter closeout complete | New Cursor thread; [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) only |

---

## Parallel IDE work (Multitask)

Cursor **Multitask** does **not** replace `run_ppe_local.cmd` or the product-ready marker. It does not run the relay control plane.

Suggested pattern:

- **Terminal:** `run_ppe_auto_local_loop.cmd` (queue, guards, evidence slices).
- **Multitask / extra Agent threads:** product BUILD, doc review, or a second slice — one BUILD thread per product slice.
- Do not merge SELECTION + BUILD + closeout + `gh` in one mega-thread ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md)).

---

## Related

- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`PPE_WORKER_MODES_V1.md`](PPE_WORKER_MODES_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
- [`.cursor/agents/`](../.cursor/agents/) — `ppe-director`, `ppe-build-worker`, `ppe-finish-worker`, `ppe-triage-worker`
