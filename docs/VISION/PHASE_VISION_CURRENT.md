# PHASE_VISION_CURRENT

**Current-cycle product vision** for the active product phase. Update when the phase changes. Long-range intent lives in `VISION_MASTER.md`.

## Current phase

**Phase: One-screen implied lab (manual exploration)**  
(Aligned with `docs/SOP/CURRENT_FRONTIER.md` and `docs/SPRINT_1_SPEC.md`; delivered through numbered **feature slices**, formerly “Sprint NNN”.)

## What this phase is trying to achieve

Turn the implied lab into a **single, scannable screen** where exploration is **manual** but **coherent**: market-implied view, belief inputs, payoff, and trade stats read as one story. Visible outputs should **flow from centralized state**, not scattered widget logic (`docs/SPRINT_1_SPEC.md` technical principle).

## What “done enough” looks like

In about **15 seconds**, a new user can answer:

- What the **market-implied** (priced / risk-neutral) view is showing  
- What **belief** (if any) they are expressing  
- What **trade / strategy shape** they are inspecting  
- What the **payoff stats** are (e.g. debit/credit, max gain/loss, breakevens; fit quality when available)

Advanced math and calculations stay **behind expanders** by default. Mode switches are obvious: **exact strikes** vs **target payoff**; **market** vs **user belief** vs **compare** (`docs/SPRINT_1_SPEC.md`).

## Current UX priorities

- **Chart high**, minimal scroll to “see the picture.”  
- **Two columns**: controls left; chart + summary right.  
- **Summary card** carries strategy name, debit/credit, max gain/loss, breakevens, fit quality when available.  
- **No mystery meat** — labels match `docs/SEMANTIC_CONTRACTS.md` (e.g. no “what the market truly believes”).

## Current semantic priorities

- Keep **market-implied pricing distribution**, **user belief**, **disagreement**, **strategy family** (explore/fit), **illustrative pattern** vs **exact priced structure**, and **fit vs recommendation** **distinct** and correctly worded in UI and hints.  
- **Disagreement** remains **descriptive**, not prescriptive.  
- **Verification** remains a visible, trustworthy thread for major outputs.

## What to defer for now

- **Framework / platform migration** — deferred while validation and demo UX are the bottleneck. When persistence, auth, or cockpit UX block growth, follow [`docs/SOP/PLATFORM_EVOLUTION_V1.md`](../SOP/PLATFORM_EVOLUTION_V1.md) (steward triggers T1–T6); do not migrate by default.
- New **AI** features, **prediction-market** integration work, and **major new strategy logic** except what is **necessary** for layout/state clarity (`docs/SPRINT_1_SPEC.md` non-goals).  
- Cross-cutting **engine/DB** rewrites unless a dedicated phase / feature slice targets them with tests.

## Current drift risks

- **Copy creep** — UI drifts into forbidden phrases or collapses “fit” into “recommendation.”  
- **State sprawl** — duplicated derivation paths that make the screen inconsistent or untestable.  
- **External data fragility** — lab depends on live-ish inputs; failures should **read clearly**, not as generic breakage (`docs/SOP/CURRENT_FRONTIER.md` risks).

## Last aligned with

`docs/SOP/CURRENT_FRONTIER.md` (2026-04-01). Refresh this file when the frontier phase changes.
