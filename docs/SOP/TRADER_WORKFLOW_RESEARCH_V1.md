# Trader workflow research v1

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
> **Status (pivot `trader-workflow-integration-v1`):** **Learning loop workstream** — part of milestone [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md).  
> Run self-serve and interview sessions; log **strong+** signal in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md); triage to backlog. **Not** a relay blocker.  
> Scope authority: [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md).
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

**Purpose:** Operational guide for **workflow research, workflow import, and design ingestion** — optional signal logging while usable demo BUILD is in flight. **Not** a BUILD gate and **not** friends-first cohort gating.

**Company context:** [`MSOS_COMPANY_VISION_V1.md`](../VISION/MSOS/MSOS_COMPANY_VISION_V1.md) · **Prerequisite gate:** [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) (primary focus shifts here when gate **PASSED**; light conversations allowed earlier per [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md))

**Log destination:** [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) · **Session timing:** [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md)

---

## What this is (and is not)

| This is | This is not |
|---------|-------------|
| Learning exact **workflow, language, trust layer, disagreement type, decision moment** | Proving “traders care about options” or “fintech tools matter” |
| Importing proven trader processes into one coherent decision environment | Copying competitor feature lists without understanding the job |
| Ingesting observations into **shippable product changes** | Vanity metrics or generic PMF theater |
| High-signal observation of emerging serious traders and small teams | Complete-beginner education research or institutional procurement research |
| Studying context handoffs between content, tools, calculations, venues, and records | Broad online sentiment scraping |

**Assumption (already held):** Traders care about market disagreement, options-implied information, and useful tools. We are learning **how MSOS/PPE fits and compresses their real decision loop**.

---

## Target participant

Prioritize:

> **An emerging serious trader or very small trading team that understands basic markets but cannot yet assemble institutional-quality research, strategy construction, risk analysis, and workflow.**

Useful adjacent participants include experienced retail traders, independent analysts, trading creators, and operators at small finance firms. Record participant type explicitly; do not average incompatible customer segments together.

---

## Workflow import frame

Capture the complete observed process:

> **Trigger → Orientation → Hypothesis → Validation → Instrument selection → Position construction → Execution → Monitoring → Review**

For each stage, record:

- the user’s goal and question;
- data, content, tool, or event that triggered the step;
- applications and screens used;
- calculations performed;
- information copied manually between tools;
- decisions, assumptions, and uncertainty;
- what was saved, where it was saved, and what was lost;
- where the user paused, guessed, abandoned, or sought help;
- what made the user trust or distrust the result.

**Research apps as workflow evidence, not as feature shopping lists.** The key unit is the context handoff: what the user had to remember, translate, re-enter, or reconstruct when moving between tools.

---

## Research methods

Use a mix of:

### 1. Recent-decision reconstruction

Ask the participant to reconstruct one real recent trade or rejected trade from trigger through review. Prefer concrete artifacts over generalized claims.

### 2. Screen-share observation

Have the participant perform a real or representative decision while sharing their screen. Observe sequence, tool switching, copy/paste, uncertainty, and workarounds. Do not lead with a product feature tour.

### 3. Workflow archaeology

Collect or inspect, with permission:

- spreadsheets and calculators;
- charts and screenshots;
- watchlists and alerts;
- trading plans and checklists;
- journals and post-trade notes;
- research documents;
- public videos, posts, or Discord-style analyses;
- broker order tickets and paper-trade records.

### 4. Product witness

Let the participant use MSOS/PPE with minimal guidance. Record where the product successfully replaces a step, creates a new handoff, or requires narration.

---

## Research questions (ask every session)

