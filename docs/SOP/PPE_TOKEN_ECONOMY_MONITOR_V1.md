# PPE token economy monitor v1

**Plane:** CONTROL-PLANE. **Purpose:** perpetual monitoring and budget enforcement for preventable fixed context across Cursor and the ChatGPT Project → GitHub → Codex workflow.

**Related:** [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`WORKFLOW_CONTEXT_AUDIT_002.md`](WORKFLOW_CONTEXT_AUDIT_002.md) · [`WORKFLOW_CONTEXT_AUDIT_003.md`](WORKFLOW_CONTEXT_AUDIT_003.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## 1. What we measure

### Cursor / local worker surfaces

| Signal | Source | Budget (default) |
|--------|--------|------------------|
| Always-on Cursor rules | `.cursor/rules/*.mdc` | ≤8k chars (~2k tok/turn); escalate >12k |
| IDE BUILD starter size | `artifacts/orchestrator/IDE_BUILD_STARTER_*.md` | ≤65 lines; escalate >80 |
| Headless vs IDE fallback | `build_worker_events.jsonl` | Codex-first; IDE = exception |
| Stale starters | completed chapters still on disk | 0 |
| Operator profile | `PPE_AUTO_OPERATOR.local.json` | `skipAcp: true`, `buildWorker: codex` |

### ChatGPT / GitHub / Codex surfaces

| Signal | Source | Budget (default) |
|--------|--------|------------------|
| ChatGPT Project instructions | fenced text in `CHATGPT_PROJECT_STARTER.md` | ≤1,500 chars |
| One role contract | role starter in `CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md` | ≤800 chars |
| Fixed startup bundle | Project instructions + one role contract | ≤2,500 chars |
| Generated continuity brief | `AGENT_CONTINUITY_BRIEF.md` | ≤4,000 chars and fresh, complete, portable |
| Index/backlog/status documents | resolver `load_always` / `load_on_demand` | On demand unless the named task requires them |

Character-derived token figures are labeled approximations using `ceil(chars / 4)`. They are **not** ChatGPT, Codex, Cursor, subscription, or API billing measurements. Proprietary hidden context is not estimated.

Cursor subscription usage itself is tracked **manually** (Cursor dashboard). Repo tooling measures **preventable fixed overhead**, startup bundles, routing, and BUILD bundle size.

---

## 2. Automated tooling

| Command | When |
|---------|------|
| `token_audit.cmd` | On demand; runs the preserved Cursor audit and the cross-surface context audit |
| `token_audit.cmd --stdout` | Print both reports without writing history/artifacts |
| `token_audit.cmd --prune-stale` | Remove starters for COMPLETE chapters; cross-surface audit remains read-only |
| `token_audit.cmd --fail-on-watch` | CI/ad-hoc gate (exit 1 if either audit returns WATCH/ESCALATE) |
| `python scripts/resolve_sop.py --role <role> --json` | Inspect fixed role routing |
| `python scripts/resolve_sop.py --topic "<phrase>" --json` | Inspect topic-specific load bundle |
| `regenerate_ide_starters.cmd` | After pulling starter generator changes |
| `generate_ide_build_starter.cmd <slice> <plan>` | On each `IDE_BUILD` handoff |
| `verify_codex.cmd` | Desktop; before relying on headless BUILD |

**Artifacts (gitignored):**

- `artifacts/control_plane/TOKEN_AUDIT_LATEST.md` — preserved Cursor/local worker report
- `artifacts/control_plane/TOKEN_AUDIT_LATEST.json` — preserved Cursor/local worker machine report
- `artifacts/control_plane/CONTEXT_SURFACE_AUDIT_LATEST.md` — ChatGPT/GitHub/Codex context report
- `artifacts/control_plane/CONTEXT_SURFACE_AUDIT_LATEST.json` — cross-surface machine report
- `artifacts/control_plane/token_economy_history.jsonl` — Cursor/local trend log (one row per audit)
- `artifacts/orchestrator/build_worker_events.jsonl` — worker routing log

---

## 3. Perpetual schedule

### Weekly (automatic)

`weekly_digest_monday.cmd` pipeline (Task Scheduler ~06:00 local):

1. `monday_morning_prep.cmd prep`
2. wait until 08:00
3. **`token_audit.cmd --prune-stale`** — Cursor snapshot/history plus cross-surface snapshot
4. `workflow_radar.cmd generate` — includes token friction candidates
5. `weekly_digest.cmd generate` + `notify`

**Operator:** read phone digest; if either token verdict is WATCH/ESCALATE, run fixes the same day.

### Before each implementation or review thread

1. Project instructions are already present; do not paste them again.
2. Use one compact role contract.
3. Load one relevant GitHub issue, program, or PR.
4. Load status, index, backlog, or generated continuity only when the task requires it.
5. If using generated continuity, require the audit to report `safe_to_load_first: true`.

### Before each IDE BUILD (agent)

1. `generate_ide_build_starter.cmd` (loop does this on handoff)
2. Confirm starter ≤80 lines (generator warns on stderr)
3. New Cursor thread; `@` starter only

### After rule, routing, starter, or context-bundle changes (agent)

1. `regenerate_ide_starters.cmd` when starter generation changed
2. `token_audit.cmd --stdout`
3. Run relevant resolver commands for changed roles/topics
4. Gate + commit the bounded control-plane slice

### Monthly (operator, 5 min)

1. Compare Cursor dashboard usage vs prior month
2. `ppe_token_reconcile.cmd record --month YYYY-MM --usd N` (Cursor dashboard total)
3. `ppe_token_reconcile.cmd summary` — compare vs advisory ledger
4. `token_audit.cmd --stdout` — check both fixed-overhead surfaces
5. If always-on >2.5k tok/turn for 3+ weeks, or a fixed startup bundle repeatedly exceeds 2,500 chars, charter a Workflow-Hardening slice

---

## 4. Verdicts and actions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **OK** | Within budgets and generated context is safe | Continue habits |
| **WATCH** | Approaching ceiling, unnecessary state is fixed-loaded, or generated continuity is unsafe | Tighten routing; regenerate or bypass stale context |
| **ESCALATE** | Hard overhead ceiling or actionable IDE fallback | Stop mega-threads; fix routing/Codex/rules before continuing |

See the latest audit recommendations blocks for generated next steps.

---

## 5. Design rules (keep fat off)

### ChatGPT Project and role startup

Keep the recurring startup bundle to:

- Project instructions already injected by ChatGPT;
- one role contract;
- one relevant program, issue, or PR.

Do not fixed-load `PHASE_CHAPTER_BACKLOG.json`, `ACTIVE_PRODUCT_DIRECTION.json`, `CHAPTER_DOC_INDEX.json`, or `AGENT_CONTINUITY_BRIEF.md` for a generic founder/charter phrase. Explicit operator, selection, closeout, or chapter lookup work may load the relevant state on demand.

### Generated continuity

`AGENT_CONTINUITY_BRIEF.md` must never override GitHub `main`. It may be first-load context only when:

- embedded HEAD matches the checkout;
- active relay, sprint, and plan are populated;
- no machine-specific path is needed.

Otherwise use current GitHub canon plus current operator status/direction, and regenerate through `apply_control_closeout_v1`.

### Always-on Cursor rules

Keep **only:**

- `ppe-operator-core.mdc`
- `ppe-desktop-vm-layout.mdc`

Everything else: `alwaysApply: false` (load on demand).

### IDE BUILD starters

Generator emits **minimal** bundle:

- Header (HEAD, plane, preset, branch)
- One-line focus, compact scope (touchSet; not full ALLOWED_PATHS)
- Slice acceptance from phase plan (not full sprint paste)
- Load list (touchSet + sprint + plan paths)
- Compact closeout

No continuity excerpt, no duplicate BUILD packet, no context band footer.

### Threads

- Steward (Ask mode when possible) ≠ BUILD (Agent + starter)
- Never paste orchestrator stdout / full pytest / full diff
- Do not duplicate Project instructions already present

---

## 6. Agent ownership

| Trigger | Agent action |
|---------|----------------|
| Generic founder/charter opener | Require one topic/program/issue; do not load broad state |
| Generated continuity stale/incomplete | Bypass it, disclose the evidence gap, regenerate through the canonical path |
| `IDE_BUILD` handoff | Ensure starter generated; warn if >80 lines |
| New always-on rule proposed | Reject unless ppe-operator-core/desktop-vm split preserved |
| Weekly radar token ESCALATE | Regenerate starters + verify_codex; gate+commit if control-plane fix |
| Chapter closeout | Starters pruned automatically on next `token_audit --prune-stale` |
| Repeated WATCH 3+ audits | Charter Workflow-Hardening slice; update thresholds only with evidence |

---

## 7. Optional CI hook

Add to control-plane pre-push after the baseline stabilizes:

```bat
token_audit.cmd --fail-on-watch
```

Not enabled by default — advisory until operator-machine baseline is stable.

---

## 8. Related thresholds code

- `scripts/ppe_token_audit.py` — `ALWAYS_ON_CHAR_TARGET`, `ALWAYS_ON_CHAR_ESCALATE`
- `scripts/ppe_ide_build_starter.py` — `STARTER_LINE_TARGET`, `STARTER_LINE_ESCALATE`
- `scripts/ppe_context_surface_audit.py` — Project, role, fixed-bundle, and continuity thresholds

Change thresholds here and in the owning script together; do not claim exact billing from character estimates.
