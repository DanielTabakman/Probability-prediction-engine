# MSOS Market Interaction Modes v0.1

**Status:** Vision / ontology — **not current build scope**  
**As-of:** 2026-06-20  
**Purpose:** Name the broader MSOS **interaction grammar** so architecture, copy, and research stay aligned before any mode is chartered for BUILD.

**Grounding rule:** Modes inform language and data-model boundaries now. Modes **2–7** stay **Planned** until trader workflow research validates entry points ([`TRADER_WORKFLOW_RESEARCH_V1.md`](../../SOP/TRADER_WORKFLOW_RESEARCH_V1.md)). Do not add queue rows or app surfaces for ungrounded modes.

**Related (do not duplicate):**

| Doc | Role |
|-----|------|
| [`storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md`](storyboard-v0.6/semantics/MSOS_Product_Semantics_State_Model_v0.1.md) | Entity hierarchy + lifecycle states |
| [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](../../SOP/MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) | Disagreement **types** (directional, vol, tail, …) |
| [`MSOS_WEBSITE_PROGRAM.md`](../../SOP/MSOS_WEBSITE_PROGRAM.md) | P5–P8 BUILD waterfall when SELECTION'd |
| [`SEMANTIC_CONTRACTS.md`](../../SEMANTIC_CONTRACTS.md) | PPE math / UX meaning contracts |

---

## Future Market Interaction Modes — Not Current Build Scope

These modes define the broader MSOS ontology. They should inform architecture and language, but should **not** be implemented until grounded by trader workflow research.

| # | Mode | User intent (short) | Build posture |
|---|------|---------------------|---------------|
| 1 | **Disagreement** | User sees something the market may not. | **CURRENT WEDGE** — PPE / Strategy Lab |
| 2 | **Expression Search** | User has a thesis and needs the right payoff structure. | **Planned** — storyboard P6; charter when research + SELECTION |
| 3 | **Hedging** | User has exposure and wants to reshape downside/upside. | **Planned** — no dedicated surface yet |
| 4 | **Scenario Planning** | User has multiple possible worlds and wants to map them. | **Planned** — no dedicated surface yet |
| 5 | **Timing** | User likes the thesis but needs a better entry/structure moment. | **Planned** — partial overlap with disagreement type `timing` |
| 6 | **Monitoring** | User has a live thesis and needs to know if it is decaying. | **Planned** — storyboard P7; monitor/history chapters deferred |
| 7 | **Learning / Review** | User wants to understand what they systematically misprice. | **Planned** — calibration loop; P7–P8 when SELECTION'd |

---

## Mode definitions

### 1. Disagreement — CURRENT WEDGE

**Intent:** Compare what the market **prices** (implied / risk-neutral distribution) with what the user **believes**, and surface the structured gap in plain language.

**Primary home today:** PPE implied lab inside Strategy Lab; MSOS embed shell when MCD-complete.

**Product rules:** Disagreement is **descriptive**, not prescriptive. No buy/sell voice. See [`SEMANTIC_CONTRACTS.md`](../../SEMANTIC_CONTRACTS.md) and backplane disagreement types for *what kind* of gap (directional, vol, tail, timing, skew, structure, liquidity/risk-premium, hedge/constraint).

### 2. Expression Search

**Intent:** Given a **confirmed thesis**, find payoff structures or strategy families that **fit** under stated constraints — not a guaranteed optimal trade.

**Language:** “Suggested expression,” “optimized expression plan,” assumptions visible. Never “recommended trade.”

**Future touchpoints:** Expression planning (storyboard `05_execution`, program P6), thesis → expression lifecycle in MSOS workflow store.

### 3. Hedging

**Intent:** User already holds risk (spot, perps, options, portfolio) and wants to **reshape** payoff — reduce downside, cap upside, or neutralize a factor — without MSOS pretending to be portfolio advice.

**Distinction:** Overlaps backplane disagreement type **hedge/constraint** and mode **Expression Search**, but entry is **exposure-first**, not thesis-first.

**Architecture note:** Requires explicit exposure inputs and instrument-compatibility rules (same as execution rails in semantics doc). Stay **Simulation only** until SELECTION'd.

### 4. Scenario Planning

**Intent:** User holds **multiple plausible worlds** (not one point belief) and wants to compare how structures behave across them — branches, weights, or discrete scenarios.

