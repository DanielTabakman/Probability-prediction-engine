# Sprint 004 — Phase 2 — Product: Candidate Edge v1

**What this file is:** the **Sprint 004 spec** (scope boundary + slice map + acceptance framing) for a **Phase 2 product** increment: a **BTC-first mispricing discovery wedge** carried as **small, testable slices**. This sprint is **not** Sprint 003; it does **not** subsume or rewrite **`docs/SOP/SPRINT_003_PHASE_2.md`** (Sprint 003 remains **evidence-plane only** — relay tooling / tests — per that sprint’s charter).

**Execution status (ledger lives elsewhere):** the **current selected slice**, BUILD/CLOSEOUT state, and the **next pending execution step** are authoritative in `docs/SOP/CURRENT_FRONTIER.md` (and summarized in `docs/SOP/HANDOFF.md`). **`Sprint004-Slice001` is CLOSED / shipped** (2026-04-21); product-of-record **`b13cb30b67457cb673514ebf8ae8183f88967f06`** on `recovery/frontier-steward-v2_1-baseline`.

**Authority model (unchanged):** **SELECTION** and **CONTROL-CLOSEOUT** are **steward-driven**. After a slice is chartered and **PREFLIGHT** authorizes work, a **relay-assisted BUILD** (when used) operates only inside **bounded BUILD loops** per `docs/SOP/CODEX_AUTONOMY_V1.md` + `docs/SOP/RELAY_RUNTIME_V0.md` + `docs/SOP/JOB_REGISTRY_V1.md` — the relay **helps execution**; it does **not** replace steward **selection** or **closeout**. This sprint spec was opened on a **CONTROL-PLANE-only** pass — **no BUILD** on that pass.

**Parent charter:** `docs/SOP/PHASE_2_CHARTER.md` (Phase 2 remains active; BTC-first and trust spine non-negotiables apply).  
**Prior sprints (do not reopen by default):** `docs/SOP/SPRINT_001_PHASE_2.md`, `docs/SOP/SPRINT_002_PHASE_2.md` (wrapped).  
**Parallel / orthogonal sprint (evidence-plane only, scope frozen here):** `docs/SOP/SPRINT_003_PHASE_2.md` — **Pilot-driven evidence-plane hardening (relay-assisted)**; Sprint 003’s **§3 / §6 / §7 acceptance and non-goals** are **not** amended by Sprint 004; further Sprint 003 work stays **deferred** unless the steward **explicitly SELECTS** a Sprint 003 slice under that spec.

---

## 1. Title

**Phase 2 Product: Candidate Edge v1**

## 2. Sprint intent

Open a **BTC-first “mispricing discovery” wedge**: surface **one narrow, descriptive, non-advisory** product strip where **belief vs market width / disagreement** suggests a **candidate** edge worth inspecting — **v0** prioritizes **legibility and falsifiability posture** over breadth, optimization, or automation language.

This sprint **advances Phase 2 product** (playability / meaning) while preserving **`docs/SOP/PHASE_2_CHARTER.md` §6** (no recommendation theater; exploration vs recommendation boundary; no silent semantic rewrites).

## 3. Acceptance criteria (sprint-level; directional)

A Sprint 004 slice is acceptable only if **all** hold at closeout:

1. **BTC-first lab** positioning is preserved (no multi-asset expansion; no cross-expiry scanner as the deliverable of this sprint’s selected slices).
2. **Non-advisory** posture: copy and affordances stay **descriptive** (“highlights,” “compares,” “candidate”) — **no** ranked plays, **no** “you should,” **no** auto-trade language.
3. **Semantic contracts** (`docs/SEMANTIC_CONTRACTS.md`) are **not** silently rewritten; if a slice needs a contract exception, it is **explicitly** steward-approved as a separate control-plane action (not the default).
4. **Trust spine** non-regression vs Phase 1 / Sprint 001 / Sprint 002: provenance, degraded honesty, verification discoverability remain intact.
5. **Universal tier:** `python -m pytest -q` green before/after BUILD with **no new unexplained failures** relative to the pre-BUILD run.
6. **Product visibility:** slices that touch user-visible implied-lab surfaces also satisfy the sprint **test plan** (primary smoke and any slice-declared harness paths per `docs/SOP/OPERATING_RULES.md` / runbook).

## 4. Not now / anti-goals (sprint-level)

- **Multi-anomaly scanner** (breadth-first surfacing of many unrelated signals).
- **Strike optimization** or “best structure” search framed as advice.
- **Auto-trade language** (execution, orders, bots, “do this trade”).
- **Cross-expiry scanner** as a v0 deliverable.
- **Broad UI redesign** (full layout / navigation overhaul).
- **Silent widening** into engine refactors, new external data products, or Phase 3–class commercial wrapper.

