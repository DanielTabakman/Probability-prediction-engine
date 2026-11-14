# Triggered ideas

**Purpose:** Park "great idea, too early" items with revisit triggers. They surface when a matching chapter enters SELECTION — dismiss when processed.

| Command | Action |
|---------|--------|
| `triggered_ideas.cmd` | List active parked ideas |
| `python scripts/ppe_triggered_ideas.py add ...` | Park a new idea |
| `python scripts/ppe_triggered_ideas.py dismiss <id>` | Done — hide from active list |
| `python scripts/ppe_triggered_ideas.py dismiss <id> --purge` | Remove + archive one line |

**Machine source:** [`TRIGGERED_IDEAS.json`](TRIGGERED_IDEAS.json) · **Alert artifact:** `artifacts/control_plane/TRIGGERED_IDEAS_ALERT.json`

> Park ideas with revisit triggers — surfaced when a matching chapter/plan enters SELECTION. Dismiss when processed: python scripts/ppe_triggered_ideas.py dismiss <id> [--purge]

## Active (parked / surfaced)

### Merge thread insight capture tooling (PR #737)

- **id:** `merge_thread_insight_capture_tooling` · **priority:** medium · **status:** parked
- **added:** 2026-06-30
- **summary:** Merge PR #737 so context_window_closeout --capture routes via ppe_thread_capture.py on main.
- **trigger keywords:** thread insight, context closeout, ppe_thread_capture

### Record operator pass at burst end only

- **id:** `operator_pass_record_at_burst_end` · **priority:** low · **status:** parked
- **added:** 2026-08-06
- **summary:** Today prepare_operator_status records every refresh (dedupe 120s). Prefer explicit --record-pass from @ppe-director / burst finish so pass streak reflects real operator cycles, not status polls. Revisit when touching burst plan, director closeout, or ppe_operator_pass_progress. Pre-split thread residual — not in DESKTOP_OPERATOR plan.
- **trigger keywords:** operator pass, burst, ppe-director, pass progress

### Per-slice SLA hint on Progress/Waiting line

- **id:** `operator_pass_slice_sla_hint` · **priority:** low · **status:** parked
- **added:** 2026-08-06
- **summary:** Surface historical median closeout duration for active phase/slice type in OPERATOR_STATUS Waiting line (e.g. typical FINISH closeout ~45m). Medians already in _budget_for_phase; expose in format_pass_lines. Revisit with pass-progress or DESKTOP_OPERATOR Step 5 truth card. Pre-split thread residual.
- **trigger keywords:** operator pass, sla, pass progress, desktop automation

### Skim THREAD_INSIGHTS during SELECTION

- **id:** `surface_thread_insights_at_selection` · **priority:** low · **status:** surfaced
- **added:** 2026-06-30
- **surfaced:** 2026-06-30T21:00:24Z
- **summary:** When burst or what's next runs SELECTION, agent should skim recent THREAD_INSIGHTS.md entries for the active chapter_id (not only TRIGGERED_IDEAS alerts).
- **trigger keywords:** selection, what's next, burst

### Revisit Uniblock vs single Web3 provider

- **id:** `web3_uniblock_revisit` · **priority:** low · **status:** parked
- **added:** 2026-06-15
- **summary:** Deferred 2026-06-15. Not needed for Deribit/Polymarket/Yahoo or Cloudflare Access email accounts. Revisit when charter includes wallet connect or on-chain per-user reads.
- **trigger chapterIds:** `msos_wallet_connect_v1`, `msos_onchain_portfolio_v1`
- **trigger keywords:** wallet connect, walletconnect, on-chain portfolio, web3 provider, uniblock
- **not for:** `msos_user_state_v1`, `msos_workflow_persistence_v1`, `msos_access_identity_v1`, `msos_billing_stripe_v1`

## Changelog

| 2026-08-06 | Auto-render from JSON |
