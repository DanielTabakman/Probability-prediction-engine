---
archived: true
chapter_id: msos_production_wiring_v1
closed: 2026-06-17
---

# MSOS production wiring v1 — evidence status

**Chapter:** `msos_production_wiring_v1`  
**Priority:** HIGH  
**Status:** **COMPLETE** 2026-06-17  
**Phase plan:** [`PHASE_PLANS/msos_production_wiring_v1_relay.json`](PHASE_PLANS/msos_production_wiring_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_PRODUCTION_WIRING_V1.md`](SPRINT_MSOS_PRODUCTION_WIRING_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-ProdWireV1-Control-Slice001 | **CLOSED** | Charter + queue align |
| MSOS-ProdWireV1-Product-Slice002 | **CLOSED** | Sign-in, CTA, nav/button wiring — merged `main` #170 (`cff9fb5`) |
| MSOS-ProdWireV1-Platform-Slice003 | **CLOSED** | Compose/Caddy/env + deploy docs — merged `main` #171 (`425d831`) |
| MSOS-ProdWireV1-Witness-Slice004 | **CLOSED** | pytest + operator checklist |
| MSOS-ProdWireV1-Closeout-Slice005 | **CLOSED** | Chapter COMPLETE + operator check-in (`MSOS-ProdWireV1-Closeout-Slice005`) |

## Operator check-in (required at closeout)

- [ ] `https://marketstructureos.com/` — **Sign in** opens `app.marketstructureos.com` (Cloudflare Access)
- [ ] Research beta CTA visible when `PPE_RESEARCH_OFFER_*` set on VPS
- [ ] `/strategy-lab` — PPE embed live (not “Embed pending”) when env built
- [ ] Nav links reach Command Center, Strategy Lab, Monitor, History, Learn
- [ ] `app.marketstructureos.com` — Streamlit lab + snapshots unchanged
- [ ] Command Center still labeled preview/fixture for KPIs (honest until user-state chapter)
- [ ] Log one row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) if demo-ready
