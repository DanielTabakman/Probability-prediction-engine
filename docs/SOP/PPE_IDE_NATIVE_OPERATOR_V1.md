# PPE IDE-native operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters without Cursor API / ACP when credits are exhausted.

**Checklist:** [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)

---

## Quick start

From repo root:

```bat
run_ppe_auto_local_loop.cmd
```

Monitor (optional):

```powershell
.\scripts\watch_ppe_live.ps1
```

When the loop stops for a **product** slice:

1. Read `artifacts/orchestrator/LAST_RUN_REPORT.md` or `OPERATOR_GUARD_REPORT.md`.
2. **IDE BUILD** — new Cursor Agent thread; load `docs/SOP/AGENT_CONTINUITY_BRIEF.md` + sprint spec; use [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).
3. Commit on the phase plan `buildBranch`.
4. **`mark_ide_product_ready.cmd <sliceId> [phasePlanPath]`**
5. **`run_ppe_local.cmd`** — finish smoke/closeout for that chapter.
6. Loop continues on the next pass (marker cleared after successful `run_ppe_local`).

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

## IDE product-ready marker

After IDE BUILD and commit, write `artifacts/orchestrator/IDE_PRODUCT_READY.json` so continuous guards allow the phase to run:

```bat
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002
mark_ide_product_ready.cmd MVP1-Phase6Trust-Product-Slice002 docs/SOP/PHASE_PLANS/my_relay.json
```

Requires commits on the plan `buildBranch` ahead of baseline. Cleared automatically when `run_ppe_local.cmd` exits 0.

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
| Guard exit **7** / `PRODUCT_BLOCKED` | IDE BUILD → commit → **mark ready** → `run_ppe_local.cmd` |
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
