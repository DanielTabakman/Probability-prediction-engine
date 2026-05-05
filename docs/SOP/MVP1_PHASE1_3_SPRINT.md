# MVP1 Phase 1–3 — Build sprint (contracted)

Purpose: provide a stable slice spec file for MVP1 Phase 1–3 implementation and relay-gated execution.

Controlling canon: `docs/VISION/PPE_MASTER_MVP1.md` (MVP1 phases + governance + exclusions).
Live steering: `docs/SOP/MVP1_FRONTIER.md`.

## Slices

### MVP1-Phase1-Slice001 — Market + benchmark substrate completion (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** complete MVP1 Phase 1 contract:
- explicit benchmark identity + version
- market width and benchmark width visible on the same horizon
- visible trust state + honest degraded-state handling

**Non-goals / exclusions (MVP1):**
- no exact strikes workflows
- no trade ticket / executable ticket generation
- no snapshot persistence (Phase 4)
- no review engine (Phase 5)
- no class summaries (Phase 6)

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)

---

### MVP1-Phase2-Slice001 — Width-gap engine v1 (benchmarked) (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** implement MVP1 Phase 2 engine contract (benchmark vs market width):
- ATM width gap calculation: **absolute + relative**
- explicit **materiality logic** (v0 proxies allowed, must be labeled as such)
- explicit **trust gating** using `usable/degraded/invalid` (must affect outputs)
- required label set:
  - `market_too_wide`
  - `market_too_narrow`
  - `mixed_unclear`
  - `insufficient_trust`
  - `insufficient_materiality`

**Non-goals / exclusions (MVP1):**
- no confidence tiers (Phase 3)
- no output-state decision surface (Phase 3)
- no exact strikes workflows
- no trade ticket / executable ticket generation
- no snapshot persistence (Phase 4)

**Acceptance evidence:**
- `python -m pytest -q` PASS
- update verification payload with explicit fields for `W_m`, `W_b`, `G_abs`, `G_rel`, trust state, and materiality evaluation

---

### MVP1-Phase3-Slice001 — Decision surface (candidate/watch/no-trade) (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** implement MVP1 Phase 3 contract:
- exactly one primary output state: `candidate` / `watch_only` / `no_trade`
- explanation (plain language)
- confidence tier
- expression-family mapping (family-level only; no exact strikes)
- falsification condition
- review horizon assignment
- first-class no-trade reasoning

**Decision precedence (must match master canon):**
1) invalid path → no-trade  
2) low-trust → no-trade  
3) mixed/unclear → watch_only or no-trade  
4) insufficient materiality → no-trade  
5) marginal disagreement → watch_only  
6) clear+material+high-trust → candidate

**Non-goals / exclusions (MVP1):**
- no snapshot persistence (Phase 4)
- no review engine (Phase 5)
- no class summaries (Phase 6)
- no exact strikes workflows
- no trade ticket / executable ticket generation

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)
- verification payload contains `primary_output_state` and the required explanation/confidence/horizon fields

---

### MVP1-UIExclusions-Slice001 — Hide out-of-scope MVP1 UI surfaces (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** enforce MVP1 out-of-scope boundaries in the UI so it cannot be mistaken for later-phase functionality.

**Required exclusions (hide/disable):**
- exact strikes / target payoff surfaces (anything that implies strike selection or payoff targeting)
- trade ticket / executable ticket surfaces and any “execution-ready” implications

**Acceptance evidence:**
- `python -m pytest -q` PASS
- `python scripts/run_implied_lab_ui_smoke.py` PASS (or explicitly classified if live-data degraded)
- MVP1 panel does not present any strike-level or ticket-level workflow; any legacy panels are hidden or gated behind a non-MVP1 flag

---

### MVP1-Phase4-Slice001 — Snapshot + memory (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** MVP1 Phase 4 canon: explicit freeze, durable persistence, retrieval/reopen, benchmark + classifier witness fields.

**Must include:**
- `build_frozen_evaluation_record` + SQLite store (`src/viz/frozen_evaluation_record.py`, `src/viz/frozen_evaluation_store.py`)
- Streamlit **Freeze this evaluation** + list + **Reopen read-only view** (under **Freeze & history** on the implied lab chart column; default DB `data/ppe_frozen_evaluations.sqlite3`, env `PPE_SNAPSHOT_DB_PATH`)

