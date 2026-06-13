# Backlog operator — add work without touching the queue

**File:** [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)

**Strategic guide:** [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md) · **Urgent / gate:** validation report **DRAFT** blocks auto-select unless `urgent: true` ([`ppe_focus_gate.py`](../../scripts/ppe_focus_gate.py))

You only edit the backlog. The loop propagates rows to the roadmap and queue.

## Quick add (tell an agent or paste JSON)

Append to the `items` array:

```json
{
  "chapterId": "my_snake_case_id",
  "status": "blocked",
  "priority": "medium",
  "focusPlaybookTier": "P2",
  "reason": "[P2] One sentence — what and why",
  "canonRef": "docs/SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md"
}
```

**IRL urgent** (bypasses validation-report gate):

```json
{
  "chapterId": "ops_hotfix",
  "status": "blocked",
  "priority": "high",
  "urgent": true,
  "urgentReason": "IRL: demo tomorrow — VPS CTA broken",
  "focusPlaybookTier": "P0",
  "planPath": "docs/SOP/PHASE_PLANS/....json"
}
```

When a relay plan already exists, add `planPath` and `selectionRecord` (copy a neighboring row).

| Field | Meaning |
|-------|---------|
| `priority` | Mechanical order: `high` → `medium` → `low` |
| `focusPlaybookTier` | Semantic tier: `P0`–`P4` or `defer` (playbook stack) |
| `urgent` | `true` = bypass validation-report gate (log reason) |
| `urgentReason` | One line — shown in operator skip messages |

## Priority

| Value | When to use | Playbook tie-in |
|-------|-------------|-------------------|
| `high` | Blocks P0 wedge or chartered closeout | Tester ops, VPS CTA, legibility |
| `medium` | Default aligned chapter | P1–P2 product/evidence |
| `low` | Nice-to-have after higher tiers | e.g. quant research v2 unless report elevates |

**Before `high` on scope expansion:** playbook **Drift guards** + validation report.

Omit `priority` → treated as **medium**.

Scheduling (`ppe_propagate_queue.py`): **high → medium → low**; ties break by position in the file.

One chapter runs at a time: while a row is `chartered` or `queued`, nothing else promotes.

## Agent hiring (new subagents)

Adding a Cursor subagent under `.cursor/agents/` is like **hiring** — it changes who does work in the operator org.

| Do | Do not |
|----|--------|
| Add a backlog row or SELECTION note naming the role and why | Create agents mid-BUILD without steward visibility |
| Update [`PPE_OPERATOR_MAP_V1.md`](PPE_OPERATOR_MAP_V1.md) verdict table if the role is operator-facing | Spawn parallel managers (one `@ppe-director` only) |
| Keep **Reads / Writes / Never** on the agent file | Give agents open-ended repo access without layer preset |

Operator-facing roles (`ppe-director`, `ppe-*-worker`) are **dev-factory** — charter via control-plane chapter when behavior changes materially.

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

- [`PRODUCT_FOCUS_PLAYBOOK_V1.md`](PRODUCT_FOCUS_PLAYBOOK_V1.md)
- [`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)
- [`MSOS_P8_VALIDATION_REPORT_V1.md`](MSOS_P8_VALIDATION_REPORT_V1.md)
- [`PPE_QUEUE_PROPAGATION_V1.md`](PPE_QUEUE_PROPAGATION_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
