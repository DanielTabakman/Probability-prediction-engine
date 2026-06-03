# PPE queue propagation v1

Deterministic **queue propagation** from a structured backlog — no Cursor API required for known chapters.

## Why

| Source | Propagates queue? |
|--------|-------------------|
| `PHASE_SELECTION_ROADMAP.json` | Mechanical advance after closeout (`pending` → `READY`) |
| `PHASE_CHAPTER_BACKLOG.json` | **New:** append next `queued` chapter when roadmap is idle |
| `ppe_steward_cursor.py` | Open-ended SELECTION when backlog is empty / blocked |

**Enough information?** Yes for **backlog rows** with `planPath` + optional `scaffold: true`. No for vague frontier prose — use `blocked` + steward or Cursor steward hook.

## Backlog item statuses

| Status | Meaning |
|--------|---------|
| `queued` | Next to propagate when roadmap has no valid `pending` |
| `chartered` | On roadmap (pending/ready/done) |
| `done` | Synced when roadmap row is `done` |
| `blocked` | Needs human direction before auto-charter |
| `skipped` | Intentionally out of auto pipeline |

## Workflow hook

```text
run_ppe.cmd
  → prepare_selection_idle
      → sync roadmap → queue
      → maybe_propagate_queue     ← NEW (backlog → pending)
      → maybe_run_steward_cursor  (if still idle)
      → bootstrap pending → READY
```

Enable/disable: `PPE_AUTO_PROPAGATE_QUEUE=1` (default **on**), or `"propagateBacklog": true` in [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) via **`run_ppe_auto.cmd`**.

## CLI

```bash
python scripts/ppe_propagate_queue.py --repo-root . --sync-only --apply
python scripts/ppe_propagate_queue.py --repo-root . --apply
```

## Adding chapters

1. Append a row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) with `status: queued`.
2. Set `planPath` to an existing phase plan **or** `scaffold: true` + `chapterTitle` / `workerMode`.
3. Run `run_ppe.cmd --continuous` — propagation runs automatically when idle.

Mark **`blocked`** when the chapter must not start yet (e.g. waits on prior MSOS phase). Rows with **`planPath`** are **auto-promoted to `queued`** when every earlier backlog row is `done` or `skipped` — triggered from `post_relay_continue` after chapter closeout and from `maybe_propagate_queue` when idle.

Mark **`blocked`** without `planPath` when canon is not ready (steward must add a relay plan before promotion can run).

## Related

- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md)
