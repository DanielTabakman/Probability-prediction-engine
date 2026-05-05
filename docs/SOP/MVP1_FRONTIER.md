## MVP1_FRONTIER

Purpose: live steering document for PPE under **MVP1 phase architecture**.

### Control rule (hard)
- **Controlling canon**: `docs/VISION/PPE_MASTER_MVP1.md`
- **This file** is the only live frontier/steering truth.
- Legacy steering documents (e.g. legacy `CURRENT_FRONTIER`, sprint specs, legacy phase language) are **historical only** and must not be used as controlling truth.

### Current execution focus (MVP1 framing)
- **Current focus**: MVP1 **Phases 4–6 v0** are present in `src/`: snapshot + memory, per-snapshot review, and **read-only class rollups** over non-pending reviews. Continue validation and operator workflow; **Phase 6** remains research-surface only (no capital / no automated class verdicts).
- **Non-goal**: Phase 5–6 do **not** add execution, tickets, or automated live trading; class summary is counts + a one-line operator hint, not a model.

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
- **Phase 3 — Candidate/watch/no-trade decision surface**: **substantially present**
  - **Present**: single `primary_output_state` with explanation/confidence/horizon fields and first-class no-trade reasoning (v0).
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

