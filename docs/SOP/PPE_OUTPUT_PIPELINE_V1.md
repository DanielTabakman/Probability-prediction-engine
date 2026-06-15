# PPE output pipeline v1

**Plane:** CONTROL-PLANE. **Purpose:** maximize regular chapter output — VM loop host, propagation, BUILD factory, multi-clone scale.

**Related:** [`PPE_AUTOBUILDER_V1.md`](PPE_AUTOBUILDER_V1.md) · [`PPE_MULTI_OPERATOR_V1.md`](PPE_MULTI_OPERATOR_V1.md) · [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)

---

## Lanes (what runs in parallel)

```text
LANE A — Relay conveyor (serial per clone)     headless loop → relay → closeout → propagate
LANE B — BUILD factory (parallel w/ A)         IDE_BUILD → Automation / build-worker
LANE C — Closeout finisher                     post-build watcher → marker → run_ppe_local
LANE D — Steward supply (async)                backlog + plans for N+1 while BUILD runs
LANE E — Sidecars                              snapshots, autobuilder_watch, CI/deploy
```

---

## VM loop host (Phase 0)

1. Hyper-V VM per [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md)
2. `set PPE_LOOP_HOST=1` inside VM only
3. `run_ppe_headless_stack.cmd --ensure`
4. Cursor + Automation **inside VM** (self-contained BUILD)
5. Daily PC: **no** loop (`PPE_STACK_FORBIDDEN=1` or stop stack)

---

## Single-instance recipe

| Step | Command |
|------|---------|
| Health | `ppe_autobuilder.cmd status --write` |
| Stuck | `ppe_autobuilder.cmd advance` |
| Queue repair | `python scripts/ppe_queue_health.py --apply` |
| Continuous | `run_ppe_auto_local_loop.cmd` (via headless stack) |
| Next chapter preview | read `AUTOBUILDER_STATUS.json` → `propagation_preview` |

**Idle heal:** `ppe_operator_status` and `ppe_queue_health` auto-repair roadmap `chartered`→`pending`, sync queue, bootstrap `READY`.

---

## Multi-clone (Phase 2+)

See [`PPE_MULTI_OPERATOR_V1.md`](PPE_MULTI_OPERATOR_V1.md).

---

## Build sequence (control-plane slices shipped)

| Sprint | Delivered |
|--------|-----------|
| A | Queue health idle pipeline + roadmap repair + propagation preview |
| B | Operator instances + multi-operator coordinator |
| C | Per-repo loop singleton + repo-scoped stack detection |
| D | `ppe_autobuilder_watch` for Task Scheduler |

---

## KPIs (weekly)

- Chapters closed / week
- Hours stuck on `IDE_BUILD`
- Closeout → next `READY` latency (target: one loop pass)
- BUILD closeouts without manual `finish_ide_build`
