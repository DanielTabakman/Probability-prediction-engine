# MVP1 distribution timeseries collector v1 — SELECTION

**Chapter:** `mvp1_distribution_timeseries_collector_v1`  
**Priority:** **LOW** · **P2** · side channel  
**Parent:** dist quant v2 daily snapshot MVP  
**Relay plan:** [`PHASE_PLANS/mvp1_distribution_timeseries_collector_v1_relay.json`](PHASE_PLANS/mvp1_distribution_timeseries_collector_v1_relay.json)

## Status

**SELECTED** 2026-06-29 — harden `collect_distribution_stats_snapshot.py` + VM scheduled task + retention policy.

## Scope

- VM daily task install script (mirror horizon collector pattern)  
- Retention + `archive_meta` for distribution snapshots  
- Operator runbook in `PPE_IDE_NATIVE_OPERATOR_V1.md`  

## Non-goals

- MSOS historical download UI; multi-asset batch export
