## MVP1_FRONTIER

Purpose: live steering document for PPE under **MVP1 phase architecture**.

### Control rule (hard)
- **Controlling canon**: `docs/VISION/PPE_MASTER_MVP1.md`
- **This file** is the only live frontier/steering truth.
- Legacy steering documents (e.g. legacy `CURRENT_FRONTIER`, sprint specs, legacy phase language) are **historical only** and must not be used as controlling truth.

### Current execution focus (MVP1 framing)
- **Current focus**: begin MVP1 **Phase 4** (snapshot + memory) in dependency order, now that Phase 1–3 substrate/engine/decision surface is present and MVP1 UI exclusions are enforced by default.
- **Non-goal**: do not treat Phases **5–6** (review engine + class summaries) as “live product truth” until Phase 4 persistence exists and Phase 3 outputs can be frozen/replayed from durable snapshots.

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
- **Phase 4 — Snapshot + memory**: **missing**
- **Phase 5 — Review engine**: **missing**
- **Phase 6 — Class summaries**: **missing**

### MVP1 gap roadmap (Phase 1–3 landed; Phase 4 next)
#### Recent build delta (repo-truth)
- **Phase 3 closeout (UI scope boundaries) — DONE**:
  - **UI exclusions landed**: `MVP1-UIExclusions-Slice001` (default hide strike/payoff/ticket surfaces; optional re-enable via `PPE_POST_MVP1_LAB_UI`).
  - **Phase plan run complete**: `docs/SOP/PHASE_PLANS/mvp1_finish_up.json` ran to `COMPLETE` with steward summary at `artifacts/orchestrator/steward_phase_summary.json`.

#### Phase 4 next (snapshot + memory)
- Snapshot + memory: freeze evaluation outputs, persist them durably, and support reopen/review transitions per master canon.

### Logging policy (low-maintenance)
- Local-first append-only logbook: `artifacts/logbook/ppe_events.jsonl` (gitignored).
- Wrapper completion reports (human-friendly): `artifacts/orchestrator/LAST_RUN_REPORT.{json,md}` (gitignored; written on every `run_slice.cmd` / `run_phase*.cmd` exit).
- Shared steering history is maintained by updating this frontier doc and the master canon doc (tracked), and by relying on existing per-run artifacts under `artifacts/**`.

