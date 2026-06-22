# Operator quickstart v1 (~30 min)

**Plane:** CONTROL-PLANE · **Related:** [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)

## 1. Install (5 min)

```bat
install_operator.cmd
```

Expect `ppe_autobuilder status --brief` → `PHASE=HEALTHY_IDLE` or actionable phase.

## 2. Status (daily)

```bat
ppe_autobuilder.cmd status
ppe_autobuilder.cmd diagnose
```

Timeline: `artifacts/orchestrator/AUTOBUILDER_TIMELINE.md`

## 3. One backlog chapter

Append a row to [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) (`blocked` + `planPath`).

```bat
run_ppe.cmd
```

## 4. Product slice (IDE BUILD)

When verdict is `IDE_BUILD`:

- `@ppe-build-worker` + `IDE_BUILD_STARTER_<sliceId>.md`
- Finish: `ppe_ide_build_closeout.cmd <sliceId> <planPath>`

Gate repair: read `artifacts/orchestrator/BUILD_REPAIR_HINT.md` if closeout fails.

## 5. Agents index

[`AGENTS.md`](../../AGENTS.md) at repo root.
