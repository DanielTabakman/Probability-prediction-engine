# Human steward backlog

**Purpose:** Policy and architecture topics too big for the auto-loop. Work through these deliberately — not via `PHASE_CHAPTER_BACKLOG.json`.

| When | Action |
|------|--------|
| **Weekly** (Monday digest) | Scan open **high** items — ntfy lists top titles |
| **Monthly** ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)) | Pick one item → `in_progress` |
| **When done** | Set `status: done` + `closed` date in JSON; run `render-md` |

**Machine source:** [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) · **Refresh this file:** `python scripts/ppe_human_backlog.py render-md`

> Policy and architecture topics for human review — not auto-loop work. Edit items here; run python scripts/ppe_human_backlog.py render-md to refresh the readable doc. Weekly ntfy digest includes open high-priority titles.

## Open

### Product lane automation

- **id:** `` · **priority:** high · **category:** architecture
- **added:** 2026-06-17
- **summary:** Auto-spawn IDE build on PRODUCT_BLOCKED, or switch product slices to ACP, or inline IDE build in the deterministic worker.
- **policy question:** Stay near-zero-API (local profile) vs pay for full autonomous product slices?

### Relay decision model reconcile

- **id:** `relay_decision_reconcile` · **priority:** medium · **category:** control-plane
- **added:** 2026-06-17
- **summary:** AUTO_ADVANCE decision (or fold Rule 7b into CONTINUE); align CODEX_AUTONOMY §15 with implementation; auto PR on REPO_STATE_DRIFT for all slice kinds.
- **policy question:** How much steward judgment should remain vs machine CONTINUE?

### Guard framework v2

- **id:** `guard_framework_v2` · **priority:** medium · **category:** operator
- **added:** 2026-06-17
- **summary:** Per-guard block|warn|off policy; context bands advisory-only; drop maxPhaseSlices in favor of batch window only.
- **policy question:** Which guards should ever hard-stop the loop vs notify only?

### Focus / validation lifecycle

- **id:** `focus_validation_lifecycle` · **priority:** low · **category:** governance
- **added:** 2026-06-17
- **summary:** Per-chapter evidence gates in backlog; retire global P8 report gate; re-enable only during tester cohort windows.
- **policy question:** When does validation report gate come back after interim COMPLETE?

### SELECTION and backlog governance

- **id:** `selection_backlog_governance` · **priority:** medium · **category:** governance
- **added:** 2026-06-17
- **summary:** Auto-charter scaffold rows; steward API charter on local profile; parallel MSOS tracks with explicit dependency DAG.
- **policy question:** Can MSOS chapters run in parallel or stay strictly linear blocked chains?

### Infrastructure / ops hardening

- **id:** `infra_ops_hardening` · **priority:** low · **category:** operator
- **added:** 2026-06-17
- **summary:** Health gate warn-only for non-critical issues; soften preflight dirty-tree in sandbox; auto-heal STALE_STATE without exit 7.
- **policy question:** How much repo drift is acceptable during operator sandbox?

### Founder / canon policy

- **id:** `founder_canon_policy` · **priority:** high · **category:** governance
- **added:** 2026-06-17
- **summary:** Which PPE_MASTER hard stops agents may auto-resolve; PR-only vs direct control-plane edits; cross-layer slice exceptions.
- **policy question:** What stays human-only forever vs delegated envelope?

### Observability — human vs informational stops

- **id:** `observability_human_signal` · **priority:** low · **category:** operator
- **added:** 2026-06-17
- **summary:** OPERATOR_STATUS needs_human vs informational_stop; skip ntfy on auto-recovered exit 20; workflow radar noise reduction.
- **policy question:** What deserves a phone ping vs weekly digest only?
- **notes:** Partial: LAST_RUN_REPORT auto_advance_promotion_recovery + phone procedural hints shipped 2026-06-17.

### MSOS Stripe billing — phase 7b (human track)

- **id:** `stripe_operator_prereq` · **priority:** medium · **category:** operator
- **added:** 2026-06-19
- **summary:** Entire msos_billing_stripe_v1 chapter moved off auto relay queue. Operator work: Stripe account, test products/prices, API keys + webhook signing secret on VPS, Checkout return URLs. When ready: mark this done and ppe_request.cmd --chapter-id msos_billing_stripe_v1 --reason 'operator Stripe ready' --apply.
- **policy question:** When is production demo verified enough to start Stripe BUILD?
- **notes:** Relay plan kept at docs/SOP/PHASE_PLANS/msos_billing_stripe_v1_relay.json — not in PHASE_CHAPTER_BACKLOG or auto SELECTION until human closes this item.

### Process library expansion

- **id:** `process_library_expansion` · **priority:** medium · **category:** governance
- **added:** 2026-06-18
- **summary:** Formalize more operator rituals beyond context window closeout: SELECTION pass closeout, recovery closeout, weekly steward pass, IDE BUILD thread close.
- **policy question:** Which ritual should we standardize next after context closeout?

## Done

### Operator friction cleanup (local profile)

- **id:** `operator_friction_cleanup_2026_06` · **priority:** medium · **category:** operator
- **added:** 2026-06-17
- **closed:** 2026-06-17
- **summary:** focusGate off, stopOnContextEscalate off, procedural exit-20 auto-advance reporting, legacy relay hard-stops demoted, human steward backlog + weekly ntfy hook.

## Changelog

| 2026-06-19 | Auto-render from JSON |