## 5. Validation posture

- **Universal:** `python -m pytest -q` on baseline before and after each BUILD slice.
- **Product witness:** `python scripts/run_implied_lab_ui_smoke.py` when `src/viz/**` (or agreed product paths) change; add **scenario-directed** harness runs when classification / disagreement / glance paths are touched.
- **Stop / escalate:** if copy would require **new quantitative claims** or **contract edits** not explicitly approved, stop and return to **steward SELECTION** — do not smuggle scope in BUILD.

---

## 6. Sprint 004 map (lightweight)

### A. Selected now (next execution boundary)

- **`Sprint004-Slice004` — Directional-disagreement candidate strip + payload/harness refactor (v0)** — **SELECTED** under tiered-delegation soft-launch (Tier 2 SELECTION; steward veto window observed). BUILD agent spawn pending; spec being folded with D3–D6 decisions.

### B. Checkpointed / not closed (Sprint004 product slice — closeout pending)

- *(empty — Slice003 closed via tiered-delegation CONTROL-CLOSEOUT 2026-04-27.)*

### C. Closed / shipped (this sprint)

- **`Sprint004-Slice003` — Candidate event logging / history foundation (v0)** — **CLOSED / shipped** (2026-04-27 **CONTROL-CLOSEOUT under tiered-delegation soft-launch**; fast-forward from `build/sprint004-slice003-closeout-v1`; pre-promotion baseline tip **`fd981dde81fb5135652acfd4d7a4a0ba7841f4b6`**; product-of-record / FF tip **`a98377a066db99f1e893c2ef86d1ba71f6a5c53d`**). **Closeout validation:** `python -m pytest -q` → **121** passed (re-verified at promotion time); `python scripts/run_implied_lab_ui_smoke.py` → **PASS** (signal `BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP`; manifest `artifacts/ui_smoke/20260427_180931/ui_smoke_manifest.json`; `schema_version: 2`). **Schema-drift fold-in shipped:** `MANIFEST_SCHEMA_VERSION` constant in `scripts/implied_lab_ui_smoke_harness.py`; canonical `docs/SOP/MANIFEST_SCHEMA.md`; assertion test `tests/test_manifest_schema_drift.py`; advisory `docs/SOP/CODE_DOCS_DRIFT_POLICY_V1.md`. **Authority note:** first slice closed under the tiered-delegation soft-launch (Tier 2 CONTROL-CLOSEOUT); steward retains escalation authority on rubric failure or semantic-contract drift; no failures triggered.
- **`Workflow-Hardening-Slice-003` — sanctioned target-region witness for Slice003 closeout** — **CLOSED / shipped** (2026-04-22 **CONTROL-PLANE PROMOTION**; fast-forward from `build/wh-slice003-sanctioned-witness-v0`; accepted baseline tip **`7ae6470a9c202998470ce093909613881b31286d`**; pre-promotion **`0a16c47df94319d4abf7adb3569f34c86dbc35bb`**). Shipped: sanctioned **target-region** witness path, **manifest/schema v2** closeout semantics, **bounded degraded** classification.
- **`Sprint004-Slice002` — Width-strip trust / confidence / falsification refinement (v0)** — **CLOSED / shipped** (2026-04-22, Steward Model 2.3).
- **`Sprint004-Slice001` — Width-disagreement candidate strip (v0) — CLOSED / shipped** (2026-04-21 **BUILD + CONTROL-CLOSEOUT**); product **`b13cb30b67457cb673514ebf8ae8183f88967f06`**.

### D. Pending / not selected (keep empty unless steward names a next slice)

### E. Deferred / parked (explicitly not Sprint 004 v0)

Items listed in **§4** remain **out of scope** until a future steward **re-charters** or opens a new sprint boundary.

---

## 7. Sprint004-Slice001 — Width-disagreement candidate strip (v0)

**Identifier:** `Sprint004-Slice001`  
**Title:** **Width-disagreement candidate strip (v0)**  
**Declared plane (expected at PREFLIGHT):** **PRODUCT-PLANE** (typical for `src/viz/**` work — confirm at PREFLIGHT; must match actual diff).  
**Execution mode:** after PREFLIGHT, **relay-assisted BUILD** is **optional** — only if the steward activates `run_selected_slice_v1` for this slice; otherwise a steward-scoped **PRODUCT-PLANE BUILD** on a short-lived branch per `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`. **Relay helps inside bounded BUILD loops**; it does **not** perform SELECTION or CONTROL-CLOSEOUT.

