# Documentation index

Start here when navigating the Probability Prediction Engine repo.

## Control plane (MVP1 — read first)

| Role | Path |
|------|------|
| **Integrated one-pager** | [`SOP/PPE_INTEGRATED_STATUS.md`](SOP/PPE_INTEGRATED_STATUS.md) |
| **Live steering / slice queue** | [`SOP/MVP1_FRONTIER.md`](SOP/MVP1_FRONTIER.md) |
| **Session handoff gate** | [`SOP/HANDOFF.md`](SOP/HANDOFF.md) |
| **Product canon** | [`VISION/PPE_MASTER_MVP1.md`](VISION/PPE_MASTER_MVP1.md) |
| **Health check history** | [`SOP/HEALTH_CHECK_LOG.md`](SOP/HEALTH_CHECK_LOG.md) |
| **Commit / test gates** | [`SOP/COMMIT_POLICY_V1.md`](SOP/COMMIT_POLICY_V1.md) · setup [`SOP/AGENT_GIT_SETUP.md`](SOP/AGENT_GIT_SETUP.md) |
| **Viz layer discipline (agents)** | [`SOP/VIZ_LAYER_DISCIPLINE_V1.md`](SOP/VIZ_LAYER_DISCIPLINE_V1.md) — thin shell, touch sets, parallel BUILD |
| **Platform evolution (layered stack)** | [`SOP/PLATFORM_EVOLUTION_V1.md`](SOP/PLATFORM_EVOLUTION_V1.md) |
| **Google Docs MCP (agents)** | [`SOP/MCP_GOOGLE_DOCS_SETUP.md`](SOP/MCP_GOOGLE_DOCS_SETUP.md) |
| **Google Docs control plane** | [`SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md`](SOP/GOOGLE_DOCS_CONTROL_PLANE_V1.md) — PPE / MSOS live mirror sync; Master read-only for Cursor |
| **Agent continuity (generated)** | [`SOP/AGENT_CONTINUITY_BRIEF.md`](SOP/AGENT_CONTINUITY_BRIEF.md) · role card [`SOP/AGENT_GUIDE_ROLE.md`](SOP/AGENT_GUIDE_ROLE.md) |
| **Active phase manifest** | [`SOP/ACTIVE_PHASE_MANIFEST.json`](SOP/ACTIVE_PHASE_MANIFEST.json) · [`SOP/ACTIVE_PHASE_MANIFEST.md`](SOP/ACTIVE_PHASE_MANIFEST.md) — input for **`run_ppe.cmd`** |

**Precedence:** pushed repo + accepted docs → `PPE_MASTER_MVP1` → `MVP1_FRONTIER` → `HANDOFF` → `OPERATING_RULES`. On slice-queue drift, **`MVP1_FRONTIER.md` wins.**

**Legacy (do not use for steering):** [`SOP/CURRENT_FRONTIER.md`](SOP/CURRENT_FRONTIER.md) and [`CURRENT_FRONTIER.md`](CURRENT_FRONTIER.md) are historical Phase 2 ledgers only.

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

## Context rules

- [`CONTEXT_RULES.md`](CONTEXT_RULES.md) — when to open a new Cursor thread vs stay in-session
- [`SOP/BUILD_PACKET_TEMPLATE.md`](SOP/BUILD_PACKET_TEMPLATE.md) — SLIM steward → BUILD handoff (paths only)

## Unified run

From repo root after steward sets the manifest to `READY`:

```bash
run_ppe.cmd --dry-run   # optional preflight
run_ppe.cmd             # full relay phase
run_ppe.cmd --status    # ACTIVE_RUN + last report summary
```
