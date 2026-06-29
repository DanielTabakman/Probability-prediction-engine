# MSOS product backplane charter v1

**Purpose:** Strategic umbrella for MSOS + PPE ownership, integration boundaries, and scope guards. Operational waterfall and relay detail live elsewhere — this doc is the **why** and **who owns what**.

**As-of:** 2026-06-20 · **Precedence:** When scope or ownership conflicts, this charter wins over ad-hoc BUILD rationale until steward SELECTION says otherwise.

**Related (do not duplicate):**

| Doc | Role |
|-----|------|
| [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) | P0–P8 waterfall + storyboard gates |
| [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) | Phased BUILD queue + MCD vs post-MCD tracks |
| [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) | Product milestone gate |
| [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) | Post-MCD research ops |
| [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) | Path/layer presets |
| [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) | Autobuilder / control-plane guards |
| [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md) | Future interaction-mode ontology (not build scope) |
| [`PPE_MODULE_REGISTRY_V1.md`](PPE_MODULE_REGISTRY_V1.md) | Analytical modules — tiers, pillars, data map ([`assets/msos_module_map.html`](assets/msos_module_map.html)) |

---

## Strategic frame

**MSOS** is currently a **platform-shaped shell** around **PPE**.

- It should look and feel like a credible platform.
- It should be architected so it can evolve into a broader platform later.
- **Active scope is narrow:** MSOS exists to hold PPE and deliver a smooth **thesis → market-implied probability → disagreement → expression → save/review** workflow.
- **Three product pillars:** **workflow** (trader process), **edge** (find/test dislocations — simulation only), **legibility** (honest readable market structure). **Market relationship** (disagreement today; more modes later) lives inside workflow — see module registry.

**PPE** is the **first real product module** inside MSOS — not a separate product the user must leave MSOS to use.

---

## Ownership boundary

| Layer | Owns | Must not |
|-------|------|----------|
| **MSOS** | Customer-facing shell, workflow, state, identity/user scope, thesis/expression lifecycle, monitor/history, entitlement **display**, UX around PPE | Reimplement PPE math, distributions, or disagreement calculations in TypeScript |
| **PPE** | Options math, implied distribution generation, disagreement calculations, evaluation/freeze outputs | Own MSOS workflow store, auth shell, or commercial UX |
| **Link** | Stable **output contract** from PPE → MSOS (display payloads, reference IDs) | Expose “snapshot” as primary user-facing concept — use **disagreement / saved evaluation** language in UX |

Streamlit/PPE may remain the **computation and output source** while MSOS becomes the **integrated user-facing shell**.

---

## Native PPE integration surface

MSOS must provide a **native PPE module slot** — embed, render, or contain PPE output without framing the journey as “leave MSOS for Streamlit.”

- **Pattern:** [`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md) — display API + MSOS chart shell; chromeless embed as fallback.
- **Rule:** MSOS displays/proxies PPE outputs only; all math stays in Python (`src/engine/`, `src/viz/`).

---

## Product primitive: Disagreement

The core object is increasingly **Disagreement**, not merely “trade.”

**Disagreement types (product grammar — docs first; app code only when SELECTION'd):**

| Type | Meaning (short) |
|------|-----------------|
| **directional** | Price level / path vs implied |
| **volatility** | Realized vs implied vol view |
| **tail** | Fat-tail / crash / melt risk |
| **timing** | When move happens vs expiry structure |
| **skew** | Put/call or wing asymmetry |
| **structure** | Payoff shape vs belief |
| **liquidity / risk-premium** | Carry, spread, funding, premium for risk |
| **hedge / constraint** | Portfolio or risk budget limits expression |

Do not overbuild typed disagreement in app code in control-plane slices.

**Interaction modes (user intent — docs first):** Disagreement is the **current wedge**; Expression Search, Hedging, Scenario Planning, Timing, Monitoring, and Learning/Review inform architecture and language but are **not** active BUILD scope until workflow research + SELECTION. See [`MSOS_Market_Interaction_Modes_v0.1.md`](../VISION/MSOS/MSOS_Market_Interaction_Modes_v0.1.md). Disagreement **types** (table above) describe *what kind of gap*; interaction **modes** describe *why the user came*.

---

## Minimum Credible Demo (MCD)

The next product milestone is **not** a complete platform. It is a **Minimum Credible Demo** where:

- MSOS feels like a coherent platform-shaped shell.
- PPE feels integrated enough that **trader workflow contact becomes high-signal**.

**Build until conversations are high-signal, not until the platform is complete.**

Gate criteria: [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md).

After MCD passes → primary focus shifts to [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md).

---

## Future-platform readiness

- Preserve architecture that can host more modules later (shell, workflow store, entitlement hooks).
- Do **not** expand active platform scope (new asset classes, execution, AI chat, broad commercial plumbing) unless **explicitly SELECTION'd**.

---

## Non-goals (active track)

Unless steward **SELECTION** says otherwise:

- New asset classes beyond current BTC options wedge
- Live execution / order routing
- AI chat / auto trade recommendations
- Broad platform expansion (multi-product marketplace)
- Excessive commercial plumbing (Stripe, entitlements automation) before MCD + workflow signal

Chartered post-MCD chapters remain in [`MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`](MSOS_LIVE_PRODUCT_SEQUENCE_V1.md) — **deferred**, not deleted.

---

## Doc precedence (scope decisions)

```
BACKPLANE (this doc)
  → MINIMUM_CREDIBLE_DEMO_GATE
  → TRADER_WORKFLOW_RESEARCH
  → MSOS_FRONTIER (BUILD order for automation)
  → MSOS_LIVE_PRODUCT_SEQUENCE (post-MCD phases deferred unless selected)
```

When **FRONTIER** and this charter disagree on **BUILD order**, FRONTIER wins for relay automation. When they disagree on **whether to widen scope**, this charter wins.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-20 | v1 — platform-shaped shell, PPE module, MCD, disagreement grammar |
| 2026-06-20 | Link interaction-mode ontology doc (vision; not build scope) |
