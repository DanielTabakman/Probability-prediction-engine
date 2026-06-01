# PPE IDE-native operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run relay chapters without Cursor API / ACP when credits are exhausted.

---

## Quick start

From repo root:

```bat
run_ppe_auto_local_loop.cmd
```

Monitor (optional):

```powershell
.\scripts\watch_ppe_live.ps1
```

When the loop stops for a **product** slice:

1. Read `artifacts/orchestrator/LAST_RUN_REPORT.md` or `OPERATOR_GUARD_REPORT.md`.
2. **IDE BUILD** — new Cursor Agent thread; load `docs/SOP/AGENT_CONTINUITY_BRIEF.md` + sprint spec; use [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).
3. Commit on the phase plan `buildBranch`.
4. **`run_ppe_local.cmd`** — finish smoke/closeout for that chapter.
5. Restart or let the loop continue for the next chapter.

---

## Two profiles

Use **one profile at a time**.

| When | Entry (continuous) | Config |
|------|-------------------|--------|
| **No API credits** | `run_ppe_auto_local_loop.cmd` | [`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json) |
| **Have API credits** | `run_ppe_auto_acp_loop.cmd` | [`PPE_AUTO_OPERATOR.acp.json`](PPE_AUTO_OPERATOR.acp.json) |

Plain `run_ppe_auto.cmd` uses [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) (defaults to **local**).

Set profile explicitly: `set PPE_OPERATOR_PROFILE=local` or `=acp`.

---

## What runs unattended

| Step | Local profile |
|------|----------------|
| Backlog → queue propagation | Yes |
| Steward charter when idle | **No** (no API) |
| Control / smoke / closeout slices | Yes (pytest/scripts) |
| Product slices | **No** — guard stop or STOP_FOR_REVIEW |

---

## Jump-in matrix

| Signal | You do |
|--------|--------|
| Guard exit **7** / `PRODUCT_BLOCKED` | IDE BUILD → commit → `run_ppe_local.cmd` |
| `SCOPE_AMBIGUITY` on product slice | Same |
| Queue idle, no `READY` | Add `queued` row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) |
| Test/smoke fail | Fix code or env; `run_ppe_local.cmd` |
| Chapter closeout complete | New Cursor thread; [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) only |

---

## Related

- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md)
- [`PPE_WORKER_MODES_V1.md`](PPE_WORKER_MODES_V1.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
