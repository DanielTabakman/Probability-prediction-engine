# PPE multi-operator v1

**Plane:** CONTROL-PLANE. **Purpose:** run **multiple relay conveyors** on one VM — one git clone per instance, coordinated status.

**Related:** [`PPE_OUTPUT_PIPELINE_V1.md`](PPE_OUTPUT_PIPELINE_V1.md) · [`PPE_VM_LOOP_HOST_V1.md`](PPE_VM_LOOP_HOST_V1.md) · [`PPE_HEADLESS_STACK_V1.md`](PPE_HEADLESS_STACK_V1.md)

---

## Model

| Rule | Detail |
|------|--------|
| **One active chapter per clone** | Each instance has its own manifest, queue, locks |
| **One headless stack per clone** | `run_ppe_headless_stack.cmd --ensure` from each repo root |
| **Disjoint layers** | MSOS (`apps/msos-web/`) vs MVP1 (`src/`) — see [`PARALLEL_AGENT_CHECKLIST_V1.md`](PARALLEL_AGENT_CHECKLIST_V1.md) |
| **Merge via PR** | Each clone pushes feature branches; merge to `main` in order |

---

## Setup (second clone on VM)

```bat
cd D:\ppe-repos
git clone https://github.com/DanielTabakman/Probability-prediction-engine.git msos-live
git clone https://github.com/DanielTabakman/Probability-prediction-engine.git mvp1-research
```

Copy [`PPE_OPERATOR_INSTANCES.example.json`](PPE_OPERATOR_INSTANCES.example.json) → `PPE_OPERATOR_INSTANCES.local.json` in the **coordinator** repo:

```json
{
  "version": 1,
  "instances": [
    { "id": "msos", "label": "MSOS live", "repoRoot": "D:/ppe-repos/msos-live", "ntfyTag": "ppe-msos" },
    { "id": "mvp1", "label": "MVP1 research", "repoRoot": "D:/ppe-repos/mvp1-research", "ntfyTag": "ppe-mvp1" }
  ]
}
```

Per clone:

```bat
set PPE_LOOP_HOST=1
set PPE_OPERATOR_INSTANCE=msos
run_ppe_headless_stack.cmd --ensure
```

Use a **different** `PPE_OPERATOR_INSTANCE` per clone. Loop singleton locks are per-repo.

---

## Commands

```bat
ppe_multi_operator.cmd status --write
ppe_multi_operator.cmd status --json
ppe_multi_operator.cmd ensure
ppe_autobuilder.cmd status --brief
```

**Artifacts:** `artifacts/orchestrator/MULTI_OPERATOR_STATUS.json` (coordinator repo)

---

## Scheduled health (optional)

Task Scheduler every 15–30 min on VM:

```bat
ppe_autobuilder_watch.cmd
```

Pings ntfy only when phase is `STACK_DOWN`, `DEGRADED`, `ERROR`, `FIX_PLAN`, or `STALE_STATE`.

---

## What not to do

- Two loops on the **same** checkout
- Two product builds on one instance (single `REMOTE_BUILD_LOCK`)
- Parallel CONTROL-CLOSEOUT across instances without steward review
