# Implied lab — operator runbook

## 1. Purpose

This runbook is the **canonical procedure** for running, validating, interpreting smoke outcomes, and closing out work on the **one-screen BTC implied lab** Streamlit workflow (`src/viz/app.py` and related viz modules).

**Audience:** execution agents, frontier stewards, and human operators touching this phase.

**MVP1 closed-loop ritual (freeze → review → class summary):** [MVP1_OPERATOR_RITUAL.md](MVP1_OPERATOR_RITUAL.md).

**Boundary:** implied lab **operations and evidence** only. It does **not** replace general repo governance, git policy, or phase-wide strategy documents—those live in the SOP docs listed under [Related docs](#9-related-docs).

---

## 2. When to use it

- **Before** a **BUILD** or **CLOSEOUT** pass that changes or verifies the implied lab UI or its closeout evidence.
- **When validating** a feature slice against agreed tiers (pytest, smoke A, conditional smoke C, manual/screenshot).
- **When interpreting** UI smoke pass/fail, timeouts, or manifest booleans—especially to separate **product regression** from **environment / live-data** effects.
- **When gathering evidence** for closeout: manifest paths, PNGs, classifications, caveats.

---

## 3. Preflight hygiene

Do this **before** smoke or live closeout validation (aligns with `docs/SOP/OPERATING_RULES.md` → **Preflight hygiene before smoke or closeout**):

- **Branch / working tree:** confirm `git status` and branch match what the execution packet claims; do not assume chat or stale handoff narrative matches the repo.
- **Source-of-truth order:** read current accepted docs in this order when resolving conflicts (per steward practice):
  1. Pushed repo + current accepted docs  
  2. `docs/VISION/PPE_MASTER_MVP1.md` (master canon)  
  3. `docs/SOP/MVP1_FRONTIER.md` (live MVP1 steering)  
  4. `docs/SOP/HANDOFF.md`  
  5. `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md`  
  6. `docs/SOP/OPERATING_RULES.md`  
  7. `docs/SPRINT_1_SPEC.md` / active sprint spec named in `MVP1_FRONTIER.md`  
  8. `docs/SEMANTIC_CONTRACTS.md`  
  9. `docs/SOP/CURRENT_FRONTIER.md` — **historical only** for MVP1 execution  
  10. Older handoff/chat only when docs are silent  

- **Stale narrative:** if handoff text disagrees with repo files or frontier docs, **trust the repo/docs** and record the correction in closeout.
- **Git posture:** stay **conservative**—do not commit, push, or branch unless explicitly requested (`OPERATING_RULES.md` → **Git**).
- **Network / live data:** UI smoke depends on reachable Yahoo/Deribit (and related paths). Timeouts, missing spot, or **"Need BTC spot price for implied distribution"** can make smoke **unreliable or flaky** without implying a code bug—classify per section 6.

Operational detail for smoke commands and artifacts is also in `docs/IMPLIED_LAB_SMOKE.md`.

---

## 4. Canonical validation flow

Authoritative definitions: `docs/SOP/OPERATING_RULES.md` → **Validation tiers (closeout)**, **Closeout runtime budget / stop rule**, **RULE 4** (classification labels).

### Tier 1 — default baseline (normal low-risk slices)

For closing a typical feature slice that touches the implied lab:

1. **Unit tests:** `python -m pytest -q` (project standard; `HANDOFF.md` may also mention `unittest`—either matches the suite under `tests/` when green).
2. **Primary UI smoke (scenario A):** **`A_width_target_payoff`** via the supported one-command wrapper from repo root:  
   `python scripts/run_implied_lab_ui_smoke.py`  
   This runs **only** scenario **A**; exit code **0** means the checks required for that run passed (see manifest `pass_criteria` / scenario notes inside the manifest).
3. **Changed-region evidence:** if the slice **changed user-visible UI**, Tier 1 also requires **one** live inspection **or** screenshot review of the **actual changed region**—not a generic “app opened” check (`OPERATING_RULES.md` → Tier 1, **RULE 3**).

### Smoke C — when required vs not

- **Required** when the slice **materially** touches: disagreement **classification**; width/peak **scenario** behavior; belief/disagreement **derivation**; scenario/**harness** logic tied to those semantics—or when the **feature slice spec explicitly names C as a gate**.
- **Supporting / optional** for **presentation**, **layout/copy**, **review legibility**, and **non-classification UI linkage** unless the spec requires **C**.

**Not** a universal closeout tax for every slice (`OPERATING_RULES.md` → **Smoke C is not a universal tax**).

**Command (explicit harness, free port):**  
`python scripts/implied_lab_ui_smoke_harness.py --scenario C_directional_peak_disagreement --port <ephemeral>`  
Use a free port; avoid collision with manual Streamlit (`docs/IMPLIED_LAB_SMOKE.md`).

### Runtime budget

If smoke is slow, hangs, or stays inconclusive: **stop after one or two** attempts, **classify** (environment-sensitive / live-data-sensitive / scenario-sensitive), and document—do not infinite-retry (`OPERATING_RULES.md` → **Closeout runtime budget**).

### Runtime tracking (health signal)

When practical, record **actual wall-clock** for **`python -m pytest -q`** and **smoke A** (`python scripts/run_implied_lab_ui_smoke.py`). Compare to **recent normal** when you know it; if materially slower, classify conservatively (**WATCH** / **ESCALATE** per `FRONTIER_STEWARD_PROTOCOL.md` → **Runtime health indicators**). **Repeated** slowdown matters more than a single slow run. Note whether the pattern looks like **live data / network / Deribit sensitivity**, **local tooling timeout or capture issue**, or **possible product regression**. **Do not fail a slice on runtime alone** unless the slowdown is **severe**, **repeated**, or **coupled with errors or flakes**.

**Recent observed example (not a guaranteed benchmark):** on **2026-04-11** (checkpoint recovery), `python -m pytest -q` **passed** in **~94.88s**—one data point only; the repo does not define a formal pytest baseline here.

### Artifact location

Each run writes under:

`artifacts/ui_smoke/<run_id>/`

Typical files: `ui_smoke_manifest.json`, scenario PNG (e.g. `A_width_target_payoff.png`, `C_directional_peak_disagreement.png`), and may include `streamlit.log` depending on harness behavior. Exact layout is defined by the harness; **always** cite the **manifest path** and relevant **PNG** in closeout when smoke ran.

---

## 5. Artifact reading

### Manifest: `artifacts/ui_smoke/<run_id>/ui_smoke_manifest.json`

- Identifies **scenario(s)**, **timestamps**, **recommended commands**, and **pass criteria** for that run.
- Contains **booleans** and diagnostics (e.g. disagreement-related fields for **C**). Use these to justify **pass** vs **fail** and to explain **scenario-sensitive** outcomes (see `IMPLIED_LAB_SMOKE.md` and historical closeouts in `CURRENT_FRONTIER.md`).
- For **`MVP1_compact_verification`**, manifest includes **`trust_strip_mvp1_found`** — true when the always-visible **Trust / provenance** strip shows **MVP1 data quality** / **MVP1 primary output** (Phase 2 Slice006 disclosure). Failure here is usually a product regression in [`build_trust_strip_lines`](../../src/viz/implied_lab_provenance.py), not a screenshot crop issue.

### PNG evidence

- Filename usually matches scenario (e.g. `A_width_target_payoff.png`).
- **Caveat:** scenario **A** uses `full_page=False` and scripted scroll/expansion order; the default **A** PNG may **omit** parts of the right column (e.g. **Trust / provenance**, **Belief vs market — at a glance**, **Trade ticket**) even when the DOM checks passed (`IMPLIED_LAB_SMOKE.md` → Sprint 006/007 notes). For closeout, supplement with **checklist row / scroll / ad-hoc capture** when pixel proof of those regions matters.

### Useful closeout bundle

Minimum useful evidence when automated smoke ran:

- **Slice id / title** and **scope** (what changed).
- **Commands** run + **pass/fail** + **classification** (deterministic vs environment-sensitive vs live-data-sensitive).
- **Paths:** `artifacts/ui_smoke/<run_id>/ui_smoke_manifest.json` and the **PNG(s)** that support the claim (or explicit note that A PNG is partial and what was inspected manually).
- **Honest caveats** (data down, timeout, scenario mismatch for **C**, harness string-timing—see section 6).

---

## 6. Known caveats / failure classification

State **UNKNOWN** when the evidence does not support a stronger label.

| Symptom / condition | Suggested classification | Notes |
|---------------------|---------------------------|--------|
| Deribit/Yahoo/spot unreachable; **"Need BTC spot price…"**; missing belief UI | **Live-data-sensitive** / **operational** | Documented in `CURRENT_FRONTIER.md`, `HANDOFF.md`, `IMPLIED_LAB_SMOKE.md`. Not automatically a product regression. |
| Smoke **timeout** with no decisive DOM failure | **Environment-sensitive** | Consistent with network/Deribit flakiness; retry with preflight; see feature slice **008** closeout notes in frontier docs. |
| **C** fails manifest gates but page looks coherent; disagreement band not “Directional” under live inputs | **Scenario-sensitive** / **live-data-sensitive** | Example: feature slice **005** closeout—**C** fail on rerun while **A** green; historical green **C** artifacts may still be valid (`CURRENT_FRONTIER.md`). |
| UI copy duplicates harness wait string (**My belief vs market**) before expander mounts | **Harness / timing fragility** (not necessarily user-visible bug) | Documented in `IMPLIED_LAB_SMOKE.md` (feature slice **008**). Fix copy or future harness scope—**out of scope** for this runbook to change code. |
| Stale Python/Streamlit/browser processes; port in use | **Environment-sensitive** | Clear stuck processes; fresh port; avoid manual+smoke on same port (`OPERATING_RULES.md` → preflight). |
| Playwright/Chromium missing or broken | **Environment-sensitive** | Install per `IMPLIED_LAB_SMOKE.md` (**Required dependencies**). |
| Process **killed** or **hung** mid-scenario (`exit_code=4294967295` on Windows, subprocess exit **124**, or harness log has no `scenario=… done` line) | **Environment-sensitive** / operator timeout | Not automatically a product regression if a rerun passes. Prefer `PYTHONUNBUFFERED=1 python scripts/run_mvp1_dual_implied_lab_smoke.py` (~20–30 min wall clock on slow hosts). Per-scenario budgets: `MVP1_compact_verification` **1200s** default; override with env **`PPE_UI_SMOKE_MVP1_COMPACT_TIMEOUT_S`**. See `scripts/implied_lab_ui_smoke_harness.py` → `SCENARIO_TIMEOUT_S_BY_SCENARIO`. |

**True product regression** is more plausible when: deterministic **pytest** fails, **A** fails with data available and clean preflight, or UI **semantics** break acceptance tied to `docs/SEMANTIC_CONTRACTS.md`—still verify before asserting.

---

## 7. Closeout checklist

Aligned with `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` → **Closeout minimums** and `OPERATING_RULES.md` → **Closeout report**.

- [ ] **Slice title** and **status** (closed / not closed).
- [ ] **Scope** (what was in / out of scope).
- [ ] **Exact files changed** (paths).
- [ ] **Validation:** commands, pass/fail, **tier** (Tier 1 vs conditional **C**), labels (deterministic / environment-sensitive / live-data-sensitive).
- [ ] **Artifact paths** (`ui_smoke_manifest.json`, PNGs) when smoke ran; note if **A** PNG is incomplete for the changed region.
- [ ] **Caveats** (honest; include UNKNOWN where needed).
- [ ] **Next truthful state:** active slice (or none) and **next step** (**SELECTION** / **BUILD** / **RECOVERY** / **CLOSEOUT**).

Update **`docs/SOP/MVP1_FRONTIER.md`** and **`docs/SOP/HANDOFF.md`** when a feature slice is formally closed.

**Docs-only slices:** if no product code changed, closeout may rely on **file/consistency review** only—state that explicitly (no fabricated pytest/smoke runs).

---

## 8. Escalation / stop conditions

Stop and return **BUILD only** (or escalate to steward) when:

- **Docs conflict materially** and cannot be reconciled without a decision.
- A **docs-only** pass accidentally requires **code** or harness changes to be honest.
- **Smoke C** (or other conditional path) is **required** but **pass/fail classification is unclear** after budgeted attempts.
- Expected **artifact path** is missing and cannot be reproduced.
- **Scope drifts** beyond the agreed feature slice (e.g. refactor, new workflow layer, semantic contract rewrite).

---

## 9. Related docs

| Document | Role |
|----------|------|
| `docs/SOP/MVP1_FRONTIER.md` | Live steering, active slice, recent closeouts |
| `docs/SOP/PPE_INTEGRATED_STATUS.md` | Cross-chapter status and gates |
| `docs/SOP/HANDOFF.md` | Session minimum, checks list, next step |
| `docs/SOP/FRONTIER_STEWARD_PROTOCOL.md` | Steward model, compact vs full closeout, closeout minimums |
| `docs/SOP/OPERATING_RULES.md` | Execution steps, validation tiers, preflight, git posture, closeout budget |
| `docs/IMPLIED_LAB_SMOKE.md` | Commands, dependencies, manifest/PNG detail, scenario notes |
| `docs/SPRINT_1_SPEC.md` | One-screen implied lab product spec |
| `docs/SEMANTIC_CONTRACTS.md` | Wording and semantics constraints for UI copy and behavior |

---

## Last updated

2026-04-11 — Feature slice **009** (Implied lab operator runbook); docs-only. Same day: runtime tracking (health signal) + recent pytest example in §4.
