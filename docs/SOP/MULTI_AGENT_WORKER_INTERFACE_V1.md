# Multi-agent worker interface v1

**Plane:** CONTROL-PLANE · **Status:** Tier 1 + Tier 2 (leases, lanes, cost routing, synthetic events)  
**Audience:** operators, agents, future external adopters

**Related:** [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md) · [`WORKER_REGISTRY_V1.json`](WORKER_REGISTRY_V1.json) · verdict SSOT [`PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md`](PPE_CANONICAL_OPERATOR_SCRIPTS_V1.md) · routing [`AGENT_ROUTING_V1.md`](AGENT_ROUTING_V1.md)

---

## Purpose

PPE runs **multiple coding agents** on one repo (Cursor native, Codex app/CLI, VM relay). Without a thin contract, agents fight over branches and paths.

This doc defines the **Agent Relay Control Plane (ARCP)** vocabulary — not a second orchestrator. `ppe_operator_status.py` remains verdict SSOT; leases add **conflict prevention** and **lane routing**.

---

## Architecture (router, not pyramid)

```
OPERATOR_STATUS (verdict SSOT)
        ↓
BURST_PLAN / router (ppe_burst_plan.py)
        ↓
ACTIVE_LEASE (exclusive branch + path scope)
        ↓
prefer_build_lane (cost + branch heuristics — Tier 2)
        ↓
Worker runtime: cursor-desktop | codex-app | vm-relay | scripts-only
        ↓
WORK_DISPATCH.json (handoff envelope)
WORKER_EVENTS.json (synthetic git/gate inference — Tier 2)
```

Cursor, Codex, and VM relay are **workers**. PPE is the **router**.

---

## Core concepts

| Concept | Meaning | PPE artifact |
|---------|---------|--------------|
| **WorkItem** | One bounded slice (BUILD, closeout, relay) | Phase slice / chapter |
| **Verdict** | What class of work | `IDE_BUILD`, `RUN_LOCAL`, … |
| **Mode** | Constraint on verdict | `CLOSEOUT_ONLY` |
| **Lane** | Machine + runtime | `cursor-desktop`, `codex-app`, … |
| **Lease** | Exclusive lock on branch + paths | `artifacts/control_plane/ACTIVE_LEASE.json` |
| **Dispatch** | Handoff package for a worker | `artifacts/control_plane/WORK_DISPATCH.json` |
| **Events** | Inferred worker progress | `artifacts/control_plane/WORKER_EVENTS.json` |
| **Registry** | Worker capabilities | [`WORKER_REGISTRY_V1.json`](WORKER_REGISTRY_V1.json) |

---

## Contracts

Templates (copy to `artifacts/control_plane/` when dispatching):

- [`templates/ACTIVE_LEASE.template.json`](templates/ACTIVE_LEASE.template.json)
- [`templates/WORK_DISPATCH.template.json`](templates/WORK_DISPATCH.template.json)

Implementation: `python scripts/ppe_worker_lease.py`

| Command | Purpose |
|---------|---------|
| `ppe_worker_lease.py --assess` | Lease vs git tree + preferred lane |
| `ppe_worker_lease.py --write-dispatch` | Emit `WORK_DISPATCH.json` |
| `ppe_worker_lease.py --infer-events` | Emit `WORKER_EVENTS.json` (Tier 2) |
| `ppe_worker_lease.py --acquire --worker …` | Hold lease before BUILD |
| `ppe_worker_lease.py --release` | Clear lease after gate + commit |

Router integration:

- `ppe_burst_plan.py` → `resolve_lease` blocks burst when lease conflicts
- `ppe_operator_status.py` → lane + lease lines in `OPERATOR_STATUS.md`

---

## Lane policy (summary)

Full table: [`WORKER_LANE_POLICY_V1.md`](WORKER_LANE_POLICY_V1.md).

| Work kind | Primary lane | Fallback |
|-----------|--------------|----------|
| Product `IDE_BUILD` | `cursor-desktop` | `codex-app` |
| Control-plane `IDE_BUILD` | `codex-app` | `cursor-desktop` |
| `RUN_LOCAL` finish (desktop) | SSH → `vm-relay` | — |
| `CLOSEOUT_ONLY` witness | `scripts-only` / `vm-relay` | — |

**Tier 2 cost preference:** when branch heuristic is ambiguous, `prefer_build_lane` uses 7d `ppe_workflow_cost` lane counts (`codex-cli` vs `cursor-cli`/`acp`) — cheaper lane wins if within policy.

---

## Lifecycle

```
Queued → Leased → Dispatched → InProgress → Gated → Committed → Relayed
```

Release lease on: gate pass + commit, `--release`, or TTL expiry.

---

## Sharing externally

Copyable without PPE: lane policy, `ACTIVE_LEASE` + `WORK_DISPATCH` JSON shapes, `ppe_worker_lease.py`.

Keep PPE VM relay / `DESKTOP_CONTINUE` as reference implementation only.
