## MVP1_FRONTIER

Purpose: live steering document for PPE under **MVP1 phase architecture**.

### Control rule (hard)
- **Controlling canon**: `docs/VISION/PPE_MASTER_MVP1.md` (full doc re-imported 2026-05-18; §12 audit + §15A repo-truth)
- **This file** is the only live frontier/steering truth.
- Legacy steering documents (e.g. legacy `CURRENT_FRONTIER`, sprint specs, legacy phase language) are **historical only** and must not be used as controlling truth.

### Current execution focus (MVP1 framing)
- **Integrated status (one-pager):** [`PPE_INTEGRATED_STATUS.md`](PPE_INTEGRATED_STATUS.md)
- **Active BUILD chapter:** **Phase 2 on `main`** — [`SPRINT_MVP1_PHASE2_ON_MAIN.md`](SPRINT_MVP1_PHASE2_ON_MAIN.md) · [`PHASE_PLANS/mvp1_phase2_on_main_relay.json`](PHASE_PLANS/mvp1_phase2_on_main_relay.json).
- **SELECTION:** [`POST_PHASE2_PRODUCT_SLICE003_SELECTION.md`](POST_PHASE2_PRODUCT_SLICE003_SELECTION.md) — Slice005 chartered.
- **Next slice:** steward **SELECTION** for post–Slice005 BUILD (no new slice chartered on frontier).
- **Steward parallel:** VPS `.env` → **Research beta (v0)** CTA PASS; paid-interest call (**N** until live conversation).
- **Non-goal**: billing automation, execution engine, multi-asset BUILD in this pass.

