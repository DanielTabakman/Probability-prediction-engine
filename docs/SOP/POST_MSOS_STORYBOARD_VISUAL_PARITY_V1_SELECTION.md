# MSOS storyboard visual parity v1 — SELECTION

**Chapter:** `msos_storyboard_visual_parity_v1`  
**Priority:** **MEDIUM**  
**Relay plan:** [`PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json`](PHASE_PLANS/msos_storyboard_visual_parity_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md`](SPRINT_MSOS_STORYBOARD_VISUAL_PARITY_V1.md)

## Status

**SELECTED** 2026-06-12 — operator request: MSOS surfaces should match storyboard v0.6 pictures, not only narrative parity.

**Blocked until** `mvp1_distribution_quant_research_v2` **COMPLETE** (smoke + closeout on current LOW chapter).

## Preconditions (met)

| Check | Status |
|-------|--------|
| MSOS P2–P8 routes on `main` | Yes — functional journey shipped |
| Storyboard v0.6 HTML + CSS in-repo | Yes — [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) |
| Prior visual witnesses | Deferred across P2–P8 evidence docs — this chapter closes that gap |

## Scope (in)

- Pixel/layout parity vs storyboard HTML prototypes (`prototype/html/*.html` + `style.css`) for screens `01`–`09`
- Shared design tokens, spacing, typography, panel chrome in `apps/msos-web/`
- Operator screenshot witness per screen in evidence doc
- VPS deploy of `msos_web` + honest routing notes (apex vs `app.*` Streamlit)

## Scope (out)

- PPE math, charts, or trust semantics in TypeScript
- Live execution, paywall, or auth server beyond existing ADR
- Replacing Streamlit embed interior — only MSOS chrome around embed

## First slice at SELECTION

`MSOS-VisParityV1-Control-Slice001`

## Local compare loop

1. Storyboard: open `docs/VISION/MSOS/storyboard-v0.6/prototype/html/<screen>.html`
2. Built app: `cd apps/msos-web && npm run dev` → matching route
3. Capture side-by-side screenshot; note deviations in evidence doc before closeout
