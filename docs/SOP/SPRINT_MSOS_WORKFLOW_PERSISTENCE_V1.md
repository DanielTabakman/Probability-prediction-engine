# MSOS workflow persistence v1

**Display name:** MSOS thesis workflow store · **chapterId:** `msos_workflow_persistence_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 3) · [`MSOS_Product_Semantics_State_Model_v0.1.md`](../VISION/MSOS/storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md)  
**Prior chapter:** [`SPRINT_MSOS_USER_STATE_V1.md`](SPRINT_MSOS_USER_STATE_V1.md)  
**SELECTION:** [`POST_MSOS_WORKFLOW_PERSISTENCE_V1_SELECTION.md`](POST_MSOS_WORKFLOW_PERSISTENCE_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Move MSOS **thesis and expression workflow** from browser `localStorage` preview to a **server-side store** in the MSOS layer. Command Center KPIs (draft/confirmed counts, current work) read from MSOS records; optional `linked_snapshot_id` ties a thesis to a PPE freeze.

**Operator goal:** Save/confirm a thesis on the website and see it on Command Center on return — not per-browser preview only.

---

## Preconditions

1. `msos_user_state_v1` **COMPLETE** (snapshot bridge live; Command Center no longer silent fixtures).
2. P5–P6 UI routes exist on `main` ([`thesisPersistence.ts`](../../apps/msos-web/src/lib/thesisPersistence.ts), [`expressionPersistence.ts`](../../apps/msos-web/src/lib/expressionPersistence.ts)).
3. Semantics model lifecycle states honored (Exploring → Draft → Confirmed → Expression saved — sim-only).

---

## Acceptance

1. **MSOS workflow DB** (SQLite under `msos_web` volume or dedicated path) with tables for theses (+ optional expression rows) aligned to P5/P6 shapes.
2. **API routes** for read/write thesis (and expression save) — replace `localStorage` as primary path; migration or one-time import from preview keys documented.
3. **Command Center:** draft/confirmed KPIs and current-work list from MSOS store when records exist; snapshot feed remains supplementary (phase 2).
4. **Honest labels:** sim-only expression; no live execution CTA.
5. **Single-operator v1:** one logical owner acceptable; document phase 4 for Access-scoped `owner_email`.
6. Pytest witness for CRUD round-trip + Command Center counts.

## Not now

- Per-user Access identity scoping (phase 4)
- Monitor/History live surfaces (phase 5)
- REST/GraphQL exposing PPE math
- Live execution / Hyperliquid

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-WorkflowV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + schema witness |
| **MSOS-WorkflowV1-Product-Slice002** | PRODUCT | MSOS_UI | API + thesis/confirm/expression UI wired to server |
| **MSOS-WorkflowV1-Platform-Slice003** | EVIDENCE | PLATFORM | Compose volume + deploy docs |
| **MSOS-WorkflowV1-Witness-Slice004** | EVIDENCE | CONTROL | pytest + evidence checklist |
| **MSOS-WorkflowV1-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