### Phase 2 on `main` — relay queue (baseline **`main`**) — **OPEN**

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MVP1-Phase2-Control-Slice001` — charter + SELECTION record | CONTROL |
| **CLOSED** | `MVP1-Phase2-Reconcile-Slice002` — [`PHASE2_RECONCILE_REPORT.md`](PHASE2_RECONCILE_REPORT.md) | CONTROL |
| **CLOSED** | `MVP1-Phase2-Product-Slice003` — MVP1 UI exclusions alignment (copy + harness) | PRODUCT |
| **CLOSED** | `MVP1-Phase2-Closeout-Slice004` — checkpoint after Product-Slice003 | CONTROL |
| **CLOSED** | `MVP1-Phase2-Product-Slice005` — decision surface / panel parity audit | PRODUCT |

**Evidence:** [`MVP1_PHASE2_EVIDENCE_STATUS.md`](MVP1_PHASE2_EVIDENCE_STATUS.md) · **SELECTION:** [`POST_PHASE2_PRODUCT_SLICE003_SELECTION.md`](POST_PHASE2_PRODUCT_SLICE003_SELECTION.md)

### MVP1 Reliability — relay queue — **COMPLETE** (2026-05-19)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `MVP1-Reliability-Control-Slice001` | CONTROL |
| **CLOSED** | `MVP1-Reliability-Smoke-Slice002` | PRODUCT |
| **CLOSED** | `MVP1-Reliability-Deploy-Slice003` | CONTROL |
| **CLOSED** | `MVP1-Reliability-Closeout-Slice004` | CONTROL |

**Evidence:** [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md)

### Archived roadmap chapters (baseline **`main`**)

| Chapter | Status | Evidence |
|---------|--------|----------|
| Validation Chapter | **COMPLETE** 2026-05-19 | [`SPRINT_VALIDATION_CHAPTER.md`](SPRINT_VALIDATION_CHAPTER.md), [`VALIDATION_EVIDENCE_STATUS.md`](VALIDATION_EVIDENCE_STATUS.md) |
| Commercial Validation | **COMPLETE** 2026-05-19 | [`SPRINT_POST_VALIDATION_COMMERCIAL.md`](SPRINT_POST_VALIDATION_COMMERCIAL.md), [`COMMERCIAL_VALIDATION_EVIDENCE_STATUS.md`](COMMERCIAL_VALIDATION_EVIDENCE_STATUS.md) |
| MVP1 Reliability | **COMPLETE** 2026-05-19 | [`SPRINT_MVP1_RELIABILITY.md`](SPRINT_MVP1_RELIABILITY.md), [`MVP1_RELIABILITY_EVIDENCE_STATUS.md`](MVP1_RELIABILITY_EVIDENCE_STATUS.md) |

### Commercial Validation — relay queue (baseline **`main`**) — **COMPLETE**

**Sprint spec:** [`SPRINT_POST_VALIDATION_COMMERCIAL.md`](SPRINT_POST_VALIDATION_COMMERCIAL.md) · **Phase plan:** [`PHASE_PLANS/post_validation_commercial_validation.json`](PHASE_PLANS/post_validation_commercial_validation.json)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `Commercial-Validation-Control-Slice001` — charter accepted, frontier sync | CONTROL |
| **CLOSED** | `Commercial-Validation-Offer-Slice002` — `PPE_RESEARCH_OFFER_*` demo banner | PRODUCT |
| **CLOSED** | `Commercial-Validation-Reality-Slice003` — operator playbook + reality log | CONTROL |
| **CLOSED** | `Commercial-Validation-Nvidia-Brief-Slice004` — manual brief | CONTROL |

**Commercial Validation status:** **COMPLETE** (2026-05-19). **Ops follow-up:** [`COMMERCIAL_OPS_COMPLETION.md`](COMMERCIAL_OPS_COMPLETION.md). **After ops:** steward **SELECTION** for next BUILD chapter.

### Validation Chapter — relay queue (baseline **`main`**) — **COMPLETE**

**Sprint spec:** [`docs/SOP/SPRINT_VALIDATION_CHAPTER.md`](SPRINT_VALIDATION_CHAPTER.md) · **Phase plan:** [`docs/SOP/PHASE_PLANS/validation_chapter_relay.json`](PHASE_PLANS/validation_chapter_relay.json)

| Status | Slice | Plane |
|--------|--------|-------|
| **CLOSED** | `Validation-Chapter-Control-Slice001` — relay baseline `main`, sprint spec, frontier sync | CONTROL |
| **SHIPPED (pre-relay)** | Bulk BUILD **`9cc536b`** — §15 contract, demo UX, operator ritual docs | ad-hoc |
| **CLOSED** | `Validation-Chapter-Smoke-Slice001` — dual smoke green (harness title + MVP1 gates) | PRODUCT |
| **CLOSED** | `Validation-Chapter-UX-Slice002` — MVP1 primary output banner above fold | PRODUCT |
| **CLOSED** | `Validation-Chapter-Deploy-Slice003` — [VALIDATION_DEPLOY_WITNESS.md](VALIDATION_DEPLOY_WITNESS.md) (2026-05-19) | CONTROL |
| **CLOSED** | `Validation-Chapter-Closeout-Slice004` — chapter complete; evidence per [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md) | CONTROL |

**Validation Chapter status:** **COMPLETE** (2026-05-19). SELECTION record: [POST_VALIDATION_CHAPTER_SELECTION.md](POST_VALIDATION_CHAPTER_SELECTION.md).

**Operator (Validation, archived):** [MVP1_OPERATOR_RITUAL.md](MVP1_OPERATOR_RITUAL.md); [VALIDATION_EVIDENCE_STATUS.md](VALIDATION_EVIDENCE_STATUS.md).

### MVP1 Phase placement (repo-truth)
This placement is repo-grounded; it is allowed to contradict legacy “phase complete” language.

- **Phase 1 — Market + benchmark substrate**: **substantially present**
  - **Present**: explicit benchmark identity/version + market width + benchmark width + honest trust/degraded handling (implemented via MVP1 substrate module and surfaced in the MVP1 panel).
  - **Evidence pointers**:
    - logbook: `artifacts/logbook/ppe_events.jsonl` (`MVP1-Phase1-Slice001`)
    - sprint spec: `docs/SOP/MVP1_PHASE1_3_SPRINT.md`
- **Phase 2 — ATM width-disagreement engine v1**: **substantially present**
  - **Present**: abs+rel ATM width gap vs benchmark; explicit trust gating (`usable/degraded/invalid`); explicit materiality logic; required label set.
  - **Evidence pointers**:
    - logbook: `artifacts/logbook/ppe_events.jsonl` (`MVP1-Phase2-Slice001`)
    - sprint spec: `docs/SOP/MVP1_PHASE1_3_SPRINT.md`
- **Phase 3 — Candidate/watch/no-trade decision surface**: **substantially present (v0; provisional materiality)**
  - **Present**: `mvp1_decision` on verification payload (`primary_output_state`, `data_quality`, `materiality`, classification); UI in verification panel.
  - **Note**: materiality floors use v0 provisional proxies — see `mvp1_decision_surface.MATERIALITY_RULE_VERSION`.
  - **Evidence pointers**:
    - logbook: `artifacts/logbook/ppe_events.jsonl` (`MVP1-Phase3-Slice001`, final exit_code=0)
    - sprint spec: `docs/SOP/MVP1_PHASE1_3_SPRINT.md`
- **Phase 4 — Snapshot + memory**: **substantially present (v0)**
  - **Present**: explicit freeze action; SQLite persistence (`src/viz/frozen_evaluation_store.py`); reopen read-only JSON; benchmark witness + classifier version in frozen record (`src/viz/frozen_evaluation_record.py`); UI under implied lab **Freeze & history**.
  - **Evidence pointers**: sprint slice `MVP1-Phase4-Slice001` in [`docs/SOP/MVP1_PHASE1_3_SPRINT.md`](docs/SOP/MVP1_PHASE1_3_SPRINT.md); unit tests `tests/test_frozen_evaluation_*.py`; persistence stack also covered by [`tests/test_frozen_review_store.py`](tests/test_frozen_review_store.py) (shared DB module).
- **Phase 5 — Review engine**: **substantially present (v0)** — `snapshot_reviews` + APIs in [`src/viz/frozen_evaluation_store.py`](src/viz/frozen_evaluation_store.py); review form + **Pending snapshot reviews** in implied lab read-only frozen path in [`src/viz/app.py`](src/viz/app.py); unit test [`tests/test_frozen_review_store.py`](tests/test_frozen_review_store.py). Sprint: **`MVP1-Phase5-Slice001`** in [`docs/SOP/MVP1_PHASE1_3_SPRINT.md`](docs/SOP/MVP1_PHASE1_3_SPRINT.md).
- **Phase 6 — Class summaries**: **substantially present (v0)** — aggregation [`src/viz/reviewed_class_summary.py`](src/viz/reviewed_class_summary.py); query helper `list_completed_review_snapshots` in [`src/viz/frozen_evaluation_store.py`](src/viz/frozen_evaluation_store.py); implied lab expander **Class summary — reviewed snapshots** in [`src/viz/app.py`](src/viz/app.py); tests [`tests/test_reviewed_class_summary.py`](tests/test_reviewed_class_summary.py). Sprint: **`MVP1-Phase6-Slice001`** in [`docs/SOP/MVP1_PHASE1_3_SPRINT.md`](docs/SOP/MVP1_PHASE1_3_SPRINT.md).

### MVP1 gap roadmap (Phases 1–5 landed; Phase 6 v0 landed)
#### Recent build delta (repo-truth)
- **Phase 3 closeout (UI scope boundaries) — DONE (tracked `src/`)**:
  - **`MVP1-UIExclusions-Slice001`**: default hides strike/payoff/ticket/post-MVP lab chrome; optional re-enable via env **`PPE_POST_MVP1_LAB_UI`** (`1` / `true` / `yes` / `on`). Implementation: [`src/viz/mvp1_lab_ui.py`](src/viz/mvp1_lab_ui.py), gated controls in [`src/viz/app.py`](src/viz/app.py).
- **Phases 4–5 — snapshot + review — v0 landed**:
  - Freeze + SQLite + reopen read-only + per-snapshot review: [`src/viz/frozen_evaluation_record.py`](src/viz/frozen_evaluation_record.py), [`src/viz/frozen_evaluation_store.py`](src/viz/frozen_evaluation_store.py), implied lab **Freeze & history** / **Pending snapshot reviews** / read-only frozen path in [`src/viz/app.py`](src/viz/app.py).
- **Phase 6 — class rollup — v0 landed**:
  - Non-pending review rollups + operator hint line: [`src/viz/reviewed_class_summary.py`](src/viz/reviewed_class_summary.py), [`src/viz/app.py`](src/viz/app.py).

#### Next validation (product surface)
- Regression: dual smoke [`scripts/run_mvp1_dual_implied_lab_smoke.py`](scripts/run_mvp1_dual_implied_lab_smoke.py) after major implied-lab changes; full `pytest` before merge when touching shared modules ([`README.md`](../../README.md) steward backlog).
- Manual: freeze → review (non-pending) → open **Class summary — reviewed snapshots** and confirm counts move off zero.

#### Phase 5 optional follow-ons (deferred)
- Spec stub **`MVP1-Phase5-Slice002`** in [`docs/SOP/MVP1_PHASE1_3_SPRINT.md`](docs/SOP/MVP1_PHASE1_3_SPRINT.md): horizon filtering UX, structured paper field, optional SQLite FK — implement only if prioritized.

#### Phase 6 next (beyond v0)
- Richer filters (date range, expiry), export CSV/JSON of rollups, stronger trust metrics when verification payload gains explicit trust enums — track as future slices; canon still excludes execution and automated deployment.

### Logging policy (low-maintenance)
- Local-first append-only logbook: `artifacts/logbook/ppe_events.jsonl` (gitignored).
- Wrapper completion reports (human-friendly): `artifacts/orchestrator/LAST_RUN_REPORT.{json,md}` (gitignored; written on every `run_slice.cmd` / `run_phase*.cmd` exit).
- Shared steering history is maintained by updating this frontier doc and the master canon doc (tracked), and by relying on existing per-run artifacts under `artifacts/**`.

