# MSOS P1 stack routing — evidence status

**Chapter:** MSOS P1 stack / routing ADR  
**Status:** **COMPLETE** 2026-06-01  
**SELECTION:** [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md)  
**Sprint:** [`SPRINT_MSOS_P1_STACK_ROUTING.md`](SPRINT_MSOS_P1_STACK_ROUTING.md)  
**ADR:** [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md)

## Deliverables

| Artifact | Status |
|----------|--------|
| [`MSOS_P1_STACK_ROUTING_ADR.md`](MSOS_P1_STACK_ROUTING_ADR.md) | **PASS** — phased Next.js shell + Streamlit PPE |
| [`MSOS_FRONTIER.md`](MSOS_FRONTIER.md) | **PASS** — P1 decisions recorded |
| Relay worktree sprint import fix | **PASS** — `scripts/ppe_slice_worker.py` |

## ADR decisions (summary)

| Topic | Decision |
|-------|----------|
| PPE UI | Streamlit in `src/viz/` (unchanged) |
| MSOS shell | `apps/msos-web/` — Next.js 15 App Router + TypeScript (P2+) |
| Auth | Cloudflare Access on `app.marketstructureos.com` |
| PPE boundary (P4) | Caddy reverse proxy to Streamlit; no TS math port |
| P2 unblock | Storyboard v0.6 in-repo + gate OPEN |

## Gate

- `python -m pytest -q` green on closeout branch
- No dual smoke (docs-only chapter)

## Next SELECTION

**MSOS P2 homepage** — **blocked** until [`MSOS_STORYBOARD_GATE.md`](../VISION/MSOS_STORYBOARD_GATE.md) satisfied.
