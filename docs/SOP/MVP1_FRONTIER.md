## MVP1_FRONTIER

Purpose: live steering document for PPE under **MVP1 phase architecture**.

### Control rule (hard)
- **Controlling canon**: `docs/VISION/PPE_MASTER_MVP1.md`
- **This file** is the only live frontier/steering truth.
- Legacy steering documents (e.g. legacy `CURRENT_FRONTIER`, sprint specs, legacy phase language) are **historical only** and must not be used as controlling truth.

### Current execution focus (MVP1 framing)
- **Current focus**: finish **MVP1 Phase 1** to contract (market + benchmark substrate), then proceed in dependency order Phase 2 → Phase 3.
- **Non-goal**: do not build memory/review/class summaries (Phases 4–6) before Phase 3’s output-state decision surface is real.

### MVP1 Phase placement (repo-truth)
This placement is repo-grounded; it is allowed to contradict legacy “phase complete” language.

- **Phase 1 — Market + benchmark substrate**: **partial**
  - **Present**: market context UI + trust/provenance surfaces exist (implied-lab dashboard; verification/trust strip).
  - **Missing**: explicit **benchmark identity** + explicit **benchmark width** shown alongside **market width** on the same horizon.
- **Phase 2 — ATM width-disagreement engine v1**: **missing**
  - **Present**: deterministic belief-vs-market disagreement logic exists, but that is not the MVP1 benchmarked width-gap engine.
  - **Missing**: ATM width gap (abs+rel) vs benchmark, materiality logic, trust gating, and required label set.
- **Phase 3 — Candidate/watch/no-trade decision surface**: **missing**
  - **Present**: explanatory candidate strip copy exists in parts.
  - **Missing**: single primary output state, confidence tier, review horizon, first-class no-trade reasoning.
- **Phase 4 — Snapshot + memory**: **missing**
- **Phase 5 — Review engine**: **missing**
- **Phase 6 — Class summaries**: **missing**

### MVP1 gap roadmap (Phase 1 → Phase 3 first)
#### Phase 1 (finish)
- Make the **benchmark identity explicit** (named benchmark ID + version).
- Make **market width** and **benchmark width** visible on the same horizon.
- Keep **trust state** explicit and preserve honest degraded-state handling.

#### Phase 2 (after Phase 1)
- Implement ATM width gap computation (absolute + relative) vs benchmark.
- Add explicit **materiality** logic and **trust gating**.
- Produce required deterministic labels (market too wide / too narrow / mixed / insufficient trust / insufficient materiality).

#### Phase 3 (after Phase 2)
- Add single primary output state: **candidate / watch only / no-trade** (exactly one).
- Add explanation, confidence tier, expression-family mapping, falsification condition, review horizon, and first-class no-trade reasoning.

### Logging policy (low-maintenance)
- Local-first append-only logbook: `artifacts/logbook/ppe_events.jsonl` (gitignored).
- Shared steering history is maintained by updating this frontier doc and the master canon doc (tracked), and by relying on existing per-run artifacts under `artifacts/**`.

