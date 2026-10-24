# Autobuilder as core internal product — decision record v1

**Plane:** CONTROL-PLANE  
**Status:** Accepted  
**Decision date:** 2026-07-11  
**Decision owner:** Founder  
**Scope:** Autobuilder, PPE/MSOS build factory, agent orchestration, technical operations, product iteration infrastructure

**Related:** [`AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md`](AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md) · [`AUTOBUILDER_LEVERAGE_SCORECARD_V1.md`](AUTOBUILDER_LEVERAGE_SCORECARD_V1.md) · [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md)

---

## Decision

The startup will continue to develop and operate the Autobuilder as a **core internal product and technical-founder system**.

The Autobuilder will remain coupled to real PPE/MSOS product work so its capabilities are tested against actual delivery, iteration, design, QA, recovery, and deployment needs.

The operating model is founder-directed:

- Daniel owns product truth, customer interpretation, priorities, definition of done, and final strategic decisions.
- The Autobuilder owns increasing portions of technical execution, continuity, coordination, validation, shipping, and recovery.
- Deterministic software handles knowable operational rules.
- Specialized agents perform bounded reasoning and implementation work.
- The system is evaluated by validated output, founder attention, compute cost, rework, reliability, and learning—not by visible feature work on any single day.

---

## Context

The startup is operated by one founder performing product, research, strategy, design, engineering coordination, QA, operations, documentation, and external work.

Those organizational functions exist regardless of whether they are automated. A manual workflow would require repeated prompting, task reconstruction, context transfer, command execution, quality checks, deployment, failure recovery, and project-state management.

Observed use of the Autobuilder has produced substantial product and organizational output, enabled rapid experimentation across multiple product directions, and contributed to discovery of the stronger **Options Made Easy** direction.

Recent bottlenecks are primarily second-order scaling problems—credits, context transmission, work isolation, parallelism, reliability, and closure bookkeeping—not evidence that the system produces no leverage.

The founder also confirmed that factory capabilities generally originated from tasks or failures experienced repeatedly, rather than from arbitrary automation for its own sake.

---

## Decision drivers

1. **Iteration is the startup strategy.** The final product is discovered through repeated credible builds, not fully specified in advance.
2. **Manual coordination is not free.** Removing the factory would return organizational work to the founder rather than eliminate it.
3. **The system has demonstrated leverage.** Output and learning exceed what the founder believes would have been feasible through manual Cursor operation alone.
4. **Design requires iteration capacity.** Product UI, websites, presentations, copy, and narratives need repeated production and evaluation.
5. **The founder cannot personally engineer every implementation.** The organization needs a durable technical execution function.
6. **The factory can compound.** Reliability, context economy, cost routing, and reusable workflows can improve future throughput across products and artifact types.

---

## Alternatives considered

### Alternative A — Return to manual Cursor-driven development

**Rejected as the default.**

This appears simpler locally but transfers coordination, memory, QA, recovery, and repeated prompting back to the founder. It likely reduces the number and range of iterations the startup can complete while Daniel performs all other founder functions.

Manual operation remains a fallback mode for narrow tasks or factory outages.

### Alternative B — Freeze the Autobuilder for a fixed period

**Rejected as a general prescription.**

A freeze based only on time spent maintaining infrastructure would ignore demonstrated output and the realistic manual baseline. A temporary freeze may still be used for a specific subsystem when evidence shows it is destabilizing delivery.

### Alternative C — Build a fully autonomous general-purpose company agent

**Rejected as the current architecture.**

The system should not replace founder product judgment or autonomously widen company scope. Generality may emerge from repeated grounded use, but it is not the immediate acceptance criterion.

### Alternative D — Founder-directed production system

**Accepted.**

Use deterministic coordination, bounded agents, explicit canon, evidence gates, cost visibility, and founder product authority to provide the technical-founder function.

---

## Expected benefits

