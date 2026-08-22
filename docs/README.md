# Documentation index

Start here when navigating the Probability Prediction Engine repo.

## Control plane (MVP1 — read first)

| Role | Path |
|------|------|
| **ChatGPT + GitHub + Codex operating contract** | [`SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`](SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md) — GitHub SSOT, thread routing, task handoffs, and mandatory agent disagreement protocol |
| **Meeting → system integration** | [`SOP/MEETING_TO_SYSTEM_INTEGRATION_V1.md`](SOP/MEETING_TO_SYSTEM_INTEGRATION_V1.md) — every substantive thread becomes durable canon, structured work, or an explicit no-write outcome with minimal founder touchpoints |
| **Autobuilder strategic thesis** | [`SOP/AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md`](SOP/AUTOBUILDER_THESIS_AND_OPERATING_MODEL_V1.md) — core internal product, technical-founder function, operating principles, and anti-regression instruction |
| **Autobuilder accepted decision** | [`SOP/AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md`](SOP/AUTOBUILDER_CORE_INTERNAL_PRODUCT_DECISION_V1.md) — decision, alternatives, accepted costs, guardrails, and reconsideration triggers |
| **Autobuilder leverage scorecard** | [`SOP/AUTOBUILDER_LEVERAGE_SCORECARD_V1.md`](SOP/AUTOBUILDER_LEVERAGE_SCORECARD_V1.md) — validated output, founder attention, compute cost, rescue, rework, and review cadence |
| **Integrated one-pager** | [`SOP/PPE_INTEGRATED_STATUS.md`](SOP/PPE_INTEGRATED_STATUS.md) |
| **Live steering / slice queue** | [`SOP/MVP1_FRONTIER.md`](SOP/MVP1_FRONTIER.md) (MVP1 engine) · [`SOP/MSOS_FRONTIER.md`](SOP/MSOS_FRONTIER.md) (MSOS website) |
| **MSOS website program canon** | [`SOP/MSOS_WEBSITE_PROGRAM.md`](SOP/MSOS_WEBSITE_PROGRAM.md) |
| **Product focus / anti-drift** | [`SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md`](SOP/PRODUCT_FOCUS_PLAYBOOK_V1.md) — wedge proof, priorities, validation gates |
| **Operating calendar** | [`SOP/OPERATING_CALENDAR_V1.md`](SOP/OPERATING_CALENDAR_V1.md) — weekly / monthly / quarterly steward cadence |
| **P8 validation report** | [`SOP/MSOS_P8_VALIDATION_REPORT_V1.md`](SOP/MSOS_P8_VALIDATION_REPORT_V1.md) — auto-select gate until **COMPLETE** |
| **Session handoff gate** | [`SOP/HANDOFF.md`](SOP/HANDOFF.md) |
| **Product canon** | [`VISION/PPE_MASTER_MVP1.md`](VISION/PPE_MASTER_MVP1.md) |
| **Health check history** | [`SOP/HEALTH_CHECK_LOG.md`](SOP/HEALTH_CHECK_LOG.md) |
| **Commit / test gates** | [`SOP/COMMIT_POLICY.md`](SOP/COMMIT_POLICY.md) |
| **Google Docs (legacy/manual fallback)** | [`SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md`](SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md) · [`SOP/MCP_GOOGLE_DOCS_SETUP.md`](SOP/MCP_GOOGLE_DOCS_SETUP.md) — non-authoritative; verify against GitHub before use |
| **Repo layer map (agents)** | [`SOP/REPO_LAYER_MAP_V1.md`](SOP/REPO_LAYER_MAP_V1.md) · presets [`SOP/REPO_LAYER_PATH_PREFIXES.json`](SOP/REPO_LAYER_PATH_PREFIXES.json) · [`SOP/PARALLEL_AGENT_CHECKLIST_V1.md`](SOP/PARALLEL_AGENT_CHECKLIST_V1.md) |
| **Agent continuity (generated)** | [`SOP/AGENT_CONTINUITY_BRIEF.md`](SOP/AGENT_CONTINUITY_BRIEF.md) · role card [`SOP/AGENT_GUIDE_ROLE.md`](SOP/AGENT_GUIDE_ROLE.md) |
| **SOP discovery (agents)** | `python scripts/resolve_sop.py --topic "<phrase>" --json` · index [`SOP/CHAPTER_DOC_INDEX.json`](SOP/CHAPTER_DOC_INDEX.json) · [`SOP/AGENT_ROUTING_V1.md`](SOP/AGENT_ROUTING_V1.md) |
| **Active phase manifest** | [`SOP/ACTIVE_PHASE_MANIFEST.json`](SOP/ACTIVE_PHASE_MANIFEST.json) · [`SOP/ACTIVE_PHASE_MANIFEST.md`](SOP/ACTIVE_PHASE_MANIFEST.md) — input for **`run_ppe.cmd`** |
| **Dev changelog (rolling)** | [`RELEASES/DEV_CHANGELOG.md`](RELEASES/DEV_CHANGELOG.md) — daily / merge release notes on `main` |
| **Weekly digest (human)** | [`RELEASES/WEEKLY_DIGEST.md`](RELEASES/WEEKLY_DIGEST.md) — Monday summary of prior week |

