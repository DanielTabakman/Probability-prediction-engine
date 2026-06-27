# Workflow Context Audit 002 — Token economy rework

**Status:** canonical record (second entry in the `WORKFLOW_CONTEXT_AUDIT_*` series).  
**Plane:** CONTROL-PLANE. **Posture:** advisory + implemented tooling.  
**Cross-refs:** [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## 1. Purpose

Record the **2026-06 token economy assessment** and the control-plane rework shipped to reduce Cursor subscription burn while preserving operator safety (VM/desktop split, Codex-first product BUILD).

---

## 2. Findings (pre-rework)

| Signal | Observation |
|--------|-------------|
| Always-on Cursor rules | ~19k chars (~4,750 tok/turn) from 6 rules with heavy overlap |
| IDE BUILD starters | ~150 lines; duplicated continuity excerpt + slim BUILD packet |
| Build worker telemetry | No structured log of Codex vs IDE fallback |
| Metrics | `workflow_metrics/` unused — no baseline |
| Routing | Profile correct (`buildWorker: codex`) but fallback opaque when Codex unavailable |

**Headline:** fixed per-turn overhead and fat BUILD starters were the largest **preventable** Cursor burns; product BUILD landing in IDE Agent (Codex fallback) is the largest **variable** burn.

---

## 3. Changes shipped (Workflow-Hardening / Token-Economy v1)

### 3.1 Always-on rule slim-down

- **New:** `.cursor/rules/ppe-operator-core.mdc` — merged verdict auto-execute + context discipline (~minimal footprint).
- **Demoted to load-on-demand:** `agent-continuity`, `ppe-unified-run`, `auto-commit`, `product-direction`, `repo-layers`.
- **Kept always-on:** `ppe-desktop-vm-layout` (machine safety), `ppe-operator-core`.

**Target:** ≤10k chars always-on (~2,500 tok/turn).

### 3.2 Slim IDE BUILD starters

- Removed inlined continuity excerpt (pointer to `AGENT_CONTINUITY_BRIEF.md` only).
- Removed duplicate slim BUILD packet block (scope + recommended loads remain).
- Shortened context ritual; acceptance excerpt cap 40 lines.
- **Target:** ≤100 lines per starter (`STARTER_LINE_TARGET` in generator).

### 3.3 Telemetry

- `scripts/ppe_token_audit.py` + `token_audit.cmd` → `artifacts/control_plane/TOKEN_AUDIT_LATEST.md`
- `build_worker_events.jsonl` — structured worker resolve / Codex exhaustion events
- Workflow radar **Token economy** section + friction candidates

### 3.4 Operator habits (unchanged canon, reinforced)

- New thread per slice; `@` starter only.
- Ask mode for steering; Agent mode for implementation.
- Never paste orchestrator stdout / full pytest / full diff.
- `verify_codex.cmd` before accepting IDE BUILD when headless should run.

---

## 4. Validation plan

1. Run `token_audit.cmd` after pull — confirm always-on ≤ target.
2. Regenerate any on-disk starters: `generate_ide_build_starter.cmd <sliceId> <plan>`.
3. One week `workflow_metrics.cmd session start/stop` during BUILD days.
4. Compare Cursor dashboard usage week-over-week.

---

## 5. Advisory bands (unchanged)

Threshold bands remain per [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md). This audit adds **tooling** to measure starter line count and always-on rule weight; it does not add a new pass/fail BUILD gate.

---

## 6. Provenance

- **Trigger:** operator report of fast Cursor token consumption (2026-06-27).
- **Evidence artifacts:** `artifacts/control_plane/TOKEN_AUDIT_LATEST.json`, `build_worker_events.jsonl`, workflow radar token section.
- **Related slices:** Token-Economy-Assessment-V1 (control-plane tooling + rule/starter slim).
