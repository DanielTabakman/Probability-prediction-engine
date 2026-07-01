# Worker lane policy v1

**Plane:** CONTROL-PLANE · **Purpose:** who may touch what — Cursor vs Codex vs VM vs scripts  
**SSOT for leases:** `python scripts/ppe_worker_lease.py --assess`

**Related:** [`MULTI_AGENT_WORKER_INTERFACE_V1.md`](MULTI_AGENT_WORKER_INTERFACE_V1.md) · [`WORKER_REGISTRY_V1.json`](WORKER_REGISTRY_V1.json)

---

## Lanes

| Lane ID | Runtime | Machine | Use for |
|---------|---------|---------|---------|
| `cursor-desktop` | Cursor native agent / subagents | Daily desktop | Product `IDE_BUILD`, UX, operator threads |
| `codex-app` | Codex desktop app or CLI | Daily desktop | Control-plane slices on `control-plane/*` |
| `vm-relay` | `run_ppe_local.cmd`, finish workers | Hyper-V loop host | `RUN_LOCAL`, `RUN_AUTO`, closeout |
| `scripts-only` | Deterministic pytest / gate | Either | Witness, smoke — no LLM |

Cost lane mapping (metrics): `cursor-desktop` → `cursor-cli` / `acp`; `codex-app` → `codex-cli`.

---

## Routing table (verdict → lane)

| Verdict | Mode | Machine | Primary lane | Never |
|---------|------|---------|--------------|-------|
| `IDE_BUILD` | `IDE_BUILD` | desktop | product → `cursor-desktop`; `control-plane/*` → `codex-app` | VM product BUILD |
| `IDE_BUILD` | `CLOSEOUT_ONLY` | VM | `vm-relay` | desktop re-BUILD |
| `RUN_LOCAL` | any | desktop | handoff → `vm-relay` | local `run_ppe_local.cmd` |
| `RUN_LOCAL` | any | VM | `vm-relay` | second manual finish |
| `RUN_AUTO` | any | VM | `vm-relay` | desktop burst |

---

## Lease rules

1. One active lease per overlapping path set on a dirty tree.
2. Acquire before BUILD: `ppe_worker_lease.py --acquire --worker codex-app --branch … --paths …`
3. Release after ship: `ppe_worker_lease.py --ship --release`
4. `CLOSEOUT_ONLY` forbids new edits under `src/**`.
5. `resolve_lease` in burst plan → stop; do not spawn second BUILD worker.

---

## Tier 2 cost preference

When branch prefix does not decide (e.g. `main` control-plane patch):

- Read 7d cost lanes from `ppe_workflow_cost.summarize_by_lane`
- Prefer `codex-app` when `codex-cli` count is lower than `cursor-cli` + `acp` combined
- Prefer `cursor-desktop` for slices with `src/**` in lease scope regardless of cost

Policy code: `prefer_build_lane()` in `scripts/ppe_worker_lease.py`.

---

## Templates

- [`templates/ACTIVE_LEASE.template.json`](templates/ACTIVE_LEASE.template.json)
- [`templates/WORK_DISPATCH.template.json`](templates/WORK_DISPATCH.template.json)
