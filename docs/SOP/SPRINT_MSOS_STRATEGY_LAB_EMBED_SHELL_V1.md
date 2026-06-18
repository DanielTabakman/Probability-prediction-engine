# MSOS Strategy Lab embed shell v1

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) · [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Visual reference:** storyboard `03_ppe_lab` — [`docs/VISION/MSOS/storyboard-v0.6/prototype/html/03_ppe_lab.html`](../VISION/MSOS/storyboard-v0.6/prototype/html/03_ppe_lab.html)  
**Prior chapters:** [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md) · [`SPRINT_MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO.md`](SPRINT_MSOS_STRATEGY_LAB_DISTRIBUTION_DEMO.md)  
**SELECTION:** [`POST_MSOS_STRATEGY_LAB_EMBED_SHELL_V1_SELECTION.md`](POST_MSOS_STRATEGY_LAB_EMBED_SHELL_V1_SELECTION.md)  
**Priority:** **MEDIUM**  
**Baseline:** **`main`**

---

## Sprint intent

Replace the **box-in-box** Strategy Lab experience — full Streamlit app chrome inside a small MSOS iframe — with a **storyboard-aligned chart region** on `/strategy-lab`. MSOS owns the shell (sidebar, header, outcome panel, belief builder); PPE remains authoritative for all distribution math.

**Operator goal:** A visitor on `marketstructureos.com/strategy-lab` sees one cohesive MSOS surface. The PPE analytical core is integrated into the chart panel — not a nested “old site” with its own sidebar and chrome.

**Problem statement (2026-06-18):** Production wiring + distribution demo shipped a live iframe to `/ppe-embed` → `app_demo`. The embed loads the entire Streamlit app inside a ~280px bordered panel. This is honest and functional but visually reads as transitional — not the storyboard `03_ppe_lab` native chart layout.

---

## Preconditions

1. `msos_production_wiring_v1` **COMPLETE** (live embed path + Caddy proxy exist).
2. `msos_workflow_persistence_v1` **COMPLETE** — thesis/expression server store live before embed UX polish (solo-operator bar 1→2→3).
3. Storyboard `03_ppe_lab` assets in-repo ([`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) OPEN).

---

## Acceptance

### A — PPE display boundary (Python, read-only)

1. **Primary path:** Read-only **display payload** endpoint (HTTP from Streamlit or documented proxy path) exposing pre-computed series for the distribution chart region — mean/quartile table + curve coordinates already computed in Python (`src/engine/`, `src/viz/`). **No new math in TypeScript.**
2. **Fallback path (if display API blocked in slice):** Streamlit **embed-only view** — minimal route/page rendering distribution summary + chart only (no Streamlit sidebar, no duplicate MSOS chrome). Document query param or path in evidence.
3. Payload/schema documented in evidence; pytest on Python boundary.

### B — MSOS chart shell (Next.js)

1. `/strategy-lab` chart panel matches storyboard `03_ppe_lab` **layout hierarchy** — belief builder, chart region, legend, controls strip — using MSOS design tokens.
2. Chart region renders from **display API** when available; falls back to **chromeless iframe** with honest degraded copy — not silent full-app embed.
3. Remove or replace the current full-app iframe default (`PpeEmbedBoundary` box-in-box) as primary UX.
4. Outcome panel + MSOS chrome unchanged; fixture metrics may remain until monitor/history live (phase 5).
5. Honest labels: **Live via PPE** when upstream healthy; degraded states visible.

### C — Platform + witness

1. Caddy/compose updates if embed path changes (e.g. `/ppe-embed-minimal/*` or display API proxy).
2. [`docs/DEPLOY/MSOS_WEB_V1.md`](../DEPLOY/MSOS_WEB_V1.md) operator steps updated.
3. Visual witness vs `03_ppe_lab.png` / HTML prototype — material deviation documented if chart is API-rendered SVG vs storyboard static SVG.
4. pytest: MSOS route + PPE boundary; operator checklist in evidence doc.

---

## Implementation options (BUILD chooses at slice time)

| Option | MSOS | PPE | Notes |
|--------|------|-----|-------|
| **1 — Display API + native shell** (preferred) | Fetch JSON; render SVG/canvas from pre-computed points | Export read-only payload from existing distribution pipeline | Best storyboard parity; no TS math |
| **2 — Chromeless embed** (fallback) | Taller iframe; MSOS owns all chrome outside frame | Streamlit embed-only page | Faster; still iframe but no double chrome |
| **3 — Hybrid** | Native chart from API; iframe only for interactive controls not yet in API | Both | Document scope split in evidence |

**Hard rule:** Option must not port payoff engine, disagreement logic, or verification math to TypeScript ([`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md)).

---

## Not now

- Full TypeScript reimplementation of PPE distributions (forbidden)
- Replacing Streamlit as authoritative lab on `app.*`
- Live execution, billing, or auth server changes
- Monitor/History fixture replacement (phase 5)
- Per-user embed scoping (phase 4b)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-EmbedShellV1-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align + witness checklist |
| **MSOS-EmbedShellV1-Product-Slice002** | PRODUCT | PPE_UI | PPE read-only display boundary (embed-only view and/or JSON payload) |
| **MSOS-EmbedShellV1-Product-Slice003** | PRODUCT | MSOS_UI | Strategy Lab chart shell — storyboard `03` chart region |
| **MSOS-EmbedShellV1-Platform-Slice004** | EVIDENCE | PLATFORM | Caddy/compose/env + deploy docs |
| **MSOS-EmbedShellV1-Witness-Slice005** | EVIDENCE | CONTROL | pytest + visual witness vs `03_ppe_lab` |
| **MSOS-EmbedShellV1-Closeout-Slice006** | EVIDENCE | CONTROL | Chapter close |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-18 | v1 — chartered steward request; MEDIUM priority; blocked until workflow persistence COMPLETE |
