# Sprint 002 — Phase 2 — Market-shape intuition and area-of-interest exploration

**What this file is:** the **Sprint 002 spec** (scope + acceptance + slice map) for Phase 2.

**Execution status (ledger lives elsewhere):** closed slices, BUILD/CLOSEOUT state, and the **next pending execution step** are authoritative in `docs/SOP/CURRENT_FRONTIER.md` (and summarized in `docs/SOP/HANDOFF.md`).

**Parent charter:** `docs/SOP/PHASE_2_CHARTER.md`  
**Prior sprint (wrapped, do not reopen by default):** `docs/SOP/SPRINT_001_PHASE_2.md`  
**Phase 1 completeness:** unchanged — `docs/SOP/PHASE_1_EXIT_CRITERIA.md`

---

## 1. Title

**Market-shape intuition and area-of-interest exploration**

## 2. Purpose

Turn the lab from something users can **play with** into something they can use to **understand, follow, and mentally carry the shape of the market**: move users from “I can make it move” to “I can see what’s going on **where I care**,” using the product’s **visual language**—without smuggling advice, widening market scope, or reopening Sprint 001 by default.

**Phase 2 experience anchors (steward):**

- **First ~15 seconds:** impulse to touch controls, see shapes change, numbers move.
- **Second interaction:** natural drift into **areas of the market they care about**.
- **Deeper goal:** pleasant, quick learning; users begin thinking about the market through the tool’s visuals **even when away from it**.

## 3. Acceptance criteria (observable, user-facing)

After BUILD + agreed validation for the sprint (may span multiple slices; each slice closes against its own bullets where noted):

1. After a **short interaction**, the user can name **at least one meaningful part** of the market shape they care about (region, tension, or comparison—**descriptive**, not a trade recommendation).
2. The interface helps the user **move toward that area** (focus, orientation, or bounded navigation) **without getting lost** (clear way back; primary object stays legible).
3. Shape behavior feels **interpretable**, not merely animated: copy and affordances tie **what they did** to **what changed on the shape** (contract-aligned, plain language).
4. The user can start forming a **reusable mental model** via consistent visual grouping and vocabulary (same labels for the same ideas across interactions).
5. Added guidance stays **descriptive and trustworthy**—**not advisory** (no “you should,” no ranked plays, no fit-as-recommendation).
6. **No regression** vs Phase 1 / Sprint 001 trust spine: provenance, degraded honesty, verification discoverability, and **exploration vs recommendation** boundary remain intact.

## 4. Non-goals

- **No asset-class expansion** (BTC-first lab unchanged).
- **No recommendation engine** or implied “best trade / best preset.”
- **No ornamental polish drift** (beauty without causal UX to shape understanding).
- **No generic text-heavy onboarding** (walls of tutorial copy; tooltips-only sprawl).
- **No reopening Sprint 001** by default (no Slice 012–style continuation unless steward explicitly re-charters).
- **No semantic contract edits** in service of “story” (`docs/SEMANTIC_CONTRACTS.md` and trust semantics unchanged unless a separately approved control-plane exception exists).

## 5. Validation posture

- **Tier:** same as Phase 2 slices to date—**universal** `python -m pytest -q` and primary **`python scripts/run_implied_lab_ui_smoke.py`** on touched flows; add **scenario-directed** harness runs only when a slice touches classification / disagreement / glance paths (per `OPERATING_RULES.md` / runbook).
- **Witness:** short **guided interaction script** (human or steward demo): first touch → name one shape region they care about → reach it again without confusion; capture screenshots optional but valuable on CLOSEOUT.
- **Stop / escalate:** if interpretive copy would require **new quantitative claims** or **contract changes**, stop and split an enabling **SELECTION** slice or defer.

---

## 6. Sprint 002 map (lightweight)

### A. Selected now

- **Sprint002-Slice001** — **Shape focus & area-of-interest prompts** (chart + belief-vs-market glance band; descriptive copy + bounded affordances; interpretability without new engine semantics).

