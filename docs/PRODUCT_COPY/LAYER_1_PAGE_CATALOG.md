# Layer 1 — Page catalog (MSOS copy)

**Load after Layer 0** in every copy session. Use this when discussing *what a page is for* before diving into *exact strings* (Layer 3).

**Surface map:** [`SURFACE_INVENTORY.json`](SURFACE_INVENTORY.json) · **Session queue:** [`HANDOFF_2026-06-22.md`](HANDOFF_2026-06-22.md)

---

## How to use this doc

| Conversation phase | Stay in | Drop to Layer 3 when |
|--------------------|---------|----------------------|
| “What should Strategy Lab feel like?” | Layer 0 + this page’s **Purpose** / **Regions** | Operator picks a region to rewrite |
| “Is Command Center too dense?” | This page’s **Purpose** + **Copy status** | Operator names KPI row or tile |
| “Draft nav labels” | `public-nav` section below | Drafting packet keys |

---

## Site map (routes)

```text
/ ........................ Homepage (public)
/strategy-lab ............ Strategy Lab (public demo + authenticated shell)
/strategy-lab/confirm .... Thesis confirmation
/strategy-lab/expression . Expression planning
/command-center .......... Command Center (authenticated hub)
/monitor ................. Market surfaces / Monitor
/history ................. History & review
/learn ................... Vision / conclusion (architecture story)
```

---

## Homepage (`/`)

**Surface id:** `homepage` · **Status:** approved · **Content:** `apps/msos-web/src/content/homepage.ts`

### Purpose

Public entry for investors and traders. Answer in one scroll: *What is MSOS? Why should I care? What can I try right now?*

### Who arrives here

Cold traffic — no account yet. May know options, may not know MSOS.

### Regions on the page

| Region | Job | Copy notes |
|--------|-----|------------|
| **Public nav** | Orient + enter product | See `public-nav` surface |
| **Hero** | Hook + primary CTA | Eyebrow, h1, body, pills; primary CTA → Strategy Lab |
| **Product cards** | Hierarchy lock | MSOS → Strategy Lab → Probability Engine |
| **Lens tags** | Honest roadmap | BTC Live; others Coming/Planned |
| **Command Center preview** | Show the hub | Demo window; **Thesis gap** label (not “Disagreement located”) |
| **Features row** | Read → State → Fit → Learn | Four-step storyboard arc |

### Locked decisions (don’t re-litigate without operator)

- Primary CTA: **Explore the platform**
- Engine name: **Probability Engine**
- Pill: **Expression, not recommendation**

---

## Public nav (chrome on public routes)

**Surface id:** `public-nav` · **Status:** approved · **Content:** `apps/msos-web/src/content/publicNav.ts`

### Purpose

Persistent orientation on homepage, Strategy Lab entry, monitor, learn. Brand + wayfinding + sign-in.

### Regions

| Region | Job | Open copy questions |
|--------|-----|---------------------|
| Brand block | Name + tagline | Tagline mirrors hero eyebrow |
| Platform / Strategy Lab / Market surfaces / Vision | Top nav | “Market surfaces” vs “Monitor”? |
| Sign in | Auth entry | |
| Enter Command Center | Hub CTA | vs “Open Command Center” on homepage |

---

## Strategy Lab (`/strategy-lab`)

**Surface id:** `strategy-lab` · **Status:** needs_packet · **Fixtures:** `strategyLabFixtures.ts`

### Purpose

**Primary demo.** Trader states a view, sees what BTC options imply, spots disagreement, explores outcome text — live Deribit when API up.

### Who arrives here

Operator walkthrough URL. Traders evaluating the product. This is the 15-second north star surface.

### Regions on the page

| Region | Job | Copy notes |
|--------|-----|------------|
| **Metrics strip** | Market context | Spot, expiry, ranges, Live/Demo tag |
| **Lens tiles** | Market roadmap | BTC Live; ETH Soon; rest Planned |
| **Belief builder** | State your view | Presets: Higher/Lower/More vol/Less vol — **don’t promise chart moves** |
| **PPE chart region** | Show disagreement | Boundary copy only — no math in TS |
| **Outcome summary** | Fit language | Structure-fit framing, not recommendation |
| **Footer** | Paper / preview | `DEMO_FOOTER` from shared |

### Sub-routes

| Route | Purpose |
|-------|---------|
| `/strategy-lab/confirm` | Lock thesis before expression — lifecycle language |
| `/strategy-lab/expression` | Plan paper trade under constraints — simulation only |

---

## Command Center (`/command-center`)

**Surface id:** `command-center` · **Status:** needs_packet · **Fixtures:** `commandCenterFixtures.ts`

### Purpose

Authenticated **home base** — where you left off, what needs review, shortcuts into Strategy Lab and monitor.

### Who arrives here

Signed-in trader returning to work. Not a marketing page — utility + narrative glue.

### Regions on the page

| Region | Job | Copy notes |
|--------|-----|------------|
| **KPI row** | At-a-glance workload | Draft ideas, confirmed views, paper/live, reviews due |
| **Lab / lens tiles** | Deep links | Honest Live/Soon/Planned per market |
| **Current work list** | Resume thesis/expression | |
| **Calibration strip** | Bridge to monitor | Paper trading only |
| **Alerts / context panel** | Stale data, trust | Use `friendlySnapshotFeedMessage` when degraded |
| **Sidebar nav** | App chrome | Theses disabled until shipped |
| **Connected markets** | Roadmap honesty | BTC Live; ETH Soon; etc. |

---

## Monitor (`/monitor`)

**Surface id:** `monitor` · **Status:** needs_packet · **Fixtures:** `monitoringFixtures.ts`

### Purpose

**Monitoring mode (planned interaction grammar)** — watch thesis health, alerts, market surfaces while paper trading.

### Regions

| Region | Job |
|--------|-----|
| Hero | What you’re watching |
| Watch panels | Per-thesis status |
| Alerts | Stale data, threshold language — non-advisory |

---

## History (`/history`)

**Surface id:** `history` · **Status:** needs_packet

### Purpose

**Learning / review tail** — what happened to past theses and paper expressions over time.

### Regions

| Region | Job |
|--------|-----|
| Timeline / feed | Observed vs saved vs simulated — honest states |
| Empty / degraded | Snapshot feed down — Strategy Lab still works |

---

## Learn / Vision (`/learn`)

**Surface id:** `learn` · **Status:** needs_packet (add to inventory before draft)

### Purpose

Architecture and vision story for curious traders — **not** a spec dump. Conclusion narrative from storyboard.

### Regions

| Region | Job |
|--------|-----|
| Conclusion narrative | Why MSOS exists |
| Next selection | Optional CTA — don’t over-promise roadmap |

---

## Shared (`*`)

**Surface id:** `shared` · **Content:** `apps/msos-web/src/lib/publicCopy.ts`

### Purpose

Footers, workspace saved labels, degraded-path messages used across authenticated surfaces.

### Key strings

- `DEMO_FOOTER` — research preview, paper only
- `friendlySnapshotFeedMessage()` — no bindings/stack traces
- `WORKSPACE_SAVED_LABEL` — “Saved to your workspace”

---

## Copy status legend

| Status | Meaning |
|--------|---------|
| **approved** | Packet + content file; BUILD wired |
| **needs_packet** | Strings may exist inline/fixtures — charter packet next |
| **draft** | Packet in progress |
| **superseded** | Old packet — do not promote |

**Next layer:** Surface packet + `content/*.ts` for the selected id — see [`packets/`](packets/).
