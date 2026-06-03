# Workflow efficiency operator v1

**Plane:** CONTROL-PLANE. **Purpose:** operational runbook for token, user-time, and throughput optimization.

Cross-refs: [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_METRICS_V1.md`](WORKFLOW_METRICS_V1.md)

---

## Four currencies

| Currency | Lever |
|----------|--------|
| **Tokens** | Local auto loop + IDE BUILD starter (one file) |
| **User time** | Guard resume → generated starter; ≤2 roundtrips per slice |
| **Computer time** | `run_pushable_gate.py` tiered gate (unchanged) |
| **Real-life time** | `workflow_metrics.cmd summary` — weighted slices per active hour |

---

## Daily (local profile)

1. `run_ppe_auto_local_loop.cmd`
2. Optional: `workflow_metrics.cmd session start` at desk open

---

## Daily (local profile)

1. `run_ppe_auto_local_loop.cmd` — **auto-starts** a metrics session and logs loop events.
2. Metrics data: `artifacts/workflow_metrics/` (gitignored).

---

## Product guard stop (automatic)

When the loop hits `PRODUCT_BLOCKED` (exit 7):

1. **IDE BUILD starter is auto-generated** under `artifacts/orchestrator/IDE_BUILD_STARTER_<sliceId>.md`.
2. Guard event logged to `artifacts/workflow_metrics/events.jsonl`.
3. Open **new** Cursor Agent thread → `@` the starter file.
4. After BUILD → `mark_ide_product_ready.cmd` (logs product slice close) → `run_ppe_local.cmd`.

Manual regen if needed:

```bat
generate_ide_build_starter.cmd <sliceId> <phasePlanPath>
```

---

## Context bands (advisory)

Heuristics from [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md):

- Sprint spec ≤200 lines → NORMAL; 201–400 → WATCH; >400 → ESCALATE (continuous run stops)
- Generated BUILD packet target ≤~80 lines
- One Cursor thread per slice/chapter; no SELECTION+BUILD+PR mega-thread

---

## Commands

| Command | Purpose |
|---------|---------|
| `generate_ide_build_starter.cmd` | One-file IDE BUILD bundle |
| `generate_build_packet.cmd` | Slim paths-only BUILD packet |
| `python scripts/ppe_context_preflight.py` | Advisory band check before BUILD |
| `workflow_metrics.cmd session start/stop` | Session logging (~30s) |
| `workflow_metrics.cmd slice close` | Per-slice roundtrips + size |
| `workflow_metrics.cmd summary --days 7` | Throughput review |
| `workflow_metrics.cmd export-csv` | Paste into Sheet tabs |

Data lives under `artifacts/workflow_metrics/` (gitignored).

---

## Thread rules

- **Steward thread:** SELECTION, manifest, read `LAST_RUN_REPORT.md`
- **IDE BUILD thread:** starter file only (not steward chat)
- **After closeout:** new thread + `AGENT_CONTINUITY_BRIEF.md` only ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md))

---

## Related

- [`PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md`](PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md)
- [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md)