### 7.1 User / problem statement (v0)

Users can see **belief vs market** tension, but the lab does not yet give a **single, bounded “candidate strip”** that names **width/disagreement-shaped** tension as a **hypothesis to inspect** — not a recommendation — aligned with existing glance / digest semantics.

### 7.2 Exact target (pinned at BUILD / closeout)

**Primary UI region:** implied-lab **right column**, dedicated `right_width_candidate_slot` — **between** **Summary** card and **Trust / provenance** strip (`src/viz/app.py`). **PRODUCT-PLANE files:** `src/viz/app.py`, `src/viz/implied_lab_provenance.py`, `tests/test_width_vol_candidate_strip.py`. **Verification commands:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.

### 7.3 Non-goals (slice-level; v0)

- No **multi-anomaly** or **cross-expiry** scanning.
- No **strike optimizer** or **auto-trade** copy.
- No **semantic contract** edits unless separately approved.

### 7.4 Acceptance bullets (slice-level; Slice001 closeout)

- [x] A **compact candidate strip** makes **width_vol** tension **legible** as a **candidate** (wording non-advisory; contract-aligned).
- [x] **pytest** + **primary UI smoke** **PASS** on the BUILD branch after changes touching product surfaces (`artifacts/ui_smoke/20260421_195139/`).
- [x] No regression to **trust / provenance / verification** discoverability.

### 7.5 Validation posture (slice-level)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** smallest relevant **harness** scenario if disagreement / glance / classification strings are touched.
- **Closeout:** steward **CONTROL-CLOSEOUT** updates `CURRENT_FRONTIER.md`, `HANDOFF.md`, and this file’s §8 ledger.

---

---

## 9. Sprint004-Slice004 — Directional-disagreement candidate strip + payload/harness refactor (v0)

**Identifier:** `Sprint004-Slice004`  
**Title:** **Directional-disagreement candidate strip + payload/harness refactor (v0)**  
**Declared plane:** **PRODUCT-PLANE** (primary: `src/viz/**`; harness/evidence: `scripts/implied_lab_ui_smoke_harness.py`, `scripts/run_implied_lab_ui_smoke.py`; control: `docs/SOP/**`).  
**Execution mode:** steward-scoped BUILD via tiered-delegation soft-launch; BUILD agent authorized under `PROTOCOL: CODEX_AUTONOMY_V1`. Authority boundary: PREFLIGHT → BUILD → bounded repair → BUILD-CLOSEOUT. CONTROL-CLOSEOUT is parent-agent (steward) owned.

### 9.1 User / problem statement (v0)

The implied lab surfaces **width_vol** tension as a candidate strip but has no corresponding strip for **location-shaped** (directional / mixed) disagreement. Users whose belief peak diverges from the market reference modal see the glance digest and strategy families but no compact, hypothesis-oriented strip in the right column naming the peak tension explicitly as a candidate to inspect. Adding the directional strip completes the two-category hypothesis surface (v0).

### 9.2 Exact target (slot, files, verification commands)

**Primary UI region:** implied-lab **right column**, dedicated `right_directional_candidate_slot` — **directly below** `right_width_candidate_slot` (between Summary card and Trust / provenance strip).

**PRODUCT-PLANE files:**
- `src/viz/implied_lab_provenance.py` — added `build_directional_candidate_strip_payload`; extracted shared helpers `_build_trust_artifact_md`, `_build_expression_families_md`; refactored `build_width_vol_candidate_strip_payload` to use shared helpers.
- `src/viz/app_panels.py` — added `render_directional_candidate_strip_payload`; added width-only caption to `render_width_vol_history_panel` per D4.
- `src/viz/app.py` — registered `right_directional_candidate_slot`; imported and called new functions.

**TEST files:**
- `tests/test_directional_candidate_strip.py` — new acceptance tests (mirrors `test_width_vol_candidate_strip.py` shape).

**HARNESS files (sanctioned):**
- `scripts/implied_lab_ui_smoke_harness.py` — bumped `MANIFEST_SCHEMA_VERSION` 2→3; added `slice004_directional_witness` row; category-driven signal helpers; refactored `_closeout_block` (replaces `_slice003_closeout_block`).
- `scripts/run_implied_lab_ui_smoke.py` — prints both witness signals (width_vol + directional).

**Verification commands:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.

### 9.3 Non-goals (slice-level; v0)

- No **directional history panel** (D4: width-only history; directional-history deferred to a future slice).
- No **multi-anomaly** or **cross-expiry** scanning.
- No **strike optimizer** or **auto-trade** copy.
- No **semantic contract** edits.
- No **second `directional_schema_version` field** or any second version number.