- more validated product iterations per month;
- lower transaction cost for experiments and pivots;
- reduced founder time spent on mechanical technical coordination;
- persistent organizational memory and boundaries;
- faster recovery from known failure modes;
- reusable website, presentation, design, and implementation workflows;
- better visibility into model spend and task economics;
- ability to explore multiple credible product directions before committing deeply;
- a compounding internal capability that can support future products.

---

## Accepted costs

- substantial up-front and ongoing factory engineering;
- periods where infrastructure work dominates visible product work;
- need for control-plane documentation and state reconciliation;
- compute and model-credit expense;
- risk of overbuilding abstractions;
- need to instrument output, cost, rescue, and rework;
- continued founder involvement in product evaluation and system design.

These costs are accepted only while they produce or plausibly protect measurable leverage.

---

## Guardrails

1. Every material factory capability must serve a purpose allowed by [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md).
2. Agents must criticize specific mechanisms before recommending rejection of the entire Autobuilder strategy.
3. New intelligence layers should not be added when deterministic software can solve the problem.
4. Agent tasks require bounded scope, canon, ownership, acceptance criteria, and evidence.
5. Product direction, customer truth, and definition of done remain founder-owned.
6. Generated activity is not counted as output until it reaches validated closure.
7. Material control-plane changes use a branch and draft PR.
8. Factory improvements should remain reversible where practical.
9. Manual fallback paths must remain available for narrow tasks and outages.
10. Frustration, credit exhaustion, or one failed run triggers diagnosis—not an automatic strategic reversal.

---

## Measurement and review

The canonical scorecard is [`AUTOBUILDER_LEVERAGE_SCORECARD_V1.md`](AUTOBUILDER_LEVERAGE_SCORECARD_V1.md).

Review levels:

- **Weekly:** operating signals and obvious failure clusters;
- **Monthly:** throughput, founder attention, compute cost, rescue, and rework trends;
- **Quarterly:** strategic comparison against the realistic manual alternative and whether the system is increasing iteration capacity.

No single metric is sufficient. In particular, raw commits, code volume, agent turns, or number of workers must not substitute for validated product output.

---

## Reconsideration triggers

A strategic review is required when one or more of the following persists across a meaningful monthly or quarterly window:

- validated throughput is lower than a realistic manual baseline;
- founder supervision per completed slice remains excessive or increases without compensating output;
- compute cost per useful closure is unsustainable;
- manual rescue or rework remains structurally high after targeted fixes;
- factory changes repeatedly block real product experiments;
- automation materially distorts product intent;
- the system cannot produce trustworthy evidence of closure;
- maintenance does not create reusable speed, reliability, range, or learning.

The review should first consider narrowing scope, replacing agent reasoning with deterministic logic, changing model routing, simplifying a subsystem, or returning selected workflows to manual mode.

---

## Consequence for future agents

Future agents must treat this as an accepted operating decision.

They may challenge it with evidence, but must not casually recommend pausing or abandoning the Autobuilder merely because:

- infrastructure work is currently intense;
- a repair day produced no visible feature;
- the system is more complex than a direct coding workflow;
- Cursor can generate code without the full factory;
- an isolated run consumed excessive credits.

A recommendation to reverse this decision must cite scorecard evidence, compare against the realistic manual alternative, and describe the expected impact on startup iteration capacity.

---

## Coordination status

```text
COORDINATION STATUS
Agreement: aligned
Compared: founder discussion; CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1; FOUNDER_COLLABORATION_CHARTER_V1; BUILD_FACTORY_BOUNDARY_V1
Disagreement: none after founder correction and explicit strategic decision
Evidence gap: scorecard instrumentation is not yet fully automated
Ownership overlap: none; documentation-only control-plane change
Risk if unresolved: future agents may misclassify demonstrated factory leverage as infrastructure distraction
Recommended default: accept this decision and instrument the scorecard
Founder decision required: no
```

---

## Changelog

| Date | Change |
|---|---|
| 2026-07-11 | v1 — accepted decision to operate the Autobuilder as a core internal product and technical-founder system |