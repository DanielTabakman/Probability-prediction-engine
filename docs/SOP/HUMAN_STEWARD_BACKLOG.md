# Human steward backlog

**Purpose:** Policy and architecture topics for **founder** review — not auto-loop work. See [`FOUNDER_OPERATOR_SURFACE_V1.md`](FOUNDER_OPERATOR_SURFACE_V1.md). Agents must not paste open items as founder todos in unrelated threads.

| When | Action |
|------|--------|
| **Weekly** (Monday digest) | `digest-only` — ntfy lists top titles; no action unless founder opts in |
| **Monthly** ([`OPERATING_CALENDAR_V1.md`](OPERATING_CALENDAR_V1.md)) | Founder charter pass — pick one item → `in_progress` |
| **When done** | Set `status: done` + `closed` date in JSON; run `render-md` |

**Machine source:** [`HUMAN_STEWARD_BACKLOG.json`](HUMAN_STEWARD_BACKLOG.json) · **Refresh this file:** `python scripts/ppe_human_backlog.py render-md`

> Founder charter work only — see FOUNDER_OPERATOR_SURFACE_V1.md. Agents must not append open items to operator-thread replies or weekly todo lists. Surface one item only when the user opens a steward/charter pass. Weekly ntfy digest lists open high-priority titles (digest-only).

## Open

### Steering coordination program v1

- **id:** `steering_coordination_program_v1` · **priority:** high · **category:** control-plane
- **added:** 2026-07-02
- **summary:** Harden relay vs steering drift: milestone gate hooks, docHints refresh, operator ACTIVE/NEXT headlines, drift gate codes, chapter lifecycle consolidate. Plan ready to charter.
- **policy question:** Charter Phase 1 now (P0) or wait for visual parity closeout?
- **notes:** Program: docs/SOP/STEERING_COORDINATION_PROGRAM_V1.md · SELECTION: POST_STEERING_COORDINATION_V1_SELECTION.md · Absorbs relay_decision_reconcile in Phase 3.

### Operator vs charter Cursor thread habit

- **id:** `operator_vs_charter_thread_habit` · **priority:** medium · **category:** operator
- **added:** 2026-06-30
- **summary:** Pin one long-lived Operator Cursor chat for what's next?; use Charter thread opener for UX, data, and SELECTION — never mix relay status into those threads.
- **policy question:** Which thread roles become pinned bookmarks vs fresh chats per slice?
- **notes:** Filed from THREAD_INSIGHTS closeout (control_plane_thread_roles).

### Operator lite status routing defaults

- **id:** `operator_lite_default_routing` · **priority:** medium · **category:** operator
- **added:** 2026-07-10
- **summary:** Make compact operator status the default read path: agents should read OPERATOR_STATUS_BRIEF first, add ppe_go --json-lite for machine consumers, and reserve full OPERATOR_STATUS/burst docs for explicit execution.
- **policy question:** Should normal status checks default to lite while full burst remains an explicit operator action?
- **notes:** Follow-up from operator status lite PR #5103; intended as the next small routing-habit slice after the compact artifacts exist.

### Relay decision model reconcile

- **id:** `relay_decision_reconcile` · **priority:** medium · **category:** control-plane
- **added:** 2026-06-17
- **summary:** AUTO_ADVANCE decision (or fold Rule 7b into CONTINUE); align CODEX_AUTONOMY §15 with implementation; auto PR on REPO_STATE_DRIFT for all slice kinds.
- **policy question:** How much steward judgment should remain vs machine CONTINUE?
- **notes:** Decision table + implementation tracked under steering_coordination_program_v1 Phase 3; close this item when Phase 3.1 ships.

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

### Observability — human vs informational stops

- **id:** `observability_human_signal` · **priority:** low · **category:** operator
- **added:** 2026-06-17
- **summary:** OPERATOR_STATUS needs_human vs informational_stop; skip ntfy on auto-recovered exit 20; workflow radar noise reduction.
- **policy question:** What deserves a phone ping vs weekly digest only?
- **notes:** Partial: LAST_RUN_REPORT auto_advance_promotion_recovery + phone procedural hints shipped 2026-06-17.

### Stripe operator prerequisites (phase 7b gate)

- **id:** `stripe_operator_prereq` · **priority:** high · **category:** operator
- **added:** 2026-06-19
- **summary:** Before msos_billing_stripe_v1 BUILD: Stripe account, test products/prices, API keys + webhook signing secret on VPS, Checkout return URLs. Also verify full E2E demo journey on production.
- **policy question:** When done, mark this item done and promote billing_stripe queue row from BLOCKED to READY.
- **notes:** Steward 2026-06-19: deferred until website demo-ready on production; Stripe accounts/setup pending.

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

