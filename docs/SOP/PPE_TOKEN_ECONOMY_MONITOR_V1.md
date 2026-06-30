# PPE token economy monitor v1

**Plane:** CONTROL-PLANE. **Purpose:** perpetual monitoring and budget enforcement for Cursor / agent token spend.

**Related:** [`PPE_TOKEN_ECONOMY_V1.md`](PPE_TOKEN_ECONOMY_V1.md) · [`WORKFLOW_CONTEXT_AUDIT_001.md`](WORKFLOW_CONTEXT_AUDIT_001.md) · [`WORKFLOW_CONTEXT_AUDIT_002.md`](WORKFLOW_CONTEXT_AUDIT_002.md) · [`WORKFLOW_EFFICIENCY_OPERATOR_V1.md`](WORKFLOW_EFFICIENCY_OPERATOR_V1.md)

---

## 1. What we measure

| Signal | Source | Budget (default) |
|--------|--------|------------------|
| Always-on Cursor rules | `.cursor/rules/*.mdc` | ≤8k chars (~2k tok/turn); escalate >12k |
| IDE BUILD starter size | `artifacts/orchestrator/IDE_BUILD_STARTER_*.md` | ≤65 lines; escalate >80 |
| Headless vs IDE fallback | `build_worker_events.jsonl` | Codex-first; IDE = exception |
| Stale starters | completed chapters still on disk | 0 |
| Operator profile | `PPE_AUTO_OPERATOR.local.json` | `skipAcp: true`, `buildWorker: codex` |

Cursor subscription usage itself is tracked **manually** (Cursor dashboard) — repo tooling measures **preventable fixed overhead** and **BUILD bundle size**.

---

## 2. Automated tooling

| Command | When |
|---------|------|
| `token_audit.cmd` | On demand; prints verdict + recommendations |
| `token_audit.cmd --prune-stale` | Remove starters for COMPLETE chapters |
| `token_audit.cmd --fail-on-watch` | CI/ad-hoc gate (exit 1 on WATCH/ESCALATE) |
| `regenerate_ide_starters.cmd` | After pulling starter generator changes |
| `generate_ide_build_starter.cmd <slice> <plan>` | On each `IDE_BUILD` handoff |
| `verify_codex.cmd` | Desktop; before relying on headless BUILD |

**Artifacts (gitignored):**

- `artifacts/control_plane/TOKEN_AUDIT_LATEST.md` — human report
- `artifacts/control_plane/TOKEN_AUDIT_LATEST.json` — machine report
- `artifacts/control_plane/token_economy_history.jsonl` — trend log (one row per audit)
- `artifacts/orchestrator/build_worker_events.jsonl` — worker routing log

---

## 3. Perpetual schedule

### Weekly (automatic)

`weekly_digest_monday.cmd` pipeline (Task Scheduler ~06:00 local):

1. `monday_morning_prep.cmd prep`
2. wait until 08:00
3. **`token_audit.cmd --prune-stale`** — snapshot + history append
4. `workflow_radar.cmd generate` — includes token friction candidates
5. `weekly_digest.cmd generate` + `notify`

**Operator:** read phone digest; if token verdict WATCH/ESCALATE, run fixes same day.

### Before each IDE BUILD (agent)

1. `generate_ide_build_starter.cmd` (loop does this on handoff)
2. Confirm starter ≤80 lines (generator warns on stderr)
3. New Cursor thread; `@` starter only

### After rule or generator changes (agent)

1. `regenerate_ide_starters.cmd`
2. `token_audit.cmd`
3. Gate + commit control-plane slice

### Monthly (operator, 5 min)

1. Compare Cursor dashboard usage vs prior month
2. `ppe_token_reconcile.cmd record --month YYYY-MM --usd N` (Cursor dashboard total)
3. `ppe_token_reconcile.cmd summary` — compare vs advisory ledger
4. `token_audit.cmd --stdout` — check trend section
5. If always-on >2.5k tok/turn for 3+ weeks → charter Workflow-Hardening slice

---

## 4. Verdicts and actions

| Verdict | Meaning | Action |
|---------|---------|--------|
| **OK** | Within budgets | Continue habits |
| **WATCH** | Approaching ceiling | Regenerate starters; check Codex; trim rules |
| **ESCALATE** | Over budget or IDE fallback | Stop mega-threads; fix Codex; demote always-on rules |

See `TOKEN_AUDIT_LATEST.md` recommendations block for auto-generated next steps.

---

## 5. Design rules (keep fat off)

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

---

## 6. Agent ownership

| Trigger | Agent action |
|---------|----------------|
| `IDE_BUILD` handoff | Ensure starter generated; warn if >80 lines |
| New always-on rule proposed | Reject unless ppe-operator-core/desktop-vm split preserved |
| Weekly radar token ESCALATE | Regenerate starters + verify_codex; gate+commit if control-plane fix |
| Chapter closeout | Starters pruned automatically on next `token_audit --prune-stale` |
| Repeated WATCH 3+ audits | Charter Workflow-Hardening slice; update this doc thresholds if needed |

---

## 7. Optional CI hook

Add to control-plane pre-push (future):

```bat
token_audit.cmd --fail-on-watch
```

Not enabled by default — advisory until baseline stable.

---

## 8. Related thresholds code

- `scripts/ppe_token_audit.py` — `ALWAYS_ON_CHAR_TARGET`, `ALWAYS_ON_CHAR_ESCALATE`
- `scripts/ppe_ide_build_starter.py` — `STARTER_LINE_TARGET`, `STARTER_LINE_ESCALATE`

Change thresholds here first, then update §1 table in this doc.
