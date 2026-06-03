# MSOS P4 — Strategy Lab / PPE integration

**Controlling canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) (P4)  
**Visual reference:** [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS/storyboard-v0.6/MANIFEST.md) — screen `03_ppe_lab`  
**Stack ADR:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)  
**Acceleration:** [`MSOS_WEBSITE_ACCELERATION_CHECKLIST.md`](MSOS_WEBSITE_ACCELERATION_CHECKLIST.md)  
**SELECTION:** [`POST_MSOS_P4_STRATEGY_LAB_SELECTION.md`](POST_MSOS_P4_STRATEGY_LAB_SELECTION.md) · [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)

---

## Sprint intent (P4)

Expose **PPE as the first Strategy Lab tool** inside the MSOS Next shell, aligned to storyboard `03_ppe_lab`, via the **lowest-risk boundary** (Caddy reverse proxy to Streamlit first; iframe fallback documented in evidence if required).

## Preconditions (at SELECTION)

1. P3 Command Center **COMPLETE** on `main`.
2. P2 design tokens + shell routes reusable in `apps/msos-web/`.
3. Storyboard gate **OPEN**.

## Acceptance

1. Strategy Lab route in `apps/msos-web/` with honest hierarchy (MSOS → Strategy Lab → PPE → BTC options preview).
2. **Caddy proxy** from MSOS host to Streamlit upstream per ADR (path prefix or subdomain — document in platform evidence).
3. **No PPE math in TypeScript** — display/proxy only; trust/degraded states visible when Streamlit exposes them.
4. Lens labels: BTC options **Live** (via PPE); prediction markets / perps **Planned** or **Pending** only.
5. Screenshot witness vs [`prototype/screens/03_ppe_lab.png`](../VISION/MSOS/storyboard-v0.6/prototype/screens/03_ppe_lab.png).

## Not now

- Durable thesis persistence API (P5).
- Live execution or Hyperliquid beyond Pending (program deferred).
- REST/GraphQL PPE API (ADR deferred).

---

## Slice map

| Slice | Plane | Preset | Deliverable |
|-------|--------|--------|-------------|
| **MSOS-P4-Control-Slice001** | EVIDENCE | CONTROL | Charter + queue align |
| **MSOS-P4-Product-Slice002** | PRODUCT | MSOS_UI | Strategy Lab route + embed boundary |
| **MSOS-P4-Platform-Slice003** | EVIDENCE | PLATFORM | Caddy/compose proxy wiring |
| **MSOS-P4-Witness-Slice004** | EVIDENCE | CONTROL | pytest + visual witness |
| **MSOS-P4-Closeout-Slice005** | EVIDENCE | CONTROL | Chapter close |
