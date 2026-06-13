# PPE operator visibility v1 — relay sprint spec

**Live steering:** [`MVP1_FRONTIER.md`](MVP1_FRONTIER.md) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**SELECTION:** [`POST_PPE_OPERATOR_VISIBILITY_V1_SELECTION.md`](POST_PPE_OPERATOR_VISIBILITY_V1_SELECTION.md)  
**Operator map:** [`PPE_OPERATOR_MAP_V1.md`](PPE_OPERATOR_MAP_V1.md)  
**Baseline:** **`main`**

---

## Sprint intent

Improve daily operator UX: **inbox** in `OPERATOR_STATUS.md`, **active IDE slice checkout**, and **queue preview** — inspired by Paperclip visibility patterns, implemented git-native in `dev-factory`. No external control plane.

## Sprint-level acceptance

1. `python scripts/ppe_operator_status.py` writes inbox block with owner, active slice, blocker, next command.
2. `generate_ide_build_starter.cmd` → writes `artifacts/orchestrator/ACTIVE_IDE_SLICE.json`; cleared by `mark_ide_product_ready.cmd`.
3. Queue preview lists up to 3 `READY` plan paths from `PHASE_QUEUE.json`.
4. [`PPE_OPERATOR_MAP_V1.md`](PPE_OPERATOR_MAP_V1.md) — verdict → agent → artifact → command.
5. `python -m pytest -q tests/test_ppe_active_ide_slice.py tests/test_ppe_operator_status_inbox.py` green.

## Not now

- `src/**`, `apps/msos-web/**`
- Paperclip server / Postgres dashboard
- Slice002+ until Slice001 witness green

---

## Slice map

### PPE-OperatorVis-Control-Slice001 — inbox + active slice (CONTROL) — **CLOSED**

**Goal:** Operator status inbox, `ACTIVE_IDE_SLICE.json`, queue preview; operator map + role cards.

**Closed** 2026-06-12 — inbox in `OPERATOR_STATUS.md`, checkout on starter write, docs in `PPE_OPERATOR_MAP_V1.md`.


### PPE-OperatorVis-Control-Slice002 — blockers + cost tags (CONTROL) — **CLOSED**

**Goal:** Auto `BLOCKERS.md`; workflow metrics lane/roundtrip fields; ntfy inbox line; priority auto-select; stale checkout guard.

**Closed** 2026-06-12 — see [`PPE_OPERATOR_IMPROVEMENTS_V1.md`](PPE_OPERATOR_IMPROVEMENTS_V1.md).

---

### PPE-OperatorVis-Witness-Slice003 — witness (EVIDENCE)

**Goal:** End-to-end: starter → active slice → mark ready → inbox clears; status readable from phone brief.

---

### PPE-OperatorVis-Closeout-Slice004 — chapter close (CONTROL)

**Goal:** Evidence doc **COMPLETE**; backlog `done`; continuity brief refresh via closeout job.

---

## Sprint status

**PPE operator visibility v1:** **IN PROGRESS** (Slice001 closed; Slice002+ pending).
