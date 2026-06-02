# MSOS P2 — design system + public homepage

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P2)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md)  
**Stack ADR:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**SELECTION:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) · [`POST_MSOS_P2_HOMEPAGE_SELECTION.md`](POST_MSOS_P2_HOMEPAGE_SELECTION.md)

---

## Sprint intent (P2)

Ship the **public MSOS homepage** on `apps/msos-web/` (Next.js 15 App Router + TypeScript) aligned to storyboard v0.6 screen `01_home`, with honest capability labels and no PPE math in the frontend.

## Preconditions (met 2026-06-02)

1. P1 ADR merged.
2. Storyboard v0.6 in-repo; [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) **OPEN**.
3. `msos_p2_homepage` **queued** with relay plan.

## Design system (minimum)

- Tokens derived from storyboard CSS (`prototype/html/style.css`) — typography, color, spacing, radii.
- Reusable layout primitives: public nav, hero, feature row, semantic-lock cards, product-window preview.
- **Live / Soon / Planned** labels for lenses not yet shipped (see MANIFEST future-lens rule).

## Homepage acceptance

1. Route serves public homepage matching storyboard **Read → State → Fit → Learn** narrative.
2. Copy preserves hierarchy: MSOS (platform) → Strategy Lab → PPE (first tool) → BTC options preview only.
3. No false claims: no live prediction-market or perps data; planned surfaces muted.
4. `apps/msos-web/` lint/test pass when added to CI.
5. Optional P2 platform slice: `msos_web` service + Caddy apex route stubbed or wired per ADR (evidence in deploy notes if not live on VPS yet).

## Hard visual closeout

Evidence doc includes screenshot witness of rendered homepage vs [`prototype/screens/01_home.png`](../VISION/MSOS/storyboard-v0.6/prototype/screens/01_home.png); material deviations noted in closeout.

## Not now

- Command Center authenticated routes (P3)
- Strategy Lab / PPE proxy (P4)
- Thesis persistence (P5+)

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P2-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-P2-Product-Slice002** | PRODUCT | MSOS_UI | Next.js app scaffold + homepage |
| **MSOS-P2-Platform-Slice003** | EVIDENCE | PLATFORM | Docker/Caddy wiring for `msos_web` (stub or route) |
| **MSOS-P2-Witness-Slice004** | EVIDENCE | CONTROL | pytest + homepage visual witness |
| **MSOS-P2-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
