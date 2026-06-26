# Options Horizon v1 — evidence status

**Program:** [`OPTIONS_HORIZON_PROGRAM_V1.md`](OPTIONS_HORIZON_PROGRAM_V1.md)  
**As-of:** 2026-06-26

---

## Shipped in this pass

| Chapter | Status | Evidence |
|---------|--------|----------|
| `horizon_charter_v1` | **COMPLETE** | Charter + vision contracts + backlog |
| `horizon_surface_archive_v1` | **COMPLETE** | `collect_horizon_surface_snapshot.py`, `horizon_surface_archive.py`, API |
| `horizon_chart_payload_v1` | **COMPLETE** | `horizon_chart_payload.py`, Streamlit spike |
| `horizon_readonly_chart_v1` | **COMPLETE** | MSOS `/options-horizon` route |
| `horizon_region_draw_v1` | **COMPLETE** | Box draw + localStorage RegionIntent |
| `horizon_expression_bridge_v1` | **COMPLETE** | Implied mass preview + Strategy Lab deep-link |

---

## Deferred (by design)

| Chapter | Gate |
|---------|------|
| `horizon_replay_scrubber_v1` | ≥30 days surface archive |
| `horizon_liquidation_overlay_v1` | Data vendor TBD |
| `horizon_outcome_ghosts_v1` | After replay scrubber |

---

## Operator commands

```bash
python scripts/collect_horizon_surface_snapshot.py
curl -s "http://localhost:8765/horizon/chart.json?asset=BTC" | head
curl -s "http://localhost:8765/horizon/surface.json?latest=1" | head
```

---

## Witness checklist

- [ ] Daily surface collector on VM cron
- [ ] MSOS nav shows Options Horizon
- [ ] Region draw → implied mass % → Open in Strategy Lab
- [ ] No execution copy in UI
