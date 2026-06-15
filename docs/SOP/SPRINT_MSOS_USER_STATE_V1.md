# MSOS user state v1 — Command Center bridge (PPE snapshots)

**Display name:** Command Center bridge · **chapterId:** `msos_user_state_v1`  
**Controlling canon:** [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) (phase 2) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Prior chapter:** [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md)  
**SELECTION:** [`POST_MSOS_USER_STATE_V1_SELECTION.md`](POST_MSOS_USER_STATE_V1_SELECTION.md)  
**Priority:** **HIGH**  
**Baseline:** **`main`**

---

## Sprint intent

Replace Command Center **fixture KPIs and current-work** with a **read-only feed** from PPE `frozen_evaluations` (+ review status). Honest labeling: snapshot-sourced activity, not MSOS thesis lifecycle until phase 3.

**Operator goal:** Opening Command Center shows your **actual recent freezes and review state** from `app.*` — not “3 draft theses” from `commandCenterFixtures.ts`.

---

## Preconditions

1. `msos_production_wiring_v1` **COMPLETE** (sign-in + embed path live).
2. `app_full` snapshots enabled on VPS (`PPE_ENABLE_SNAPSHOTS=1`).
3. [`frozen_evaluation_store.py`](../../src/viz/frozen_evaluation_store.py) list/read APIs usable from a read-only boundary.

---

## Acceptance

1. **Read API:** `apps/msos-web` exposes server route (e.g. `/api/command-center/summary`) returning recent snapshots + review metadata — **read-only**, no writes to PPE DB.
2. **Platform:** `msos_web` has read-only access to snapshot SQLite (shared volume mount or documented internal path); deploy notes in [`MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md).
3. **Command Center UI:** KPI row and current-work list driven by API when data exists; fallback degraded state when DB unavailable (not silent fixtures).
4. **Honest copy:** Panel subheads state **“From PPE snapshots”**; do not label snapshot rows as “Draft thesis” / “Confirmed” unless mapped explicitly in evidence doc.
5. **Single-operator v1:** Shared DB acceptable; evidence doc documents multi-user gap (phase 4).
6. Pytest witness for API shape + Command Center renders live summary when fixture DB seeded in test.

## Not now

- MSOS thesis server store (phase 3)
- `owner_email` on snapshot rows (phase 4)
- Port PPE math to TypeScript
- Monitor/History live data (phase 5)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-UserStateV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-UserStateV1-Product-Slice002** | PRODUCT | MSOS_UI | Command Center + read API route |
| **MSOS-UserStateV1-Platform-Slice003** | EVIDENCE | PLATFORM | Compose volume mount + deploy docs |
| **MSOS-UserStateV1-Witness-Slice004** | EVIDENCE | CONTROL | pytest + evidence checklist |
| **MSOS-UserStateV1-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
