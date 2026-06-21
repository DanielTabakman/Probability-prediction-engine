# Product direction pivot v1

**Purpose:** One place to change product direction without hunting ghost references across twenty steering files.

**Single source of truth (SSOT):** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json)

**Who runs this:** **Agents and stewards only.** The operator states intent in plain language; agents edit JSON, sync, queue, and commit. The operator does **not** need to remember sync steps.

**Agent rule:** [`.cursor/rules/product-direction.mdc`](../../.cursor/rules/product-direction.mdc) (always applied).

---

## When to pivot

- Operator changes primary focus (e.g. research-first → BUILD-first)
- A gate or chapter is marked COMPLETE prematurely
- Frontier / integrated status / playbook disagree

---

## How to pivot (agent ritual)

### 0. Operator says what changed (plain language)

Example: *"Drop friends-first; beeline to usable demo with PPE in the shell."*

### 1. Edit the JSON SSOT

Open [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) and update:

| Field | Meaning |
|-------|---------|
| `pivotId` | New slug (e.g. `usable-demo-build-v2`) — bump on every direction change |
| `asOf` | ISO date |
| `primaryFocus` | One sentence — what BUILD optimizes for |
| `currentStage` | `design_complete` · `build_integration` · `demo_walkable` · `expansion` |
| `activeBuildChapterId` | Relay chapter id |
| `activeBuildPlanPath` | Relay JSON path |
| `deprecatedApproaches` | List what agents must **stop** steering by |
| `nextStewardAction` | One line for operators |

### 2. Propagate (automatic after closeout; agent runs on pivot)

From repo root:

```cmd
sync_product_direction.cmd
```

**Automatic:** `post_relay_continue` / `apply_control_closeout_v1` calls sync after every chapter closeout.

**Manual (agent):** direction pivot, context window closeout, or detected marker drift.

This rewrites `<!-- ACTIVE_PRODUCT_DIRECTION:START -->` … `END` blocks in:

- `MSOS_FRONTIER.md`
- `PPE_INTEGRATED_STATUS.md`
- `PRODUCT_FOCUS_PLAYBOOK_V1.md`
- `MINIMUM_CREDIBLE_DEMO_GATE_V1.md`
- `BUILD_FACTORY_BOUNDARY_V1.md`
- `MSOS_LIVE_PRODUCT_SEQUENCE_V1.md`
- `TRADER_WORKFLOW_RESEARCH_V1.md`
- `AGENT_CONTINUITY_BRIEF.md`
- `artifacts/control_plane/WHATS_NEXT.md`

### 3. Queue BUILD (if chapter changed)

1. Add `status: "queued"` row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json)
2. Add `status: "READY"` row to [`PHASE_QUEUE.json`](PHASE_QUEUE.json) with `planPath`
3. Run `python scripts/ppe_auto_select.py --apply` or `run_ppe.cmd`

### 4. Verify

```bash
python scripts/run_pushable_gate.py
python scripts/sync_active_product_direction.py --dry-run
```

Confirm `skipped` list is empty (all marker blocks found).

### 5. Commit

One commit per pivot:

```
direction(control-plane): usable-demo-build-v1 — SSOT + steering propagation
```

---

## Adding a new propagation target

1. Insert marker block in the target doc (once):

```markdown
<!-- ACTIVE_PRODUCT_DIRECTION:START -->
_(placeholder — run sync_product_direction.cmd)_
<!-- ACTIVE_PRODUCT_DIRECTION:END -->
```

2. Add a `render_*_block()` in `scripts/active_product_direction.py`
3. Register the path in `propagate()` and `ACTIVE_PRODUCT_DIRECTION.json` → `propagationTargets`
4. Add a pytest in `tests/test_active_product_direction.py`

---

## Precedence

| Question | Answer |
|----------|--------|
| What is primary focus? | `ACTIVE_PRODUCT_DIRECTION.json` |
| What slice runs next? | `MSOS_FRONTIER.md` + `PHASE_QUEUE.json` |
| Is research a BUILD gate? | **No** unless pivot JSON says so |
| Historical chapter docs | Archive — do not delete; mark superseded in pivot `deprecatedApproaches` |

---

## Current pivot

See [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json) — `pivotId`, `primaryFocus`, `activeBuildChapterId`.
