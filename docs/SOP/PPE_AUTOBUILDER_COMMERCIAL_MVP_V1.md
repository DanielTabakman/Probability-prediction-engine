# PPE autobuilder — commercial MVP reference (parked)

**Plane:** CONTROL-PLANE · **Status:** **parked** — reference only; not active SELECTION. Revisit via human backlog `autobuilder_landscape_review`.

**Related:** [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) · [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) (`ppe_autobuilder_*` chapters)

---

## Positioning (one line)

**Governed agent factory for solo technical founders** — chartered slices, hard relay gates, PR-only shipping, near-zero API burn. Not a Devin competitor; sell the **discipline layer**.

---

## Two layers

### Layer 1 — Prove-it MVP (dogfood)

**Goal:** Run a full product chapter for **7 days** without `ppe_go.cmd` or phone pings on the happy path.

| Gate | Evidence |
|------|----------|
| Happy path ships | `ppe_autobuilder_happy_path_v1` chapter DONE |
| Self-heal on gate fail | `ppe_autobuilder_bounded_repair_v1` DONE |
| Debug without archaeology | `ppe_autobuilder_timeline_v1` DONE |
| 7-day unattended run | Operator log + `workflow_metrics` summary |

**Not required:** SaaS, billing, design partners.

### Layer 2 — Sellable MVP (first paying customer)

**Buyer:** Solo founder or 2-person shop using Cursor, burned by unconstrained agents.

**Package ("Relay Operator" v1):**

| # | Deliverable |
|---|-------------|
| 1 | One-command install (`install_operator.cmd` — Windows or Linux VM) |
| 2 | Starter repo template (AGENTS.md + minimal SOP kit, PPE/MSOS canon stripped) |
| 3 | Loop + autobuilder + relay gate (existing stack) |
| 4 | Phone/web status (ntfy or simple status page) |
| 5 | Cursor integration (local trigger watcher + IDE_BUILD starters) |
| 6 | Docs: 30-min setup + one worked example chapter |

**Core user journey (must work end-to-end):**

1. Clone template → `install_operator.cmd` → stack healthy (`ppe_autobuilder status`)
2. Append one chapter row to backlog JSON
3. Loop runs (or `ppe_autobuilder advance` on demand)
4. Product slice → gate → commit → PR → merge on green CI
5. Phone pings **only** on `STOP_FOR_REVIEW` / `FIX_PLAN` — not every slice

**Success metrics (design-partner ready):**

- Partner completes **3 chartered chapters** without a support call
- Setup **< 2 hours** (not multi-day VM fiddling)
- **< 2 human interventions per chapter** on average
- Partner can explain the system in one sentence

---

## Explicitly out of sellable MVP

| Cut | Why |
|-----|-----|
| Hosted multi-tenant SaaS | Ops before happy path proven |
| Open-ended "build me X" SELECTION | Moat is governance, not magic prompts |
| Cloud sandbox / browser testing | Devin's lane; win on local + cheap |
| Parallel slice fleet | v2 (`ppe_autobuilder_parallel_slices_v1`) |
| Operator product billing | Manual design partners first |
| MSOS/PPE bundled | Operator is infra; MSOS is proof customer |

---

## Pricing sketch (design-partner stage only)

| Tier | Price | What |
|------|-------|------|
| OSS core | $0 | Relay runtime + autobuilder + SOP templates on GitHub |
| Operator Kit | ~$99/mo | Template repo, setup scripts, ntfy, email support |
| Managed VM | ~$299/mo | Hosted loop VM; customer uses Cursor locally for product slices |

Start with **3 design partners at $0–99** before building hosted anything.

---

## Path from today

```text
Happy path + repair + timeline (factory chapters)
  → 7-day dogfood PASS on MSOS/PPE
  → Strip PPE-specific canon → template repo
  → install_operator one-command + worked example chapter
  → 3 design partners
  → They finish 3 chapters alone? → sellable MVP
  → No? → fix onboarding, not features
```

Rough effort after usable demo: **~3–4 relay chapters** for happy path + onboarding template (not a year; not a weekend).

---

## vs commercial agents (reminder)

| | Devin / Factory | PPE autobuilder |
|---|-----------------|-----------------|
| Input | Ticket / NL prompt | Pre-chartered `PHASE_PLANS` |
| Output | PR in cloud sandbox | Relay CONTINUE + steering sync + zero-touch merge |
| Risk | Hope agent didn't break prod | Layer map, relay gate, human SELECTION |
| Cost model | $500+/mo autonomous sessions | Near-zero API local profile |

---

## When to un-park

1. Human backlog `autobuilder_landscape_review` — monthly or after factory chapters ship.
2. `msos_usable_demo_v1` walkable on production (product proof for MSOS, not operator).
3. 7-day dogfood PASS documented in operator session notebook.

Until then: **MSOS product + UX design** stay dominant; factory chapters in [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) may run during product UX pause per [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) priority 2.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-15 | Initial reference from Cursor landscape analysis — parked |
