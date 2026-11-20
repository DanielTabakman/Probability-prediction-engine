# Build factory boundary v1

**Purpose:** Guardrails for **autobuilder** and control-plane work — meta-infrastructure is allowed; **ungrounded** meta-infrastructure is not.

**Strategic context:** [`AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md`](AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md) · [`AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md`](AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md) · [`AUTOBUILDER_LEVERAGE_SCORECARD_V1.md`](AUTOBUILDER_LEVERAGE_SCORECARD_V1.md) · [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md)  
**Operator runbook:** [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## Frame

**Autobuilder** is a **core internal product and technical-founder system** implemented through meta-infrastructure: relay, IDE BUILD starters, operator status, gates, closeout automation, deterministic coordination, and bounded agents.

- Meta-infrastructure **is allowed** and necessary for product-slice throughput.
- **Infinite operational meta-structure** is a valid long-term ambition only when **grounded in product learning and shipping**.
- **Codex fallback** is allowed when it protects throughput during Cursor quota exhaustion.
- High infrastructure effort alone is **not** evidence that the Autobuilder should be paused; evaluate validated output, founder attention, compute cost, rework, rescue, reliability, and iteration value.
- The founder owns product truth and direction; the Autobuilder increasingly owns technical execution, continuity, validation, shipping, and recovery.

---

## Allowed purposes (new factory/control-plane features must serve one)

| # | Purpose | Examples |
|---|---------|----------|
| **a** | **Product-slice throughput** | IDE BUILD starter generation, mark-ready, tiered pushable gate |
| **b** | **Operator interruption reduction** | ntfy fix pings, autobuilder phase machine, brief operator status |
| **c** | **Build reliability / recovery** | stale-state triage, handoff retry, VM ensure scripts |
| **d** | **Workflow learning → shippable changes** | Backlog hooks from validation log; starter Focus blocks citing MCD gaps |
| **e** | **System efficiency / efficacy** | Token economy, context preflight, workflow metrics |
| **f** | **Iteration range / artifact production** | Reusable website, presentation, design, research, and product iteration workflows grounded in repeated use |

If a proposed control-plane slice does not clearly serve **(a–f)**, **defer** unless steward SELECTION explicitly authorizes it.

---

## Ungrounded meta (say no)

Stop and escalate if a BUILD packet would:

1. Add orchestration surface **without** a linked product chapter, repeated operator pain point, measured bottleneck, or concrete artifact-iteration need.
2. Expand agent/rule/docs hierarchy **faster** than product witnesses or reusable factory proofs ship.
3. Build “platform for platforms” before [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) criteria are met, unless the work directly protects demonstrated iteration throughput.
4. Replace human SELECTION with automation that widens scope (new assets, execution, billing) without validation signal.
5. Add an intelligent supervisory layer where deterministic state, routing, validation, or recovery logic would be sufficient.
6. Optimize agent activity, concurrency, code volume, or document count instead of validated closure.

**Prefer:** small product witnesses and proven reusable capability upgrades over large ungrounded control-plane expansions.

---

## Anti-regression evaluation rule

Do **not** infer from a difficult repair day, quota exhaustion, or a high share of infrastructure work that the Autobuilder strategy has failed.

Before recommending a freeze, demotion, or removal, an agent must:

1. identify the specific failing mechanism;
2. compare measured output against the realistic manual alternative;
3. use the leverage scorecard over a meaningful operating window;
4. estimate impact on future iteration capacity;
5. propose the smallest reversible correction first.

Criticism of model routing, context duplication, recovery loops, state architecture, or documentation sprawl is encouraged. Casual rejection of the accepted Autobuilder thesis is not.

---

## Current dominant focus

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
| Priority | Focus |
|----------|--------|
| **1** | **Trader workflow integration** — milestone charter + four workstreams |
| **2** | **Active relay** — `` (Workflow loop fidelity (P4–P7)) |
| **3** | **Factory stability** — relay, autobuilder, gates, closeout |
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

---

## Not active unless explicitly SELECTION'd

- Broad platform expansion (multi-module marketplace)
- Live execution / new asset classes
- AI chat assistant
- Excessive commercial plumbing (Stripe automation, entitlement productization beyond MCD needs)

Chartered chapters in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) phases 4a–7b remain **post-MCD deferred**.

---

## Agent routing

| Agent | Factory rule |
|-------|----------------|
| [`ppe-director`](../../.cursor/agents/ppe-director.md) | Route toward MCD before broad expansion; protect future-platform readiness without premature sprawl |
| [`ppe-autobuilder-operator`](../../.cursor/agents/ppe-autobuilder-operator.md) | Build meta-infrastructure only when grounded in (a–f); prefer product workers and deterministic mechanisms over control-plane churn |

**No parallel Cursor Skills layer:** PPE operator workflows use rules + generated `OPERATOR_STATUS` (`Mode:` / `CLOSEOUT_ONLY`) + starters + subagents ([`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)). Do not bulk-migrate SOP/rules into skills.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-07-11 | Aligned boundary with accepted Autobuilder core-product thesis, technical-founder function, scorecard, and anti-regression rule |
| 2026-06-20 | v1 — grounded meta-infrastructure doctrine |