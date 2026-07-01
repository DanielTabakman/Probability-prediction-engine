---
archived: true
chapter_id: mvp1_distribution_quant_research_v2
closed: 2026-06-13
---

# MVP1 distribution quant research v2 — evidence status

**Chapter:** `mvp1_distribution_quant_research_v2`  
**Priority:** LOW  
**Status:** **COMPLETE** 2026-06-13  
**Phase plan:** [`PHASE_PLANS/mvp1_distribution_quant_research_v2_relay.json`](PHASE_PLANS/mvp1_distribution_quant_research_v2_relay.json)  
**Sprint:** [`SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md`](SPRINT_MVP1_DISTRIBUTION_QUANT_RESEARCH_V2.md)

| Slice | Status | Notes |
|-------|--------|-------|
| MVP1-DistQuantV2-Control-Slice001 | CLOSED | Charter witness |
| MVP1-DistQuantV2-Product-Slice002 | CLOSED | Tail quantiles + P(>K) ladder (`implied_distribution.py`) |
| MVP1-DistQuantV2-Product-Slice003 | CLOSED | Extended CSV + summary panel (IQR, BL−LN gap) |
| MVP1-DistQuantV2-Product-Slice004 | CLOSED | `collect_distribution_stats_snapshot.py` + runbook |
| MVP1-DistQuantV2-Smoke-Slice005 | CLOSED | pytest witness |
| MVP1-DistQuantV2-Closeout-Slice006 | CLOSED | Chapter COMPLETE |

## Deliverables

- Tail quantiles (q05/q10/q90/q95) and strike-level P(S > K) helpers in `src/engine/implied_distribution.py`
- Extended distribution CSV + summary panel quant columns in `src/viz/`
- Daily snapshot collector → `artifacts/distribution_snapshots/`

## Share checklist (operator)

- [ ] Chapter COMPLETE on `main` after PR merge
- [ ] Implied lab → **Download distribution stats (CSV)** shows IQR and gap columns
- [ ] Optional: `python scripts/collect_distribution_stats_snapshot.py`
