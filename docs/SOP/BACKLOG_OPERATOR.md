# Backlog operator — add work without touching the queue

**File:** [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)

You only edit the backlog. The loop propagates rows to the roadmap and queue.

## Quick add (tell an agent or paste JSON)

Append to the `items` array:

```json
{
  "chapterId": "my_snake_case_id",
  "status": "blocked",
  "priority": "medium",
  "reason": "[MEDIUM] One sentence — what and why",
  "canonRef": "docs/SOP/MVP1_FRONTIER.md"
}
```

When a relay plan already exists, add `planPath` and `selectionRecord` (copy a neighboring row).

## Priority

| Value | When to use |
|-------|-------------|
| `high` | Demo blockers, ops fixes, urgent product path |
| `medium` | Default — most chapters |
| `low` | Nice-to-have; runs after high and medium are cleared |

Omit `priority` → treated as **medium**.

Scheduling (`ppe_propagate_queue.py`): **high → medium → low**; ties break by position in the file. **List order no longer gates promotion** — append anywhere.

One chapter runs at a time: while a row is `chartered` or `queued`, nothing else promotes.

## Status

| Status | Use |
|--------|-----|
| `blocked` | **Default for new ideas** — waits until pipeline idle |
| `queued` | Rare — force “run next when idle” (needs `planPath`) |
| `skipped` | Never auto-run |

Do not set `done` / `chartered` by hand.

## No plan yet?

`blocked` without `planPath` is fine — it waits until someone charters a relay plan under `docs/SOP/PHASE_PLANS/`.

## Do not edit

- `PHASE_QUEUE.json`
- `PHASE_SELECTION_ROADMAP.json`
- `ACTIVE_PHASE_MANIFEST.json`

## Related

- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