### 9.4 Acceptance bullets (Slice004 closeout)

- [ ] Directional candidate strip renders in `right_directional_candidate_slot` with **"Location-shaped tension — hypothesis to inspect"** heading; non-advisory copy.
- [ ] When disagreement category is `directional` or `mixed`, the strip surfaces; otherwise it gracefully skips (parallel to width_vol behavior).
- [ ] Width-history panel still renders with width-only caption per D4: `*History scope: width-only (v0). Directional-history slated for a future slice.*`
- [ ] **pytest** → all tests pass on the BUILD branch (count ≥ 121 + new directional tests).
- [ ] **UI smoke** (`python scripts/run_implied_lab_ui_smoke.py`) → **PASS**; manifest `schema_version: 3`; both witnesses (width_vol + directional) present in the manifest; `evidence_plane_complete: true` (or explicit sanctioned bounded-degraded reason).
- [ ] `tests/test_manifest_schema_drift.py` still passes (reads v3 from `docs/SOP/MANIFEST_SCHEMA.md` and matches the bumped constant).
- [ ] No regression to width_vol strip behavior, history panel, or trust/provenance discoverability.
- [ ] No semantic-contract drift: no advisory copy ("recommended", "should buy", "best", "trade signal").

### 9.5 Validation posture (slice-level)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** `python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <PORT>` for live directional strip witness (gated — not a universal tax).
- **Closeout:** steward CONTROL-CLOSEOUT updates `CURRENT_FRONTIER.md`, `HANDOFF.md`, and the slice ledger below.

---

## 10. Slice ledger (Sprint 004)

