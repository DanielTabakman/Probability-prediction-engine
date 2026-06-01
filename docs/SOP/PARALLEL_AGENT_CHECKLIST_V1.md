# Parallel agent checklist v1

**Canon:** [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) · [`REPO_LAYER_PATH_PREFIXES.json`](REPO_LAYER_PATH_PREFIXES.json)

Use this when running **more than one** Cursor agent, relay worker, or IDE BUILD at the same time.

---

## Before starting

1. **One layer per agent** — assign `LAYER_PRESET` from the table in [`BUILD_PACKET_TEMPLATE.md`](BUILD_PACKET_TEMPLATE.md).
2. **Disjoint paths** — confirm `ALLOWED_PATHS` do not overlap between concurrent agents (or use separate worktrees).
3. **Phase plan** — add `layerPreset` on each slice in `docs/SOP/PHASE_PLANS/*.json` when steward authors a chapter (inference fills gaps for legacy plans).
4. **Branch / worktree** — never two agents on the same dirty checkout; orchestrator uses `_worktrees/orchestrator/<slice>/`.

---

## Per-agent packet (minimum)

```text
LAYER_PRESET: PPE_UI
ALLOWED_PATHS: (from REPO_LAYER_PATH_PREFIXES.json)
FORBIDDEN_PATHS: (from preset)
SLICE_ID: ...
SPRINT_SPEC: docs/SOP/SPRINT_....md
```

Relay workers: read `repo_layer` in `artifacts/relay/runs/<run_id>/task_envelope.json`.

---

## Before commit / resume

```bat
python scripts/ppe_layer_audit.py --repo-root . --dirty
python scripts/ppe_layer_audit.py --repo-root . --diff origin/main
```

With active phase manifest:

```bat
python scripts/ppe_layer_audit.py --repo-root . --manifest
```

Failures block **pushable gate** when `PPE_LAYER_AUDIT=1` (default for tier 1/2) or relay **resume** when the diff violates the staged envelope.

---

## Safe parallel combinations

| Agent A | Agent B | OK? |
|---------|---------|-----|
| `PPE_UI` | `CONTROL` | Yes |
| `PPE_UI` | `PPE_CORE` | Yes (if slices split; do not edit same files) |
| `MSOS_UI` | `PPE_UI` | Yes (after `apps/msos-web/` exists) |
| `PPE_UI` | `PPE_UI` | Only in different worktrees/branches |
| `PPE_CORE` + `PPE_UI` in one slice | No — split slices |

---

## Operator loop (IDE native)

See [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md). After IDE BUILD on a product slice:

1. `ppe_layer_audit.py --dirty` on the build branch.
2. `mark_ide_product_ready.cmd`
3. `run_ppe_local.cmd`

---

## Steward

- [`FRONTIER_STEWARD_PROTOCOL.md`](FRONTIER_STEWARD_PROTOCOL.md) — BUILD packets include layer fields.
- [`PHASE_PLAN_CONTRACT_V1.md`](PHASE_PLANS/PHASE_PLAN_CONTRACT_V1.md) — `layerPreset` on slices.