**Precedence:** accepted files on GitHub `main` → explicitly approved open PR → fresh code/test/deployment evidence → current thread proposals → historical chats, Google Docs, or stale mirrors. Within accepted repo docs: `PPE_MASTER_MVP1` → `MVP1_FRONTIER` (MVP1 engine) / `MSOS_FRONTIER` (MSOS website) → `HANDOFF` → `OPERATING_RULES`. On slice-queue drift, the matching frontier wins for its track. Agent disagreement must be surfaced using the Coordination Status contract; it must not be silently resolved.

**Legacy (do not use for steering):** [`SOP/CURRENT_FRONTIER.md`](SOP/CURRENT_FRONTIER.md) and [`CURRENT_FRONTIER.md`](CURRENT_FRONTIER.md) are historical Phase 2 ledgers only. Google Docs are also non-authoritative unless reconfirmed against GitHub.

## By plane

| Plane | Directory | Contents |
|-------|-----------|----------|
| **SOP / workflow** | [`SOP/`](SOP/) | Operating rules, relay, steward protocol, sprints, evidence status, phase plans (`SOP/PHASE_PLANS/`) |
| **Vision** | [`VISION/`](VISION/) | MVP1 master canon, vision templates |
| **Deploy** | [`DEPLOY/`](DEPLOY/) | Production and early-customer runbooks |
| **Agents** | [`agents/`](agents/) | Role briefs (app engineer, QA smoke, etc.) |
| **Control plane prompts** | [`CONTROL_PLANE/PROMPTS/`](CONTROL_PLANE/PROMPTS/) | Manager/worker prompt standards |

## Deploy path picker

| Your situation | Use |
|----------------|-----|
| **Production VPS** (Caddy, Cloudflare Access, dual Streamlit) | [`DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md) |
| **GitHub Actions → VPS** | [`DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md`](DEPLOY/GITHUB_ACTIONS_VPS_DEPLOY.md) |
| **Early / Render-style** (historical) | [`DEPLOY/RUNBOOK_CLOUDFLARE_ACCESS_RENDER.md`](DEPLOY/RUNBOOK_CLOUDFLARE_ACCESS_RENDER.md) |

Release protocol: [`SOP/PRODUCTION_DEPLOY_PROTOCOL.md`](SOP/PRODUCTION_DEPLOY_PROTOCOL.md) · Demo checklist: [`SOP/DEMO_UI_RELEASE_CHECKLIST.md`](SOP/DEMO_UI_RELEASE_CHECKLIST.md)

## Product / design (root `docs/`)

- [`PLAN.md`](PLAN.md) — stack, data sources, canonical events
- [`PRODUCT_THESIS.md`](PRODUCT_THESIS.md) — north star
- [`SEMANTIC_CONTRACTS.md`](SEMANTIC_CONTRACTS.md) — market-implied vs belief vs disagreement
- [`IMPLIED_LAB_SMOKE.md`](IMPLIED_LAB_SMOKE.md) — Playwright UI smoke procedures

## Bounded MSOS initiatives

| Initiative | Status | Execution |
|------------|--------|-----------|
| [`VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md`](VISION/MSOS/MSOS_HEDGE_BACKED_EVENT_LIQUIDITY_INITIATIVE_V0_1.md) | Chartered for feasibility; not current BUILD scope | [`SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md`](SOP/HEDGE_BACKED_EVENT_LIQUIDITY_STAGE0_CODEX_PACKET_V1.md) — evidence-only Stage 0 handoff |

## Context rules

- [`CONTEXT_RULES.md`](CONTEXT_RULES.md) — when to open a new Cursor or ChatGPT thread vs stay in-session
- [`SOP/MEETING_TO_SYSTEM_INTEGRATION_V1.md`](SOP/MEETING_TO_SYSTEM_INTEGRATION_V1.md) — integrate durable meeting outcomes incrementally; do not require founder copy-paste or end-of-chat reminders
- [`SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md`](SOP/CHATGPT_GITHUB_CODEX_CONTROL_PLANE_V1.md) — ChatGPT Project layout, GitHub handoff packets, and reconciliation protocol
- [`SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md`](SOP/CONTEXT_WINDOW_CLOSEOUT_V1.md) — end a long chat: push/pull sweep, narrative, backlog triage
- [`SOP/BUILD_PACKET_TEMPLATE.md`](SOP/BUILD_PACKET_TEMPLATE.md) — SLIM steward → BUILD handoff (paths only; includes layer presets)
- [`SOP/REPO_LAYER_MAP_V1.md`](SOP/REPO_LAYER_MAP_V1.md) — MSOS / PPE / factory folder boundaries

## Unified run

From repo root after steward sets the manifest to `READY`:

```bash
run_ppe.cmd --dry-run   # optional preflight
run_ppe.cmd             # full relay phase
run_ppe.cmd --status    # ACTIVE_RUN + last report summary
```

**No API credits (IDE-native):** [`SOP/PPE_IDE_NATIVE_OPERATOR_V1.md`](SOP/PPE_IDE_NATIVE_OPERATOR_V1.md) · [checklist](SOP/PPE_IDE_NATIVE_OPERATOR_CHECKLIST.md) — `run_ppe_auto_local_loop.cmd`; IDE BUILD → `mark_ide_product_ready.cmd` → `run_ppe_local.cmd`.

**With API credits:** `run_ppe_auto_acp_loop.cmd` — see [`SOP/PPE_CONTINUOUS_OPERATOR.md`](SOP/PPE_CONTINUOUS_OPERATOR.md).