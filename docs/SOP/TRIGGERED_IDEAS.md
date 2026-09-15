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

### Simplify founder surface for recovery preflight

- **id:** `founder_surface_recovery_simplify` · **priority:** medium · **status:** parked
- **added:** 2026-08-06
- **summary:** After repo-state SSOT: trim founder/operator surface recovery wording so mixed-plane/recovery parks to operator without checklist sprawl; align FOUNDER_OPERATOR_SURFACE with severity ladder + park scaffolding from PR #1939.
- **trigger keywords:** founder_surface, recovery, mixed-plane, operator_status
- **not for:** `factory FC roadmap Tier 2-5 duplicates of factory SSOT/dispatch`

### Consolidate frontier_preflight into ppe_repo_state

- **id:** `frontier_preflight_repo_state_consolidation` · **priority:** medium · **status:** parked
- **added:** 2026-08-06
- **summary:** Post repo-state SSOT (PR #1939): fold remaining frontier_preflight checks into ppe_repo_state severity ladder / recovery transaction so mixed-plane preflight has one SSOT. Do not re-park factory FC-3/FC-5 gate/dispatch work already on factory surfaces.
- **trigger keywords:** repo_state, frontier_preflight, mixed-plane, recovery
- **not for:** `factory_fc3_gate_enforce; factory_fc5_slice_starters; factory SSOT/dispatch/worktrees already covered post-split`

### SSH log-tail when stuck and local desktop logs stale

- **id:** `in_flight_ssh_log_tail_when_stale` · **priority:** medium · **status:** parked
- **added:** 2026-08-06
- **summary:** When in-flight monitor detects stuck and local desktop logs are unchanged for ~15m, run one bounded SSH tail of VM relay/build logs (not an open-ended poll). Complements local log-tail already shipped; only when desktop logs are stale so operator is not blind to VM-side progress.
- **trigger keywords:** in-flight, operator, ssh, vm, stuck, log-tail

### Merge thread insight capture tooling (PR #737)

- **id:** `merge_thread_insight_capture_tooling` · **priority:** medium · **status:** parked
- **added:** 2026-06-30
- **summary:** Merge PR #737 so context_window_closeout --capture routes via ppe_thread_capture.py on main.
- **trigger keywords:** thread insight, context closeout, ppe_thread_capture

### Milestone gate v2 phases 3-5 (NEXT_BUILD_RESOLVED + umbrella tracker + merge-time markers)

- **id:** `milestone_gate_v2_phases_3_5_next_build_resolved_umbrella_tracke` · **priority:** medium · **status:** parked
- **added:** 2026-08-06
- **summary:** Pre-split thread designed milestone gate v2. Phases 1-2 (actionable clock, ACTIVE_CHAPTER_GATE/STEERING_CANDIDATE_STALE/CLOSEOUT_REGISTRY_DEBT, post_relay_continue reconcile) were implemented on a recovery branch but ppe_milestone_gate.py is absent after autobuilder/MSOS split — do not re-land as ad-hoc product. Revisit as control-plane/factory chapter: Phase 3 NEXT_BUILD_RESOLVED.json + steward doc sync; Phase 4 umbrella milestone tracker separate from relay BUILD; Phase 5 marker+registry at product merge. Drop if PIPELINE_HEALTH / chapter coordination already covers this on main.
- **trigger keywords:** pipeline health, milestone gate, closeoutonlychapterids, factory

### ntfy when vm-mirror PR merges during wait_for_vm

- **id:** `vm_mirror_merge_ntfy_during_inflight` · **priority:** medium · **status:** parked
- **added:** 2026-08-06
- **summary:** During wait_for_vm / BUILD_IN_FLIGHT, desktop may stay blind until pull. Notify via ntfy when an ops/vm-mirror PR merges so operator knows mirror status advanced without watching GitHub. Ops polish only — not a product chapter.
- **trigger keywords:** vm-mirror, wait_for_vm, in-flight, ntfy, operator, mirror

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
