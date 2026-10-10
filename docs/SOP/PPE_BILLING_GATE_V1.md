# PPE billing gate v1

**Plane:** CONTROL-PLANE. **Purpose:** prevent product BUILD dispatch when the repo's token/context evidence is outside policy.

This is a **policy and context gate**, not provider billing telemetry. It does not claim access to hidden ChatGPT, Cursor, Codex, or API token usage. It composes the existing repo audits before dispatch.

## Covered entrypoint

`ppe_autobuilder.cmd` runs `scripts/ppe_billing_gate.py` before:

- `retry-build`
- `handoff`
- `advance` when the current phase is `AWAITING_BUILD`

Non-dispatching `advance` actions such as stack recovery or closeout are not blocked by this gate.

## Policy

| Combined verdict | Result |
|---|---|
| `OK` / `NORMAL` | Dispatch allowed |
| `WATCH` | Blocked unless the operator supplies an explicit reason |
| `ESCALATE` | Blocked; no override |
| Audit unavailable / unknown verdict | Fail closed as `ESCALATE` |
| Missing slice or phase-plan scope | Fail closed as `ESCALATE` |

The combined verdict is the worse of:

1. `scripts/ppe_token_audit.py` — always-on Cursor rules, starter size/staleness, worker routing, and operator configuration.
2. `scripts/ppe_context_preflight.py` — active sprint spec, phase slice count, BUILD packet, and IDE starter context band.

## Commands

Normal dispatch:

```bat
ppe_autobuilder.cmd retry-build
ppe_autobuilder.cmd handoff
ppe_autobuilder.cmd advance
```

Accept a `WATCH` result for one bounded dispatch:

```bat
ppe_autobuilder.cmd retry-build --allow-budget-watch "Known legacy starter; one-file bounded fix"
```

The reason is written to:

```text
artifacts/control_plane/BILLING_GATE_LATEST.json
```

An `ESCALATE` result cannot be bypassed. Shrink the sprint/build packet, remove stale starters, reduce fixed-loaded rules, or repair the failed audit, then run the command again.

## Direct audit

```bat
python scripts/ppe_billing_gate.py --command retry-build
python scripts/ppe_billing_gate.py --command retry-build --allow-watch --watch-reason "bounded exception"
python scripts/ppe_billing_gate.py --command retry-build --json
```

Exit codes:

- `0` — allowed
- `2` — blocked

## Boundary

The gate currently protects the canonical Windows operator entrypoint. Calling `scripts/ppe_autobuilder.py` directly bypasses the wrapper and is not the supported operator path. A future hardening slice may move the same decision into the Python action layer after the current autobuilder file is decomposed into smaller ownership modules.
