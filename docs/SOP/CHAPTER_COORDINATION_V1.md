# Chapter coordination v1

**Plane:** CONTROL-PLANE · **Audience:** operators, stewards, IDE BUILD agents  
**Role:** Prevent relay deadlocks when product ships on `main` before the factory finishes witness/closeout.

**Related:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md) · [`RECOVERY_PROTOCOL.md`](RECOVERY_PROTOCOL.md) · [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md)

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
| Manual audit | `python scripts/ppe_chapter_coordination.py` |
| Safe repair | `python scripts/ppe_chapter_coordination.py --repair --plan <relay.json>` |

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

1. Desktop: `python scripts/ppe_chapter_coordination.py --repair --plan <relay.json>`
2. Align evidence + frontier (witness rows honest)
3. VM: `fix_vm_operator.cmd` if `BUILD_IN_FLIGHT` > 45m
4. VM: `run_ppe_local.cmd` to advance witness/closeout slices
5. Verify: `python scripts/ppe_operator_status.py --brief` → `RUN_LOCAL` or advancing phase