**Acceptance evidence:**
- `python -m pytest -q tests/test_frozen_evaluation_record.py tests/test_frozen_evaluation_store.py tests/test_mvp1_lab_ui.py` PASS
- Manual: default (no `PPE_POST_MVP1_LAB_UI`) hides strike/payoff/ticket chrome; freeze writes a row; reopen shows verification-style readout + optional debug JSON
- Optional: `python scripts/run_mvp1_dual_implied_lab_smoke.py` (MVP1 default scenario + full-lab scenario; requires Playwright)

---

### MVP1-Phase5-Slice001 — Review engine (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** MVP1 Phase 5 canon ([`docs/VISION/PPE_MASTER_MVP1.md`](docs/VISION/PPE_MASTER_MVP1.md) ~1017–1037): review frozen cases after the review horizon with finite statuses, outcome fields, and notes — **without** real-money execution or class-level automation.

**Implemented attachment model (v0):** SQLite table **`snapshot_reviews`** in the same file as `frozen_evaluations` (`src/viz/frozen_evaluation_store.py`): `id`, `snapshot_id` (unique, logical FK to `frozen_evaluations.id`), `review_status` (`pending` / `supportive` / `contradictory` / `contaminated` / `not_judgeable`), `outcome_notes`, `reviewed_at_utc`, `review_horizon_ref` (digest from frozen verification when saved).

**Must include (v0):**
- Reopen frozen case → enter review → persist status + notes → reload shows same review row.
- **Pending snapshot reviews** list (snapshots with no review row or status `pending`).
- Finite review statuses per canon; contaminated / not judgeable supported.

**Must exclude:** execution / ticket engine; automated class verdicts beyond basic summaries (Phase 6).

**Acceptance evidence:**
- `python -m pytest -q tests/test_frozen_review_store.py tests/test_frozen_evaluation_store.py` PASS
- Manual: freeze → reopen read-only → set review status + notes → **Save review** → reload page → values persist; optional: open a row from **Pending snapshot reviews**

---

### MVP1-Phase5-Slice002 — Review UX / persistence hardening (optional; deferred)

**Plane:** PRODUCT-PLANE  
**Goal:** Close remaining MVP1 Phase 5 canon gaps from [`docs/VISION/PPE_MASTER_MVP1.md`](docs/VISION/PPE_MASTER_MVP1.md) beyond v0 — **only if prioritized**.

**Candidate scope (pick subsets):**
- Review-horizon handling in UI: filter/sort **Pending snapshot reviews** or frozen history by expiry / `review_horizon_ref` digest.
- Lightweight structured **paper** tag or single-line field (still no execution ledger).
- SQLite **`PRAGMA foreign_keys=ON`** + optional `FOREIGN KEY(snapshot_id)` / `ON DELETE CASCADE` on `snapshot_reviews` if snapshots are ever deleted.

**Must still exclude:** execution, ticket engine, automated class verdicts (Phase 6 remains descriptive-only).

**Acceptance evidence (when implemented):** targeted pytest + manual checklist per chosen bullet.

---

### MVP1-Phase6-Slice001 — Class summaries (v0)

**Plane:** PRODUCT-PLANE  
**Goal:** MVP1 Phase 6 canon ([`docs/VISION/PPE_MASTER_MVP1.md`](docs/VISION/PPE_MASTER_MVP1.md) ~1039–1053): aggregate **reviewed** frozen cases into countable dimensions and a single operator-facing guidance line — **without** live capital, portfolio logic, or automated deployment.

**Implemented (v0):**
- Query helper **`list_completed_review_snapshots`** — inner join frozen rows with `snapshot_reviews` where `review_status != 'pending'` ([`src/viz/frozen_evaluation_store.py`](../../src/viz/frozen_evaluation_store.py)).
- Pure aggregation **`build_class_summary`** / **`extract_summary_dimensions`** ([`src/viz/reviewed_class_summary.py`](../../src/viz/reviewed_class_summary.py)): counts by review outcome, disagreement category (direction proxy), shape-gap strength (confidence proxy), Breeden gate (trust proxy), benchmark method, classifier version.
- Streamlit **Class summary — reviewed snapshots (Phase 6)** expander on the implied lab column ([`src/viz/app.py`](../../src/viz/app.py)).

**Must exclude:** automated capital deployment; broad anomaly scanning; strategy optimization beyond descriptive counts.

**Acceptance evidence:**
- `python -m pytest -q tests/test_reviewed_class_summary.py tests/test_frozen_review_store.py` PASS
- Manual: save at least one frozen snapshot with review status other than **pending** → open **Class summary** → non-zero reviewed count and JSON breakdowns

