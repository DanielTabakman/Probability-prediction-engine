# PPE queue propagation v1

Deterministic **queue propagation** from a structured backlog — no Cursor API required for known chapters.

## Why

| Source | Propagates queue? |
|--------|-------------------|
| `PHASE_SELECTION_ROADMAP.json` | Mechanical advance after closeout (`pending` → `READY`) |
| `PHASE_CHAPTER_BACKLOG.json` | Append highest-priority `queued` chapter when roadmap is idle |
| `ppe_steward_cursor.py` | Open-ended SELECTION when backlog is empty / blocked |

**Enough information?** Yes for **backlog rows** with `planPath` + optional `scaffold: true`. No for vague frontier prose — use `blocked` + steward or Cursor steward hook.

## Backlog item statuses

| Status | Meaning |
|--------|---------|
| `queued` | Ready to propagate when roadmap has no valid `pending` |
| `chartered` | On roadmap (pending/ready/done) |
| `done` | Synced when roadmap row is `done` |
| `blocked` | Default for new rows; auto-promotes when pipeline idle |
| `skipped` | Intentionally out of auto pipeline |

| Field | Meaning |
|-------|---------|
| `priority` | Optional: `high` \| `medium` \| `low` (default `medium`) — selects among eligible rows |

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

## Priority scheduling

Among eligible backlog rows (`queued`, or `blocked` with `planPath` when pipeline idle):

1. **high** before **medium** before **low**
2. Same tier → earlier row in the `items` array wins (stable tie-break)

**Pipeline idle** = no row in `chartered` or `queued`. Only one chapter propagates at a time.

Operator cheat sheet: [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md).

## Adding chapters

1. Read [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — tier + drift guards.
2. Append a row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) with `status: blocked`, `priority`, and optional `focusPlaybookTier` / `urgent` per [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md).
3. Set `planPath` when a phase plan exists **or** omit until chartered.
4. Run `run_ppe.cmd --continuous` — propagation runs automatically when idle (blocked by validation-report gate unless `urgent: true`).

Rows with **`planPath`** auto-promote `blocked` → `queued` when the pipeline is idle — from `post_relay_continue` after closeout and from `maybe_propagate_queue` when idle.

Mark **`blocked`** without `planPath` when canon is not ready (steward must add a relay plan before promotion can run).

## Related

- [`BACKLOG_OPERATOR.md`](BACKLOG_OPERATOR.md)
- [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)
- [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md)
- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_STEWARD_CURSOR_V1.md`](PPE_STEWARD_CURSOR_V1.md)
