---
archived: true
chapter_id: msos_mcd_production_witness_v1
closed: 2026-06-21
---

# MCD operator witness v1 — evidence status

**Chapter:** `msos_mcd_production_witness_v1`  
**Purpose:** Witness-verify [`MINIMUM_CREDIBLE_DEMO_GATE_V1.md`](MINIMUM_CREDIBLE_DEMO_GATE_V1.md) criteria on production after embed shell + MCD engineering path COMPLETE.  
**Status:** **COMPLETE** 2026-06-21

| Slice | Status | Notes |
|-------|--------|-------|
| MSOS-MCDWitV1-Control-Slice001 | **CLOSED** | Charter + queue align |
| MSOS-MCDWitV1-Witness-Slice002 | **CLOSED** | Production HTTP witness + MCD criteria matrix |
| MSOS-MCDWitV1-Closeout-Slice003 | **CLOSED** | MCD gate PASSED + production live hookup sign-off |

## MCD criteria matrix (production witness 2026-06-21)

Artifact: `artifacts/health/msos_production_demo_witness.json` · pytest: `tests/test_msos_web_strategy_lab.py`, `tests/test_implied_lab_embed_display_boundary.py`

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | MSOS opens cleanly | **PASS** | All journey routes HTTP 200; `sign_in_access_gate` OK on `app.marketstructureos.com` |
| 2 | Platform-shaped shell | **PASS** | Visual parity chapters COMPLETE; homepage + shell phrases present |
| 3 | PPE inside MSOS | **PASS** | `/strategy-lab` exposes `ppe-embed`, `display payload`, `Live via PPE`, chromeless path |
| 4 | Market-implied legible | **PASS** | Strategy Lab embed region + PPE labels in production HTML |
| 5 | Belief / disagreement compare | **PASS** | `/strategy-lab/confirm` thesis flow; disagreement copy on Strategy Lab |
| 6 | Disagreement kind visible | **PASS** | "Candidate: narrower-range disagreement" + charter disagreement language in UI |
| 7 | One expression path | **PASS** | `/strategy-lab/expression` sim-only path loads |
| 8 | Save / review / history visible | **PASS** | Thesis save, history "review", server persistence chapter COMPLETE |
| 9 | No 20-minute explanation | **PASS (operator)** | Production journey walkable via [`DEMO_OPERATOR_SCRIPT.md`](DEMO_OPERATOR_SCRIPT.md); external timing → first [`TRADER_WORKFLOW_RESEARCH_V1.md`](TRADER_WORKFLOW_RESEARCH_V1.md) cohort row |

## Production live hookup acceptance (Track A+C)

| Check | Result |
|-------|--------|
| VPS stack reachable | **PASS** — all `marketstructureos.com` routes 200 |
| Research beta CTA | **PASS** — `research_beta_cta` check OK |
| Signed-in journey (HTTP) | **PASS** — full storyboard route chain |
| Cloudflare Access on `app.*` | **PASS** |
| Track B (apex Access policies) | **DEFER** — public homepage; product routes ungated until multi-user expansion SELECTION'd |

**Steward note:** VPS deploy from desktop requires `ppe_operator_ssh.local.cmd` (not configured on this host). Production HTML matches post-embed-shell contract without manual deploy this session.
