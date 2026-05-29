# PPE token economy v1

**Plane:** CONTROL-PLANE. **Purpose:** keep Cursor / agent billing predictable while running relay chapters at scale.

---

## Two lanes

| Lane | Entry | Worker | Cursor billing |
|------|--------|--------|----------------|
| **Auto (low token)** | [`run_ppe_auto.cmd`](../../run_ppe_auto.cmd) / [`run_ppe.cmd`](../../run_ppe.cmd) | Deterministic (`PPE_SKIP_ACP=1`) | None for relay slices (pytest/scripts only) |
| **Product (explicit)** | [`run_product_slice.cmd`](../../run_product_slice.cmd) | `local-agent` → `agent-cli` | Yes — one agent run per invocation |

Do **not** disable `skipAcp` on the auto-operator to “fix” product slices — that runs **every** slice through ACP/cloud agents.

---

## Auto lane

Configured in [`PPE_AUTO_OPERATOR.json`](PPE_AUTO_OPERATOR.json) (default when enabled):

- `skipAcp: true` → [`ppe_relay_phase.py`](../../scripts/ppe_relay_phase.py), not npm `ppe-orchestrator-acp`.
- `stewardCharter: true` has **no effect** while `skipAcp` is true ([`ppe_operator_config.py`](../../scripts/ppe_operator_config.py) does not set `PPE_AUTO_STEWARD`).

**Continuous guards** ([`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)):

- `PRODUCT_BLOCKED` — product slice would run deterministic-only under global skip-ACP; use the product lane instead.
- `CONTEXT_ESCALATE` — sprint spec &gt;400 lines; shrink or split before unattended runs.

**After auto chapter exit:** read [`artifacts/orchestrator/LAST_RUN_REPORT.md`](../../artifacts/orchestrator/LAST_RUN_REPORT.md); open a **new** Cursor thread with [`AGENT_CONTINUITY_BRIEF.md`](AGENT_CONTINUITY_BRIEF.md) only ([`CONTEXT_RULES.md`](../CONTEXT_RULES.md)).

---

## Product lane

When a phase plan has a **Product** slice (e.g. `workerMode: local-agent` + `touchSet`):

```bat
run_product_slice.cmd MVP1-Phase6Trust-Product-Slice002 docs/SOP/PHASE_PLANS/mvp1_phase6_trust_metrics_v1_relay.json
```

Omit the plan path to use [`ACTIVE_PHASE_MANIFEST.json`](ACTIVE_PHASE_MANIFEST.json) `phasePlanPath`.

**What it does:**

1. Sets `PPE_OPERATOR_ENV_APPLIED=1` so [`run_ppe.cmd`](../../run_ppe.cmd) does not re-apply operator `PPE_SKIP_ACP=1`.
2. Sets `PPE_SKIP_ACP=0`, `PPE_WORKER_MODE=local-agent`, `PPE_RUN_KIND=product_slice`.
3. Runs one slice via [`ppe_run.cmd --slice`](../../scripts/ppe_run.py) → [`run_slice.cmd`](../../run_slice.cmd) → [`phase_orchestrator_v0.py`](../../scripts/phase_orchestrator_v0.py) `agent-cli`.

Preflight: slice must be product kind or `workerMode: local-agent`; non-empty `touchSet` unless `--no-require-touch-set`.

Requires `agent` CLI logged in (`agent login` or `CURSOR_API_KEY`).

---

## Anti-patterns

- Turning off `skipAcp` and running `run_ppe_auto.cmd --continuous` for a full phase (multiplies agent/ACP cost).
- Pasting orchestrator stdout, full pytest, or full `git diff` into steward Cursor chat.
- Re-running the **entire phase** in Agent to fix one product slice — use `run_product_slice.cmd` once.
- Expecting auto continuous to run product BUILD while global `PPE_SKIP_ACP=1` (by design it blocks or stubs).

---

## Related

- [`PPE_WORKER_MODES_V1.md`](PPE_WORKER_MODES_V1.md)
- [`PPE_CONTINUOUS_OPERATOR.md`](PPE_CONTINUOUS_OPERATOR.md)
- [`RELAY_ORCHESTRATOR_RUNBOOK_V1.md`](RELAY_ORCHESTRATOR_RUNBOOK_V1.md)
- [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) — context window (companion to billing)