- **`Sprint004-Slice001` — Width-disagreement candidate strip (v0)** — **CLOSED / shipped** (2026-04-21 **BUILD + CONTROL-CLOSEOUT**). Product-of-record **`b13cb30b67457cb673514ebf8ae8183f88967f06`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/sprint004-slice001-width-candidate-strip-v0`; pre-promotion tip **`478d2cf5ecb5eaa82e02e9cca022e3968e6a58e4`**). **Closeout validation:** `python -m pytest -q` → **120** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS**; **manual one-screen checklist** → **PASS**.
- **`Sprint004-Slice002` — Width-strip trust / confidence / falsification refinement (v0)** — **CLOSED / shipped** (2026-04-22 **BUILD-CLOSEOUT / CONTROL-CLOSEOUT**). Product-of-record **`069d76f`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/sprint004-slice002-widthstrip-refine`; pre-promotion baseline tip **`bec9024`**). **Change boundary:** copy/semantic refinement only in the existing **width_vol** candidate strip payload (no layout-slot move; no new gating dimensions). **Closeout validation:** `python -m pytest -q` → **PASS**; `python scripts/run_implied_lab_ui_smoke.py` → **PASS**.
- **`Workflow-Hardening-Slice-003` — sanctioned target-region witness for Slice003 closeout** — **CLOSED / shipped** (2026-04-22 **CONTROL-PLANE PROMOTION**; fast-forward from `build/wh-slice003-sanctioned-witness-v0`; tip **`7ae6470a9c202998470ce093909613881b31286d`**; pre-promotion **`0a16c47df94319d4abf7adb3569f34c86dbc35bb`**).
- **`Sprint004-Slice003` — Candidate event logging / history foundation (v0)** — **CLOSED / shipped** (2026-04-27 **CONTROL-CLOSEOUT under tiered-delegation soft-launch**). Product-of-record / FF tip **`a98377a066db99f1e893c2ef86d1ba71f6a5c53d`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/sprint004-slice003-closeout-v1`; pre-promotion tip **`fd981dde81fb5135652acfd4d7a4a0ba7841f4b6`**). **Honest visual closeout achieved:** session-local history (`Sprint004-Slice003` product) + schema-drift fold-in (`MANIFEST_SCHEMA_VERSION` constant; `docs/SOP/MANIFEST_SCHEMA.md`; `tests/test_manifest_schema_drift.py`; `docs/SOP/CODE_DOCS_DRIFT_POLICY_V1.md`). **Closeout validation:** `python -m pytest -q` → **121** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** (`BOUNDED_LIVE_DATA_NO_WIDTH_VOL_STRIP`; `artifacts/ui_smoke/20260427_180931/`; `schema_version: 2`). **Stale exec branch:** `exec/sprint004-slice003-history-v0` deleted at promotion (sibling tip `dc98a541...` superseded; no unique product work lost — sibling carried checkpoint-only commits). **Accepted baseline gate (verify):** `git merge-base --is-ancestor 7ae6470a9c202998470ce093909613881b31286d HEAD` on `recovery/frontier-steward-v2_1-baseline`.
- **`Sprint004-Slice004` — Directional-disagreement candidate strip + payload/harness refactor (v0)** — **BUILD-CLOSEOUT complete on combined recovery branch `build/sprint004-slice004-and-wh004-combined-recovery-v1` @ `c4f9f09e1af742455f526d53df9c0f2af594a336`; awaiting steward CONTROL-CLOSEOUT.** Recovery note: original BUILD branch `build/sprint004-slice004-directional-strip-v0` @ `7f8ec19e` was partially orphaned by a 2026-04-27 parallel-agent collision; Slice004 product cherry-picked onto fresh recovery branch together with WH-Slice-004 and worktree-rule canonization. **Evidence (re-validated on recovery branch):** pytest **127** passed (121 baseline + 6 directional); UI smoke **PASS** (`schema_version: 3`; `evidence_plane_complete: true`; `artifacts/ui_smoke/20260427_200556/`).
- **`WH-Slice-004` — Stale-canon pointer callouts (tiered-delegation soft-launch)** — **folded into combined recovery branch** `build/sprint004-slice004-and-wh004-combined-recovery-v1` (collision recovery, 2026-04-27). Under normal (non-collision) flow, WH-Slice-004 would have been a separate control-plane slice. Original isolated tip: `build/wh-slice004-softlaunch-canon-pointer-v0` @ `7af4f91e` (preserved as incident evidence; not deleted). Also folded into recovery branch: worktree-rule canonization in `FRONTIER_STEWARD_PROTOCOL.md` and `HANDOFF.md` (incident-driven operational rule; adds `git worktree add` per-agent dispatch requirement). Awaiting steward CONTROL-CLOSEOUT with Slice004.

---

## 11. Execution posture (reference)

- **Preflight:** per `CODEX_AUTONOMY_V1` §5 + `RELAY_RUNTIME_V0` §8 when relay is used — **CLEAN** tree, explicit `slice_id`, `sprint_spec_path = docs/SOP/SPRINT_004_PHASE_2.md`, declared plane matches actual touched paths.
- **BUILD:** one slice at a time; bounded repair; no mixed-plane contamination.
- **CONTROL-CLOSEOUT:** steward-only; frontier + handoff + this ledger updated on acceptance.

---

## 12. Last updated

2026-04-22 — **CONTROL-PLANE PROMOTION / CLOSEOUT (Steward Model 2.3):** **`Workflow-Hardening-Slice-003` — CLOSED / shipped** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/wh-slice003-sanctioned-witness-v0`; tip **`7ae6470a9c202998470ce093909613881b31286d`**). **`Sprint004-Slice003` remains CHECKPOINTED / NOT CLOSED** — **honest visual closeout next** (PREFLIGHT → sanctioned smoke). **Accepted baseline gate (verify):** `git merge-base --is-ancestor 7ae6470a9c202998470ce093909613881b31286d HEAD` on `recovery/frontier-steward-v2_1-baseline`. **Sprint 003** remains **evidence-plane only**; Sprint 004 does not modify Sprint 003 scope. **No** Slice003 rerun in this pass.

2026-04-22 — **CONTROL-PLANE SELECTION (Steward Model 2.3, historical):** **`Workflow-Hardening-Slice-003` — SELECTED** (same-day precursor to BUILD + promotion above).

2026-04-21 — **CONTROL-CLOSEOUT (Steward Model 2.3):** **`Sprint004-Slice001` — CLOSED / shipped**; accepted baseline on `recovery/frontier-steward-v2_1-baseline` includes BUILD product **`b13cb30b67457cb673514ebf8ae8183f88967f06`** plus CONTROL-CLOSEOUT doc commits (verify `git merge-base --is-ancestor b13cb30b67457cb673514ebf8ae8183f88967f06 HEAD`). **Sprint 003** remains **evidence-plane only**; Sprint 004 does not modify Sprint 003 scope.

2026-04-21 — **CONTROL-PLANE sprint open (Steward Model 2.3):** chartered **Sprint 004 — Phase 2 Product: Candidate Edge v1**; **SELECTED** **`Sprint004-Slice001` — Width-disagreement candidate strip (v0)**; **next pending execution step:** **PREFLIGHT** for Slice001. **No BUILD** on this pass. **Sprint 003** remains **evidence-plane only** (`docs/SOP/SPRINT_003_PHASE_2.md`); Sprint 004 does not modify Sprint 003 scope.
