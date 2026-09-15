# Autobuilder leverage scorecard v1

**Plane:** CONTROL-PLANE  
**Status:** Active measurement contract  
**Owner:** Founder + Autobuilder operator  
**Purpose:** Measure whether the Autobuilder increases startup iteration capacity rather than merely generating activity.

**Related:** [`AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md`](AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md) · [`AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md`](AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md) · [`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)

---

## North-star measure

> **Validated organizational output per unit of founder attention and compute cost.**

This is a directional composite, not a single number to optimize blindly.

The scorecard exists to answer:

1. Is the startup closing more useful iterations because the Autobuilder exists?
2. Is Daniel's technical supervision per useful closure declining or being used on higher-value judgment?
3. Are compute and model costs economically legible?
4. Is the system learning from repeated failures and reducing rescue/rework?
5. Is the factory widening the range of credible experiments the startup can perform?

---

## Unit of output: validated closure

A work item counts as a **validated closure** only when all applicable conditions are met:

- the intended output exists;
- acceptance criteria are satisfied;
- relevant tests, runtime checks, visual review, or human evidence are recorded;
- the change is merged or otherwise stored in its canonical destination;
- steering or completion state reflects reality;
- no known blocking defect makes the output unusable for its intended learning or operation.

Examples include:

- a merged and tested product slice;
- a deployed interface iteration with screenshots and founder review;
- a completed presentation or website version that can be used externally;
- a repaired factory capability proven by a successful subsequent run;
- a research artifact that changes a product decision and is recorded in canon.

The following do **not** count by themselves:

- agent turns;
- generated code volume;
- commits without acceptance evidence;
- documents that do not alter execution or understanding;
- opened branches or PRs;
- worker concurrency;
- retries;
- plans without shipped or decision-relevant output.

---

## Core scorecard

| Metric | Definition | Why it matters | Cadence |
|---|---|---|---|
| **Validated closures** | Count of useful work items reaching validated closure | Primary throughput measure | Weekly / monthly |
| **Product iterations closed** | Validated closures that change a customer- or founder-evaluable product surface | Separates product learning from internal activity | Weekly / monthly |
| **Median direction-to-closure time** | Median elapsed time from documented direction/selection to validated closure | Measures iteration speed | Monthly |
| **Founder active supervision minutes per closure** | Estimated minutes Daniel spends prompting, repairing, operating, or making technical choices for each closure | Measures attention leverage | Weekly sample / monthly |
| **Founder judgment minutes per closure** | Time spent on product evaluation, customer meaning, priority, and strategic decisions | Should be preserved or increase in quality, not eliminated | Monthly |
| **Compute cost per closure** | Model/API/infra cost allocated to validated closures | Measures economic efficiency | Weekly / monthly |
| **Manual rescue rate** | Closures or runs requiring unplanned founder technical intervention ÷ relevant runs | Measures operational independence | Weekly / monthly |
| **Rework rate** | Closed items requiring material correction because implementation missed accepted intent or evidence | Measures quality and context fidelity | Monthly |
| **First-pass acceptance rate** | Items accepted at first meaningful review ÷ reviewed items | Measures task packet and execution quality | Monthly |
| **Known-failure recurrence** | Repeat occurrences of a previously classified failure after remediation | Measures whether repairs compound | Monthly |
| **Closure ratio** | Validated closures ÷ materially started work items | Detects activity without finish | Weekly / monthly |
| **Iteration range** | Distinct useful output classes closed: product, website, deck, research, deployment, factory, etc. | Measures breadth of founder leverage | Monthly / quarterly |
| **Strategic learning events** | Closures that materially change product direction, prioritization, customer framing, or architecture | Measures discovery value | Monthly / quarterly |
| **Manual-baseline comparison** | Estimated equivalent time/cost under realistic direct Cursor/manual coordination | Tests whether leverage is real | Quarterly |

---

## Supporting diagnostics

These metrics explain the core scorecard but are not success metrics on their own:

- tokens by model and task class;
- context bytes transmitted per closure;
- premium-model share;
- retry count by failure class;
- queue age;
- time blocked by credits;
- time blocked by state disagreement;
- PR cycle time;
- test failure categories;
- deployment failure categories;
- number of duplicated plans or repeated repository rediscovery passes;
- deterministic versus agent-handled step share;
- parallel worker utilization and collision rate.

Use diagnostics to locate mechanisms. Do not present them as output.

---

## Minimum event record

Each material work item should eventually produce or reference a compact record with:

```json
{
  "workItemId": "stable identifier",
  "workClass": "product|website|presentation|research|factory|deploy|other",
  "selectedAt": "ISO-8601 timestamp",
  "closedAt": "ISO-8601 timestamp or null",
  "status": "selected|in_progress|blocked|closed|abandoned",
  "validatedClosure": true,
  "evidence": ["PR, commit, screenshot, test, artifact, or decision path"],
  "founderSupervisionMinutes": 0,
  "founderJudgmentMinutes": 0,
  "computeCostUsd": 0.0,
  "manualRescue": false,
  "materialRework": false,
  "firstPassAccepted": true,
  "failureClasses": [],
  "learningOutcome": "none|incremental|material",
  "notes": "short plain-language context"
}
```

This schema is a target for instrumentation, not a requirement to block current delivery. Begin with the fields already available and improve coverage incrementally.

---

## Founder attention classification

Track founder time in two categories because reducing all founder involvement is not the goal.

### Technical supervision

Examples:

- repeating context agents should already have;
- operating git, branches, or scripts;
- diagnosing known infrastructure failures;
- manually coordinating worker handoffs;
- repairing bookkeeping;
- re-running routine checks;
- resolving low-level technical choices.

This should generally decline per closure.

### Founder judgment

Examples:

- deciding which customer problem matters;
- evaluating whether an interface feels right;
- choosing between product directions;
- interpreting trader feedback;
- setting priority and definition of done;
- deciding what story a website or presentation should tell.

This is high-value work. The Autobuilder should create more opportunities for it and make each judgment easier to exercise through fast, credible iterations.

---

## Cost allocation rules

1. Attribute model/API spend to a work item when possible.
2. Shared infrastructure work may be allocated across the closures it enables over the review period.
3. Record large failed runs separately rather than hiding them inside successful averages.
4. Distinguish premium reasoning spend from commodity execution spend.
5. Track credit exhaustion and throttling as capacity failures.
6. Do not optimize cost by reducing necessary validation or strategic learning.

Useful derived measures:

```text
compute_cost_per_closure = total_allocated_compute_cost / validated_closures
supervision_minutes_per_closure = founder_technical_supervision_minutes / validated_closures
closure_ratio = validated_closures / materially_started_work_items
manual_rescue_rate = rescued_relevant_runs / relevant_runs
rework_rate = materially_reworked_closures / validated_closures
```

---

## Weekly review

Keep the weekly pass operational and short.

Report:

- validated closures;
- product iterations closed;
- major factory repair proven by reuse;
- compute cost and obvious outliers;
- manual rescues;
- recurring failure classes;
- current bottleneck;
- next highest-leverage correction.

Do not make a strategic verdict from one week unless there is a severe failure or existential cost problem.

---

## Monthly review

Assess trends:

- Are closures increasing?
- Is direction-to-closure time improving?
- Is technical supervision per closure declining?
- Are costs becoming more predictable?
- Are known failures recurring less often?
- Is product/design iteration happening more frequently?
- Is the factory enabling work Daniel otherwise would not complete?
- Did any factory investment produce reusable leverage?
- Which subsystem consumed effort without measurable reuse?

The monthly review may recommend targeted simplification, model rerouting, deterministic replacement, or temporary manual fallback for a subsystem.

---

## Quarterly strategic review

Compare the Autobuilder against the **realistic manual alternative**, not an imaginary zero-coordination workflow.

Estimate:

- useful product/design/research/factory outputs completed;
- Daniel's total technical supervision burden;
- total compute and infrastructure cost;
- credible experiments enabled;
- product learning generated;
- reliability and capability gained;
- equivalent direct-Cursor/manual coordination effort;
- what would likely not have been attempted without the factory.

Quarterly conclusion options:

- **Compound:** continue and invest in the highest-leverage bottleneck;
- **Constrain:** preserve the thesis but narrow or simplify a subsystem;
- **Reroute:** move tasks between deterministic code, cheaper models, premium models, or manual handling;
- **Rebuild:** replace a mechanism whose architecture repeatedly fails;
- **Reconsider:** challenge the accepted strategy using the decision record's evidence standard.

---

## Anti-gaming rules

- Do not split work artificially to inflate closure count.
- Do not count factory documents unless they change operation, decision quality, or future execution.
- Do not treat merged code as closed when steering/evidence remains knowingly false.
- Do not reduce rescue rate by hiding founder intervention.
- Do not lower cost by skipping validation.
- Do not claim manual-baseline superiority without describing the actual manual workflow.
- Do not treat a pivot as wasted output when the built experiment produced the learning that justified the pivot.
- Do not count abandoned work as failure automatically; record whether it prevented larger waste or created strategic learning.

---

## Initial instrumentation posture

Until automated measurement is complete:

1. use PRs, commits, evidence ledgers, artifacts, and founder pulses as source data;
2. sample founder time rather than demanding perfect tracking;
3. record obvious cost outliers and rescue events;
4. perform a qualitative monthly comparison;
5. automate only the fields that prove useful in repeated reviews.

Measurement must not become a new ungrounded control-plane project. Instrument the smallest dataset that improves decisions.

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-11 | v1 — defined validated closure, leverage metrics, review cadence, and anti-gaming rules |