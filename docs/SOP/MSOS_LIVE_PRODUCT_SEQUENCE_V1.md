# MSOS live product sequence v1

**Purpose:** Canonical phased plan to make the **apex MSOS shell** a real, **customer-acquirable** product — not a fixture walkthrough. Agents and stewards use this when MSOS UI work touches Command Center data, auth, persistence, or commercial tiers.

**As-of:** 2026-06-20 · **Controlling canon:** [`MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md`](MSOS_PRODUCT_BACKPLANE_CHARTER_V1.md) · [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

**Live queue:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)

---

## Strategic interpretation (binding)

- **MSOS** is currently a **platform-shaped shell around PPE** — credible platform UX, **narrow active scope**.
- The product should feel **platform-ready** but remain focused on thesis → implied probability → disagreement → expression → save/review.
- **Seamless PPE-in-MSOS UX** is required — native integration surface, not “leave MSOS for Streamlit.”
- **PPE math** stays in PPE; MSOS integrates outputs via stable contract ([`SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md)).
- **Product completeness** is judged by whether it enables **high-signal workflow contact** ([`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md)), not by finishing every commercial phase.

---

## MCD track vs post-demo track

<!-- ACTIVE_PRODUCT_DIRECTION:START -->
| Track | Phases | When |
|-------|--------|------|
| **Usable demo (active)** | Storyboard BUILD + production wiring + embed shell + walkable witness | **Now** — pivot `usable-demo-lemon-squeezy-v1` |
| **Post-demo expansion** | 4a → 4b → 5 → 6 → 7a → 7b | **Only when SELECTION'd** after usable demo is walkable on production URLs |

Phases 4a–7b remain chartered for multi-user and commercial work — they are **not** the current default BUILD priority.
<!-- ACTIVE_PRODUCT_DIRECTION:END -->

---

## Long-term architecture (binding intent)

| Layer | Owns | Long-term home |
|-------|------|----------------|
| **MSOS** | Thesis lifecycle, expression plans, monitor/history, entitlements | **Server-side workflow store**, user-scoped via Cloudflare Access |
| **PPE** | Distributions, disagreement, freeze/review **math** | **Streamlit +** `frozen_evaluation_store` (with `owner_email`) |
| **Commercial** | Free / research_beta / paid tiers | `msos_entitlements` → **Lemon Squeezy** (phase 7b) |
| **Link** | Thesis ↔ saved PPE evaluation (snapshot ID internal) | Reference IDs — **no PPE math in TypeScript**; UX favors **disagreement / saved evaluation** language |

---

## Phased queue (execute in order)

| Phase | chapterId | Priority | Outcome |
|-------|-----------|----------|---------|
| **1** | [`msos_production_wiring_v1`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md) | HIGH | Sign-in, live embed, CTAs, wired nav |
| **2** | [`msos_user_state_v1`](SPRINT_MSOS_USER_STATE_V1.md) | HIGH | Command Center from **PPE snapshots** (read-only) |
| **3** | [`msos_workflow_persistence_v1`](SPRINT_MSOS_WORKFLOW_PERSISTENCE_V1.md) | HIGH | MSOS theses/expressions **server-side** |
| **4a** | [`mvp1_snapshot_owner_v1`](SPRINT_MVP1_SNAPSHOT_OWNER_V1.md) | HIGH | `owner_email` on PPE freezes |
| **4b** | [`msos_access_identity_v1`](SPRINT_MSOS_ACCESS_IDENTITY_V1.md) | HIGH | Access on MSOS routes; scoped APIs |
| **5** | [`msos_monitor_history_live_v1`](SPRINT_MSOS_MONITOR_HISTORY_LIVE_V1.md) | HIGH | Monitor + History + CC strip live |
| **6** | [`msos_e2e_product_witness_v1`](SPRINT_MSOS_E2E_PRODUCT_WITNESS_V1.md) | MEDIUM | Full journey operator witness |
| **7a** | [`msos_entitlements_v1`](SPRINT_MSOS_ENTITLEMENTS_V1.md) | HIGH | **Free accounts** + manual paid path |
| **7b** | [`msos_billing_lemon_squeezy_v1`](SPRINT_MSOS_BILLING_LEMON_SQUEEZY_V1.md) | MEDIUM | **Lemon Squeezy** self-serve pay — BUILD when usable demo walkable |

