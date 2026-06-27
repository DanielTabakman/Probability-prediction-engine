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

[`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md) — hybrid `autoRemoteBuild: true` with **`buildWorker: codex`** (headless Codex first; Cursor IDE/CLI for exceptions). Strict IDE-only via `ppe_operator_near_zero_api.local.cmd`.

---

## Cursor token conservation (when IDE is needed)

Reserve Cursor for **exceptions**; default product BUILD goes to **Codex CLI** (see local profile `ideHandoff.buildWorker`).

| Do | Why |
|----|-----|
| Run relay on VM (`run_ppe_auto_local_loop.cmd`) | Deterministic slices — no LLM |
| Headless product BUILD via Codex | Burns Codex quota, not Cursor |
| **`setup_codex.cmd`** + **`verify_codex.cmd`** | Required for headless path |
| New Agent thread per slice; `@` starter only | Smallest context (`IDE_BUILD_STARTER_*.md`) |
| Steward thread separate from BUILD | Avoid SELECTION+BUILD+PR mega-thread |
| After closeout: new thread + `AGENT_CONTINUITY_BRIEF.md` only | Drop orchestrator noise |
| `python scripts/ppe_context_preflight.py` before BUILD | Advisory band check |
| `clear_build_worker_quota.cmd` after plan reset | Clears stale CLI exhaustion from old logs |

| Avoid | Why |
|-------|-----|
| Pasting orchestrator stdout / full pytest logs into chat | Largest avoidable token burn |
| `buildWorker: auto` or `cursor` unless debugging CLI | Sends headless work to Cursor first |
| Phone **fix** expecting Cursor CLI | Fix dispatch now follows `buildWorker` (Codex when configured) |
| Long “what's next / triage / planning” in Agent mode | Use Ask/read-only or Codex for research |

When Cursor quota returns: keep **Codex for implementation**; use Cursor only for quick steward reads, merge triage, or slices Codex cannot finish.

---

## Related

- [`PPE_NEAR_ZERO_API_OPERATOR_V1.md`](PPE_NEAR_ZERO_API_OPERATOR_V1.md)
- [`PPE_IDE_NATIVE_OPERATOR_V1.md`](PPE_IDE_NATIVE_OPERATOR_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)
