# Forward Consistency program v1

**Purpose:** Canonical map for the **Forward Consistency Pipeline** — put-call parity synthetic forward vs tradable future/perp, asset-catalog-driven, Strategy Lab–first.

**As-of:** 2026-06-28 · **Milestone:** [`MILESTONE_FORWARD_CONSISTENCY_V1.md`](MILESTONE_FORWARD_CONSISTENCY_V1.md)

**Vision contract:** [`docs/VISION/FORWARD_CONSISTENCY/JSON_CONTRACT_V1.md`](../VISION/FORWARD_CONSISTENCY/JSON_CONTRACT_V1.md)

**Trader milestone tie-in:** [`MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md`](MILESTONE_TRADER_WORKFLOW_INTEGRATION_V1.md) — teaches market literacy before thesis/disagreement loops.

---

## North star

**See whether options and futures/perp quote the same executable forward for a given asset/expiry — and when they do not, know if it is worth human attention.**

Spot vs future basis and spot vs chart median are **shown but labeled not comparable** for arb.

---

## Prerequisites

| Chapter | Status | Delivers |
|---------|--------|----------|
| `ppe_tradeable_universe_v1` | **COMPLETE** | Asset catalog + registry |
| `msos_strategy_lab_embed_shell_v1` | **COMPLETE** | Native Strategy Lab chart shell |

---

## Chapter sequence (relay order)

| # | Chapter | Priority | Blocked until | Delivers |
|---|---------|----------|---------------|----------|
| 0 | `forward_consistency_charter_v1` | MEDIUM | — | Program + milestone + JSON contract + backlog |
| 1 | **`forward_consistency_v1`** | MEDIUM | charter COMPLETE | Engine, API, debug spike, Strategy Lab panel (Deribit BTC/ETH) — **PR #447** |
| 2 | `forward_consistency_bybit_v1` | MEDIUM | v1 COMPLETE | Bybit quote adapter; SOL tier-1 |
| 3 | `forward_consistency_surfaces_v1` | LOW | bybit COMPLETE | Horizon strip + Command Center glance |
| 4a | `forward_consistency_archive_v1` | LOW · DEFER | surfaces COMPLETE | Snapshot archive + persistence |
| 4b | `forward_consistency_expression_bridge_v1` | LOW · DEFER | archive + expression UX | Simulated legs → Expression Lab prefill |

---

## Operator artifacts

| Artifact | Path |
|----------|------|
| Live check API | `GET /ppe-display-api/forward-consistency.json?asset=BTC&expiry=YYYY-MM-DD` |
| Engine | `src/engine/forward_consistency.py` |
| Venue quotes | `src/data/forward_consistency_quotes.py` |
| Display boundary | `src/viz/forward_consistency_boundary.py` |
| Streamlit debug | `src/viz/forward_consistency_spike.py` (`?forward_consistency=1`) |
| MSOS panel | `apps/msos-web/src/components/ForwardConsistencyPanel.tsx` |

---

## Status enum (conservative)

| Status | Meaning |
|--------|---------|
| `NO_ARB` | Future market inside synthetic band after costs |
| `WATCH` | Gross edge positive but net inside cost buffer |
| `POSSIBLE_ARB` | Net edge &gt; 0 after estimated costs (research flag only) |
| `BAD_DATA` | Missing/crossed quotes or no reliable strikes |
| `NOT_COMPARABLE` | Venue/instrument grammar unsupported (e.g. equity v1) |

**Bid/ask only** for edge math — never midpoint.

---

## What the program excludes (v1–v3)

| Excluded | Why |
|----------|-----|
| Live execution | Separate future milestone |
| TS parity math | Layer rule — Python only |
| Polymarket / prediction-market parity | Cross-venue scan owns that edge type |
| Auto-trading on `POSSIBLE_ARB` | Recommendation theater |

---

## Source docs (by chapter)

| Chapter | SELECTION | Sprint | Relay |
|---------|-----------|--------|-------|
| charter | [`POST_FORWARD_CONSISTENCY_CHARTER_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_CHARTER_V1_SELECTION.md) | [`SPRINT_FORWARD_CONSISTENCY_CHARTER_V1.md`](SPRINT_FORWARD_CONSISTENCY_CHARTER_V1.md) | [`forward_consistency_charter_v1_relay.json`](PHASE_PLANS/forward_consistency_charter_v1_relay.json) |
| v1 | [`POST_FORWARD_CONSISTENCY_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_V1_SELECTION.md) | [`SPRINT_FORWARD_CONSISTENCY_V1.md`](SPRINT_FORWARD_CONSISTENCY_V1.md) | [`forward_consistency_v1_relay.json`](PHASE_PLANS/forward_consistency_v1_relay.json) |
| bybit | [`POST_FORWARD_CONSISTENCY_BYBIT_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_BYBIT_V1_SELECTION.md) | [`SPRINT_FORWARD_CONSISTENCY_BYBIT_V1.md`](SPRINT_FORWARD_CONSISTENCY_BYBIT_V1.md) | [`forward_consistency_bybit_v1_relay.json`](PHASE_PLANS/forward_consistency_bybit_v1_relay.json) |
| surfaces | [`POST_FORWARD_CONSISTENCY_SURFACES_V1_SELECTION.md`](POST_FORWARD_CONSISTENCY_SURFACES_V1_SELECTION.md) | [`SPRINT_FORWARD_CONSISTENCY_SURFACES_V1.md`](SPRINT_FORWARD_CONSISTENCY_SURFACES_V1.md) | [`forward_consistency_surfaces_v1_relay.json`](PHASE_PLANS/forward_consistency_surfaces_v1_relay.json) |
