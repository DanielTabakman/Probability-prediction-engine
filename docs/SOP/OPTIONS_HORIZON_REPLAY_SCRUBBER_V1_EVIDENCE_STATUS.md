# Options Horizon replay scrubber v1 — evidence status

**Chapter:** `horizon_replay_scrubber_v1`  
**Status:** **CHARTERED** (awaiting archive replay gate + relay)  
**SELECTION:** [`POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md`](POST_OPTIONS_HORIZON_REPLAY_SCRUBBER_V1_SELECTION.md)  
**Phase plan:** [`PHASE_PLANS/horizon_replay_scrubber_v1_relay.json`](PHASE_PLANS/horizon_replay_scrubber_v1_relay.json)

| Slice | Status | Notes |
|-------|--------|-------|
| Horizon-ReplayScrub-Control-Slice001 | **PENDING** | Charter package |
| Horizon-ReplayScrub-Product-Slice002 | **PENDING** | Scrubber UI + archive API wiring |
| Horizon-ReplayScrub-Closeout-Slice003 | **PENDING** | Chapter close |

## Archive gate

| Field | Value |
|-------|--------|
| `replay_threshold_days` | 30 |
| `replay_ready` | false (promote queue to READY when true; backlog **blocked** until gate) |
| Collector | [`HORIZON_SURFACE_COLLECTOR_OPS_V1.md`](HORIZON_SURFACE_COLLECTOR_OPS_V1.md) |