**Operator note (post-MCD only):** Phases 7a–7b may start BUILD after **4b** if commercial urgency and MCD **PASSED**; default post-MCD order runs **6** before monetization gates expand.

**Parallel UX (MCD-required):** [`msos_strategy_lab_embed_shell_v1`](SPRINT_MSOS_STRATEGY_LAB_EMBED_SHELL_V1.md) — **HIGH for MCD**; replaces box-in-box Streamlit iframe on `/strategy-lab` with storyboard `03_ppe_lab` chart shell. **Blocked until phase 3 COMPLETE**; required for MCD gate criterion §3.

---

## Product completeness bars

| Bar | Phases required |
|-----|-----------------|
| **Minimum Credible Demo** | 1 → 2 → 3 + **embed shell** — gate: [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) |
| **Trader workflow research (optional)** | MCD passed + sessions per [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) — **not a BUILD gate** |
| **Usable demo (active BUILD)** | Storyboard implementation + PPE-in-MSOS integration — [`SPRINT_MSOS_USABLE_DEMO_V1.md`](SPRINT_MSOS_USABLE_DEMO_V1.md) |
| **Solo operator — works** | 1 → 2 → 3 (subset of MCD) |
| **Multi-user research beta** | + 4a → 4b → 5 — **post-MCD, SELECTION only** |
| **Shippable demo / PMF test** | + 6 — **post-MCD** |
| **Acquire customers (free)** | + 7a — **post-MCD** |
| **Charge self-serve** | + 7b (Lemon Squeezy) — **post-usable-demo** |

---

## Commercial path (summary)

See [`MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md`](MSOS_COMMERCIAL_ENTITLEMENTS_ADR.md).

1. **Now (phase 7a):** Free tier on first Access login; operator grants `paid` manually.
2. **After usable demo (phase 7b):** Lemon Squeezy checkout via `MSOS_UPGRADE_OFFER_URL`; manual grant v0 → webhook BUILD when volume warrants.

---

## Data flow (target end state)

```mermaid
flowchart TB
  CF[Cloudflare Access]
  ENT[msos_entitlements]
  CC[Command Center]
  MSOS[(MSOS workflow DB)]
  SNAP[(PPE snapshots)]
  STRIPE[Lemon Squeezy webhooks]

  CF --> ENT
  CF --> CC
  ENT --> CC
  CC --> MSOS
  CC --> SNAP
  STRIPE -.->|phase 7b| ENT
```

---

## Hard rules (all phases)

1. **No PPE math in TypeScript** — display/proxy/read only.
2. **Honest labels** — preview/fixture/snapshot-sourced when not MSOS-native.
3. **No custom auth server** — Cloudflare Access per stack ADR.
4. **No live execution** — sim-only expression until new SELECTION.
5. **No revenue claims** without [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) evidence.

---

## Operator-visible milestones

| After phase | Operator can… |
|-------------|----------------|
| 1 | Sign in, live PPE embed, working nav/CTAs |
| 2 | Command Center shows real PPE snapshot activity |
| 3 | Save/reopen theses server-side |
| 4a–4b | Each customer sees only their data |
| 5 | Full monitor/history loop live |
| 6 | Prove end-to-end journey on production URL |
| 7a | Onboard free users; manually upgrade paid |
| 7b | Customers pay via Lemon Squeezy |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-14 | v1 — initial phased sequence |
| 2026-06-14 | v2 — phases 4a–7b chartered (identity, monitor, E2E, entitlements, Stripe deferred) |
| 2026-06-18 | v3 — parallel UX chapter `msos_strategy_lab_embed_shell_v1` (MEDIUM, post–phase 3) |
| 2026-06-19 | v4 — production hookup charter [`MSOS_PRODUCTION_LIVE_HOOKUP_V1.md`](MSOS_PRODUCTION_LIVE_HOOKUP_V1.md) (relay DONE ≠ production usable) |
| 2026-06-20 | v5 — MCD vs post-MCD tracks; backplane charter; embed shell MCD-required |
