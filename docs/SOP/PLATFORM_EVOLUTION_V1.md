# Platform evolution — layered stack (v1)

**Status:** Accepted steering (2026-05-25)  
**Purpose:** Record how PPE grows its stack **by layer** (UI, API, data/auth), not by big-bang rewrites. Agents and stewards must follow this before proposing Streamlit → Supabase/React migrations or chartering architecture slices.

**Precedence:** Does not override MVP1 scope in [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md). For slice queue, [`docs/SOP/MVP1_FRONTIER.md`](MVP1_FRONTIER.md) still wins. This doc governs **when** platform swaps are allowed and **how** they are sequenced.

---

## Default posture (until triggers fire)

| Layer | Current choice | Policy |
|-------|----------------|--------|
| **UI** | Streamlit (`src/viz/`) | **Keep** for product surfaces on demo + full app until a trigger below fires. |
| **Compute** | Python (`src/engine/`, `src/data/`) | **Keep** — not replaced by Supabase or a frontend framework. |
| **Persistence** | SQLite on full-app volume (`frozen_evaluation_store.py`) | **Keep** for MVP1 validation / friends-first beta. |
| **Auth (edge)** | Cloudflare Access on `app.` | **Keep** unless app-level auth trigger fires. |
| **Deploy** | Docker + Caddy + dual Streamlit (`docker-compose.yml`) | **Keep** unless a new surface needs a separate hostname/service. |

**Supabase** is a candidate for **persistence + app auth**, not a drop-in replacement for Streamlit. **React/Next** is a candidate for **customer-grade UI**, not a database.

**Do not** charter a "framework migration" or "move to Supabase" BUILD slice unless a **steward trigger** in §3 is satisfied **or** the steward explicitly requests it in the BUILD packet.

---

## Layered evolution (how we grow)

Replace **one layer at a time** when pain is specific:

1. **API layer (first extract, when needed)** — Thin HTTP API (e.g. FastAPI) around freeze, lab state, and engine calls. Streamlit (or a future UI) calls the API. Tests stop importing `src.viz.app` for non-UI logic.
2. **Data layer** — Move snapshots/reviews to **Postgres** (Supabase or self-hosted). Per-user rows, RLS if using Supabase.
3. **Auth layer** — App-level identity (Supabase Auth or other) when Cloudflare-only gating is insufficient (billing, teams, per-user API keys).
4. **UI layer** — New frontend (e.g. Next.js) for **one critical flow at a time** (e.g. implied lab + freeze), backed by the same API + DB.

**Hybrid is allowed indefinitely:** Streamlit for demo, internal ops, or experiments; customer product on a new UI + shared API.

---

## Steward triggers (human decision required)

Before any BUILD work that **introduces** Supabase, replaces Streamlit on `app.`, or splits the monolith into API + new UI, the agent must **STOP** and ask the steward to confirm **which trigger** applies. Do not infer approval from casual chat.

| ID | Trigger | Typical response |
|----|---------|------------------|
| **T1** | Per-user snapshot history across devices / accounts | Data layer (+ likely auth); API extract may precede UI |
| **T2** | Paid SaaS: billing, teams, or in-app roles | Auth + data; plan API before UI |
| **T3** | Public or partner **API** consuming freeze/lab state | API layer required |
| **T4** | Mobile or non-browser client | API + UI strategy; Streamlit not sufficient |
| **T5** | Streamlit rerun/state blocks a **scoped** product slice | API extract and/or UI slice for that flow only |
| **T6** | Steward explicitly requests platform slice in BUILD packet | Named layer + acceptance criteria |

If **none** of T1–T6 apply, **defer** platform migration; continue Streamlit + SQLite + existing deploy.

---

## Agent behavior (hard)

1. **Read this file** when the user or packet mentions: Supabase, Postgres migration, React/Next, FastAPI, "replace Streamlit", framework migration, multi-tenant, or SaaS auth.
2. If the request implies a platform change and **no trigger** is cited: reply with a short summary of §2–§3 and **ask which trigger** (T1–T6) the steward is invoking.
3. **Do not** widen MVP1 scope (`PPE_MASTER_MVP1`, `MVP1_FRONTIER`) with platform work unless the frontier or steward packet explicitly charters it.
4. Prefer **smallest layer first** (usually API or DB, not full UI rewrite).
5. Document the chosen trigger in the slice spec / HANDOFF when a platform slice is approved.

---

## Suggested migration order (when a trigger fires)

```text
Trigger confirmed →
  (optional) API extract for freeze + lab state →
  Postgres / Supabase for persistence →
  Auth if T1/T2 →
  New UI slice for one flow →
  Cut over app. hostname when parity + smoke pass
```

Evidence: extend existing pytest; add contract tests on API; keep or adapt Playwright smoke per surface ([`docs/IMPLIED_LAB_SMOKE.md`](../IMPLIED_LAB_SMOKE.md)).

---

## What stays out of scope by default

- Big-bang "rewrite the app in Next"
- Supabase-only change with no product trigger
- Dropping Python engine into edge functions for heavy quant work
- Removing Streamlit from demo host without steward sign-off

---

## Related docs

- Stack baseline: [`docs/PLAN.md`](../PLAN.md)
- Deploy surfaces: [`docs/VISION/PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md) (Deployment surfaces), [`docs/DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)
- Deferred migration (phase): [`docs/VISION/PHASE_VISION_CURRENT.md`](../VISION/PHASE_VISION_CURRENT.md)
- Commit/CI gates: [`docs/SOP/COMMIT_POLICY_V1.md`](COMMIT_POLICY_V1.md)