### Product lane automation

- **id:** `product_lane_automation` · **priority:** high · **category:** architecture
- **added:** 2026-06-17
- **closed:** 2026-06-30
- **summary:** Auto-spawn IDE build on PRODUCT_BLOCKED, or switch product slices to ACP, or inline IDE build in the deterministic worker.
- **policy question:** Stay near-zero-API (local profile) vs pay for full autonomous product slices?
- **notes:** DECISION: Option A default — manual DESKTOP_BUILD / ppe_go paste (autoRemoteBuild=false). Mid-month burn boost: after day 16, if Cursor credits <35% used (operator records via ppe_remote_build_policy.cmd), autoRemoteBuild ON for rest of month. Implemented: remoteBuildPolicy in PPE_AUTO_OPERATOR.local.json + scripts/ppe_remote_build_policy.py.

### Founder vs operator surface v1

- **id:** `founder_operator_surface_v1` · **priority:** high · **category:** governance
- **added:** 2026-07-01
- **closed:** 2026-07-01
- **summary:** Codify founder (work ON product) vs agent factory (work IN product); stop surfacing relay/git/recovery as human todos.
- **policy question:** What stays founder-only forever vs delegated envelope?
- **notes:** Shipped FOUNDER_OPERATOR_SURFACE_V1.md + routing/rules/calendar/workflow patches.

### Founder / canon policy

- **id:** `founder_canon_policy` · **priority:** high · **category:** governance
- **added:** 2026-06-17
- **closed:** 2026-06-30
- **summary:** Which PPE_MASTER hard stops agents may auto-resolve; PR-only vs direct control-plane edits; cross-layer slice exceptions.
- **policy question:** What stays human-only forever vs delegated envelope?
- **notes:** DECISION: Balanced smart delegation — agents/control-plane auto-ship routine hygiene. human_only: secrets, pivotId/northStar, billing, prod access. steward_packet: PPE_MASTER, mixed-plane. DELEGATION_ENVELOPE_V1 + ppe_delegation_envelope.py.

### MSOS production live hookup (usable demo)

- **id:** `msos_production_live_hookup` · **priority:** high · **category:** operator
- **added:** 2026-06-19
- **closed:** 2026-06-21
- **summary:** Close relay-DONE vs production-usable gap: VPS .env (research CTA, embed), deploy latest main, Cloudflare Access on apex product routes, production witness PASS, tester journey sign-off. Charter: MSOS_PRODUCTION_LIVE_HOOKUP_V1.md; SSH via ppe_operator_ssh.local.cmd.
- **policy question:** Protect apex product routes only (recommended) or entire marketstructureos.com for early demo cohort?
- **notes:** Track A+C witness PASS 2026-06-21; Track B apex Access deferred. See MSOS_MCD_OPERATOR_WITNESS_V1_EVIDENCE_STATUS.md.

### VM loop-host git push credentials

- **id:** `vm_loop_host_git_push_credentials` · **priority:** high · **category:** ops
- **added:** 2026-06-26
- **closed:** 2026-06-27
- **summary:** run_ppe_local closeout on VM failed to push ops/loop-publish branch (wincredman / no TTY). Fix GitHub auth on ppeloop@desktop-caqll8k so steering docs reach main.
- **notes:** Verified 2026-06-27: gh auth logged in on VM; ops/loop-publish PRs merging (#413-426).

### Cross-venue collector VM task (ppeloop)

- **id:** `cross_venue_collector_vm_install` · **priority:** medium · **category:** ops
- **added:** 2026-06-28
- **closed:** 2026-06-29
- **summary:** After #529 merge on main: on ppeloop run git pull, install_cross_venue_collector_task.cmd (daily 07:15), smoke run_cross_venue_daily.cmd. Runbook: CROSS_VENUE_COLLECTOR_OPS_V1.md.
- **notes:** 2026-06-29: tasks confirmed on ppeloop (Horizon 06:30 + Cross-Venue 07:15 Ready); smoke run wrote 2026-06-29 snapshot + latest.md/json.

### ppeloop gh auth setup-git

- **id:** `ppeloop_gh_auth_setup_git` · **priority:** medium · **category:** ops
- **added:** 2026-06-27
- **closed:** 2026-06-27
- **summary:** VM loop cannot push ops/loop-publish branches; run gh auth setup-git on ppeloop@desktop-caqll8k
- **notes:** Same resolution as vm_loop_host_git_push_credentials — loop publish working.

## Changelog

| 2026-07-10 | Auto-render from JSON |
