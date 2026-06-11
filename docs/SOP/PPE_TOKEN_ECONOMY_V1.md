# PPE token economy v1

**Plane:** CONTROL-PLANE. **Purpose:** keep Cursor / agent billing predictable while running relay chapters at scale.

---

## Three lanes

| Lane | Entry | Worker | Billing |
|------|--------|--------|---------|
| **Auto local** | `run_ppe_auto_local_loop.cmd` | Deterministic (`PPE_SKIP_ACP=1`) | None for relay slices |
| **IDE product** | Cursor Agent chat | Human + subscription | IDE plan (not API relay) |
| **ACP** | `run_ppe_auto_acp_loop.cmd` | `ppe-orchestrator-acp` | API / agent credits |

Do **not** disable `skipAcp` on the local profile to “fix” product slices — that multiplies API cost.

---

## Local auto lane

[`PPE_AUTO_OPERATOR.local.json`](PPE_AUTO_OPERATOR.local.json):

- `skipAcp: true`, `stewardCharter: false`
- Product slices: guard stop or STOP_FOR_REVIEW → [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)

---

## Product lane (explicit)

Generate starter before IDE BUILD (local profile):

```bat
generate_ide_build_starter.cmd <sliceId> <phasePlanPath>
```

After IDE BUILD and commit:

```bat
run_ppe_local.cmd
```

Optional metrics (~30s): [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

Optional one-shot API product slice (when credits exist): `run_product_slice.cmd <sliceId>` — see runbook if present in repo.

---

## Anti-patterns

- Running `run_ppe_auto_acp_loop` without credits.
- Expecting continuous local auto to implement `src/` product code.
- Pasting orchestrator logs into steward chat.

---

## Near-zero API (recommended default)

[`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) — `autoRemoteBuild: false`, IDE handoff on exit 7, product in Cursor Agent.

---

## Related

- [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md)
- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)
