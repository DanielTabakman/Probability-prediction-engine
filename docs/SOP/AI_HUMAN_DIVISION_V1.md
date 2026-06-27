# AI / human division v1

**Plane:** CONTROL-PLANE  
**Purpose:** Codify what in this repo is **AI-first**, **human-first**, or **hybrid** — so stewards and agents do not “AI-ify” trader surfaces or expand factory meta faster than product ships.

**Related:** [`BUILD_FACTORY_BOUNDARY_V1.md`](BUILD_FACTORY_BOUNDARY_V1.md) · [`REPO_LAYER_MAP_V1.md`](REPO_LAYER_MAP_V1.md) · [`PHASE_PLAN_SLICE_SCHEMA.md`](PHASE_PLAN_SLICE_SCHEMA.md)

---

## Three categories

| Category | Optimized for | Examples |
|----------|---------------|----------|
| **AI-first** | Agents, relay, bounded automation | Phase plans, `OPERATOR_STATUS.md`, IDE BUILD starters, `REPO_LAYER_PATH_PREFIXES.json`, gates, `.cursor/rules`, agent indexes |
| **Human-first** | Traders and operators | Streamlit implied lab, MSOS UI copy, vision/storyboard, phone ntfy buttons |
| **Hybrid** | Both; drift is the risk | Sprint specs, `AGENT_CONTINUITY_BRIEF.md`, frontier docs with synced markers |

**Design goal:** strengthen **AI-first factory** and **hybrid contracts** without changing human-first product UX.

---

## AI-first (agents own execution)

- **Direction SSOT:** [`ACTIVE_PRODUCT_DIRECTION.json`](ACTIVE_PRODUCT_DIRECTION.json)
- **Slice contracts:** [`PHASE_PLAN_SLICE_SCHEMA.md`](PHASE_PLAN_SLICE_SCHEMA.md)
- **Verdict → action:** `artifacts/orchestrator/OPERATOR_STATUS.md`
- **Navigation:** [`agent_index/`](agent_index/)
- **Preflight:** `python scripts/ppe_context_preflight.py --phase-plan … --slice-id …`

---

## Human-first (do not AI-ify)

Trader UI, public copy (`MSOS_PUBLIC_COPY_V1.md`), vision docs, operator buttons, plain-language SELECTION intent.

---

## Hybrid

Sprint markdown for humans; JSON `acceptance[]` / `touchSet` for agents. When duplicated, **JSON wins** for agents.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-06-27 | v1 — AI/human/hybrid split |
