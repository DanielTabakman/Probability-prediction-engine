# Sprint 002 — Phase 2 — Market-shape intuition and area-of-interest exploration

**What this file is:** the **Sprint 002 spec** (scope + acceptance + slice map) for Phase 2.

**Execution status (ledger lives elsewhere):** closed slices, BUILD/CLOSEOUT state, and the **next pending execution step** are authoritative in `docs/SOP/CURRENT_FRONTIER.md` (and summarized in `docs/SOP/HANDOFF.md`). **Sprint002-Slice004** is **closed/shipped** — **§10** (product **`6be6d7c5401c489bb702fb1ea40b4bee93ad8907`**). **Sprint 002 — SELECTION (2026-04-18, Frontier Steward 2.2):** **outcome A** — **ready to wrap / primary loop complete** (**§11**); **next** = **Sprint 002 wrap closeout** / **next sprint or phase decision** (steward).

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

- **No slice in-flight under BUILD** (post–**Sprint002-Slice004** **CLOSEOUT**, 2026-04-18). **Sprint 002 SELECTION — outcome A:** **no further Sprint 002 BUILD slice**; sprint is **ready to wrap** (**§11**). **Latest shipped:** **Sprint002-Slice004** — **local region story / chart-adjacent meaning cue** (product **`6be6d7c5401c489bb702fb1ea40b4bee93ad8907`**); **Sprint002-Slice003** — vocabulary / **shape window** alignment (product **`6e5f5635acb9371af17ce7d8621f70ceb0072215`**); **Sprint002-Slice002** — focus persistence / return to last chart view (product **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`**); **Sprint002-Slice001** — shape focus & AOI scaffolding (product **`ff40b48deb7acf4b2d897a09287e69ed7148abd9`**).

### B. Deferred batch (after Slice004 CLOSEOUT unless steward re-orders)

- **§6.C** batch candidates — **not** chartered for Sprint 002 by **SELECTION outcome A** (2026-04-18); remain **deferred map only** unless a **future** sprint/phase **SELECTION** revives them with explicit justification. **Coherence / demo witness** vs **§3** + **`docs/SOP/PHASE_2_CHARTER.md` §9** may inform **wrap closeout** but does **not** imply another Sprint 002 BUILD slice.

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

## 7. Sprint002-Slice001 (closed / shipped)

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

### 7.8 Control-plane supplement: execution / CLOSEOUT status

**2026-04-18 (Frontier Steward 2.2 — CONTROL-PLANE CLOSEOUT):** **Sprint002-Slice001** is **closed/shipped** on accepted baseline **`recovery/frontier-steward-v2_1-baseline`** at product commit **`ff40b48deb7acf4b2d897a09287e69ed7148abd9`**. **Product delta:** `src/viz/app.py` only. **Evidence:** `python -m pytest -q` → **51** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — `artifacts/ui_smoke/20260418_160804/ui_smoke_manifest.json`, screenshot `artifacts/ui_smoke/20260418_160804/A_width_target_payoff.png`. Authoritative ledger: `docs/SOP/CURRENT_FRONTIER.md`. **Sprint002-Slice002** history: **§8**.

---

## 8. Sprint002-Slice002 (closed / shipped)

### 8.1 Identifier

**Sprint002-Slice002**

### 8.2 Title

**Focus persistence / “return to my region” (session-scoped)**

### 8.3 User problem

“After I **narrow** the chart to the band I care about (or follow Slice001’s **where-to-look** cue), a **reset**, **other control**, or **natural exploration** **throws away** that framing. I want a **bounded way back** to **my last meaningful chart window** **without** hunting the same controls again or **losing** trust/provenance context.”

### 8.4 Exact UI target (product surface)

**Bounded to:** the **primary implied-distribution chart** (Plotly main figure) **and** the **same chart-adjacent / shape-focus surface** established in **Sprint002-Slice001** (compact shape-focus strip + x-axis window behavior **already shipped** — extend **only** with **session-local** persistence and **one** explicit **return/restore** affordance **or** one **equivalent** minimal pattern (e.g. single **“Return to last chart view”** control placed in the existing strip / chart chrome; **no** new secondary panels).

**State rule:** **`st.session_state` (Streamlit) only** — remember the **last user-established meaningful x-range** (or equivalent **single** bounded window token the BUILD agent derives from existing Slice001 mechanics); **no** cross-session storage, **no** DB, **no** state-centralization program beyond what Slice001 already uses.

**Primary files expected (BUILD planning only):** `src/viz/app.py` (and only closely related viz helpers if unavoidable); **no** `docs/SEMANTIC_CONTRACTS.md` edits.

### 8.5 Non-goals (slice)

- **No** new overlay series, payoff modes, or **preset** explosion.
- **No** cross-browser / cross-tab persistence; **no** URL deep-link state program.
- **No** vocabulary-wide relabel of **“What changed?”** or glance digest (**defer** to **Sprint002-Slice003**).
- **No** advisory framing; **no** semantic changes to disagreement / belief math.
- **No** chart **x-range affordance** sprawl beyond **§6.C** (sliders, keyboard program, etc.) — this slice is **return-to-view**, not **more controls**.

### 8.6 Acceptance criteria (slice)

1. After the user establishes a **non-default** chart x-window (via existing Slice001 mechanics), **later** in the **same session** they can **restore that window** using the **new explicit affordance** (or the single equivalent pattern named in CLOSEOUT) **without** manual re-entry of identical bounds.
2. The affordance is **visible but non-dominant**; it does **not** hide provenance, verification entry, or the **main chart**.
3. **“What changed?”** / last-action readouts **remain contract-true** on paths they already cover; **no contradictions** introduced by persistence copy.
4. Copy remains **descriptive** (orientation), not **prescriptive** (advice).
5. **`python -m pytest -q`** and **`python scripts/run_implied_lab_ui_smoke.py`** → **PASS** on the BUILD branch.

### 8.7 Validation posture (slice)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** if glance / classification / disagreement strings are touched beyond unavoidable labels, add the **smallest** harness scenario per runbook for touched paths.
- **Witness (human/steward):** narrow chart → change something that alters view → **return** → confirm same band; optional screenshot pair on CLOSEOUT.

### 8.8 Control-plane supplement: execution / CLOSEOUT status

**2026-04-18 (Frontier Steward 2.2 — CONTROL-PLANE CLOSEOUT):** **Sprint002-Slice002** is **closed/shipped** on accepted baseline **`recovery/frontier-steward-v2_1-baseline`** at product commit **`bd12b7cc09bee0399a755e5dd322f4e63a04fe0a`**. **Product delta:** `src/viz/app.py` only (session bookmark + **Return to last chart view**). **Evidence:** `python -m pytest -q` → **51** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — `artifacts/ui_smoke/20260418_163043/ui_smoke_manifest.json`, screenshot `artifacts/ui_smoke/20260418_163043/A_width_target_payoff.png`. Authoritative ledger: `docs/SOP/CURRENT_FRONTIER.md`. **Superseded (steering):** **Sprint002-Slice003** **closed/shipped** at **`6e5f563`** (**§9**); **next** = **SELECTION** (see **`docs/SOP/CURRENT_FRONTIER.md`**).

---

## 9. Sprint002-Slice003 (closed / shipped)

### 9.1 Identifier

**Sprint002-Slice003**

### 9.2 Title

**Vocabulary consistency / local region meaning alignment**

### 9.3 User problem

“I can **find** a band on the chart (Slice001) and **come back** to it (Slice002), but the **words** on the screen don’t always **name the same region the same way**—shape-focus strip, chart-adjacent captions, glance lines, and **‘What changed?’** can feel like **different dialects**. I want a **single, visual-language-consistent read** so I can **think about the market through the tool’s shape language** without guessing which label is ‘the real one.’”

### 9.4 Exact UI target (product surface)

**Bounded to:** the **primary implied-distribution chart** (Plotly main figure) **and** the **Sprint002-Slice001** **shape-focus strip** (prompts / AOI copy), **plus** **chart-adjacent** and **glance-adjacent** strings that **refer to the same x-window / local-region concepts** (e.g. narrowed band, last chart view, where-to-look cues), **and** the **last-action / “What changed?”** readout **only where** it touches **chart-window / shape-focus / AOI vocabulary**—so one interaction does not produce **contradictory region naming** across those surfaces.

**Primary files expected (BUILD planning only):** `src/viz/app.py` (and only closely related viz helpers if unavoidable); **no** `docs/SEMANTIC_CONTRACTS.md` edits.

### 9.5 Non-goals (slice)

- **No** recommendation logic, ranked plays, or “best” framing.
- **No** new overlay series, payoff modes, or **preset** explosion.
- **No** major semantic **contract** rewrite or quantitative **new claims**—if copy would require them, **stop** and split a **SELECTION** enabling slice or defer.
- **No** **§6.C** program in this slice (sliders, keyboard x-range affordances, broad glance/memory systems, cross-session persistence).
- **No** advisory tone; **no** changes to disagreement / belief **math**—**interpretation and naming only** where strings are adjusted.

### 9.6 Acceptance criteria (slice)

1. **Vocabulary alignment:** terms for the **user’s local chart region** / **shape-focus object** read **consistently** across the **shape-focus strip**, **chart-adjacent** copy tied to x-window behavior, and **last-action / “What changed?”** strings **on paths already covered**, where those strings describe the **same** region/window concept (same idea → same **family** of labels; no accidental synonym sprawl).
2. **Contract-true:** adjusted wording stays aligned with **`docs/SEMANTIC_CONTRACTS.md`** and existing numeric semantics (**descriptive**, not new quantitative assertions).
3. **Non-advisory:** copy remains **orientation / description** (“shows,” “highlights,” “returns to”)—not **prescription** (“you should,” “favor,” “best”).
4. **Trust spine intact:** provenance, verification entry, degraded honesty, and **exploration vs recommendation** boundary remain **as visible and true** as on the Slice002-closeout baseline.
5. **`python -m pytest -q`** and **`python scripts/run_implied_lab_ui_smoke.py`** → **PASS** on the BUILD branch.

### 9.7 Validation posture (slice)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** if glance / classification / disagreement **wiring or strings** beyond **pure** chart-chrome relabel are touched, add the **smallest** harness scenario per **`IMPLIED_LAB_OPERATOR_RUNBOOK.md`** / **`OPERATING_RULES.md`** for touched paths.
- **Witness (human/steward):** narrow chart → use shape-focus cue → trigger a covered **“What changed?”** path → confirm **one coherent local-region story** in plain English across strip + chart + readout (optional screenshot on **CLOSEOUT**).

### 9.8 Control-plane supplement: execution / CLOSEOUT status

**2026-04-18 (Frontier Steward 2.2 — CONTROL-PLANE CLOSEOUT):** **Sprint002-Slice003** is **closed/shipped** on accepted baseline **`recovery/frontier-steward-v2_1-baseline`** at product commit **`6e5f5635acb9371af17ce7d8621f70ceb0072215`**. **Product delta:** `src/viz/app.py`, `src/viz/implied_lab_last_action.py`, `tests/test_implied_lab_last_action.py`. **Evidence:** `python -m pytest -q` → **52** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — `artifacts/ui_smoke/20260418_220503/ui_smoke_manifest.json`, screenshot `artifacts/ui_smoke/20260418_220503/A_width_target_payoff.png`. Authoritative ledger: **`docs/SOP/CURRENT_FRONTIER.md`**. **Superseded (steering):** **Sprint002-Slice004** **closed/shipped** at **`6be6d7c`** (**§10**); **next** = **SELECTION** (see **`docs/SOP/CURRENT_FRONTIER.md`**).

---

## 10. Sprint002-Slice004 (closed / shipped)

### 10.1 Identifier

**Sprint002-Slice004**

### 10.2 Title

**Local region story / chart-adjacent meaning cue**

### 10.3 User problem

“I can **find** a region (Slice001), **return** to it (Slice002), and **read one vocabulary** for it across surfaces (Slice003)—but when I **glance** at the chart and its neighbors, I still lack **one compact, coherent, non-advisory sentence** for **what is going on in that region right now** (what the shape is **showing** there), so the band feels **labeled** but not yet **situated** in my head.”

### 10.4 Exact UI target (product surface)

**Bounded to:** the **primary implied-distribution chart** (Plotly main figure) **and** the **Sprint002-Slice001** **shape-focus strip**, **plus** **chart-adjacent** and **glance-adjacent** surfaces already tied to **local chart window / shape window** meaning (captions, compact hints, lead lines)—deliver **one** **short** (roughly **one to three sentences** or **one** tight bullet block), **always visible or clearly glance-adjacent** when a **non–full-range** window is active, and **explicitly neutral / de-emphasized** when the view is **full range** (no fake specificity).

**Composition rule:** **reuse** existing payload fields, glance strings, last-action tokens, and shape-window state **already on the baseline** after Slice003—**no new quantitative metrics** or engine outputs **if** the story can be assembled from those fields; if a BUILD agent discovers a **hard dependency** on a **new** computed field, **stop** and return to **SELECTION** / steward for an enabling slice (do not silently widen).

**Primary files expected (BUILD planning only):** `src/viz/app.py` and closely related viz/last-action helpers **if unavoidable** (e.g. `src/viz/implied_lab_last_action.py`); **no** `docs/SEMANTIC_CONTRACTS.md` edits.

### 10.5 Non-goals (slice)

- **No** recommendation logic, ranked plays, “best,” or “you should.”
- **No** major **semantic contract** rewrite or **new** disagreement/belief **math** claims.
- **No** new overlay series, payoff modes, or **preset** explosion.
- **No** **§6.C** program: sliders / keyboard x-range sprawl, **broad** glance↔memory↔comparison subsystem, cross-session persistence, or URL deep-link state.
- **No** ornamental copy walls; keep the read **skimmable** and **testable**.

### 10.6 Acceptance criteria (slice)

1. When the user has a **meaningful local chart window** (non-default x-window consistent with Slice001–002 behavior), the UI presents **one coherent descriptive “local region story”** tying **what the window is showing** to **existing** shape/glance vocabulary—**without** contradicting **“What changed?”** on covered paths.
2. When the view is **full range** (or no local window applies), the UI **does not invent** a false local story—**neutral / omitted / clearly global** posture only.
3. Copy stays **descriptive and contract-aligned** (orientation: “shows,” “highlights,” “in this window”)—**not advisory**.
4. **Trust spine intact:** provenance, verification entry, degraded honesty, and **exploration vs recommendation** boundary remain **as visible and true** as on the Slice003-closeout baseline.
5. **`python -m pytest -q`** and **`python scripts/run_implied_lab_ui_smoke.py`** → **PASS** on the BUILD branch.

### 10.7 Validation posture (slice)

- **Required:** `python -m pytest -q`; `python scripts/run_implied_lab_ui_smoke.py`.
- **Conditional:** if glance / classification / disagreement **wiring** beyond string assembly is touched, add the **smallest** harness scenario per **`IMPLIED_LAB_OPERATOR_RUNBOOK.md`** / **`OPERATING_RULES.md`** for touched paths.
- **Witness (human/steward):** narrow chart → read the **local region story** in one glance → trigger a covered **“What changed?”** path → confirm **no contradiction** and **non-advisory** tone (optional screenshot on **CLOSEOUT**).

### 10.8 Control-plane supplement: execution / CLOSEOUT status

**2026-04-18 (Frontier Steward 2.2 — CONTROL-PLANE CLOSEOUT):** **Sprint002-Slice004** is **closed/shipped** on accepted baseline **`recovery/frontier-steward-v2_1-baseline`** at product commit **`6be6d7c5401c489bb702fb1ea40b4bee93ad8907`**. **Product delta:** `src/viz/app.py`, `src/viz/implied_lab_last_action.py`, `tests/test_implied_lab_last_action.py`. **Evidence:** `python -m pytest -q` → **55** passed; `python scripts/run_implied_lab_ui_smoke.py` → **PASS** — `artifacts/ui_smoke/20260418_222621/ui_smoke_manifest.json`, screenshot `artifacts/ui_smoke/20260418_222621/A_width_target_payoff.png`. Authoritative ledger: **`docs/SOP/CURRENT_FRONTIER.md`**. **Next execution step (steering):** **Sprint 002 wrap closeout** / **next sprint or phase decision** (see **`docs/SOP/CURRENT_FRONTIER.md`**).

---

## 11. Sprint 002 wrap posture (SELECTION — outcome A, 2026-04-18)

**Control-plane SELECTION (Frontier Steward 2.2):** **Outcome A** — **Sprint 002 is ready to wrap**; **primary interaction spine for this sprint is complete** on the shipped sequence **Sprint002-Slice001 → Slice004** (**find a region → return → consistent naming → compact local-region story**).

**Reasoning (summary):** Sprint **§3** acceptance is **substantially met** by the integrated spine plus Phase 2 / Sprint 001 trust and meaning infrastructure already on baseline. Remaining **§6.C** items (**x-range affordance sprawl**, **deeper glance↔last-interaction ties**, optional docs-only demo pack) are **explicitly optional** in this sprint map and would mostly add **controls, copy surface, or narration** without a **new fuzzy→legible category**—i.e. **polish drift / low-value expansion** relative to the closed narrative, not a **deterministic blocker**.

**Next pending execution step:** **Sprint 002 wrap closeout** / **next sprint or phase decision** (steward). **No** chartered **Sprint002-Slice005** under this pass.

---

## Last updated

2026-04-18 — **CONTROL-PLANE SELECTION** (Frontier Steward 2.2): **Sprint 002** **ready to wrap** (**outcome A**); **next** = **wrap closeout** / **next sprint or phase decision**. Prior same day: **CLOSEOUT** Slice004 (`6be6d7c`); **SELECTION** Slice004 boundary; **CLOSEOUT** Slice003 (`6e5f563`); **CLOSEOUT** Slice002 (`bd12b7c`); **CLOSEOUT** Slice001.
