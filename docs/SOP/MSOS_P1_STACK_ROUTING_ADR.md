# MSOS P1 — Stack and routing ADR

**Status:** Accepted (2026-06-01)  
**Chapter:** MSOS P1 stack routing  
**Sprint:** [`SPRINT_MSOS_P1_STACK_ROUTING.md`](SPRINT_MSOS_P1_STACK_ROUTING.md)  
**Canon:** [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) · [`PPE_MASTER_MVP1.md`](../VISION/PPE_MASTER_MVP1.md)

---

## Context

Market Structure OS (MSOS) needs a customer-facing platform shell (homepage, Command Center, Strategy Lab) while the Probability Prediction Engine (PPE) implied lab remains the authoritative math surface in Python. The repo today ships production PPE as **Streamlit** only; there is no separate frontend framework in-tree.

P1 must choose the smallest stable path for MSOS UI **without** rewriting PPE math or widening MVP1 evidence contracts.

---

## Inventory (repo ground truth)

| Asset | Location / notes |
|-------|------------------|
| PPE implied lab (product) | [`src/viz/`](../../src/viz/) — Streamlit [`app.py`](../../src/viz/app.py) |
| Production deploy | [`docker-compose.yml`](../../docker-compose.yml) — `app_demo` (apex), `app_full` (`app.*`) |
| Edge routing | [`Caddyfile`](../../Caddyfile) — host-based split |
| Auth | Cloudflare Access on **`app.marketstructureos.com`** ([`RUNBOOK_VPS_CLOUDFLARE_ACCESS.md`](../DEPLOY/RUNBOOK_VPS_CLOUDFLARE_ACCESS.md)) |
| Tests | `pytest`; dual implied-lab smoke scripts (MVP1 witness only) |
| MSOS shell (future) | **Not in repo yet** — chartered at P2 as `apps/msos-web/` |

---

## Decisions

### 1. Frontend root strategy

| Layer | Decision |
|-------|----------|
| **PPE engine UI** | **Keep Streamlit** in `src/viz/`. No TypeScript port of calculations, payoff engine, or MVP1 decision surface. |
| **MSOS platform shell (P2–P3)** | Add **`apps/msos-web/`** — **Next.js 15 App Router + TypeScript** for public homepage (P2) and authenticated platform chrome / Command Center routes (P3). |
| **Rationale** | Repo has zero React/Next today; storyboard-driven marketing and authenticated shell need a proper web app. Streamlit alone is a poor fit for investor-facing homepage and multi-route platform IA. [`ARCHITECT_NOTES.md`](../ARCHITECT_NOTES.md) “keep Streamlit” applies to **PPE core**, not MSOS shell. |

### 2. Auth model

| Surface | Auth |
|---------|------|
| **`marketstructureos.com` (apex)** | Public **demo** Streamlit (no login); snapshots disabled — unchanged. |
| **`app.marketstructureos.com`** | **Cloudflare Access** (Google login) + full Streamlit lab + persisted snapshots — unchanged. |
| **MSOS Next shell (P2+)** | Public routes on apex without Access; authenticated MSOS routes behind **same Cloudflare Access** policies as today (extend policies when MSOS routes ship; no custom auth server in P1–P3). |

### 3. PPE integration boundary (P4)

| Priority | Mechanism |
|----------|-----------|
| **Primary** | **Caddy reverse proxy** from MSOS host to existing Streamlit upstream — path prefix (e.g. `/strategy-lab/*`) or dedicated subdomain (e.g. `lab.marketstructureos.com` → `app_full:8501`). Same-origin preferred for cookies and CSP. |
| **Fallback** | iframe to `app.marketstructureos.com` only if proxy path is blocked by Streamlit URL assumptions (document in P4 evidence if used). |
| **Deferred** | REST/GraphQL API exposing PPE math to the frontend — not before P5 thesis persistence needs are defined. |

**Non-widening:** MSOS UI displays PPE outputs; it does not reimplement distributions, disagreement, or verification logic in TypeScript.

### 4. Deploy path

| Phase | Deploy |
|-------|--------|
| **P1 (this ADR)** | No new containers or CI jobs. |
| **P2** | Add **`msos_web`** service to existing VPS **Docker Compose + Caddy** stack; build `apps/msos-web` in CI when that directory exists. |
| **PPE** | Existing `app_demo` / `app_full` images unchanged until a deliberate PPE deploy chapter. |

### 5. P2 unblock criteria

P2 (design system + public homepage) may be SELECTION'd only when **all** are true:

1. This ADR merged on `main`.
2. **Market Structure OS Website Storyboard v0.6** assets in-repo under [`docs/VISION/MSOS/storyboard-v0.6/`](../VISION/MSOS_STORYBOARD_GATE.md).
3. [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) updated to **OPEN** with file manifest.
4. [`PHASE_CHAPTER_BACKLOG.json`](PHASE_CHAPTER_BACKLOG.json) row `msos_p2_homepage` moved from `blocked` → `queued` with relay plan.

**Status (2026-06-02):** Criteria 2–4 satisfied; P2 **READY** for relay SELECTION ([`POST_MSOS_P2_HOMEPAGE_SELECTION.md`](POST_MSOS_P2_HOMEPAGE_SELECTION.md)).

---

## Consequences

### Positive

- Clear separation: **MSOS shell** (Next) vs **PPE lab** (Streamlit).
- Reuses production VPS, Caddy, and Cloudflare patterns already proven on demo + app hosts.
- MVP1 pytest/smoke gates stay focused on Streamlit; MSOS adds Node CI only when `apps/msos-web` exists.

### Tradeoffs

- Two UI stacks to operate (Next + Streamlit) until/unless a future SELECTION consolidates.
- P4 proxy integration requires Caddy config + Streamlit `baseUrlPath` / header validation in a dedicated chapter.

### Explicit non-goals (P1)

- Homepage or Command Center UI implementation
- New `docker-compose` services or Cloudflare policy edits
- Porting PPE calculations to TypeScript
- iframe-first Strategy Lab without trying reverse proxy first

---

## Phased roadmap (MSOS program)

| Priority | Deliverable | Stack touch |
|----------|-------------|-------------|
| **P2** | Public homepage + design tokens | `apps/msos-web`, Caddy route on apex |
| **P3** | Authenticated shell + Command Center | Next routes + CF Access |
| **P4** | Strategy Lab / PPE entry | Caddy proxy to Streamlit; honest Live/Soon labels |
| **P5+** | Thesis persistence | May introduce read APIs; not decided in P1 |

---

## Related documents

- [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) — live MSOS slice queue
- [`MSOS_WEBSITE_PROGRAM.md`](MSOS_WEBSITE_PROGRAM.md) — waterfall P0–P8
- [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) — P2+ visual gate
- [`SPRINT_MSOS_P1_STACK_ROUTING.md`](SPRINT_MSOS_P1_STACK_ROUTING.md) — sprint acceptance