1. **What started this decision?** What event, content, market move, alert, or recurring routine created attention?
2. **What did the trader need to understand before holding a view?** What was happening, what had happened, and what did the market appear to price?
3. **What kind of disagreement is this?** (directional, vol, tail, timing, skew, structure, liquidity/risk-premium, hedge/constraint — see [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md))
4. **When does the trader notice it?** (pre-market, during session, after move, rolling expiry)
5. **What data/tool/content triggers or validates the thought?**
6. **Which tools do they open, in what order, and what must they manually carry between them?**
7. **How do they currently express it?** (structure, size, venue, notes)
8. **What alternatives do they compare, including waiting or not trading?**
9. **What would make them trust or distrust the tool or calculation?**
10. **What do they check before acting?**
11. **What do they monitor after entry?**
12. **What makes them abandon or revise the thesis?**
13. **What gets recorded, and can they later recover what they actually believed at the time?**
14. **Usage mode:** pre-trade, post-trade, research, journal, alert, or expression planner?
15. **Interaction mode:** why did they open MSOS? (disagreement, expression search, hedging, scenario planning, timing, monitoring, learning/review — see [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md))

Tag answers in validation log rows. Prefer ordinary customer language in direct notes, while mapping observations to internal `interaction_mode`, `disagreement_type`, and workflow-stage tags.

---

## Session record minimum

Every useful session record should contain:

- participant type and sophistication;
- real decision or workflow observed;
- workflow stage sequence;
- tools and application switches;
- copied/re-entered context;
- calculations or interpretation bottlenecks;
- trust and provenance requirements;
- strongest product opportunity;
- signal rank;
- evidence link or artifact reference;
- whether the observation strengthens the current wedge, a deferred phase, or neither.

Do not log only a feature request. Translate it into the underlying job, evidence, and current workaround.

---

## Signal ranking (tag every observation)

| Rank | Signal | Example |
|------|--------|---------|
| **Weak** | What traders say they like online | Twitter polls, generic “cool chart” |
| **Medium** | Content/tools they **repeatedly consume** | Same vendor screen daily, bookmarked calc |
| **Strong** | Their **current decision workflow** | Screen-share or artifact-backed walkthrough of last trade thesis |
| **Very strong** | **Observed use** of our product | Unprompted return, shared screen using MSOS/PPE |
| **Strongest** | **Return, referral, payment** | Comes back without ping, introduces peer, offers to pay |

When logging in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md), include field or note: `signal: weak|medium|strong|very_strong|strongest`.

**Build rule:** Prefer changes backed by **strong+** signals. **Weak** alone does not justify platform expansion.

---

## Ingestion path (learning → shippable)

1. Log the observed decision with signal rank, participant type, workflow stages, tools, handoffs, and disagreement type.
2. Extract the underlying job and context handoff; do not preserve the source tool’s interface by default.
3. Steward triage: does this map to an MCD gap, embed UX, workflow copy, PPE legibility, shared decision object, or validated next-stage capability?
4. Apply the company-vision hierarchy: **integrate → clone and simplify → build deeply → avoid/defer**.
5. Apply the platform-bloat gate: a broad capability needs at least three qualifying reasons from [`MSOS_COMPANY_VISION_V1.md`](../VISION/MSOS/MSOS_COMPANY_VISION_V1.md).
6. If shippable → backlog row with `focusPlaybookTier` and link to the observation.
7. If not shippable → note in validation log; do not auto-widen scope.

Autobuilder/control-plane work that ingests workflow learning must cite the observation per [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md).

---

## Allowed before MCD pass

**Light** workflow research is allowed while factory + MCD chapters run when it is low-interruption and does not block BUILD throughput. This may include occasional trader conversations, public workflow teardowns, and artifact collection.

Before MCD pass:

- do not launch a separate research product;
- do not convert findings directly into broad platform construction;
- do not pull forward live execution, new asset classes, certification, or institutional features;
- record promising workflows for post-MCD triage.

---

## Session script (compact)

Full script: [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) § Session script.

After demo, spend **≥50% of session time** on the participant’s real workflow — not feature tour. Ask for a recent concrete decision, follow the artifacts, and identify the context handoffs.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v1 — workflow research ops, signal ranking, ingestion path |
| 2026-06-20 | Research Q10 + tagging — interaction modes ontology |
| 2026-07-13 | Harden target participant, workflow-import frame, observation methods, session record, context-handoff analysis, and integrate/clone/build/defer ingestion rules |
