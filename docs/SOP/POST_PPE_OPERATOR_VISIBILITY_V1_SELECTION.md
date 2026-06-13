# POST PPE operator visibility v1 — SELECTION

**Status:** **SELECTION COMPLETE** — chapter chartered on **`main`**.

**As-of:** 2026-06-12

---

## Why now

Daily operator flow (phone ntfy → Termius/RDP → IDE BUILD) lacked a single **inbox** view: active slice ownership, blockers, and queue preview were spread across guard reports, manifest JSON, and memory. Paperclip-inspired visibility improvements ship as a bounded **dev-factory** chapter without replacing relay/orchestrator.

## Charter

| Field | Value |
|-------|-------|
| Chapter | `ppe_operator_visibility_v1` |
| Priority | **high** |
| Plan | [`PHASE_PLANS/ppe_operator_visibility_v1_relay.json`](PHASE_PLANS/ppe_operator_visibility_v1_relay.json) |
| Sprint | [`SPRINT_PPE_OPERATOR_VISIBILITY_V1.md`](SPRINT_PPE_OPERATOR_VISIBILITY_V1.md) |
| Layer | `dev-factory` / `CONTROL` preset |
| Operator map | [`PPE_OPERATOR_MAP_V1.md`](PPE_OPERATOR_MAP_V1.md) |

## Slice001 scope (this pass)

- `ACTIVE_IDE_SLICE.json` checkout on IDE starter generation; clear on `mark_ide_product_ready`
- **Inbox block** in `OPERATOR_STATUS.md` (owner, active slice, blocker, next command)
- **Queue preview** — next 3 `READY` items from `PHASE_QUEUE.json`
- Manual docs: operator map, role cards, adapter decision tree, agent-hiring rule

## Not now

- `BLOCKERS.md` auto-generator (Slice002)
- Workflow metrics cost tags (Slice002)
- Static HTML dashboard (defer)
- External Paperclip integration

## Operator

After Slice001 lands: `python scripts/ppe_operator_status.py` — confirm inbox section. Loop: `run_ppe.cmd --plan docs/SOP/PHASE_PLANS/ppe_operator_visibility_v1_relay.json` when manifest is set **READY**.
