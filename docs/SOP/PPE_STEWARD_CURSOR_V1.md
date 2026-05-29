# PPE Cursor steward v1 (local SDK)

Automates **intellectual SELECTION** when the roadmap has no next `pending` chapter: a **local** Cursor SDK agent reads steering docs and charters the next **evidence-only** relay chapter.

## What “hook” means

A **hook** is not a separate operator step. `run_ppe.cmd` already calls `ppe_auto_select` → `prepare_selection_idle`. The steward hook runs **inside** that path:

```text
run_ppe.cmd
  → ppe_auto_select
      → prepare_selection_idle
          → sync roadmap → queue
          → **maybe_run_steward_cursor**   ← hook (this doc)
          → bootstrap first pending → READY
      → select READY → manifest
  → relay phase …
```

You do not run the steward by hand unless debugging.

## Enable

**Recommended:** [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) with `"stewardCharter": true` and **`run_ppe_auto.cmd`** (see [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)).

Manual env:

```bat
pip install cursor-sdk
set CURSOR_API_KEY=your_key
set PPE_AUTO_STEWARD=1
set PPE_WORKER_MODE=deterministic
set PPE_SKIP_ACP=1
run_ppe.cmd --continuous
```

| Variable | Default | Meaning |
|----------|---------|---------|
| `PPE_AUTO_STEWARD` | off unless `PPE_AUTO_OPERATOR.json` has `stewardCharter: true` | `1` runs steward when idle |
| `CURSOR_API_KEY` | — | Required for SDK (local runtime still uses API) |
| `PPE_STEWARD_MODEL` | `composer-2.5` | Model id |
| `PPE_STEWARD_ALLOW_PRODUCT` | off | Allow `workerMode` other than `deterministic` |

**Local runtime** (`LocalAgentOptions(cwd=repo)`) runs tools against your machine — no Cursor cloud VM — which is usually cheaper than cloud agents for repo edits.

## When it runs

All must be true:

- `PPE_AUTO_STEWARD=1`
- Manifest **COMPLETE**, empty `phasePlanPath`
- No **READY** queue row
- No **pending** roadmap row with a **valid** phase plan
- Roadmap enabled (`PHASE_SELECTION_ROADMAP.json` exists)

## What the steward does

1. Builds a bounded prompt from `AGENT_CONTINUITY_BRIEF.md`, `MVP1_FRONTIER.md`, roadmap.
2. `Agent.prompt(..., local=repo)` — Cursor SDK **local**.
3. Expects `artifacts/steward/last_proposal.json` (agent may also scaffold `docs/SOP/` files).
4. Appends one roadmap row: `status: pending`, `workerMode: deterministic`.
5. `prepare_selection_idle` then **bootstraps** `pending` → `READY` and `ppe_auto_select` writes the manifest.

Steward does **not** set `READY` directly (human policy: charter first, then mechanical bootstrap).

## Debug CLI

```bat
python scripts/ppe_steward_cursor.py --repo-root . --check
python scripts/ppe_steward_cursor.py --repo-root . --apply
python scripts/ppe_steward_cursor.py --repo-root . --proposal artifacts/steward/last_proposal.json --apply
```

## Safety

- Default: **deterministic** / evidence-only chapters only.
- Must not edit `src/` or `docs/VISION/` (prompt + `PPE_STEWARD_ALLOW_PRODUCT` gate).
- Product BUILD still needs ACP or explicit steward widening.

## Related

- [`PPE_AUTO_SELECTION_ROADMAP_V1.md`](PPE_AUTO_SELECTION_ROADMAP_V1.md)
- [`PPE_WORKER_MODES_V1.md`](PPE_WORKER_MODES_V1.md)
- [`CONTEXT_RULES.md`](../CONTEXT_RULES.md) — steward thread vs BUILD
