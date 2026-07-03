# Chapter coordination v1

**Plane:** CONTROL-PLANE · **Audience:** operators, stewards, IDE BUILD agents  
**Role:** Prevent relay deadlocks when product ships on `main` before the factory finishes witness/closeout.

**Related:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`RECOVERY_PROTOCOL.md`](RECOVERY_PROTOCOL.md) · [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) · [`FACTORY_CHANGE_COORDINATION_V1.md`](FACTORY_CHANGE_COORDINATION_V1.md) (building new factory code — not runtime layer sync) · [`STEERING_COORDINATION_PROGRAM_V1.md`](STEERING_COORDINATION_PROGRAM_V1.md) (steering drift — charter draft)

---

## Problem

The relay spine tracks **four layers** that must agree:

| Layer | Source | What it claims |
|-------|--------|----------------|
| **Factory queue** | `PHASE_QUEUE.json` + `ACTIVE_PHASE_MANIFEST.json` | Active chapter, slice order |
| **IDE marker** | `artifacts/orchestrator/IDE_PRODUCT_READY.json` | Product slices cleared for deterministic relay |
| **Evidence** | `docs/SOP/*_EVIDENCE_STATUS.md` | Witness/closeout truth |
| **Steering** | `MSOS_FRONTIER.md` + `AGENT_STEERING_V1.json` | Human-facing chapter status |

When product lands on `main` **outside** the relay (or ahead of witness slices), layers diverge:

- Guard → `IDE_BUILD` (marker missing)
- Mode → `CLOSEOUT_ONLY` (touchsets on `main`)
- VM → `BUILD_IN_FLIGHT` (stuck lock)

**Symptom:** “Doing well on product, stuck on factory.”

---

## Required coordination (product-on-main)

When product code for a relay chapter is already on `main`:

1. **Do not re-BUILD product** — witness/closeout slices only.
2. **Write IDE marker** for every product slice on `main`:
   ```bat
   mark_ide_product_ready.cmd <sliceId> docs/SOP/PHASE_PLANS/<chapter>_relay.json
   ```
   Or batch repair:
   ```bat
   python scripts/ppe_chapter_coordination.py --repair --plan docs/SOP/PHASE_PLANS/<chapter>_relay.json
   ```
3. **Register closeout-only** in `AGENT_STEERING_V1.json` → `closeoutOnlyChapterIds` (repair script adds this when product is on `main`).
4. **Align evidence** — product rows may show `SHIPPED_ON_MAIN`; witness/deploy rows stay `PENDING` until done.
5. **Do not mark MSOS_FRONTIER `COMPLETE`** until evidence doc is `**Status:** **COMPLETE**` with no `PENDING` slice rows.
6. **VM:** `run_ppe_local.cmd` / `fix_vm_operator.cmd` — clear stale `BUILD_IN_FLIGHT` after markers exist.

---

## Automated checks

| When | Command / hook |
|------|----------------|
| Operator status | `ppe_operator_blind_spots` → `chapter_coordination` issues |
| Pushable gate | Warns after tier pass when changed paths touch coordination-sensitive files |
| Burst plan | `ppe_coordination_check.py` + `ppe_pipeline_health.py` → `PIPELINE_HEALTH.json`; blocks burst on `recovery`/`park` |
| Founder diagnostic | `ppe_pipeline_health.cmd` or `python scripts/ppe_pipeline_health.py --write` — see [`PIPELINE_HEALTH_V1.md`](PIPELINE_HEALTH_V1.md) |
| Manual audit | `python scripts/ppe_chapter_coordination.py` |
| Agent synthesizer | `@ppe-coordination-check` — read-only; runs audits + routes repair/recovery |
| Safe repair | `python scripts/ppe_chapter_coordination.py --repair --plan <relay.json>` |

### Coordination check verdicts

| Verdict | Meaning | Burst |
|---------|---------|-------|
| `proceed` | Layers aligned enough for relay | Allowed |
| `repair` | Safe auto-repair available (markers/registry) | Allowed after repair |
| `recovery` | Mixed-plane or branch blocks relay | Blocked — run recovery first |
| `park` | Human-only or frontier/evidence mismatch | Blocked — manual alignment |

```bat
python scripts/ppe_coordination_check.py --write --json
```

### Coordination-sensitive changes (gate warns)

- `PHASE_QUEUE.json`, `ACTIVE_PHASE_MANIFEST.json`, `AGENT_STEERING_V1.json`
- `MSOS_FRONTIER.md`, `PHASE_PLANS/*`, `*_EVIDENCE_STATUS.md`
- `apps/msos-web/**`, `IDE_PRODUCT_READY.json`

After editing these, run:

```bat
python scripts/ppe_chapter_coordination.py
```

Fix high-severity issues before merging. Gate warnings are **non-blocking**; blind spots surface them on `what's next?`.

---

## Issue codes

| Code | Meaning | Safe auto-repair? |
|------|---------|-------------------|
| `PRODUCT_ON_MAIN_NO_MARKER` | Touchsets on `main`, marker missing | Yes — `--repair` marks slices |
| `CLOSEOUT_REGISTRY_MISSING` | Not in `closeoutOnlyChapterIds` | Yes — `--repair` adds chapter id |
| `FRONTIER_AHEAD_OF_EVIDENCE` | FRONTIER says COMPLETE, evidence does not | **No** — align docs honestly |
| `QUEUE_ACTIVE_PRODUCT_DESYNC` | READY queue + product on `main` without marker | Yes — repair markers/registry |

---

## Steward rule

**Never** mark a chapter `COMPLETE` in `MSOS_FRONTIER.md` until the evidence doc closeout block is `COMPLETE` and witnesses are checked. Product shipping early is normal; **lying about witness completion** causes re-queue deadlocks.

---

## Recovery sequence (deadlocked chapter)

1. Desktop: `python scripts/ppe_prepare_desktop_handoff.py` (or `--dry-run` to audit only)
   - Runs `--repair` for active manifest plan + all repairable plans
   - Must reach **`VERDICT=RUN_LOCAL`** before handoff
2. Desktop: `DESKTOP_CONTINUE.cmd --no-pause` (step 0 runs prepare automatically; VM step runs `--repair` again)
3. Align evidence + frontier (witness rows honest) when `FRONTIER_AHEAD_OF_EVIDENCE` remains
4. VM: `fix_vm_operator.cmd` if `BUILD_IN_FLIGHT` > 45m or `prepare-handoff` ff-only fails (diverging `main`)
5. VM: `run_ppe_local.cmd` to advance witness/closeout slices when not auto-spawned
6. Verify: `python scripts/ppe_operator_status.py --brief` → `RUN_LOCAL` or advancing phase
7. Spine progress: `python scripts/ppe_chapter_coordination.py --spine-audit`

### Marker repair (atomic batch)

`--repair` writes **all** missing product slices for a plan in **one** `IDE_PRODUCT_READY.json` update. Do not loop `mark_ide_product_ready.cmd` per slice when multiple product slices shipped on `main` — partial sequential writes can drop earlier slice ids.

### DESKTOP_CONTINUE step order

| Step | Where | Action |
|------|-------|--------|
| 0 | Desktop | `ppe_prepare_desktop_handoff.py` — repair + verify `RUN_LOCAL` |
| 1 | Desktop | `git pull origin main` |
| 2 | VM (SSH) | `ppe_chapter_coordination.py --repair` → `prepare-handoff-auto` → `finish_ide_build.cmd` |
| 3 | VM (SSH) | `check_vm_loop.cmd` |
| 4 | Desktop | `ppe_chapter_coordination.py --spine-audit` |
