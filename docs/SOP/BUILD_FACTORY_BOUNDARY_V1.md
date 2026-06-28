# Build factory boundary v1

**Purpose:** Guardrails for **autobuilder** and control-plane work — meta-infrastructure is allowed; **ungrounded** meta-infrastructure is not.

**Strategic context:** [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) · **Operator runbook:** [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## Frame

**Autobuilder** is **meta-infrastructure**: relay, IDE BUILD starters, operator status, gates, closeout automation.

- Meta-infrastructure **is allowed** and necessary for product-slice throughput.
- **Infinite operational meta-structure** is a valid long-term ambition only when **grounded in product learning and shipping**.
- **Codex fallback** is allowed when it protects throughput during Cursor quota exhaustion.

---

## Allowed purposes (new factory/control-plane features must serve one)

| # | Purpose | Examples |
|---|---------|----------|
| **a** | **Product-slice throughput** | IDE BUILD starter generation, mark-ready, tiered pushable gate |
| **b** | **Operator interruption reduction** | ntfy fix pings, autobuilder phase machine, brief operator status |
| **c** | **Build reliability / recovery** | stale-state triage, handoff retry, VM ensure scripts |
| **d** | **Workflow learning → shippable changes** | Backlog hooks from validation log; starter Focus blocks citing MCD gaps |
| **e** | **System efficiency / efficacy** | Token economy, context preflight, workflow metrics |

If a proposed control-plane slice does not clearly serve **(a–e)**, **defer** unless steward SELECTION explicitly authorizes it.

---

## Ungrounded meta (say no)

Stop and escalate if a BUILD packet would:

1. Add orchestration surface **without** a linked product chapter or operator pain point.
2. Expand agent/rule/docs hierarchy **faster** than product witnesses ship.
3. Build “platform for platforms” before [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) criteria are met.
4. Replace human SELECTION with automation that widens scope (new assets, execution, billing) without validation signal.

**Prefer:** small product witnesses over large ungrounded control-plane expansions.

---

## Current dominant focus

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
| Priority | Focus |
|----------|--------|
| **1** | **Trader workflow integration** — milestone charter + four workstreams |
| **2** | **Active relay** — `msos_workflow_asset_parity_v1` (msos_workflow_asset_parity_v1) |
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
| [`ppe-autobuilder-operator`](../../.cursor/agents/ppe-autobuilder-operator.md) | Build meta-infrastructure only when grounded in (a–e); prefer product workers over control-plane churn |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v1 — grounded meta-infrastructure doctrine |
