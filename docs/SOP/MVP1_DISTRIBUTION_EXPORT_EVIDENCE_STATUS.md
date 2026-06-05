# MVP1 distribution export — evidence status

**Chapter:** `mvp1_distribution_export`  
**Status:** **PENDING** — chartered 2026-06-05; awaits relay after MSOS P4 COMPLETE  
**Phase plan:** [`PHASE_PLANS/mvp1_distribution_export_relay.json`](PHASE_PLANS/mvp1_distribution_export_relay.json)  
**Sprint:** [`SPRINT_MVP1_DISTRIBUTION_EXPORT.md`](SPRINT_MVP1_DISTRIBUTION_EXPORT.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-DistExport-Control-Slice001 | PENDING | Charter witness |
| MVP1-DistExport-Product-Slice002 | PENDING | `ppe-core` quantile helpers + tests |
| MVP1-DistExport-Product-Slice003 | PENDING | CSV serializer + implied-lab download |
| MVP1-DistExport-Smoke-Slice004 | PENDING | Full pytest witness |
| MVP1-DistExport-Closeout-Slice005 | PENDING | Frontier COMPLETE + share instructions |

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after PR merge  
- [ ] Private app implied lab → **Download distribution stats (CSV)**  
- [ ] Confirm row count ≈ `2 × N expiries` (lognormal + BL per expiry)  
- [ ] Send CSV + one-line schema pointer to research contact
