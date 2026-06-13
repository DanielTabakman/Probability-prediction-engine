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

Wired for auto-loop (2026-06-12):

- **Roadmap:** `ready` (before LOW `mvp1_distribution_quant_research_v2`)
- **Queue:** first `READY` row
- **Manifest:** `ACTIVE_PHASE_MANIFEST.json` → this plan, `status: READY`, `workerMode: deterministic`

When the loop is running, `run_ppe.cmd` / `run_ppe_auto_local_loop.cmd` will drive slices 002–004 after Slice001 closeout. No manual `--plan` needed.
