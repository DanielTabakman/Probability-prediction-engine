# MSOS trader review loop v1 — relay sprint spec

**Display name:** Trader review loop (post-mortem in MSOS) · **chapterId:** `msos_trader_review_loop_v1`  
**Controlling canon:** [`TRADER_LEARNING_SPINE_PROGRAM_V1.md`](TRADER_LEARNING_SPINE_PROGRAM_V1.md)  
**Prior:** P7 monitor/history live read path — [`SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md`](SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md)  
**SELECTION:** [`POST_MSOS_TRADER_REVIEW_LOOP_V1_SELECTION.md`](POST_MSOS_TRADER_REVIEW_LOOP_V1_SELECTION.md)  
**Priority:** **P0 spine**  
**Baseline:** **`main`**

---

## Sprint intent

Close the **save → review** loop inside MSOS: a trader opens a saved snapshot from Monitor, submits a post-mortem (supportive / contradictory / …), and Command Center KPIs update — without opening Streamlit.

---

## Preconditions

1. `msos_monitor_history_live_v1` **COMPLETE** (read path live).  
2. `frozen_evaluation_store.upsert_review` semantics are canon (Python).  
3. MSOS reads `ppe_frozen_evaluations.sqlite3` for Command Center today.

---

## Acceptance

1. `/monitor` lists snapshots with review-due vs reviewed tags (existing).  
2. **New:** snapshot detail page or drawer opens frozen summary + review form.  
3. **New:** `POST` review API persists `snapshot_reviews` row; invalid status rejected.  
4. After save, Command Center **Reviews due** / **Reviews complete** counts refresh on next load.  
5. Honest copy: paper / research only — no live-fill claims.  
6. `pytest` covers API validation + MSOS route smoke.

## Not now

- Class-summary aggregation UI  
- Auto-prompt when expiry passes (cron)  
- MSOS freeze/create snapshot (Streamlit or future slice)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-RevLoop-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue (this doc) |
| **MSOS-RevLoop-Product-Slice002** | PRODUCT | MSOS_UI | Review API + Monitor detail + form |
| **MSOS-RevLoop-Witness-Slice003** | EVIDENCE | CONTROL | pytest witness |
| **MSOS-RevLoop-Closeout-Slice004** | EVIDENCE | CONTROL | Chapter COMPLETE |
