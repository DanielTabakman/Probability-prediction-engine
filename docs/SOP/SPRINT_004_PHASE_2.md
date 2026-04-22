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

### A. Selected now

- **None** — steward **SELECTION** required for the next Sprint 004 slice under §6 (**§6.B–§6.C** remain deferred until explicitly chosen). **`Sprint004-Slice001` — Width-disagreement candidate strip (v0) — CLOSED / shipped** (2026-04-21 **BUILD + CONTROL-CLOSEOUT**); product **`b13cb30b67457cb673514ebf8ae8183f88967f06`**.

### B. Likely next (not selected; require explicit SELECTION)

- **Trust / confidence / falsification layer** — make “candidate” status **honest** (limits, disconfirming views, what would change the label) without becoming advisory.

### C. Likely after that (not selected)

- **Candidate event logging / history** — lightweight, inspectable record of **candidate appearances** (still non-advisory; no auto-trade).

### D. Deferred / parked (explicitly not Sprint 004 v0)

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

## 8. Slice ledger (Sprint 004)

- **`Sprint004-Slice001` — Width-disagreement candidate strip (v0)** — **CLOSED / shipped** (2026-04-21 **BUILD + CONTROL-CLOSEOUT**). Product-of-record **`b13cb30b67457cb673514ebf8ae8183f88967f06`** on `recovery/frontier-steward-v2_1-baseline` (fast-forward from `build/sprint004-slice001-width-candidate-strip-v0`; pre-promotion tip **`478d2cf5ecb5eaa82e02e9cca022e3968e6a58e4`**). **Closeout validation:** `python -m pytest -q` → **120** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS**; **manual one-screen checklist** → **PASS**.

---

## 9. Execution posture (reference)

- **Preflight:** per `CODEX_AUTONOMY_V1` §5 + `RELAY_RUNTIME_V0` §8 when relay is used — **CLEAN** tree, explicit `slice_id`, `sprint_spec_path = docs/SOP/SPRINT_004_PHASE_2.md`, declared plane matches actual touched paths.
- **BUILD:** one slice at a time; bounded repair; no mixed-plane contamination.
- **CONTROL-CLOSEOUT:** steward-only; frontier + handoff + this ledger updated on acceptance.

---

## 10. Last updated

2026-04-21 — **CONTROL-CLOSEOUT (Steward Model 2.3):** **`Sprint004-Slice001` — CLOSED / shipped**; accepted baseline on `recovery/frontier-steward-v2_1-baseline` includes BUILD product **`b13cb30b67457cb673514ebf8ae8183f88967f06`** plus CONTROL-CLOSEOUT doc commits (verify `git merge-base --is-ancestor b13cb30b67457cb673514ebf8ae8183f88967f06 HEAD`); **next pending execution step:** **SELECTION** for the next Sprint 004 slice. **Sprint 003** remains **evidence-plane only**; Sprint 004 does not modify Sprint 003 scope.

2026-04-21 — **CONTROL-PLANE sprint open (Steward Model 2.3):** chartered **Sprint 004 — Phase 2 Product: Candidate Edge v1**; **SELECTED** **`Sprint004-Slice001` — Width-disagreement candidate strip (v0)**; **next pending execution step:** **PREFLIGHT** for Slice001. **No BUILD** on this pass. **Sprint 003** remains **evidence-plane only** (`docs/SOP/SPRINT_003_PHASE_2.md`); Sprint 004 does not modify Sprint 003 scope.