**Distinction:** Not the same as a single belief band in PPE today. Scenario objects may eventually sit **above** a single thesis in the workflow model.

**Risk:** Easy to over-build branching UI before traders validate the need. Research tag heavily before any BUILD.

### 5. Timing

**Intent:** User agrees directionally (or on vol/tail) but cares about **when** — entry window, expiry choice, roll timing, event proximity.

**Distinction:** **Interaction mode** (why they opened the tool) vs backplane **disagreement type** `timing` (what kind of gap). A session can be Timing mode with a directional disagreement type.

**Partial coverage today:** Expiry and structure choice in PPE; no dedicated “timing planner” surface.

### 6. Monitoring

**Intent:** User has a **live** thesis and/or saved expression and needs decay signals — data freshness, thesis invalidation, expression risk drift, trust state.

**Future touchpoints:** Monitoring plan entity, Command Center alerts, storyboard `06_monitor` / `08_updated_command`, program P7.

**Rule:** Do not ship undefined “thesis health” metrics. Every monitor signal must trace to a named check and source.

### 7. Learning / Review

**Intent:** User wants **calibration** — what they systematically mispriced, which disagreement types they overweight, how saved/simulated/executed theses resolved.

**Future touchpoints:** History (`07_history`), conclusion / learn loop (`09_conclusion`), calibration memory in semantics model, program P7–P8.

**Distinction:** Retrospective and aggregate; not the same as in-session Disagreement exploration.

---

## Distinctions (do not conflate)

| Concept | Question it answers | Example |
|---------|---------------------|---------|
| **Interaction mode** | Why did the user come to MSOS **now**? | “I'm hedging existing exposure.” |
| **Disagreement type** | What **kind** of gap vs market? | directional, vol, tail, timing, … |
| **Lifecycle state** | Where is this thesis in its **journey**? | Draft → Confirmed → Monitoring → Reviewed |
| **Usage moment** | When in their **day**? | pre-trade, post-trade, journal (research log field) |
| **Lens** | Which **market surface**? | BTC options (Live), prediction markets (Planned) |

One session may tag **multiple** dimensions: e.g. `interaction_mode=disagreement`, `disagreement_type=vol`, `lifecycle=exploring`, `usage_moment=pre-trade`.

---

## Mapping to storyboard / program (when built)

| Mode | Storyboard screen | MSOS program phase |
|------|-------------------|-------------------|
| Disagreement | `03_ppe_lab` | P4 (+ embed shell) |
| Expression Search | `05_execution` | P6 |
| Hedging | (no dedicated screen yet) | — |
| Scenario Planning | (no dedicated screen yet) | — |
| Timing | partial in `03_ppe_lab` | P4 |
| Monitoring | `06_monitor`, `08_updated_command` | P7 |
| Learning / Review | `07_history`, `09_conclusion` | P7–P8 |

Chartered chapters for P5–P8 remain in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](../../SOP/MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) — **deferred**, not deleted.

---

## Research tagging

When logging sessions in [`VALIDATION_REALITY_CHECKS.md`](../../SOP/VALIDATION_REALITY_CHECKS.md), include where possible:

```
interaction_mode: disagreement | expression_search | hedging | scenario_planning | timing | monitoring | learning_review
disagreement_type: <from backplane table, when relevant>
usage_moment: pre-trade | post-trade | research | journal | alert | expression_planner
signal: weak | medium | strong | very_strong | strongest
```

**Build rule:** Strong+ signal for a **Planned** mode may justify copy, navigation hints, or data-model **hooks** — not full mode implementation — unless steward **SELECTION** charters a chapter.

---

## Agent / BUILD rules

1. **Do not** implement UI, APIs, or persistence for modes 2–7 without SELECTION and research grounding.
2. **Do** use mode names in vision docs, UX copy drafts, and workflow research notes.
3. **Do** keep thesis, expression, execution, monitoring, and review as **separate** states (semantics model) even when a mode spans several.
4. **Do** label unshipped mode entry points **Planned** or **Soon** — never imply live monitoring, scenario branching, or hedge optimization.
5. **Do not** add rows to [`PHASE_CHAPTER_BACKLOG.json`](../../SOP/PHASE_CHAPTER_BACKLOG.json) from this doc alone.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v0.1 — seven interaction modes; distinctions; research tags; not build scope |