### B. Likely next

- **Sprint002-Slice002** — **Focus persistence / “return to my region”** (remember last user-named or last-interacted band within session; minimal state; no centralization program).
- **Sprint002-Slice003** — **Shape-reading consistency pass** (align labels, captions, and “What changed?” vocabulary with the shape-focus model—**copy/layout only**).

### C. Batch candidates (pick up only with explicit SELECTION; not default bundled)

- Chart **x-range affordances** (slider, double-click reset, keyboard-safe labels) **if** Slice001–002 prove insufficient for “not lost.”
- **Deeper glance digest** ties to **last interaction** (still descriptive; still non-advisory).
- **Optional** steward demo pack (one-page operator script) — docs-only **if** it reduces validation thrash.

### D. Not now / anti-goals

- Phase 3–class **commercial wrapper**, accounts, billing.
- **Strategy taxonomy / navigation** overhaul.
- **Engine / distribution** rewrites or new overlays “for drama.”
- **State centralization** as a goal (only as separately chartered enabling slice if a **deterministic blocker** appears).

---

## 7. Sprint002-Slice001 (selected)

### 7.1 Identifier

**Sprint002-Slice001**

### 7.2 Title

**Shape focus prompts + AOI scaffolding on the main surface**

### 7.3 User problem

“I can move the lab, but I don’t yet have a **stable handle** on **which part of the shape matters to me**, and I don’t know how to **look there deliberately** without losing the thread of what I’m seeing.”

### 7.4 Exact UI target (product surface)

**Bounded to:** the **primary implied-distribution chart** (Plotly main figure) **and** the adjacent **Belief vs market glance** block (digest / width vs market / main mismatch lines and immediate chart-adjacent captions in the one-screen implied lab), **plus** at most **one** compact **horizontal “shape focus” strip** (captions + **≤ 3** descriptive prompts or micro-affordances) **directly above or beside** that chart+glance column—**no** secondary-panel expansion program.

**Primary files expected (for BUILD agent planning only):** `src/viz/app.py` (and only closely related viz helpers if unavoidable); **no** contract edits.

### 7.5 Non-goals (slice)

- No **new** overlay series, metrics, or payoff modes.
- No **preset** count explosion; no new “strategy families” navigation.
- No **advisory** framing (“best,” “should,” “favor long tails,” etc.).
- No **semantic** changes to disagreement formulas—**interpretation and orientation only**.

### 7.6 Acceptance criteria (slice)

1. After **one** meaningful interaction (preset, belief toggle, or obvious primary control), the UI offers a **short, descriptive prompt** that helps the user **name a region of interest** on the chart (e.g., tails vs center vs strike-adjacent band—wording must match existing semantics).
2. At least **one** affordance **moves the user’s attention** to that region **without hiding** trust/provenance or the main chart (e.g., chart zoom/x-range preset, scroll-to-glance anchor, or **explicit** “reset view”—pick **one** minimal pattern).
3. **“What changed?”** (or equivalent last-action readout) **still reads true** for the interaction paths it already covers; no contradictions with new copy.
4. Copy passes a **non-advisory lint** intent: **descriptive** (“shows,” “compares,” “highlights”) not **prescriptive**.
5. **pytest** + **primary implied-lab UI smoke** remain **PASS** on the BUILD branch.

### 7.7 Validation posture (slice)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** if glance/classification strings or disagreement digest wiring is touched, add the smallest relevant **harness** scenario per runbook for touched paths.
- **Closeout:** before/after screenshot of chart+glance band optional; must list **files changed** and any **deferred** map items explicitly.

---

## Last updated

2026-04-18 — **CONTROL-PLANE SELECTION** (Frontier Steward 2.2): Sprint 002 canon + map + **Sprint002-Slice001** selected; next execution step **BUILD** (see `docs/SOP/CURRENT_FRONTIER.md`). **No product BUILD** in this pass.
