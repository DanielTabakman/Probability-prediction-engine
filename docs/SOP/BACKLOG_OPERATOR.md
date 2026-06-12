# Backlog operator — add work without touching the queue

**File:** [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)

**Strategic guide (read before adding rows):** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — priority stack P0–P4, drift guards, validation gates. After P8 cohort data: [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) §6 **bosses** the next chapter.

You only edit the backlog. The loop propagates rows to the roadmap and queue.

## Quick add (tell an agent or paste JSON)

Append to the `items` array:

```json
{
  "chapterId": "my_snake_case_id",
  "status": "blocked",
  "priority": "medium",
  "reason": "[MEDIUM] One sentence — what and why (cite playbook tier: P0/P1/P2 or defer)",
  "canonRef": "docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md",
  "focusPlaybookTier": "P2"
}
```

Optional field **`focusPlaybookTier`:** `P0` | `P1` | `P2` | `P3` | `P4` | `defer` — documents alignment with [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) priority stack (agents/stewards; not read by propagate script today).

When a relay plan already exists, add `planPath` and `selectionRecord` (copy a neighboring row).

## Priority

Mechanical scheduling: **high → medium → low** (`ppe_propagate_queue.py`). **Semantic priority** (what deserves `high`) comes from the playbook — not urgency alone.

| Value | When to use | Playbook tie-in |
|-------|-------------|-------------------|
| `high` | Blocks **P0 wedge proof** or **P1 chartered closeout** | Tester sessions, VPS CTA, lab legibility that improves 15-second comprehension |
| `medium` | Default — chartered product/evidence aligned with playbook P1–P2 | MSOS/PPE slices that support thesis → payoff loop without widening scope |
| `low` | Nice-to-have; runs after high and medium are cleared | e.g. `mvp1_distribution_quant_research_v2` unless validation report elevates it |

**Before `high` on scope expansion** (new asset, execution, platform surface, paywall automation): check playbook **Drift guards** + validation report fork. If unclear, `blocked` without `planPath` until steward SELECTION.

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

- [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) — strategic focus, anti-drift, validation gates
- [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md) — rollup + next SELECTION after tester cohort
- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
