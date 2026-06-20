# MSOS user state v1 — evidence status

**Chapter:** `msos_user_state_v1`  
**Display name:** Command Center bridge (PPE snapshots)  
**Priority:** HIGH  
**Status:** **IN PROGRESS** — Witness-Slice004 next (Product #184 + Platform #212 on `main`)  
**Phase plan:** [`PHASE_PLANS/msos_user_state_v1_relay.json`](PHASE_PLANS/msos_user_state_v1_relay.json)  
**Sprint:** [`SPRINT_MSOS_USER_STATE_V1.md`](SPRINT_MSOS_USER_STATE_V1.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-UserStateV1-Control-Slice001 | **CLOSED** | Charter + queue align |
| MSOS-UserStateV1-Product-Slice002 | **DONE** | Command Center + read API — merged `main` #184 |
| MSOS-UserStateV1-Platform-Slice003 | **CLOSED** | Read-only snapshot volume — `main` #212 + deploy doc |
| MSOS-UserStateV1-Witness-Slice004 | PENDING | pytest + operator checklist |
| MSOS-UserStateV1-Closeout-Slice005 | PENDING | Chapter COMPLETE |

## Operator check-in (required at closeout)

- [ ] Command Center shows **recent PPE freezes** (not fixture copy) when snapshots exist on VPS
- [ ] Labels say **snapshot-sourced** — not fake MSOS thesis counts
- [ ] Degraded state when DB missing (no silent fallback to fixtures)
- [ ] Sign-in + embed from production wiring still work
- [ ] Log row in [`VALIDATION_REALITY_CHECKS.md`](VALIDATION_REALITY_CHECKS.md) if demo-ready
